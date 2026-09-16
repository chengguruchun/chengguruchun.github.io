#!/usr/bin/env python3
"""Build /api/knowledge.json and attach knowledge{} to catalog indexes.

Usage:
  python3 scripts/build_knowledge.py
  python3 scripts/build_knowledge.py --seed-frontmatter
  python3 scripts/build_knowledge.py --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import (  # noqa: E402
    CATALOG,
    CRITERIA_OUT,
    KNOWLEDGE_OUT,
    ROOT as LAB,
    build_registry,
    dump_json,
    load_criteria,
    load_json,
    merge_indexes,
    page_parity_gaps,
    rebuild_tags,
    seed_frontmatter,
    write_registry,
)


def seed(registry: dict) -> int:
    n = 0
    for item in registry.get("items") or []:
        rel = item.get("content")
        rec = item.get("knowledge") or {}
        if not rel or not rec.get("last_verified") or not rec.get("cadence_days"):
            continue
        path = LAB / str(rel).lstrip("/")
        if not path.exists():
            continue
        if seed_frontmatter(path, rec["last_verified"], int(rec["cadence_days"])):
            print(f"  seeded {path.relative_to(LAB)}")
            n += 1
    return n


def check(registry: dict, criteria: dict) -> int:
    fails = 0
    if not KNOWLEDGE_OUT.exists() or not CRITERIA_OUT.exists():
        print("FAIL missing api/knowledge.json or api/knowledge-criteria.json — run build_knowledge.py")
        return 1
    on_disk = load_json(KNOWLEDGE_OUT)
    want_items = {x["id"]: x["knowledge"] for x in registry["items"]}
    got_items = {x["id"]: x.get("knowledge") for x in on_disk.get("items") or []}
    if want_items != got_items:
        print("FAIL api/knowledge.json knowledge fields drifted")
        fails += 1
    else:
        print("  OK  knowledge.json items")
    gaps = page_parity_gaps()
    if gaps:
        print("FAIL published HTML missing catalog/markdown: " + ", ".join(gaps[:8]))
        fails += 1
    else:
        print("  OK  published HTML has catalog + markdown")
    if load_json(CRITERIA_OUT).get("version") != criteria.get("version"):
        print("FAIL api/knowledge-criteria.json version drifted")
        fails += 1
    else:
        print("  OK  knowledge-criteria.json")
    catalog = load_json(CATALOG)
    for it in catalog.get("items") or []:
        if it.get("type") == "Times":
            if it.get("knowledge"):
                print(f"FAIL Times {it.get('id')} should not carry knowledge")
                fails += 1
            continue
        if it.get("type") in {"Articles", "Diverse Lab"}:
            rec = (it.get("knowledge") or {})
            expected = want_items.get(it.get("id"))
            if rec != expected:
                print(f"FAIL catalog {it.get('id')} knowledge mismatch")
                fails += 1
    if not fails:
        print("  OK  catalog knowledge fields")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-frontmatter", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    criteria = load_criteria()
    registry = build_registry()
    if args.seed_frontmatter:
        n = seed(registry)
        if n:
            registry = build_registry()
        print(f"seeded {n} markdown files")
    if args.check:
        return 1 if check(registry, criteria) else 0

    write_registry(registry, criteria)
    touched = merge_indexes(registry)
    touched.append(rebuild_tags())
    print(f"wrote {KNOWLEDGE_OUT.relative_to(LAB)} items={len(registry['items'])} due={len(registry['due'])}")
    for path in touched:
        print(f"  merged {path.relative_to(LAB)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
