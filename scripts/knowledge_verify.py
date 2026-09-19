#!/usr/bin/env python3
"""Research Runtime: Observe cited URLs, then Judge. Never edits article bodies.

Usage:
  python3 scripts/knowledge_verify.py --due
  python3 scripts/knowledge_verify.py --id h-neurons-paper-reading
  python3 scripts/knowledge_verify.py --id h-neurons-paper-reading --dry-run
  python3 scripts/knowledge_verify.py --file report.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import (  # noqa: E402
    REPORTS,
    VERDICTS,
    build_registry,
    dump_json,
    load_criteria,
    load_json,
    period_now,
    utc_now,
    validate_report,
    write_json,
)
from knowledge_runtime import (  # noqa: E402
    constrain_to_observe,
    judge_from_observe,
    observe_entry,
    observed_urls,
    url_fetch,
)

DEEPSEEK = "https://api.deepseek.com/chat/completions"


def claim_for(item: dict) -> str:
    excerpt = str(item.get("excerpt") or "").strip()
    rel = item.get("content")
    if rel:
        path = ROOT / str(rel).lstrip("/")
        if path.exists():
            text = path.read_text(encoding="utf-8")
            m = re.search(r"^> (.+)$", text, re.M)
            if m:
                return m.group(1).strip()
    return excerpt


def body_excerpt(item: dict, limit: int = 1800) -> str:
    rel = item.get("content")
    if not rel:
        return str(item.get("excerpt") or "")
    path = ROOT / str(rel).lstrip("/")
    if not path.exists():
        return str(item.get("excerpt") or "")
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    return text.strip()[:limit]


def compact_observe(observe: dict) -> dict:
    return {
        "observed_at": observe.get("observed_at"),
        "used": observe.get("used"),
        "citations": [c.get("url") for c in (observe.get("citations") or [])],
        "fetches": [
            {
                "url": f.get("url"),
                "ok": f.get("ok"),
                "status": f.get("status"),
                "signal": f.get("signal"),
                "title": f.get("title"),
                "error": f.get("error"),
            }
            for f in (observe.get("fetches") or [])
        ],
        "arxiv": [
            {
                "arxiv_id": a.get("arxiv_id"),
                "ok": a.get("ok"),
                "title": a.get("title"),
                "updated": a.get("updated"),
                "cited_version": a.get("cited_version"),
                "latest_version": a.get("latest_version"),
                "newer_than_cite": a.get("newer_than_cite"),
                "updated_after_verified": a.get("updated_after_verified"),
                "error": a.get("error"),
            }
            for a in (observe.get("arxiv") or [])
        ],
        "signals": observe.get("signals") or [],
    }


def call_deepseek(payload: dict, criteria: dict) -> dict:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY missing")
    body = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Return compact JSON only. No markdown fences."},
            {"role": "user", "content": criteria["prompt"] + "\n\n输入：\n" + dump_json(payload)},
        ],
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        DEEPSEEK,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode())
    text = data["choices"][0]["message"]["content"].strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise SystemExit("model returned no JSON object")
    parsed = json.loads(m.group(0))
    if not isinstance(parsed, dict):
        raise SystemExit("model JSON was not an object")
    parsed.setdefault("model", "deepseek-chat")
    return parsed


def harden_file_report(report: dict) -> dict:
    """Human/agent --file path: live-check evidence URLs. Observe is optional."""
    verdict = report.get("verdict")
    evidence = report.get("evidence") if isinstance(report.get("evidence"), list) else []
    live = []
    for e in evidence:
        if not isinstance(e, dict):
            continue
        url = str(e.get("url") or "").strip()
        if not url.startswith("https://"):
            continue
        fetched = url_fetch(url)
        if fetched.get("ok"):
            live.append(
                {
                    "url": url,
                    "note": e.get("note") or "",
                    "tool": e.get("tool") or "url_fetch",
                    "observed_at": fetched.get("observed_at"),
                }
            )
    report["evidence"] = live
    if verdict in {"changed", "obsolete"} and not live:
        report["verdict"] = "insufficient"
        report["note"] = (report.get("note") or "") + "；https 证据无法核验，降为 insufficient"
    if report.get("verdict") not in VERDICTS:
        report["verdict"] = "insufficient"
    return report


def harden_runtime_report(report: dict, observe: dict) -> dict:
    allowed = observed_urls(observe)
    evidence = []
    for e in report.get("evidence") or []:
        if not isinstance(e, dict):
            continue
        url = str(e.get("url") or "").strip()
        if url in allowed:
            evidence.append(
                {
                    "url": url,
                    "note": e.get("note") or "",
                    "tool": e.get("tool") or "url_fetch",
                    "observed_at": e.get("observed_at") or observe.get("observed_at"),
                }
            )
    report["evidence"] = evidence
    if report.get("verdict") in {"changed", "obsolete"} and not evidence:
        report["verdict"] = "insufficient"
        report["note"] = (report.get("note") or "") + "；https 证据不在本轮 Observe 里，降为 insufficient"
    if report.get("verdict") not in VERDICTS:
        report["verdict"] = "insufficient"
    return report


def write_report(entry: dict, raw: dict, criteria: dict, period: str, observe: dict | None = None) -> Path:
    payload = {
        "id": f"{entry['id']}-{period}",
        "entry_id": entry["id"],
        "period": period,
        "criteria_version": raw.get("criteria_version") or criteria.get("version"),
        "model": raw.get("model") or "unknown",
        "verdict": raw.get("verdict"),
        "note": raw.get("note") or "",
        "evidence": raw.get("evidence") or [],
        "proposed_change": raw.get("proposed_change") or "",
        "created": utc_now(),
        "human": None,
    }
    if observe is not None:
        payload["observe"] = observe
        payload = harden_runtime_report(payload, observe)
    else:
        payload = harden_file_report(payload)
    errors = validate_report(payload, criteria)
    if errors:
        raise SystemExit(f"{entry['id']}: " + "; ".join(errors))
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{payload['id']}.json"
    write_json(path, payload)
    return path


def due_entries(registry: dict, eid: str | None) -> list[dict]:
    items = registry.get("items") or []
    if eid:
        found = [x for x in items if x.get("id") == eid]
        if not found:
            raise SystemExit(f"unknown knowledge id {eid}")
        return found
    return [x for x in items if (x.get("knowledge") or {}).get("status") == "stale"]


def verify_one(entry: dict, criteria: dict, *, use_model: bool) -> tuple[dict, dict]:
    observe = observe_entry(entry, criteria)
    det = judge_from_observe(observe, entry)
    det["criteria_version"] = criteria.get("version")
    if observe.get("signals"):
        return observe, det
    if not use_model:
        return observe, det
    kn = entry.get("knowledge") or {}
    raw = call_deepseek(
        {
            "id": entry.get("id"),
            "title": entry.get("title"),
            "type": entry.get("type"),
            "tags": entry.get("tags"),
            "excerpt": entry.get("excerpt"),
            "claim": claim_for(entry),
            "last_verified": kn.get("last_verified"),
            "cadence_days": kn.get("cadence_days"),
            "published_date": entry.get("published_date"),
            "body_excerpt": body_excerpt(entry),
            "observe": compact_observe(observe),
        },
        criteria,
    )
    return observe, constrain_to_observe(raw, observe, det)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--due", action="store_true", help="Verify stale items only")
    ap.add_argument("--id", default="")
    ap.add_argument("--file", default="", help="Apply a human/agent report JSON; still does not edit articles")
    ap.add_argument("--limit", type=int, default=3)
    ap.add_argument("--period", default="")
    ap.add_argument("--dry-run", action="store_true", help="Print Observe + verdict, do not write a report")
    ap.add_argument("--observe-only", action="store_true", help="Skip the model even if DEEPSEEK_API_KEY is set")
    args = ap.parse_args()

    criteria = load_criteria()
    period = args.period or os.environ.get("PERIOD") or period_now()

    if args.file:
        data = load_json(Path(args.file))
        registry = build_registry()
        entry = next((x for x in registry["items"] if x.get("id") == data.get("entry_id")), None)
        if not entry:
            raise SystemExit(f"entry_id {data.get('entry_id')} is not in the registry")
        path = write_report(entry, data, criteria, period)
        print(f"wrote {path.relative_to(ROOT)} (article untouched)")
        return 0

    if not args.due and not args.id:
        raise SystemExit("pass --due or --id")

    registry = build_registry()
    targets = due_entries(registry, args.id or None)
    if args.due:
        targets.sort(key=lambda x: (x.get("knowledge") or {}).get("next_review") or "")
        targets = targets[: max(0, args.limit)]
    if not targets:
        print("no stale items to verify")
        return 0

    use_model = bool(os.environ.get("DEEPSEEK_API_KEY", "").strip()) and not args.observe_only
    if not use_model:
        print("Judge = Observe only (no model, or --observe-only)")

    written = 0
    for entry in targets:
        print(f"observe {entry['id']} …")
        observe, raw = verify_one(entry, criteria, use_model=use_model)
        used = observe.get("used") or {}
        signals = observe.get("signals") or []
        print(
            f"  fetch={used.get('url_fetch', 0)} arxiv={used.get('arxiv_lookup', 0)} "
            f"signals={len(signals)} verdict={raw.get('verdict')}"
        )
        if args.dry_run:
            print(dump_json({"observe": compact_observe(observe), "judge": raw}))
            continue
        path = write_report(entry, raw, criteria, period, observe)
        print(f"  {path.relative_to(ROOT)}")
        written += 1
    if args.dry_run:
        print("dry-run; no report written; no article bodies changed")
        return 0
    print(f"wrote {written} report(s); no article bodies changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
