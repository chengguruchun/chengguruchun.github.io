#!/usr/bin/env python3
"""Run an advisory critic over one changed article.

The critic never edits the article. It emits JSON + Markdown under
api/critic/runs/; the workflow publishes Markdown to a GitHub Issue.
"""
from __future__ import annotations
import argparse, html, json, os, re, subprocess, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYSTEM_PROMPT = r"""
You are Critic Lab, an adversarial reviewer for a personal AI-agent engineering
knowledge base. Do not praise or rewrite the article. Challenge it constructively.

Review five dimensions:
1. logic: unsupported jumps, ambiguous definitions, circular reasoning, overly
   strong conclusions;
2. counterexamples: concrete cases that could falsify or limit the thesis;
3. novelty: distinguish established ideas from potentially distinctive
   combinations. Never claim originality as fact. Without external browsing,
   call novelty a preliminary assessment;
4. facts: flag time-sensitive, version-sensitive, numerical, attributed, or
   primary-source-dependent claims;
5. missing_points: important boundary conditions or engineering details that
   materially affect feasibility.

Rules:
- Separate article-internal reasoning from external evidence.
- Never invent sources or citations.
- Do not turn an engineering heuristic into a universal law.
- Prefer a small number of high-signal findings over generic writing advice.
- For important criticism, explain why it matters and give a concrete test,
  counterexample, or clarification.
- The article may intentionally present evolving thinking; identify hypotheses
  that should be labeled as hypotheses rather than treating that as a flaw.

Return ONLY valid JSON with this exact top-level shape:
{
  "status": "clear|needs_review|major_review",
  "summary": "one short paragraph",
  "logic": [{"severity":"high|medium|low","claim":"...","issue":"...","why_it_matters":"...","test_or_fix":"..."}],
  "counterexamples": [{"severity":"high|medium|low","thesis":"...","counterexample":"...","boundary":"..."}],
  "novelty": [{"claim":"...","assessment":"established|common_combination|potentially_distinctive|unknown","basis":"..."}],
  "facts": [{"severity":"high|medium|low","claim":"...","reason_to_verify":"...","preferred_source":"official|primary|multiple_independent"}],
  "missing_points": [{"severity":"high|medium|low","point":"...","why_it_matters":"..."}],
  "recommended_changes": ["..."],
  "evidence_level": "E0|E1|E2|E3|E4"
}
"""


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)


def strip_html(raw: str) -> str:
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def article_catalog(current: str) -> list[str]:
    items = []
    pages = list(Path("articles").glob("*.html")) + list(Path("bench").glob("*.html"))
    for p in sorted(pages):
        if p.name == "index.html" or str(p) == current:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
            items.append(f"{p.as_posix()}: {strip_html(m.group(1)) if m else p.stem}")
        except OSError:
            pass
    return items[:100]


MOVED_ARTICLES = {
    "articles/agent-runtime-model-learning-runtime.html": "bench/agent-runtime-model-learning-runtime.html",
}


def rebuild_index(out: Path) -> None:
    """Rewrite api/critic/runs/index.json from the JSON reports on disk."""
    runs = []
    for path in sorted(out.glob("*.json")):
        if path.name == "index.json" or path.name.startswith("."):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        article = str(data.get("article") or "")
        moved = MOVED_ARTICLES.get(article)
        if moved and not Path(article).exists() and Path(moved).exists():
            data["article"] = moved
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            md_path = path.with_suffix(".md")
            if md_path.exists():
                md = md_path.read_text(encoding="utf-8")
                md_path.write_text(md.replace(f"Article: `{article}`", f"Article: `{moved}`"), encoding="utf-8")
            article = moved
        slug = Path(article).stem if article.endswith(".html") else path.stem.rsplit("-", 1)[0]
        summary = re.sub(r"\s+", " ", str(data.get("summary") or "")).strip()
        if len(summary) > 220:
            summary = summary[:217] + "..."
        runs.append({
            "id": path.stem,
            "article": slug,
            "article_slug": slug,
            "status": data.get("status"),
            "summary": summary,
            "commit": data.get("commit"),
            "generated_at": data.get("generated_at"),
            "json": f"/api/critic/runs/{path.name}",
            "markdown": f"/api/critic/runs/{path.stem}.md",
        })
    runs.sort(key=lambda row: str(row.get("generated_at") or ""), reverse=True)
    payload = {
        "name": "Critic Lab runs",
        "kind": "read",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(runs),
        "runs": runs,
    }
    (out / "index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"critic index {len(runs)} runs")


def clean_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)


