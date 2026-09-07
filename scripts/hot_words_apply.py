#!/usr/bin/env python3
"""Apply a Hot Words entry to the Knowledge Lab static site (no git push)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
import html as html_lib
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hot_words_lib import PERIOD_SCHEME, proposal_hash, verify_applied


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


def catalog_entry_from_issue(entry: dict) -> dict:
    word = entry.get("word") or ""
    return {
        "id": entry["id"],
        "type": "Times",
        "title": entry.get("title") or f"{entry.get('period')} · {word}",
        "excerpt": entry.get("why") or "",
        "url": entry.get("url") or "/times/",
        "date": entry.get("date") or today(),
        "tags": ["Times", "Hot Words"] + ([word] if word else []),
        "markdown": entry.get("markdown"),
        "period": entry.get("period"),
        "word": word,
    }


def upsert_times_into_indexes(root: Path, entry: dict, dry_run: bool) -> list[str]:
    """Keep content/index.json and api/catalog.json coherent with api/times.json."""
    changed: list[str] = []
    cat_entry = catalog_entry_from_issue(entry)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def upsert(path: Path, wrap_catalog: bool) -> None:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}
        if wrap_catalog:
            data.setdefault("name", "AI Knowledge Lab")
            data.setdefault("skill", "/SKILL.md")
            data.setdefault("product", "/PRODUCT.md")
            data.setdefault("llms", "/llms.txt")
            data.setdefault("base_url", "https://chengguruchun.github.io")
        items = data.get("items") if isinstance(data.get("items"), list) else []
        # drop Videos from index if any linger; drop old same Times id/period
        new_items = []
        for it in items:
            if not isinstance(it, dict):
                continue
            if it.get("type") == "Videos":
                continue
            if it.get("type") == "Times" and (
                it.get("id") == cat_entry["id"] or it.get("period") == entry.get("period")
            ):
                continue
            if it.get("id") == cat_entry["id"]:
                continue
            new_items.append(it)
        # keep Articles + Diverse Lab first, then Times current at end (or after diverse)
        non_times = [x for x in new_items if x.get("type") != "Times"]
        other_times = [x for x in new_items if x.get("type") == "Times"]
        data["items"] = non_times + [cat_entry] + other_times
        data["generated"] = generated
        changed.append(str(path))
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    upsert(root / "content" / "index.json", wrap_catalog=False)
    upsert(root / "api" / "catalog.json", wrap_catalog=True)
    return changed


def apply(period: str, word: str, why: str, cadence: str, dry_run: bool, root: Path) -> dict:
    period = period.strip()
    word = word.strip()
    why = why.strip()
    if not period or not word or not why:
        raise SystemExit("period/word/why required")
    word_html = html_lib.escape(word, quote=True)
    why_html = html_lib.escape(why, quote=False)
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

    article = f"""        <article class="times-year times-period" data-period="{period}" data-cadence="{cadence}" data-word="{word_html}">
          <p class="times-year__meta">
            <span class="times-year__badge">{"Weekly" if cadence == "weekly" else cadence}</span>
            <span>{week_label(period)}</span>
            <span>更新于 {date}</span>
          </p>
          <h2 class="times-year__word">{word_html}</h2>
          <p class="times-year__why">{why_html}</p>
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
        f'<meta name="description" content="Hot Words · {html_lib.escape(word, quote=True)} · {html_lib.escape(period, quote=True)}">',
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
    api["periodScheme"] = PERIOD_SCHEME
    api["currentProposalHash"] = proposal_hash(period, word, why)
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

    payloads = {
        md_path: md,
        html_path: html,
        api_path: json.dumps(api, ensure_ascii=False, indent=2) + "\n",
    }
    changed = [str(md_path), str(html_path), str(api_path)]
    if not dry_run:
        for path, text in payloads.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    changed.extend(upsert_times_into_indexes(root, entry, dry_run))
    checked = verify_applied(root, period, word) if not dry_run else {"ok": True, "errors": [], "gate": "skip"}
    if not dry_run and not checked["ok"]:
        raise SystemExit("consistency failed: " + "; ".join(checked["errors"]))

    return {
        "dryRun": dry_run,
        "period": period,
        "word": word,
        "date": date,
        "changed": changed,
        "markdown": entry["markdown"],
        "proposalHash": api["currentProposalHash"],
        "consistency": checked,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Apply Hot Words entry (no push)")
    p.add_argument("--period", required=True, help="e.g. 2026-09-W2")
    p.add_argument("--word", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--cadence", default="weekly")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verify", action="store_true", help="only check existing files")
    p.add_argument("--root", type=Path, default=None)
    args = p.parse_args()
    root = repo_root(args.root)
    if args.verify:
        checked = verify_applied(root, args.period, args.word)
        print(json.dumps(checked, ensure_ascii=False, indent=2))
        raise SystemExit(0 if checked["ok"] else 2)
    result = apply(args.period, args.word, args.why, args.cadence, args.dry_run, root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
