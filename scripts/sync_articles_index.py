#!/usr/bin/env python3
"""Keep articles/index.html in sync with published article HTML pages.

The Articles landing page is intentionally hand-designed, but article cards are
managed by this script. Existing cards are preserved; missing article cards are
inserted at the top of the grid. This makes publishing a new article idempotent:
adding an article HTML file is enough for the next GitHub Actions run to expose
it in the Articles index.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "articles" / "index.html"
ARTICLE_DIR = ROOT / "articles"

CARD_RE = re.compile(r'<a class="card" href="([^"]+)"')
TITLE_RE = re.compile(r"<h1>(.*?)</h1>", re.S | re.I)
DESC_RE = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"', re.S | re.I)
DATE_RE = re.compile(r'<meta\s+property="article:published_time"\s+content="([^"]+)"', re.I)
TAG_RE = re.compile(r'<meta\s+property="article:tag"\s+content="([^"]+)"', re.I)
META_RE = re.compile(r'<p class="article-meta">(.*?)</p>', re.S | re.I)


def clean(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def article_info(path: Path) -> dict[str, object] | None:
    text = path.read_text(encoding="utf-8")
    title_match = TITLE_RE.search(text)
    desc_match = DESC_RE.search(text)
    if not title_match or not desc_match:
        return None

    title = clean(title_match.group(1))
    description = clean(desc_match.group(1))
    date_match = DATE_RE.search(text)
    date = date_match.group(1) if date_match else ""
    tags = [clean(x) for x in TAG_RE.findall(text)]
    if not tags:
        tags = ["Agent"]

    # Prefer the short article metadata line as the display date when available.
    meta_match = META_RE.search(text)
    if meta_match:
        m = re.search(r"思路\s+(\d{4}-\d{2}-\d{2})", meta_match.group(1))
        if m:
            date = m.group(1)

    return {
        "href": path.name,
        "title": title,
        "description": description,
        "date": date,
        "tags": tags,
    }


def card(item: dict[str, object]) -> str:
    href = html.escape(str(item["href"]), quote=True)
    title = html.escape(str(item["title"]))
    description = html.escape(str(item["description"]))
    date = html.escape(str(item["date"]))
    tags = [str(x) for x in item["tags"]]  # type: ignore[index]
    data_tags = html.escape(" ".join(tags), quote=True)
    tag_html = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags[:4])
    label = " · ".join(tags[:2])
    return (
        f'<a class="card" href="{href}" data-tags="{data_tags}">'
        f'<div class="card__meta"><span>思路 {date} · 发表 {date}</span><span>{html.escape(label)}</span></div>'
        f'<h2 class="card__title">{title}</h2>'
        f'<p class="card__excerpt">{description}</p>'
        f'<div class="card__tags">{tag_html}</div></a>\n'
    )


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    existing = set(CARD_RE.findall(text))

    items: list[dict[str, object]] = []
    for path in ARTICLE_DIR.glob("*.html"):
        if path.name == "index.html":
            continue
        item = article_info(path)
        if item and item["href"] not in existing:
            items.append(item)

    if not items:
        print("Articles index already up to date")
        return 0

    # Newest articles first; keep the existing hand-curated ordering untouched.
    items.sort(key=lambda x: str(x["date"]), reverse=True)
    insertion = "".join(card(item) for item in items)
    marker = '<div class="grid grid--2">'
    if marker not in text:
        raise SystemExit("articles/index.html: grid marker not found")

    text = text.replace(marker, marker + "\n" + insertion, 1)
    INDEX.write_text(text, encoding="utf-8")
    print("Added article cards:", ", ".join(str(x["href"]) for x in items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
