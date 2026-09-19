#!/usr/bin/env python3
"""Run an advisory critic over one changed article.

The critic never edits the article. It emits a JSON + Markdown report under
api/critic/runs/; the workflow publishes the Markdown to a GitHub Issue.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.openai.com/v1/responses"

SYSTEM_PROMPT = r"""
You are Critic Lab, an adversarial reviewer for a personal AI-agent engineering
knowledge base. Your job is NOT to praise, rewrite, or make the author's
political/career decisions. Challenge the article constructively.

Review five dimensions:
1. logic: unsupported jumps, ambiguous definitions, circular reasoning, overly
   strong conclusions;
2. counterexamples: concrete cases that could falsify or limit the thesis;
3. novelty: distinguish common/established ideas from potentially distinctive
   combinations. Never claim originality as a fact. If no external browsing is
   available, explicitly say novelty is only a preliminary assessment;
4. facts: flag claims that are time-sensitive, version-sensitive, numerical,
   attributed, or likely to require primary-source verification;
5. missing_points: important boundary conditions or engineering details that
   materially affect feasibility.

Important reviewing rules:
- Separate article-internal reasoning from externally verified evidence.
- Do not invent sources or citations.
- Do not turn a plausible engineering heuristic into a universal law.
- Prefer a small number of high-signal findings over generic writing advice.
- For every important criticism, explain why it matters and give a concrete
  test, counterexample, or clarification that could resolve it.
- The article may intentionally present the author's evolving thinking; do not
  punish it merely for being a hypothesis. Instead, identify where the text
  should label a hypothesis as such.

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
    items: list[str] = []
    for p in sorted(Path("articles").glob("*.html")):
        if str(p) == current:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<h1[^>]*>(.*?)</h1>", text, flags=re.I | re.S)
            title = strip_html(m.group(1)) if m else p.stem
            items.append(f"{p}: {title}")
        except OSError:
            continue
    return items[:100]


def response_text(data: dict) -> str:
    # Responses API commonly returns message content items with output_text.
    chunks: list[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if chunks:
        return "\n".join(chunks).strip()
    if isinstance(data.get("output_text"), str):
        return data["output_text"].strip()
    raise RuntimeError("No output_text found in Responses API response")


def call_openai(prompt: str) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API HTTP {exc.code}: {detail[:1000]}") from exc
    text = response_text(data)
    # Be tolerant of accidental markdown fences while still requiring JSON.
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)


def render_markdown(report: dict, article: str, sha: str, model: str) -> str:
    lines = [
        "## 🤖 Critic Lab Report",
        "",
        f"Article: `{article}`",
        f"Commit: `{sha}`",
        f"Model: `{model}`",
        f"Status: **{report.get('status', 'unknown')}**",
        "",
        report.get("summary", ""),
        "",
    ]

    def section(title: str, key: str, renderer):
        values = report.get(key) or []
        lines.extend([f"## {title}", ""])
        if not values:
            lines.append("No high-signal findings.")
            lines.append("")
            return
        for value in values:
            lines.append(renderer(value))
            lines.append("")

    section("1. Logic", "logic", lambda x: (
        f"- **{x.get('severity','?').upper()}** — {x.get('claim','')}\n"
        f"  - Issue: {x.get('issue','')}\n"
        f"  - Why it matters: {x.get('why_it_matters','')}\n"
        f"  - Test / fix: {x.get('test_or_fix','')}"
    ))
    section("2. Counterexamples", "counterexamples", lambda x: (
        f"- **{x.get('severity','?').upper()}** — Thesis: {x.get('thesis','')}\n"
        f"  - Counterexample: {x.get('counterexample','')}\n"
        f"  - Boundary: {x.get('boundary','')}"
    ))
    section("3. Novelty", "novelty", lambda x: (
        f"- **{x.get('assessment','unknown')}** — {x.get('claim','')}\n"
        f"  - Basis: {x.get('basis','')}"
    ))
    section("4. Facts", "facts", lambda x: (
        f"- **{x.get('severity','?').upper()}** — {x.get('claim','')}\n"
        f"  - Why verify: {x.get('reason_to_verify','')}\n"
        f"  - Preferred source: `{x.get('preferred_source','')}`"
    ))
    section("5. Missing Points", "missing_points", lambda x: (
        f"- **{x.get('severity','?').upper()}** — {x.get('point','')}\n"
        f"  - Why it matters: {x.get('why_it_matters','')}"
    ))

    lines.extend(["## 6. Recommended Changes", ""])
    for item in report.get("recommended_changes") or []:
        lines.append(f"- {item}")
    if not report.get("recommended_changes"):
        lines.append("No changes required from this review.")
    lines.extend([
        "",
        f"Evidence level: `{report.get('evidence_level', 'E0')}`",
        "",
        "> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    article_path = Path(args.article)
    article_text = strip_html(article_path.read_text(encoding="utf-8"))
    try:
        diff = run(["git", "diff", args.before, args.after, "--", args.article])
    except subprocess.CalledProcessError:
        diff = "(diff unavailable)"

    prompt = f"""
ARTICLE PATH:
{args.article}

CURRENT ARTICLE TEXT:
{article_text[:60000]}

GIT DIFF FOR THIS CHANGE:
{diff[:30000]}

OTHER ARTICLES IN THIS KNOWLEDGE LAB (for local overlap only; do not infer external originality):
{chr(10).join(article_catalog(args.article))}

Review the article as an evolving engineering hypothesis. Pay special attention
to whether formulas such as "Domain Object × Action = Tool" are definitions,
heuristics, or universal claims; whether tool consolidation can itself create
parameter explosion; and whether runtime/risk/verification boundaries are
being conflated with domain boundaries.
"""

    report = call_openai(prompt)
    report["article"] = args.article
    report["commit"] = args.after
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    report["model"] = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = article_path.stem
    stem = f"{slug}-{args.after[:12]}"
    (out / f"{stem}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / f"{stem}.md").write_text(render_markdown(report, args.article, args.after, report["model"]), encoding="utf-8")

    print(json.dumps({"status": report.get("status"), "article": args.article, "output": stem}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
