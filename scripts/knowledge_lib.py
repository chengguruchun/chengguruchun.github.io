#!/usr/bin/env python3
"""Shared helpers for the knowledge lifecycle registry."""
from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CRITERIA_SRC = ROOT / "content" / "knowledge" / "criteria.json"
OVERRIDES = ROOT / "content" / "knowledge" / "overrides"
REPORTS = ROOT / "content" / "knowledge" / "reports"
KNOWLEDGE_OUT = ROOT / "api" / "knowledge.json"
CRITERIA_OUT = ROOT / "api" / "knowledge-criteria.json"
RUNS = ROOT / "api" / "knowledge" / "runs"
CATALOG = ROOT / "api" / "catalog.json"
INDEX = ROOT / "content" / "index.json"
ARTICLES = ROOT / "api" / "articles.json"
DIVERSE = ROOT / "api" / "diverse-lab.json"

STATUSES = ("fresh", "stale", "changed", "contested", "archived")
STICKY = {"changed", "contested", "archived"}
VERDICTS = ("unchanged", "changed", "insufficient", "obsolete")
DECISIONS = ("keep", "changed", "contested", "archived")
FRONT = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def shanghai_today() -> date:
    return datetime.now(ZoneInfo("Asia/Shanghai")).date()


def period_now(when: datetime | None = None) -> str:
    now = when or datetime.now(ZoneInfo("Asia/Shanghai"))
    week = (now.day - 1) // 7 + 1
    return f"{now:%Y-%m}-W{week}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(data), encoding="utf-8")


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    m = DATE_RE.match(text)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def load_criteria() -> dict[str, Any]:
    if not CRITERIA_SRC.exists():
        raise SystemExit("missing content/knowledge/criteria.json")
    data = load_json(CRITERIA_SRC)
    if not data.get("version") or not data.get("prompt") or not data.get("axes"):
        raise SystemExit("knowledge criteria.json needs version, prompt, axes")
    return data


def parse_frontmatter(text: str) -> dict[str, Any]:
    m = FRONT.match(text)
    if not m:
        return {}
    out: dict[str, Any] = {}
    for raw in m.group(1).splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key == "cadence_days":
            try:
                out[key] = int(value)
            except ValueError:
                continue
        elif key == "tags":
            inner = value.strip()
            if inner.startswith("[") and inner.endswith("]"):
                out[key] = [p.strip().strip("'\"") for p in inner[1:-1].split(",") if p.strip()]
            else:
                out[key] = [value] if value else []
        else:
            out[key] = value
    return out


def read_markdown_meta(rel: str) -> dict[str, Any]:
    path = ROOT / str(rel).lstrip("/")
    if not path.exists():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def seed_frontmatter(path: Path, last_verified: str, cadence_days: int) -> bool:
    text = path.read_text(encoding="utf-8")
    m = FRONT.match(text)
    if not m:
        return False
    block = m.group(1)
    extra = ""
    if not re.search(r"^last_verified\s*:", block, re.M):
        extra += f"last_verified: {last_verified}\n"
    if not re.search(r"^cadence_days\s*:", block, re.M):
        extra += f"cadence_days: {cadence_days}\n"
    if not extra:
        return False
    seeded = f"---\n{block.rstrip()}\n{extra}---\n"
    rest = text[m.end() :]
    if rest.startswith("\n"):
        new = seeded + rest
    else:
        new = seeded + "\n" + rest
    path.write_text(new, encoding="utf-8")
    return True


def load_override(eid: str) -> dict[str, Any]:
    path = OVERRIDES / f"{eid}.json"
    if not path.exists():
        return {}
    data = load_json(path)
    return data if isinstance(data, dict) else {}


def write_override(eid: str, data: dict[str, Any]) -> Path:
    OVERRIDES.mkdir(parents=True, exist_ok=True)
    path = OVERRIDES / f"{eid}.json"
    write_json(path, data)
    return path


def list_reports(eid: str) -> list[dict[str, Any]]:
    if not REPORTS.exists():
        return []
    items = []
    for path in sorted(REPORTS.glob("*.json"), reverse=True):
        if path.name.startswith("."):
            continue
        try:
            data = load_json(path)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        if data.get("entry_id") != eid and not path.name.startswith(eid + "-"):
            continue
        data.setdefault("path", f"/content/knowledge/reports/{path.name}")
        items.append(data)
    return items


