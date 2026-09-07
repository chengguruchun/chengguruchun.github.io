#!/usr/bin/env python3
"""Write / update Hot Words run manifests (observable Execute loop)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for _ in range(12):
        if (cur / "times" / "index.html").exists() and (cur / "api").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd().resolve()


def runs_dir(root: Path) -> Path:
    return root / "api" / "hot-words" / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def evidence_count(candidates: list[Any], chosen: dict[str, Any] | None = None) -> int:
    n = 0
    for c in candidates:
        if not isinstance(c, dict):
            continue
        ev = c.get("evidence")
        if isinstance(ev, list):
            n += len(ev)
        elif isinstance(ev, str) and ev.strip():
            n += 1
        elif isinstance(ev, dict):
            n += 1
    if chosen and isinstance(chosen.get("evidence"), list):
        n += len(chosen["evidence"])
    return n


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert_index(root: Path, manifest: dict[str, Any]) -> None:
    idx_path = runs_dir(root) / "index.json"
    idx = load_json(idx_path)
    items = idx.get("items") if isinstance(idx.get("items"), list) else []
    run_id = manifest.get("runId")
    summary = {
        "runId": run_id,
        "period": manifest.get("period"),
        "phase": manifest.get("phase"),
        "word": ((manifest.get("proposal") or {}).get("word")),
        "finishedAt": manifest.get("finishedAt"),
        "path": f"/api/hot-words/runs/{run_id}.json" if run_id else None,
    }
    items = [x for x in items if isinstance(x, dict) and x.get("runId") != run_id]
    items.insert(0, summary)
    idx = {
        "name": "Hot Words run index",
        "generated": utc_now(),
        "items": items[:40],
    }
    write_json(idx_path, idx)


def write_manifest(
    root: Path,
    *,
    run_id: str,
    period: str,
    phase: str,
    started_at: str | None = None,
    finished_at: str | None = None,
    input_state: dict[str, Any] | None = None,
    proposal: dict[str, Any] | None = None,
    gates: dict[str, Any] | None = None,
    apply_info: dict[str, Any] | None = None,
    publish: dict[str, Any] | None = None,
    error: str | None = None,
    merge: bool = True,
) -> Path:
    """Create or merge a run manifest; always refresh latest.json + index."""
    path = runs_dir(root) / f"{run_id}.json"
    base: dict[str, Any] = load_json(path) if merge else {}
    if not base:
        base = {
            "runId": run_id,
            "period": period,
            "phase": phase,
            "startedAt": started_at or utc_now(),
            "finishedAt": None,
            "input": {},
            "proposal": {},
            "gates": {},
            "apply": {},
            "publish": {},
            "error": None,
        }
    base["runId"] = run_id
    base["period"] = period
    base["phase"] = phase
    if started_at:
        base["startedAt"] = started_at
    if finished_at is not None:
        base["finishedAt"] = finished_at
    elif phase in ("published", "skipped", "failed", "applied", "awaiting_review"):
        base["finishedAt"] = utc_now()
    if input_state is not None:
        base["input"] = input_state
    if proposal is not None:
        base["proposal"] = proposal
    if gates is not None:
        base["gates"] = gates
    if apply_info is not None:
        base["apply"] = apply_info
    if publish is not None:
        base["publish"] = publish
    if error is not None:
        base["error"] = error
    write_json(path, base)
    write_json(runs_dir(root) / "latest.json", base)
    upsert_index(root, base)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--period", required=True)
    ap.add_argument(
        "--phase",
        required=True,
        choices=[
            "started",
            "proposed",
            "validated",
            "awaiting_review",
            "applied",
            "published",
            "skipped",
            "failed",
        ],
    )
    ap.add_argument("--started-at", default=None)
    ap.add_argument("--finished-at", default=None)
    ap.add_argument("--input-json", default=None, help="JSON object or path to JSON file")
    ap.add_argument("--proposal-json", default=None)
    ap.add_argument("--gates-json", default=None)
    ap.add_argument("--apply-json", default=None)
    ap.add_argument("--publish-json", default=None)
    ap.add_argument("--error", default=None)
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args()
    root = repo_root(args.root)

    def parse_obj(raw: str | None) -> dict[str, Any] | None:
        if raw is None or raw == "":
            return None
        p = Path(raw)
        if p.exists() and p.is_file():
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            data = json.loads(raw)
        if not isinstance(data, dict):
            raise SystemExit("JSON value must be an object")
        return data

    path = write_manifest(
        root,
        run_id=args.run_id,
        period=args.period,
        phase=args.phase,
        started_at=args.started_at,
        finished_at=args.finished_at,
        input_state=parse_obj(args.input_json),
        proposal=parse_obj(args.proposal_json),
        gates=parse_obj(args.gates_json),
        apply_info=parse_obj(args.apply_json),
        publish=parse_obj(args.publish_json),
        error=args.error,
        merge=not args.no_merge,
    )
    print(path)


if __name__ == "__main__":
    main()
