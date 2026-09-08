#!/usr/bin/env python3
"""Check whether the Lab still looks agent-native, then write a run manifest.

Usage:
  python3 scripts/agent_native_check.py
  python3 scripts/agent_native_check.py --write
  python3 scripts/agent_native_check.py --write --live
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://chengguruchun.github.io"
RUNS = ROOT / "api" / "agent-native" / "runs"

SURFACES = [
    "SKILL.md",
    "api/discover.json",
    "mcp/tools.json",
    "api/catalog.json",
    "content/index.json",
    "llms.txt",
    ".well-known/agent-card.json",
    "api/projects.json",
    "api/projects-personal.json",
    "api/projects-research.json",
    "api/agent-native/criteria.json",
    "api/thoughts.json",
    "api/thoughts-criteria.json",
]

LIVE_PATHS = [
    "/SKILL.md",
    "/api/discover.json",
    "/mcp/tools.json",
    "/api/catalog.json",
    "/llms.txt",
    "/.well-known/agent-card.json",
    "/api/agent-native/criteria.json",
    "/api/thoughts.json",
    "/api/thoughts-criteria.json",
    "/THOUGHT_LOOP.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def period_now() -> str:
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    week = (now.day - 1) // 7 + 1
    return f"{now:%Y-%m}-W{week}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gate(results: list[dict[str, Any]], gid: str, ok: bool, detail: str, hard: bool = True) -> None:
    results.append({"gate": gid, "ok": ok, "hard": hard, "detail": detail})
    mark = "OK" if ok else ("FAIL" if hard else "WARN")
    print(f"  {mark}  {gid}: {detail}")


def check_surfaces(results: list[dict[str, Any]]) -> None:
    missing = [rel for rel in SURFACES if not (ROOT / rel).exists()]
    gate(results, "surfaces", not missing, "missing: " + ", ".join(missing) if missing else "all stable surfaces present")


def check_protocol(results: list[dict[str, Any]]) -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    ok = (
        "Blog for Agents" in skill
        and "discover" in skill.lower()
        and "execute" in skill.lower()
        and "lab_discover" in skill
        and "lab_execute" in skill
    )
    disc = load_json(ROOT / "api" / "discover.json")
    proto = disc.get("protocol") == "discover-then-execute"
    gate(results, "protocol", ok and proto, "SKILL + discover.json use discover-then-execute" if ok and proto else "protocol drift in SKILL.md or discover.json")


def check_tool_parity(results: list[dict[str, Any]]) -> None:
    disc = load_json(ROOT / "api" / "discover.json")
    tools = load_json(ROOT / "mcp" / "tools.json")
    dnames = {t["name"] for t in disc.get("tools", []) if isinstance(t, dict) and t.get("name")}
    tnames = {t["name"] for t in tools.get("tools", []) if isinstance(t, dict) and t.get("name")}
    only_d = sorted(dnames - tnames)
    only_t = sorted(tnames - dnames)
    ok = not only_d and not only_t and "lab_discover" in dnames and "lab_execute" in dnames
    detail = f"{len(dnames)} tools"
    if only_d:
        detail += f"; only discover: {only_d}"
    if only_t:
        detail += f"; only tools.json: {only_t}"
    gate(results, "tool_parity", ok, detail)


def check_canonical_md(results: list[dict[str, Any]]) -> None:
    catalog = load_json(ROOT / "api" / "catalog.json")
    missing = []
    for it in catalog.get("items") or []:
        if not isinstance(it, dict):
            continue
        path = it.get("content") or it.get("markdown")
        if not path:
            missing.append(f"{it.get('id')}:no-path")
            continue
        if not (ROOT / str(path).lstrip("/")).exists():
            missing.append(str(path))
    gate(results, "canonical_md", not missing, "all catalog entries have markdown" if not missing else "missing " + ", ".join(missing[:8]))


def check_catalog_index(results: list[dict[str, Any]]) -> None:
    index = load_json(ROOT / "content" / "index.json")
    catalog = load_json(ROOT / "api" / "catalog.json")
    i_ids = [x.get("id") for x in (index.get("items") or [])]
    c_ids = [x.get("id") for x in (catalog.get("items") or [])]
    gate(results, "catalog_index", i_ids == c_ids and bool(i_ids), "index and catalog ids match" if i_ids == c_ids else f"mismatch {i_ids} vs {c_ids}")


def check_machine_map(results: list[dict[str, Any]]) -> None:
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    need = ["/SKILL.md", "/api/discover.json", "/mcp/tools.json", "/api/catalog.json", "/content/", "/api/thoughts.json", "/api/thoughts-criteria.json"]
    missing = [n for n in need if n not in text]
    gate(results, "machine_map", not missing, "llms.txt lists core surfaces" if not missing else "llms.txt missing " + ", ".join(missing))


def check_agent_card(results: list[dict[str, Any]]) -> None:
    card = load_json(ROOT / ".well-known" / "agent-card.json")
    skills = {s.get("id") for s in (card.get("skills") or []) if isinstance(s, dict)}
    caps = card.get("capabilities") or {}
    ok = (
        {"discover", "catalog", "skill-protocol"}.issubset(skills)
        and bool(card.get("documentationUrl"))
        and caps.get("readonly") is True
    )
    gate(results, "agent_card", ok, "card is read-only and lists discover/catalog/skill" if ok else "agent-card missing skill ids or not readonly")


def check_projects_api(results: list[dict[str, Any]]) -> None:
    personal = load_json(ROOT / "api" / "projects-personal.json")
    items = [x for x in (personal.get("items") or []) if isinstance(x, dict)]
    need = ("full_name", "html_url", "description")
    bad = [x.get("full_name") or "?" for x in items if any(not x.get(k) for k in need)]
    ok = bool(items) and not bad
    names = [x.get("name") or x.get("full_name") for x in items]
    gate(
        results,
        "projects_api",
        ok,
        f"personal JSON snapshot ({', '.join(str(n) for n in names)})" if ok else "personal snapshot missing fields or empty",
    )


def check_live(results: list[dict[str, Any]], enabled: bool) -> None:
    if not enabled:
        gate(results, "live", True, "skipped (no --live)", hard=False)
        return
    bad = []
    for path in LIVE_PATHS:
        url = BASE + path
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "agent-native-check"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if not (200 <= resp.status < 300):
                    bad.append(f"{path}->{resp.status}")
        except Exception as e:
            bad.append(f"{path}:{e.__class__.__name__}")
    gate(results, "live", not bad, "production surfaces 2xx" if not bad else "live fail " + ", ".join(bad[:6]), hard=False)


def upsert_index(manifest: dict[str, Any]) -> None:
    path = RUNS / "index.json"
    idx = load_json(path) if path.exists() else {}
    items = idx.get("items") if isinstance(idx.get("items"), list) else []
    run_id = manifest.get("runId")
    summary = {
        "runId": run_id,
        "period": manifest.get("period"),
        "phase": manifest.get("phase"),
        "verdict": manifest.get("verdict"),
        "finishedAt": manifest.get("finishedAt"),
        "path": f"/api/agent-native/runs/{run_id}.json" if run_id else None,
    }
    items = [x for x in items if isinstance(x, dict) and x.get("runId") != run_id]
    items.insert(0, summary)
    write_json(
        path,
        {
            "name": "Agent-native run index",
            "generated": utc_now(),
            "items": items[:40],
        },
    )


def write_manifest(manifest: dict[str, Any]) -> None:
    run_id = manifest["runId"]
    write_json(RUNS / f"{run_id}.json", manifest)
    write_json(RUNS / "latest.json", manifest)
    upsert_index(manifest)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write run manifest under api/agent-native/runs/")
    ap.add_argument("--live", action="store_true", help="Also GET production surfaces")
    ap.add_argument("--period", default="", help="Override YYYY-MM-WN")
    args = ap.parse_args()

    period = args.period or os.environ.get("PERIOD") or period_now()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = os.environ.get("RUN_ID") or f"agent-native-{period}-{ts}"
    started = utc_now()
    results: list[dict[str, Any]] = []

    print(f"agent_native_check root={ROOT} period={period} live={args.live}")
    check_surfaces(results)
    check_protocol(results)
    check_tool_parity(results)
    check_canonical_md(results)
    check_catalog_index(results)
    check_machine_map(results)
    check_agent_card(results)
    check_projects_api(results)
    check_live(results, args.live)

    hard_fails = [r for r in results if r["hard"] and not r["ok"]]
    warns = [r for r in results if (not r["hard"]) and not r["ok"]]
    passes = [r for r in results if r["ok"]]
    verdict = "agent-native" if not hard_fails else "drift"
    phase = "checked" if not hard_fails else "failed"
    finished = utc_now()

    gates = {r["gate"]: ("pass" if r["ok"] else ("warn" if not r["hard"] else "fail")) for r in results}
    manifest = {
        "runId": run_id,
        "period": period,
        "phase": phase,
        "verdict": verdict,
        "startedAt": started,
        "finishedAt": finished,
        "input": {
            "live": bool(args.live),
            "periodScheme": "YYYY-MM-WN = Nth 7-day block of the calendar month (Asia/Shanghai), not ISO week",
        },
        "gates": gates,
        "checks": results,
        "summary": {"pass": len(passes), "fail": len(hard_fails), "warn": len(warns)},
        "criteria": "/api/agent-native/criteria.json",
        "publish": {
            "url": "https://chengguruchun.github.io/api/agent-native/runs/latest.json",
        },
        "error": "; ".join(f"{r['gate']}: {r['detail']}" for r in hard_fails) or None,
    }

    if args.write:
        write_manifest(manifest)
        print(f"wrote /api/agent-native/runs/{run_id}.json verdict={verdict}")

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"run_id={run_id}\n")
            f.write(f"verdict={verdict}\n")
            f.write(f"failed={'true' if hard_fails else 'false'}\n")
            f.write(f"error={manifest['error'] or ''}\n")

    print(f"RESULT: {verdict}  fail={len(hard_fails)} warn={len(warns)}")
    return 1 if hard_fails else 0


if __name__ == "__main__":
    sys.exit(main())
