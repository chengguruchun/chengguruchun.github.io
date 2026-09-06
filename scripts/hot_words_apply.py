#!/usr/bin/env python3
"""Apply a Hot Words entry to the Knowledge Lab static site (no git push)."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for _ in range(12):
        if (cur / "times" / "index.html").exists() and (cur / "content").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path.cwd().resolve()


def today() -> str:
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")


def week_label(period: str) -> str:
    m = re.match(r"^(\d{4})-(\d{2})-W(\d+)$", period, re.I)
    if not m:
        return period
    y, mo, w = m.group(1), m.group(2), int(m.group(3))
    return f"{y}-{mo} · Week {w}"


def apply(period: str, word: str, why: str, cadence: str, dry_run: bool, root: Path) -> dict:
    period = period.strip()
    word = word.strip()
    why = why.strip()
    slug = period.lower()
    date = today()
    eid = f"times-{slug}"
    md_path = root / "content" / "times" / f"{slug}.md"
    html_path = root / "times" / "index.html"
    api_path = root / "api" / "times.json"

    md = f"""---
id: {eid}
type: Times
title: {period} · {word}
period: {period}
cadence: {cadence}
date: {date}
word: {word}
---

# {word}

{why}
"""

    article = f"""        <article class="times-year times-period" data-period="{period}" data-cadence="{cadence}" data-word="{word}">
          <p class="times-year__meta">
            <span class="times-year__badge">{"Weekly" if cadence == "weekly" else cadence}</span>
            <span>{week_label(period)}</span>
            <span>更新于 {date}</span>
          </p>
          <h2 class="times-year__word">{word}</h2>
          <p class="times-year__why">{why}</p>
          <div class="times-vote" data-times-vote>
            <p class="times-vote__label">你的态度</p>
            <div class="times-vote__actions" role="group" aria-label="Like or dislike this hot word">
              <button type="button" class="times-vote__btn" data-vote="like" aria-pressed="false">Like</button>
              <button type="button" class="times-vote__btn" data-vote="dislike" aria-pressed="false">Dislike</button>
            </div>
            <p class="times-vote__hint" data-vote-hint></p>
          </div>
        </article>"""

    html = html_path.read_text(encoding="utf-8")
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="Hot Words · {word} · {period}">',
        html,
        count=1,
    )
    if re.search(r'<article class="times-year times-period"[\s\S]*?</article>', html):
        html = re.sub(
            r'<article class="times-year times-period"[\s\S]*?</article>',
            article,
            html,
            count=1,
        )
    else:
        html = html.replace('<div class="wrap">', '<div class="wrap">\n' + article, 1)

    m = re.match(r"^(\d{4}-\d{2})-W(\d+)$", period, re.I)
    if m:
        title = f"{m.group(1)} Week {int(m.group(2))} · {word}"
    else:
        title = f"{period} · {word}"
    entry = {
        "id": eid,
        "period": period,
        "cadence": cadence,
        "word": word,
        "title": title,
        "why": why,
        "date": date,
        "url": "/times/",
        "markdown": f"/content/times/{slug}.md",
    }
    if api_path.exists():
        try:
            api = json.loads(api_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            api = {}
    else:
        api = {}
    api.setdefault("type", "Times")
    api.setdefault("format", "one-word-per-issue (annual-hotword style)")
    api.setdefault("cadence", "weekly-or-monthly")
    issues = api.get("issues") if isinstance(api.get("issues"), list) else []
    if not issues and isinstance(api.get("items"), list):
        issues = [x for x in api["items"] if isinstance(x, dict)]
        api.pop("items", None)
    issues = [entry] + [
        x for x in issues
        if isinstance(x, dict) and x.get("id") != eid and x.get("period") != period
    ]
    api["issues"] = issues
    api["updated"] = date
    api["current"] = period

    changed = [str(md_path), str(html_path), str(api_path)]
    if not dry_run:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md, encoding="utf-8")
        html_path.write_text(html, encoding="utf-8")
        api_path.parent.mkdir(parents=True, exist_ok=True)
        api_path.write_text(json.dumps(api, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "dryRun": dry_run,
        "period": period,
        "word": word,
        "date": date,
        "changed": changed,
        "markdown": entry["markdown"],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Apply Hot Words entry (no push)")
    p.add_argument("--period", required=True, help="e.g. 2026-09-W2")
    p.add_argument("--word", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--cadence", default="weekly")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--root", type=Path, default=None)
    args = p.parse_args()
    root = repo_root(args.root)
    result = apply(args.period, args.word, args.why, args.cadence, args.dry_run, root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