def latest_report(eid: str) -> dict[str, Any] | None:
    reports = list_reports(eid)
    return reports[0] if reports else None


def cadence_days_for(item: dict[str, Any], fm: dict[str, Any], override: dict[str, Any], criteria: dict[str, Any]) -> int:
    if override.get("cadence_days"):
        try:
            return int(override["cadence_days"])
        except (TypeError, ValueError):
            pass
    if fm.get("cadence_days"):
        try:
            return int(fm["cadence_days"])
        except (TypeError, ValueError):
            pass
    policy = criteria.get("cadence") if isinstance(criteria.get("cadence"), dict) else {}
    tags = [str(t) for t in (item.get("tags") or fm.get("tags") or [])]
    by_tag = policy.get("by_tag") if isinstance(policy.get("by_tag"), dict) else {}
    hit = [int(by_tag[t]) for t in tags if t in by_tag]
    if hit:
        return max(hit)
    by_type = policy.get("by_type") if isinstance(policy.get("by_type"), dict) else {}
    kind = str(item.get("type") or "")
    if kind in by_type:
        return int(by_type[kind])
    return int(policy.get("default_days") or 90)


def last_verified_for(item: dict[str, Any], fm: dict[str, Any], override: dict[str, Any]) -> date:
    for source in (override.get("last_verified"), fm.get("last_verified"), item.get("published_date"), item.get("date"), fm.get("published_date"), fm.get("date")):
        parsed = parse_date(source)
        if parsed:
            return parsed
    return shanghai_today()


def compute_status(sticky: str | None, next_review: date, today: date) -> str:
    if sticky in STICKY:
        return sticky
    if today > next_review:
        return "stale"
    return "fresh"


def knowledge_record(
    item: dict[str, Any],
    criteria: dict[str, Any],
    today: date | None = None,
) -> dict[str, Any] | None:
    kind = item.get("type")
    exclude = set(criteria.get("exclude_types") or ["Times"])
    if kind in exclude:
        return None
    eid = str(item.get("id") or "")
    if not eid:
        return None
    rel = item.get("content") or item.get("markdown") or ""
    fm = read_markdown_meta(str(rel)) if rel else {}
    override = load_override(eid)
    today = today or shanghai_today()
    cadence = cadence_days_for(item, fm, override, criteria)
    verified = last_verified_for(item, fm, override)
    nxt = verified + timedelta(days=cadence)
    sticky = str(override.get("status") or "").strip().lower() or None
    if sticky not in STICKY:
        sticky = None
    status = compute_status(sticky, nxt, today)
    report = latest_report(eid)
    rec: dict[str, Any] = {
        "status": status,
        "last_verified": iso(verified),
        "next_review": iso(nxt),
        "cadence_days": cadence,
        "due": status == "stale" or status in {"changed", "contested"},
        "sticky": bool(sticky),
        "source": {
            "frontmatter": bool(fm.get("last_verified") or fm.get("cadence_days")),
            "override": f"/content/knowledge/overrides/{eid}.json" if override else None,
        },
    }
    if override.get("note"):
        rec["note"] = override["note"]
    if report:
        rec["report"] = {
            "path": report.get("path"),
            "verdict": report.get("verdict"),
            "period": report.get("period"),
            "created": report.get("created"),
        }
    return rec


def catalog_items() -> list[dict[str, Any]]:
    catalog = load_json(CATALOG)
    items = catalog.get("items") if isinstance(catalog.get("items"), list) else []
    return [x for x in items if isinstance(x, dict)]


def build_registry(today: date | None = None) -> dict[str, Any]:
    criteria = load_criteria()
    today = today or shanghai_today()
    items: list[dict[str, Any]] = []
    counts = {s: 0 for s in STATUSES}
    due: list[str] = []
    for raw in catalog_items():
        rec = knowledge_record(raw, criteria, today)
        if rec is None:
            continue
        entry = {
            "id": raw.get("id"),
            "type": raw.get("type"),
            "title": raw.get("title"),
            "excerpt": raw.get("excerpt"),
            "url": raw.get("url"),
            "content": raw.get("content") or raw.get("markdown"),
            "tags": raw.get("tags") or [],
            "published_date": raw.get("published_date") or raw.get("date"),
            "history_url": raw.get("history_url"),
            "knowledge": rec,
        }
        items.append(entry)
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
        if rec.get("due"):
            due.append(str(raw.get("id")))
    return {
        "name": "AI Knowledge Lab · Knowledge registry",
        "generated": utc_now(),
        "as_of": iso(today),
        "criteria": "/api/knowledge-criteria.json",
        "criteria_version": criteria.get("version"),
        "loop": "/KNOWLEDGE_LOOP.md",
        "exclude_types": criteria.get("exclude_types") or ["Times"],
        "counts": counts,
        "due": due,
        "items": items,
    }


