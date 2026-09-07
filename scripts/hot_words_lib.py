"""Shared Hot Words helpers: period scheme, hashes, post-apply consistency."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PERIOD_SCHEME = {
    "format": "YYYY-MM-WN",
    "meaning": (
        "Nth 7-day block of the calendar month in Asia/Shanghai "
        "(days 1–7 = W1, 8–14 = W2, …). Not an ISO 8601 week number."
    ),
    "timezone": "Asia/Shanghai",
}


def proposal_hash(period: str, word: str, why: str) -> str:
    raw = f"{period.strip()}\n{word.strip()}\n{why.strip()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def normalize_evidence(raw: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if raw is None:
        return out
    if isinstance(raw, str):
        s = raw.strip()
        if s:
            out.append(
                {
                    "title": s[:80],
                    "url": "",
                    "sourceType": "note",
                    "publishedAt": "",
                    "claim": s,
                }
            )
        return out
    items = [raw] if isinstance(raw, dict) else (raw if isinstance(raw, list) else [])
    for it in items:
        if isinstance(it, str):
            s = it.strip()
            if s:
                out.append(
                    {
                        "title": s[:80],
                        "url": "",
                        "sourceType": "note",
                        "publishedAt": "",
                        "claim": s,
                    }
                )
            continue
        if not isinstance(it, dict):
            continue
        url = str(it.get("url") or "").strip()
        title = str(it.get("title") or "").strip() or (url[:80] if url else "")
        out.append(
            {
                "title": title,
                "url": url,
                "sourceType": str(
                    it.get("sourceType") or it.get("source_type") or "article"
                ).strip()
                or "article",
                "publishedAt": str(
                    it.get("publishedAt") or it.get("published_at") or ""
                ).strip(),
                "claim": str(it.get("claim") or it.get("notes") or "").strip(),
            }
        )
    return out


def evidence_stats(candidates: list[Any], chosen_evidence: Any = None) -> dict[str, Any]:
    structured = 0
    with_url = 0
    legacy_only = 0
    types: set[str] = set()
    all_ev: list[dict[str, Any]] = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        all_ev.extend(normalize_evidence(c.get("evidence")))
    all_ev.extend(normalize_evidence(chosen_evidence))
    for ev in all_ev:
        url = ev.get("url") or ""
        parsed = urlparse(url)
        if url and parsed.scheme in ("http", "https") and parsed.netloc:
            with_url += 1
            structured += 1
            types.add(str(ev.get("sourceType") or "article"))
        elif ev.get("claim") or ev.get("title"):
            if not url:
                legacy_only += 1
            else:
                structured += 1
    return {
        "total": len(all_ev),
        "withUrl": with_url,
        "structured": structured,
        "legacyOnly": legacy_only,
        "sourceTypes": sorted(types),
        "items": all_ev,
    }


def relevance_hit(word: str, catalog: dict[str, Any]) -> bool:
    needle = word.strip().lower()
    if not needle:
        return False
    items = catalog.get("items") if isinstance(catalog.get("items"), list) else []
    for it in items:
        if not isinstance(it, dict):
            continue
        blob = " ".join(
            [
                str(it.get("title") or ""),
                str(it.get("excerpt") or ""),
                " ".join(it.get("tags") or []) if isinstance(it.get("tags"), list) else "",
            ]
        ).lower()
        if needle in blob:
            return True
        parts = re.split(r"[\s/\-·,]+", needle)
        if any(len(p) >= 4 and p in blob for p in parts):
            return True
    return False


def verify_applied(root: Path, period: str, word: str) -> dict[str, Any]:
    errors: list[str] = []
    slug = period.strip().lower()
    md = root / "content" / "times" / f"{slug}.md"
    html = root / "times" / "index.html"
    times = root / "api" / "times.json"
    catalog = root / "api" / "catalog.json"
    index = root / "content" / "index.json"

    if not md.exists():
        errors.append("markdown missing")
    elif word not in md.read_text(encoding="utf-8"):
        errors.append("markdown does not contain word")

    if not html.exists() or word not in html.read_text(encoding="utf-8"):
        errors.append("times/index.html missing word")

    try:
        api = json.loads(times.read_text(encoding="utf-8"))
        if api.get("current") != period:
            errors.append(f"times.current is {api.get('current')!r}, expected {period!r}")
        issues = api.get("issues") if isinstance(api.get("issues"), list) else []
        top = issues[0] if issues and isinstance(issues[0], dict) else {}
        if top.get("word") != word or top.get("period") != period:
            errors.append("times.issues[0] does not match period/word")
    except Exception as e:
        errors.append(f"times.json: {e}")

    for path in (catalog, index):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data.get("items") if isinstance(data.get("items"), list) else []
            hit = any(
                isinstance(it, dict)
                and it.get("type") == "Times"
                and (it.get("period") == period or it.get("word") == word)
                for it in items
            )
            if not hit:
                errors.append(f"{path.name} missing Times entry")
        except Exception as e:
            errors.append(f"{path.name}: {e}")

    return {
        "ok": not errors,
        "errors": errors,
        "gate": "pass" if not errors else "fail",
    }
