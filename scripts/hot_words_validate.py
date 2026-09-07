#!/usr/bin/env python3
"""Validate a Hot Words proposal (no writes)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hot_words_lib import (
    evidence_stats,
    proposal_hash,
    relevance_hit,
    verify_applied,
)


def repo_root() -> Path:
    cur = Path.cwd().resolve()
    for _ in range(12):
        if (cur / "api" / "times.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd().resolve()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--period", required=True)
    ap.add_argument("--word", required=True)
    ap.add_argument("--why", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--candidates-json", default=None, help="path or inline JSON array")
    ap.add_argument(
        "--require-evidence-url",
        action="store_true",
        help="fail unless at least one https evidence URL exists",
    )
    ap.add_argument("--min-source-types", type=int, default=0)
    ap.add_argument(
        "--verify-applied",
        action="store_true",
        help="also check workspace files match period/word",
    )
    args = ap.parse_args()
    root = repo_root()

    gates = {
        "schema": "pass",
        "duplicate": "pass",
        "editorial": "pass",
        "evidence": "skip",
        "relevance": "skip",
        "consistency": "skip",
    }
    errors: list[str] = []
    word = args.word.strip()
    why = args.why.strip()
    if not word:
        gates["schema"] = "fail"
        errors.append("word empty")
    if len(why) < 40:
        gates["editorial"] = "fail"
        errors.append(f"why length {len(why)} < 40")

    times_path = root / "api" / "times.json"
    current_word = ""
    current_hash = ""
    if times_path.exists():
        try:
            data = json.loads(times_path.read_text(encoding="utf-8"))
            issues = data.get("issues") if isinstance(data.get("issues"), list) else []
            if issues and isinstance(issues[0], dict):
                current_word = str(issues[0].get("word") or "")
            current_hash = str(data.get("currentProposalHash") or "")
        except json.JSONDecodeError:
            pass
    digest = proposal_hash(args.period, word, why)
    if (not args.force) and current_word and word == current_word:
        gates["duplicate"] = "fail"
        errors.append(f"word equals current {current_word!r}")
    if (not args.force) and current_hash and current_hash == digest:
        gates["duplicate"] = "fail"
        errors.append(f"same proposalHash already published: {digest}")

    candidates: list[Any] = []
    if args.candidates_json:
        raw = args.candidates_json
        p = Path(raw)
        try:
            payload = json.loads(p.read_text(encoding="utf-8") if p.exists() else raw)
            if isinstance(payload, list):
                candidates = payload
            elif isinstance(payload, dict) and isinstance(payload.get("candidates"), list):
                candidates = payload["candidates"]
        except Exception as e:
            errors.append(f"candidates parse: {e}")

    stats = evidence_stats(candidates)
    if stats["withUrl"] > 0:
        gates["evidence"] = "pass"
        if args.min_source_types and len(stats["sourceTypes"]) < args.min_source_types:
            gates["evidence"] = "weak"
            if args.require_evidence_url:
                gates["evidence"] = "fail"
                errors.append(
                    f"need {args.min_source_types} source types, got {stats['sourceTypes']}"
                )
    elif stats["total"] > 0:
        gates["evidence"] = "weak"
        if args.require_evidence_url:
            gates["evidence"] = "fail"
            errors.append("evidence has no https URL")
    else:
        gates["evidence"] = "skip"
        if args.require_evidence_url:
            gates["evidence"] = "fail"
            errors.append("evidence missing")

    catalog_path = root / "api" / "catalog.json"
    if catalog_path.exists() and word:
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            gates["relevance"] = "pass" if relevance_hit(word, catalog) else "weak"
        except json.JSONDecodeError:
            gates["relevance"] = "skip"

    if args.verify_applied:
        checked = verify_applied(root, args.period, word)
        gates["consistency"] = checked["gate"]
        errors.extend(checked["errors"])

    out = {
        "ok": not errors,
        "gates": gates,
        "errors": errors,
        "period": args.period,
        "word": word,
        "proposalHash": digest,
        "evidence": {
            "withUrl": stats["withUrl"],
            "total": stats["total"],
            "legacyOnly": stats["legacyOnly"],
            "sourceTypes": stats["sourceTypes"],
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["ok"] else 2)


if __name__ == "__main__":
    main()
