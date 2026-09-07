#!/usr/bin/env python3
"""Build Hot Words feedback snapshot for Observe / next-week Learn context."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for _ in range(12):
        if (cur / "api" / "times.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd().resolve()


def load(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def citation_count(root: Path, word: str) -> int:
    if not word:
        return 0
    n = 0
    for rel in ("api/catalog.json", "content/index.json"):
        data = load(root / rel) or {}
        items = data.get("items") if isinstance(data.get("items"), list) else []
        for it in items:
            if not isinstance(it, dict):
                continue
            blob = " ".join(
                [
                    str(it.get("title") or ""),
                    str(it.get("excerpt") or ""),
                    " ".join(str(x) for x in (it.get("tags") or [])),
                ]
            )
            if word in blob:
                n += 1
    return n


def build(root: Path) -> dict[str, Any]:
    times = load(root / "api" / "times.json") or {}
    latest = load(root / "api" / "hot-words" / "runs" / "latest.json") or {}
    index = load(root / "api" / "hot-words" / "runs" / "index.json") or {}
    issues = times.get("issues") if isinstance(times.get("issues"), list) else []
    current = issues[0] if issues and isinstance(issues[0], dict) else {}

    runs = index.get("items") if isinstance(index.get("items"), list) else []
    proposal = latest.get("proposal") if isinstance(latest.get("proposal"), dict) else {}
    chosen = str(proposal.get("word") or current.get("word") or "")
    rejected = []
    for c in proposal.get("candidates") or []:
        if isinstance(c, dict):
            w = str(c.get("word") or "").strip()
            if w and w != chosen:
                rejected.append({
                    "word": w,
                    "reason": "not_chosen",
                    "notes": str(c.get("notes") or "")[:200],
                })

    gates = latest.get("gates") if isinstance(latest.get("gates"), dict) else {}
    evidence = gates.get("evidence") or "skip"
    prefer = "优先选能落到本站软件 / 系统 / Agent 主线的词，并带至少一条可点开的 https 证据。"
    avoid = "回避与当前词重复、口号化、以及只有空泛描述没有来源的词。"
    if evidence in ("weak", "skip", "fail"):
        prefer = "下一轮务必补齐结构化证据（title/url/claim）；先有来源，再谈热度。"
    if rejected:
        avoid = avoid + " 最近未入选：" + "、".join(x["word"] for x in rejected[:5]) + "。"

    cites = citation_count(root, chosen)
    feedback = {
        "name": "Hot Words feedback",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period": times.get("current") or latest.get("period"),
        "word": current.get("word") or chosen,
        "signals": {
            "visits": {
                "site": None,
                "page": None,
                "note": "页面访问由 Abacus 在浏览器端展示；静态 JSON 不权威计数。",
            },
            "votes": {
                "like": None,
                "dislike": None,
                "note": "投票存在读者本机 localStorage；观测面板会读取当前浏览器的选择。",
            },
            "comments": {
                "count": None,
                "note": "可后续接入 GitHub Issues 留言。",
            },
            "citations": {
                "count": cites,
                "note": "根据 catalog/index 中标题、摘要、标签是否出现该词估算。",
            },
        },
        "lastRun": {
            "runId": latest.get("runId"),
            "phase": latest.get("phase"),
            "gates": gates,
            "evidenceCount": (proposal.get("evidenceCount") if isinstance(proposal, dict) else 0),
            "publish": latest.get("publish") or {},
            "error": latest.get("error"),
        },
        "learnHints": {
            "recentWords": [f"{i.get('period')}: {i.get('word')}" for i in issues[:8] if isinstance(i, dict)],
            "rejectedCandidates": rejected[:8],
            "prefer": prefer,
            "avoid": avoid,
        },
        "recentRuns": runs[:10],
        "endpoints": {
            "times": "/api/times.json",
            "latestRun": "/api/hot-words/runs/latest.json",
            "runsIndex": "/api/hot-words/runs/index.json",
            "feedback": "/api/hot-words/feedback.json",
        },
    }
    return feedback


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    root = repo_root(args.root)
    fb = build(root)
    text = json.dumps(fb, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        out = root / "api" / "hot-words" / "feedback.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(out)
    else:
        print(text)


if __name__ == "__main__":
    main()
