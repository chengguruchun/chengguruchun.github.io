#!/usr/bin/env python3
"""Human decision after a knowledge check. Updates override + registry, never ghostwrites.

Usage:
  python3 scripts/knowledge_review.py --id k8s-to-agent-control-plane --decision keep
  python3 scripts/knowledge_review.py --id foo --decision changed --note "…"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import (  # noqa: E402
    DECISIONS,
    build_registry,
    iso,
    load_criteria,
    load_override,
    merge_indexes,
    shanghai_today,
    write_override,
    write_registry,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--decision", required=True, choices=DECISIONS)
    ap.add_argument("--note", default="")
    ap.add_argument("--cadence-days", type=int, default=0)
    args = ap.parse_args()

    registry = build_registry()
    entry = next((x for x in registry["items"] if x.get("id") == args.id), None)
    if not entry:
        raise SystemExit(f"unknown knowledge id {args.id}")

    today = shanghai_today()
    prev = load_override(args.id)
    data = dict(prev)
    data["id"] = args.id
    data["updated"] = iso(today)
    if args.note:
        data["note"] = args.note
    if args.cadence_days:
        data["cadence_days"] = args.cadence_days

    if args.decision == "keep":
        data["last_verified"] = iso(today)
        data.pop("status", None)
    else:
        data["status"] = args.decision
        if args.decision != "archived":
            data["last_verified"] = prev.get("last_verified") or (entry.get("knowledge") or {}).get("last_verified")

    path = write_override(args.id, data)
    criteria = load_criteria()
    registry = build_registry()
    write_registry(registry, criteria)
    merge_indexes(registry)
    kn = next(x["knowledge"] for x in registry["items"] if x["id"] == args.id)
    print(f"reviewed {args.id} → {kn['status']} ({path.relative_to(ROOT)})")
    print("article body not modified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
