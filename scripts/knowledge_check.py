#!/usr/bin/env python3
"""Deterministic weekly knowledge check. Writes a run manifest. Does not edit articles.

Usage:
  python3 scripts/knowledge_check.py
  python3 scripts/knowledge_check.py --write
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import (  # noqa: E402
    CATALOG,
    CRITERIA_SRC,
    KNOWLEDGE_OUT,
    RUNS,
    build_registry,
    load_criteria,
    load_json,
    merge_indexes,
    period_now,
    utc_now,
    write_json,
    write_registry,
)


def gate(results: list[dict], gid: str, ok: bool, detail: str, hard: bool = True) -> None:
    results.append({"gate": gid, "ok": ok, "hard": hard, "detail": detail})
    mark = "OK" if ok else ("FAIL" if hard else "INFO")
    print(f"  {mark}  {gid}: {detail}")


def upsert_index(manifest: dict) -> None:
    path = RUNS / "index.json"
    idx = load_json(path) if path.exists() else {}
    items = idx.get("items") if isinstance(idx.get("items"), list) else []
    run_id = manifest.get("runId")
    summary = {
        "runId": run_id,
        "period": manifest.get("period"),
        "phase": manifest.get("phase"),
        "due": (manifest.get("summary") or {}).get("due"),
        "finishedAt": manifest.get("finishedAt"),
        "path": f"/api/knowledge/runs/{run_id}.json" if run_id else None,
    }
    items = [x for x in items if isinstance(x, dict) and x.get("runId") != run_id]
    items.insert(0, summary)
    write_json(
        path,
        {
            "name": "Knowledge lifecycle run index",
            "generated": utc_now(),
            "items": items[:40],
        },
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--period", default="")
    args = ap.parse_args()

    criteria = load_criteria()
    registry = build_registry()
    if args.write:
        write_registry(registry, criteria)
        merge_indexes(registry)

    period = args.period or os.environ.get("PERIOD") or period_now()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = os.environ.get("RUN_ID") or f"knowledge-{period}-{ts}"
    started = utc_now()
    results: list[dict] = []

    items = registry.get("items") or []
    due = [x for x in items if (x.get("knowledge") or {}).get("due")]
    stale = [x for x in items if (x.get("knowledge") or {}).get("status") == "stale"]
    changed = [x for x in items if (x.get("knowledge") or {}).get("status") == "changed"]
    contested = [x for x in items if (x.get("knowledge") or {}).get("status") == "contested"]

    catalog = load_json(CATALOG)
    times_ok = all(not it.get("knowledge") for it in (catalog.get("items") or []) if it.get("type") == "Times")
    covered = {x.get("id") for x in items}
    published = {
        it.get("id")
        for it in (catalog.get("items") or [])
        if it.get("type") in {"Articles", "Diverse Lab"}
    }

    gate(results, "surfaces", CRITERIA_SRC.exists() and KNOWLEDGE_OUT.exists(), "criteria + knowledge.json present")
    gate(results, "coverage", covered == published, "all catalog Articles/Diverse are in the registry" if covered == published else f"gap {sorted(published - covered)}")
    gate(results, "times_excluded", times_ok, "Times/Hot Words excluded from lifecycle")
    gate(results, "cadence", all((x.get("knowledge") or {}).get("next_review") for x in items), "every item has next_review")
    gate(results, "due", not due, f"{len(due)} item(s) need review", hard=False)

    hard_fails = [r for r in results if r["hard"] and not r["ok"]]
    infos = [r for r in results if (not r["hard"]) and not r["ok"]]
    verdict = "ok" if not hard_fails else "drift"
    phase = "checked" if not hard_fails else "failed"
    if due and not hard_fails:
        phase = "needs_review"
        verdict = "needs_review"

    due_ids = [str(x.get("id")) for x in due]
    manifest = {
        "runId": run_id,
        "period": period,
        "phase": phase,
        "verdict": verdict,
        "startedAt": started,
        "finishedAt": utc_now(),
        "input": {
            "periodScheme": "YYYY-MM-WN = Nth 7-day block of the calendar month (Asia/Shanghai), not ISO week",
            "as_of": registry.get("as_of"),
        },
        "gates": {r["gate"]: ("pass" if r["ok"] else ("info" if not r["hard"] else "fail")) for r in results},
        "checks": results,
        "due": due_ids,
        "stale": [str(x.get("id")) for x in stale],
        "changed": [str(x.get("id")) for x in changed],
        "contested": [str(x.get("id")) for x in contested],
        "summary": {
            "items": len(items),
            "due": len(due),
            "stale": len(stale),
            "changed": len(changed),
            "contested": len(contested),
            "fail": len(hard_fails),
        },
        "criteria": "/api/knowledge-criteria.json",
        "registry": "/api/knowledge.json",
        "publish": {"url": "https://chengguruchun.github.io/api/knowledge/runs/latest.json"},
        "error": "; ".join(f"{r['gate']}: {r['detail']}" for r in hard_fails) or None,
    }

    if args.write:
        write_json(RUNS / f"{run_id}.json", manifest)
        write_json(RUNS / "latest.json", manifest)
        upsert_index(manifest)
        print(f"wrote /api/knowledge/runs/{run_id}.json verdict={verdict}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"run_id={run_id}\n")
            f.write(f"verdict={verdict}\n")
            f.write(f"due_count={len(due)}\n")
            f.write(f"due_ids={','.join(due_ids)}\n")
            f.write(f"needs_issue={'true' if due or hard_fails else 'false'}\n")
            f.write(f"failed={'true' if hard_fails else 'false'}\n")
            f.write(f"error={manifest['error'] or ''}\n")

    print(f"RESULT: {verdict}  items={len(items)} due={len(due)} fail={len(hard_fails)} info={len(infos)}")
    return 1 if hard_fails else 0


if __name__ == "__main__":
    sys.exit(main())
