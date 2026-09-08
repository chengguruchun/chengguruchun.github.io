#!/usr/bin/env python3
"""Build /api/thoughts.json from content/thoughts/*.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content" / "thoughts"
CRITERIA_SRC = SRC / "criteria.json"
OUT = ROOT / "api" / "thoughts.json"
CRITERIA_OUT = ROOT / "api" / "thoughts-criteria.json"
REQUIRED = ("id", "thought", "stage", "status", "origin", "contribution")
SKIP_NAMES = {"criteria.json"}
STAGES = {"topic", "candidate", "validated", "article_candidate", "published"}
ORIGINS = {"user", "ai", "joint", "external"}
CONTRIB = {"known", "synthesis", "extension", "original_candidate"}
ROUTES = {"diverse", "articles", "videos", "projects"}
GATE_SPEC = (
    ("origin", "Origin", "candidate"),
    ("contribution", "Contribution", "candidate"),
    ("articles_ok", "¬ ai+known", "article_candidate"),
    ("evidence", "Evidence", "validated"),
    ("route", "Route", "validated"),
    ("published", "Published", "published"),
)


def load_criteria() -> dict:
    if not CRITERIA_SRC.exists():
        raise SystemExit("missing content/thoughts/criteria.json")
    data = json.loads(CRITERIA_SRC.read_text(encoding="utf-8"))
    if not data.get("version") or not data.get("prompt") or not data.get("axes"):
        raise SystemExit("criteria.json needs version, prompt, axes")
    for axis in data["axes"]:
        if not axis.get("id") or not axis.get("name"):
            raise SystemExit("criteria axis needs id and name")
    return data


def compute_model_gates(data: dict, criteria: dict) -> list[dict]:
    version = criteria["version"]
    judgement = data.get("judgement") if isinstance(data.get("judgement"), dict) else {}
    raw = judgement.get("verdicts") if isinstance(judgement.get("verdicts"), list) else []
    verdicts = {v["id"]: v for v in raw if isinstance(v, dict) and v.get("id")}
    has = bool(verdicts)
    stale = has and judgement.get("criteria_version") != version
    out = []
    for axis in criteria["axes"]:
        v = verdicts.get(axis["id"])
        if not has:
            status = "pending"
            passed = False
        elif stale:
            status = "stale"
            passed = False
        elif v and v.get("pass") is True:
            status = "pass"
            passed = True
        else:
            status = "unpass"
            passed = False
        item = {
            "id": axis["id"],
            "name": axis["name"],
            "kind": "model",
            "pass": passed,
            "status": status,
            "required_from": axis.get("required_from") or "candidate",
            "criteria_version": judgement.get("criteria_version"),
        }
        if v and v.get("note") and status in {"pass", "unpass"}:
            item["note"] = v["note"]
        out.append(item)
    return out


def compute_gates(data: dict) -> list[dict]:
    checks = {
        "origin": data.get("origin") in ORIGINS,
        "contribution": data.get("contribution") in CONTRIB,
        "articles_ok": not (data.get("origin") == "ai" and data.get("contribution") == "known"),
        "evidence": bool(data.get("evidence")),
        "route": bool(data.get("route")),
        "published": data.get("stage") == "published" and bool(data.get("published_url")),
    }
    return [
        {
            "id": gid,
            "name": name,
            "pass": bool(checks[gid]),
            "required_from": req,
        }
        for gid, name, req in GATE_SPEC
    ]


def main() -> int:
    criteria = load_criteria()
    items = []
    for path in sorted(SRC.glob("*.json")):
        if path.name in SKIP_NAMES:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = [k for k in REQUIRED if not data.get(k)]
        if missing:
            raise SystemExit(f"{path.name} missing {missing}")
        if data["stage"] not in STAGES:
            raise SystemExit(f"{path.name} bad stage {data['stage']}")
        if data["origin"] not in ORIGINS:
            raise SystemExit(f"{path.name} bad origin {data['origin']}")
        if data["contribution"] not in CONTRIB:
            raise SystemExit(f"{path.name} bad contribution {data['contribution']}")
        route = data.get("route")
        if route in ("", None):
            data["route"] = None
        elif route not in ROUTES:
            raise SystemExit(f"{path.name} bad route {route}")
        also = data.get("also") or []
        if not isinstance(also, list) or any(x not in ROUTES for x in also):
            raise SystemExit(f"{path.name} bad also {also}")
        if data["stage"] in {"validated", "published", "article_candidate"} and not data.get("route"):
            raise SystemExit(f"{path.name} promoted stage needs route")
        if data["stage"] == "published":
            failed = [g["id"] for g in compute_gates(data) if not g["pass"]]
            if failed:
                raise SystemExit(f"{path.name} published but gates failed: {failed}")
        data["gates"] = compute_gates(data)
        data["model_gates"] = compute_model_gates(data, criteria)
        data["content"] = f"/content/thoughts/{path.name}"
        items.append(data)
    items.sort(key=lambda x: (x.get("updated") or "", x["id"]), reverse=True)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    criteria_pub = dict(criteria)
    criteria_pub["content"] = "/content/thoughts/criteria.json"
    criteria_pub["generated"] = generated
    CRITERIA_OUT.write_text(
        json.dumps(criteria_pub, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    OUT.write_text(
        json.dumps(
            {
                "type": "Thoughts",
                "loop": "Chat(off-site, distill) → Topic (inbound) → Candidate → Validated → Route → Published",
                "intake": {
                    "inbound": "topic",
                    "from": "Any agent that loaded /SKILL.md. Chat and rough ideas distill to one sentence.",
                    "transcripts": "off-site",
                    "publish_only_after_gates": True,
                },
                "criteria": "/api/thoughts-criteria.json",
                "criteria_version": criteria["version"],
                "gates_layers": {
                    "field": "build_thoughts.py checks fields. No model is called on the site.",
                    "model": "An agent runs the criteria prompt and files thought.judgement.",
                },
                "note": "Inbound is topic, not a conclusion. Agents filter and validate. They do not ghostwrite. Field PASS is not enough to publish.",
                "generated": generated,
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(items)} thoughts) + {CRITERIA_OUT.relative_to(ROOT)} v{criteria['version']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