def call_critic(prompt: str) -> tuple[dict, str]:
    provider = os.environ.get("CRITIC_PROVIDER", "deepseek").lower()
    if provider == "deepseek":
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")
        model = os.environ.get("CRITIC_MODEL", "deepseek-chat")
        url = "https://api.deepseek.com/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        provider_name = "DeepSeek"
    elif provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        model = os.environ.get("CRITIC_MODEL", "gpt-5.6-luna")
        url = "https://api.openai.com/v1/responses"
        payload = {
            "model": model,
            "input": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        provider_name = "OpenAI"
    else:
        raise RuntimeError(f"Unsupported CRITIC_PROVIDER: {provider}")

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{provider_name} API HTTP {exc.code}: {detail[:1000]}") from exc

    if provider == "deepseek":
        text = data["choices"][0]["message"]["content"]
    else:
        chunks = []
        for item in data.get("output", []):
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                    chunks.append(content["text"])
        text = "\n".join(chunks).strip() or data.get("output_text", "")
    return clean_json(text), model


def render_markdown(report: dict, article: str, sha: str, model: str) -> str:
    lines = ["## 🤖 Critic Lab Report", "", f"Article: `{article}`", f"Commit: `{sha}`",
             f"Model: `{model}`", f"Status: **{report.get('status','unknown')}**", "",
             report.get("summary", ""), ""]
    def section(title, key, renderer):
        values = report.get(key) or []
        lines.extend([f"## {title}", ""])
        if not values:
            lines.extend(["No high-signal findings.", ""]); return
        for value in values:
            lines.extend([renderer(value), ""])
    section("1. Logic", "logic", lambda x: f"- **{x.get('severity','?').upper()}** — {x.get('claim','')}\n  - Issue: {x.get('issue','')}\n  - Why it matters: {x.get('why_it_matters','')}\n  - Test / fix: {x.get('test_or_fix','')}")
    section("2. Counterexamples", "counterexamples", lambda x: f"- **{x.get('severity','?').upper()}** — Thesis: {x.get('thesis','')}\n  - Counterexample: {x.get('counterexample','')}\n  - Boundary: {x.get('boundary','')}")
    section("3. Novelty", "novelty", lambda x: f"- **{x.get('assessment','unknown')}** — {x.get('claim','')}\n  - Basis: {x.get('basis','')}")
    section("4. Facts", "facts", lambda x: f"- **{x.get('severity','?').upper()}** — {x.get('claim','')}\n  - Why verify: {x.get('reason_to_verify','')}\n  - Preferred source: `{x.get('preferred_source','')}`")
    section("5. Missing Points", "missing_points", lambda x: f"- **{x.get('severity','?').upper()}** — {x.get('point','')}\n  - Why it matters: {x.get('why_it_matters','')}")
    lines.extend(["## 6. Recommended Changes", ""])
    for item in report.get("recommended_changes") or []: lines.append(f"- {item}")
    if not report.get("recommended_changes"): lines.append("No changes required from this review.")
    lines.extend(["", f"Evidence level: `{report.get('evidence_level','E0')}`", "",
                  "> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article")
    parser.add_argument("--before")
    parser.add_argument("--after")
    parser.add_argument("--output-dir", default="api/critic/runs")
    parser.add_argument("--reindex", action="store_true", help="Rebuild index.json from reports on disk")
    args = parser.parse_args()
    if args.reindex:
        rebuild_index(Path(args.output_dir))
        return 0
    if not args.article or not args.before or not args.after:
        parser.error("--article, --before, and --after are required unless --reindex")
    article_path = Path(args.article)
    article_text = strip_html(article_path.read_text(encoding="utf-8"))
    try: diff = run(["git", "diff", args.before, args.after, "--", args.article])
    except subprocess.CalledProcessError: diff = "(diff unavailable)"
    prompt = f"""
ARTICLE PATH:
{args.article}

CURRENT ARTICLE TEXT:
{article_text[:60000]}

GIT DIFF FOR THIS CHANGE:
{diff[:30000]}

OTHER ARTICLES IN THIS KNOWLEDGE LAB (local overlap only):
{chr(10).join(article_catalog(args.article))}

Review this as an evolving engineering hypothesis. Pay special attention to
whether "Domain Object × Action = Tool" is a definition, heuristic, or universal
claim; whether tool consolidation can cause parameter explosion; and whether
runtime/risk/verification boundaries are being conflated with domain boundaries.
"""
    report, model = call_critic(prompt)
    report.update({"article": args.article, "commit": args.after,
                   "generated_at": datetime.now(timezone.utc).isoformat(), "model": model})
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    stem = f"{article_path.stem}-{args.after[:12]}"
    (out / f"{stem}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / f"{stem}.md").write_text(render_markdown(report, args.article, args.after, model), encoding="utf-8")
    rebuild_index(out)
    print(json.dumps({"status": report.get("status"), "article": args.article, "model": model}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