def attach_knowledge(items: list[Any], by_id: dict[str, dict[str, Any]]) -> list[Any]:
    out = []
    for it in items:
        if not isinstance(it, dict):
            out.append(it)
            continue
        copy = dict(it)
        rec = by_id.get(str(copy.get("id") or ""))
        if rec is None:
            copy.pop("knowledge", None)
        else:
            copy["knowledge"] = rec
        out.append(copy)
    return out


def merge_indexes(registry: dict[str, Any]) -> list[Path]:
    by_id = {
        str(it["id"]): it["knowledge"]
        for it in registry.get("items") or []
        if isinstance(it, dict) and it.get("id") and it.get("knowledge")
    }
    touched: list[Path] = []
    generated = registry.get("generated")
    for path, wrap in ((CATALOG, True), (INDEX, False), (ARTICLES, False), (DIVERSE, False)):
        if not path.exists():
            continue
        data = load_json(path)
        items = data.get("items") if isinstance(data.get("items"), list) else []
        data["items"] = attach_knowledge(items, by_id)
        if wrap or "generated" in data:
            data["generated"] = generated
        write_json(path, data)
        touched.append(path)
    return touched


def write_registry(registry: dict[str, Any], criteria: dict[str, Any]) -> None:
    write_json(KNOWLEDGE_OUT, registry)
    write_json(CRITERIA_OUT, criteria)


def rebuild_tags() -> Path:
    """Derive /api/tags.json from catalog so agents and the Tags page stay aligned."""
    catalog = load_json(CATALOG)
    tags: dict[str, list[str]] = {}
    for it in catalog.get("items") or []:
        if not isinstance(it, dict) or not it.get("id"):
            continue
        for tag in it.get("tags") or []:
            name = str(tag)
            tags.setdefault(name, [])
            if it["id"] not in tags[name]:
                tags[name].append(it["id"])
    path = ROOT / "api" / "tags.json"
    write_json(path, {"updated": shanghai_today().isoformat(), "tags": dict(sorted(tags.items()))})
    return path


def published_html_pages() -> list[Path]:
    pages = []
    for folder in ("articles", "diverse"):
        root = ROOT / folder
        if not root.exists():
            continue
        for path in sorted(root.glob("*.html")):
            if path.name == "index.html":
                continue
            pages.append(path)
    return pages


def page_parity_gaps() -> list[str]:
    catalog = load_json(CATALOG)
    by_url = {str(it.get("url") or ""): it for it in catalog.get("items") or [] if isinstance(it, dict)}
    gaps = []
    for path in published_html_pages():
        url = "/" + path.relative_to(ROOT).as_posix()
        item = by_url.get(url)
        if not item:
            gaps.append(f"{url}:not-in-catalog")
            continue
        rel = item.get("content") or item.get("markdown")
        if not rel or not (ROOT / str(rel).lstrip("/")).exists():
            gaps.append(f"{url}:missing-markdown")
    return gaps


def validate_report(data: dict[str, Any], criteria: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not data.get("entry_id"):
        errors.append("entry_id required")
    verdict = data.get("verdict")
    if verdict not in VERDICTS:
        errors.append(f"verdict must be one of {VERDICTS}")
    if criteria and data.get("criteria_version") and data.get("criteria_version") != criteria.get("version"):
        errors.append("criteria_version does not match current criteria")
    evidence = data.get("evidence") if isinstance(data.get("evidence"), list) else []
    https = [
        e
        for e in evidence
        if isinstance(e, dict) and str(e.get("url") or "").startswith("https://")
    ]
    if verdict in {"changed", "obsolete"} and not https:
        errors.append("changed/obsolete requires at least one https evidence URL")
    return errors
