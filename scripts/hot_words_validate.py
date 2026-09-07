#!/usr/bin/env python3
"""Validate a Hot Words proposal (no writes)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def repo_root() -> Path:
    cur = Path.cwd().resolve()
    for _ in range(12):
        if (cur / "api" / "times.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd().resolve()


def normalize_evidence(raw: Any) -> list[dict[str, Any]]:
    """Accept list of objects, single object, or legacy string."""
    out: list[dict[str, Any]] = []
    if raw is None:
        return out
    if isinstance(raw, str):
        s = raw.strip()
        if s:
            out.append({"title": s[:80], "url": "", "sourceType": "note", "publishedAt": "", "claim": s})
        return out
    if isinstance(raw, dict):
        items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        return out
    for it in items:
        if isinstance(it, str):
            s = it.strip()
            if s:
                out.append({"title": s[:80], "url": "", "sourceType": "note", "publishedAt": "", "claim": s})
            continue
        if not isinstance(it, dict):
            continue
        url = str(it.get("url") or "").strip()
        title = str(it.get("title") or "").strip() or (url[:80] if url else "")
        out.append({
            "title": title,
            "url": url,
            "sourceType": str(it.get("sourceType") or it.get("source_type") or "article").strip() or "article",
            "publishedAt": str(it.get("publishedAt") or it.get("published_at") or "").strip(),
            "claim": str(it.get("claim") or it.get("notes") or "").strip(),
        })
    return out


def evidence_stats(candidates: list[Any], chosen_evidence: Any = None) -> dict[str, Any]:
    structured = 0
    with_url = 0
    legacy_only = 0
    all_ev: list[dict[str, Any]] = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        evs = normalize_evidence(c.get("evidence"))
        all_ev.extend(evs)
    all_ev.extend(normalize_evidence(chosen_evidence))
    for ev in all_ev:
        url = ev.get("url") or ""
        if url and urlparse(url).scheme in ("http", "https") and urlparse(url).netloc:
            with_url += 1
            structured += 1
        elif ev.get("claim") or ev.get("title"):
            # note without url counts as legacy/weak
            if not url:
                legacy_only += 1
            else:
                structured += 1
    return {
        "total": len(all_ev),
        "withUrl": with_url,
        "structured": structured,
        "legacyOnly": legacy_only,
        "items": all_ev,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--period", required=True)
    ap.add_argument("--word", required=True)
    ap.add_argument("--why", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--candidates-json", default=None, help="path or inline JSON array")
    ap.add_argument("--require-evidence-url", action="store_true", help="fail if no https evidence URL")
    args = ap.parse_args()

    gates = {"schema": "pass", "duplicate": "pass", "editorial": "pass", "evidence": "skip"}
    errors: list[str] = []
    word = args.word.strip()
    why = args.why.strip()
    if not word:
        gates["schema"] = "fail"
        errors.append("word empty")
    if len(why) < 40:
        gates["editorial"] = "fail"
        errors.append(f"why length {len(why)} < 40")

    times_path = repo_root() / "api" / "times.json"
    current_word = ""
    if times_path.exists():
        try:
            data = json.loads(times_path.read_text(encoding="utf-8"))
            issues = data.get("issues") if isinstance(data.get("issues"), list) else []
            if issues and isinstance(issues[0], dict):
                current_word = str(issues[0].get("word") or "")
        except json.JSONDecodeError:
            pass
    if (not args.force) and current_word and word == current_word:
        gates["duplicate"] = "fail"
        errors.append(f"word equals current {current_word!r}")

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

    out = {
        "ok": not errors,
        "gates": gates,
        "errors": errors,
        "period": args.period,
        "word": word,
        "evidence": {"withUrl": stats["withUrl"], "total": stats["total"], "legacyOnly": stats["legacyOnly"]},
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["ok"] else 2)


if __name__ == "__main__":
    main()
