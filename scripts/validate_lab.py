#!/usr/bin/env python3
"""Validate AI Knowledge Lab agent surfaces, indexes, and content coherence.

Usage:
  python3 scripts/validate_lab.py
  python3 scripts/validate_lab.py --live   # optional HTTP checks (may be flaky)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://chengguruchun.github.io"
FAIL = 0
WARN = 0


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def fail(msg: str) -> None:
    global FAIL
    FAIL += 1
    print(f"FAIL  {msg}")


def warn(msg: str) -> None:
    global WARN
    WARN += 1
    print(f"WARN  {msg}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"JSON parse {path.relative_to(ROOT)}: {e}")
        return None


def check_agent_surfaces() -> None:
    print("\n== Agent surfaces ==")
    required = [
        "SKILL.md",
        "api/discover.json",
        "mcp/tools.json",
        "api/catalog.json",
        "content/index.json",
        "api/projects.json",
        "api/projects-research.json",
        "api/projects-personal.json",
        "api/videos.json",
        "api/times.json",
        "api/tags.json",
        "api/feeds.json",
        "feed.xml",
        "llms.txt",
        ".well-known/agent-card.json",
        "api/agent-native/criteria.json",
        "api/agent-native/runs/latest.json",
        "api/thoughts.json",
        "api/thoughts-criteria.json",
        "content/thoughts/criteria.json",
        "THOUGHT_LOOP.md",
        "bench/index.html",
    ]
    for rel in required:
        p = ROOT / rel
        if p.exists():
            ok(rel)
        else:
            fail(f"missing {rel}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "Blog for Agents" not in skill:
        fail("SKILL.md missing Blog for Agents positioning")
    else:
        ok("SKILL.md Blog for Agents")
    if "discover" not in skill.lower() or "execute" not in skill.lower():
        fail("SKILL.md missing discover→execute protocol")
    else:
        ok("SKILL.md discover→execute")

    disc = load_json(ROOT / "api" / "discover.json")
    tools = load_json(ROOT / "mcp" / "tools.json")
    if disc and tools:
        dnames = {t["name"] for t in disc.get("tools", [])}
        tnames = {t["name"] for t in tools.get("tools", [])}
        for need in (
            "lab_discover",
            "lab_execute",
            "lab_list_entries",
            "lab_hot_words_apply",
            "lab_list_projects_research",
            "lab_list_projects_personal",
            "lab_agent_native_status",
            "lab_list_thoughts",
            "lab_get_thought",
            "lab_propose_topic",
            "lab_thought_validate",
            "lab_thought_criteria",
            "lab_thought_judge",
        ):
            if need not in dnames:
                fail(f"discover missing {need}")
            else:
                ok(f"discover has {need}")
            if need not in tnames:
                fail(f"tools missing {need}")
            else:
                ok(f"tools has {need}")
        # descriptions
        for bag, label in ((disc["tools"], "discover"), (tools["tools"], "tools")):
            by = {t["name"]: t for t in bag}
            apply = by.get("lab_hot_words_apply", {})
            desc = apply.get("description") or ""
            if "review before push" in desc.lower():
                fail(f"{label} lab_hot_words_apply still says review before push")
            if "auto-publish" not in desc.lower() and "auto-publishes" not in desc.lower() and "Mondays" not in desc:
                # accept "Actions auto-publishes" variants
                if "Actions" not in desc and "Monday" not in desc and "Mondays" not in desc:
                    warn(f"{label} lab_hot_words_apply should mention Actions Monday auto-publish")
            entries = by.get("lab_list_entries", {})
            ed = entries.get("description") or ""
            if "Times" not in ed or "Projects" not in ed:
                fail(f"{label} lab_list_entries should document type filter / Projects dedicated APIs")
            else:
                ok(f"{label} lab_list_entries docs")


def check_scrub() -> None:
    print("\n== Scrub (user-facing) ==")
    banned = ["占位", "即将上线"]
    # Public HTML / Chinese UI surfaces
    roots = [
        ROOT / "index.html",
        ROOT / "articles",
        ROOT / "diverse",
        ROOT / "projects",
        ROOT / "videos",
        ROOT / "times",
        ROOT / "about",
        ROOT / "tags",
        ROOT / "content",
    ]
    files: list[Path] = []
    for r in roots:
        if r.is_file():
            files.append(r)
        elif r.is_dir():
            files.extend(p for p in r.rglob("*") if p.suffix in {".html", ".md"})
    for p in files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for b in banned:
            if b in text:
                fail(f"banned '{b}' in {p.relative_to(ROOT)}")
    # orphan project HTML must be gone
    for name in ("concurrency.html", "redpacket.html", "miaoshao.html"):
        if (ROOT / "projects" / name).exists():
            fail(f"orphan projects/{name} still exists")
        else:
            ok(f"orphan projects/{name} absent")
    # series framing gone
    art_html = (ROOT / "articles" / "k8s-to-agent-control-plane.html").read_text(encoding="utf-8")
    art_md = (ROOT / "content" / "articles" / "k8s-to-agent-control-plane.md").read_text(encoding="utf-8")
    for label, text in (("html", art_html), ("md", art_md)):
        if "第 1 篇" in text or "系列" in text and "From K8s" in text:
            fail(f"article {label} still has 系列/第 1 篇 framing")
        else:
            ok(f"article {label} no series framing")


def check_index_coherence() -> None:
    print("\n== Index coherence ==")
    index = load_json(ROOT / "content" / "index.json")
    catalog = load_json(ROOT / "api" / "catalog.json")
    if not index or not catalog:
        return
    i_items = index.get("items") or []
    c_items = catalog.get("items") or []
    i_ids = [x.get("id") for x in i_items]
    c_ids = [x.get("id") for x in c_items]
    if i_ids != c_ids:
        fail(f"index/catalog id order mismatch: {i_ids} vs {c_ids}")
    else:
        ok("index and catalog ids match")

    types = {x.get("type") for x in i_items}
    if "Videos" in types:
        fail("Videos must not appear in content/index.json / catalog")
    else:
        ok("no Videos in catalog/index")
    if "Projects" in types:
        fail("old static Projects HTML entries must not be in catalog")
    else:
        ok("no Projects HTML entries in catalog")
    if "Times" not in types:
        fail("Times/Hot Words entry missing from catalog")
    else:
        ok("Times in catalog")
    if "Articles" not in types or "Diverse Lab" not in types:
        fail("Articles / Diverse Lab missing from catalog")
    else:
        ok("Articles + Diverse Lab present")

    for it in i_items:
        if it.get("type") in ("Articles", "Diverse Lab"):
            content = it.get("content") or it.get("markdown")
            if not content:
                fail(f"{it.get('id')} missing content path")
            else:
                rel = content.lstrip("/")
                if not (ROOT / rel).exists():
                    fail(f"missing markdown {content}")
                else:
                    ok(f"content {content}")
        if it.get("type") == "Times":
            md = it.get("markdown")
            if not md or not (ROOT / md.lstrip("/")).exists():
                fail(f"Times markdown missing: {md}")
            else:
                ok(f"Times markdown {md}")

    # tags coherence: every catalog id should appear under its tags
    tags = load_json(ROOT / "api" / "tags.json")
    if tags:
        tagmap = tags.get("tags") or {}
        for it in i_items:
            eid = it["id"]
            for t in it.get("tags") or []:
                if eid not in (tagmap.get(t) or []):
                    fail(f"tags.json missing {eid} under {t}")
        # no video/project orphan ids from old model
        for bad in ("vid-control-plane", "vid-runtime", "vid-registry", "proj-concurrency", "proj-redpacket", "proj-miaoshao"):
            for t, ids in tagmap.items():
                if bad in ids:
                    fail(f"tags.json still references removed id {bad} under {t}")
        ok("tags.json scanned")


def check_hot_words() -> None:
    print("\n== Hot Words ==")
    times = load_json(ROOT / "api" / "times.json")
    if not times:
        return
    issues = times.get("issues") or []
    if not issues:
        fail("api/times.json has no issues")
        return
    cur = issues[0]
    word = (cur.get("word") or "").strip()
    why = (cur.get("why") or "").strip()
    if not word:
        fail("current hot word empty")
    else:
        ok(f"current word: {word}")
    if len(why) < 40:
        fail(f"current why too short ({len(why)})")
    else:
        ok("why length >= 40")
    if times.get("current") != cur.get("period"):
        fail("times.current != issues[0].period")
    else:
        ok("times.current matches")
    # workflow gates present
    wf = (ROOT / ".github" / "workflows" / "hot-words-weekly.yml").read_text(encoding="utf-8")
    for needle in ("force", "quality gate", "[hot-words] failed", "len(why) < 40"):
        if needle not in wf:
            # allow slight variants
            if needle == "len(why) < 40" and "why length" not in wf and "< 40" not in wf:
                fail(f"workflow missing gate hint: {needle}")
            elif needle != "len(why) < 40" and needle not in wf:
                fail(f"workflow missing: {needle}")
    if "force" in wf and "[hot-words] failed" in wf and ("< 40" in wf or "len(why)" in wf):
        ok("workflow has force + failure issue + why length gate")
    apply = (ROOT / "scripts" / "hot_words_apply.py").read_text(encoding="utf-8")
    if "content/index.json" not in apply or "catalog.json" not in apply:
        fail("hot_words_apply.py should upsert index/catalog")
    else:
        ok("hot_words_apply upserts index/catalog")


def check_thoughts() -> None:
    print("\n== Thought loop ==")
    thoughts = load_json(ROOT / "api" / "thoughts.json")
    if not thoughts:
        return
    items = thoughts.get("items") or []
    if len(items) < 1:
        fail("thoughts.json should have at least 1 inbound topic")
    else:
        ok(f"thoughts {len(items)} items")
    if thoughts.get("intake", {}).get("inbound") != "topic":
        fail("thoughts.json intake.inbound should be topic")
    else:
        ok("intake inbound is topic")
    stages = {x.get("stage") for x in items if isinstance(x, dict)}
    if "topic" not in stages:
        fail("need at least one topic (inbound, not a conclusion)")
    else:
        ok("has inbound topic")
    if "candidate" not in stages and "published" not in stages:
        ok("bench is staging inbound topic only")
    for it in items:
        if not isinstance(it, dict):
            continue
        for k in ("id", "thought", "stage", "origin", "contribution"):
            if not it.get(k):
                fail(f"thought {it.get('id')} missing {k}")
        if not it.get("gates"):
            fail(f"thought {it.get('id')} missing gates")
        if not it.get("model_gates"):
            fail(f"thought {it.get('id')} missing model_gates")
        if it.get("stage") in {"validated", "published", "article_candidate"} and not it.get("route"):
            fail(f"thought {it.get('id')} needs route")
        if it.get("stage") == "published":
            dest = it.get("promotes_to") or ""
            if not dest or not (ROOT / str(dest).lstrip("/")).exists():
                fail(f"published thought {it.get('id')} missing promotes_to file")
            else:
                ok(f"promoted {it.get('id')} → {it.get('route')}")
        src = ROOT / str((it.get("content") or "")).lstrip("/")
        if it.get("content") and not src.exists():
            fail(f"missing thought source {it.get('content')}")
    if thoughts.get("criteria") != "/api/thoughts-criteria.json":
        fail("thoughts.json should point at thoughts-criteria.json")
    else:
        ok("thoughts.json has criteria pointer")
    criteria = load_json(ROOT / "api" / "thoughts-criteria.json")
    src_criteria = load_json(ROOT / "content" / "thoughts" / "criteria.json")
    if not criteria or not src_criteria:
        pass
    elif not criteria.get("prompt") or not criteria.get("version") or not criteria.get("axes"):
        fail("thoughts-criteria.json needs prompt, version, axes")
    elif criteria.get("version") != src_criteria.get("version"):
        fail("api/thoughts-criteria.json version != content/thoughts/criteria.json")
    else:
        ok(f"model criteria v{criteria.get('version')}")
    loop_doc = (ROOT / "THOUGHT_LOOP.md").read_text(encoding="utf-8")
    if "off-site" not in loop_doc and "offsite" not in loop_doc.lower():
        fail("THOUGHT_LOOP.md should keep chats off-site")
    else:
        ok("THOUGHT_LOOP.md chats off-site")
    if "model_gates" not in loop_doc or "criteria.json" not in loop_doc:
        fail("THOUGHT_LOOP.md should document model gates + living criteria")
    else:
        ok("THOUGHT_LOOP.md documents model criteria")
    bench = (ROOT / "bench" / "index.html").read_text(encoding="utf-8")
    if "lab-thoughts" not in bench:
        fail("bench page should render thoughts")
    else:
        ok("bench page has thought mount")
    if "bench-flow" not in bench:
        fail("bench page should mount the flow")
    else:
        ok("bench page has flow mount")
    if 'id="bench-stage"' not in bench or 'id="bench-flow"' not in bench:
        fail("bench page should mount the stage play")
    else:
        ok("bench page has stage play")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "Bench process" not in skill or "lab_thought_judge" not in skill:
        fail("SKILL.md should document the Bench process")
    else:
        ok("SKILL.md documents Bench process")
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "Bench 过程" not in home or "lab_propose_topic" not in home:
        fail("home should include the Bench process in the Skill panel")
    else:
        ok("home Skill panel has Bench process")
    if 'href="bench/"' not in home or ">Agent Bench<" not in home:
        fail("home nav should include Bench")
    else:
        ok("home nav has Bench")


def check_projects() -> None:
    print("\n== Projects ==")
    proj = load_json(ROOT / "api" / "projects.json")
    research = load_json(ROOT / "api" / "projects-research.json")
    personal = load_json(ROOT / "api" / "projects-personal.json")
    if not proj or not research or not personal:
        return
    if proj.get("url") != "/projects/":
        fail("projects.json url should be /projects/")
    else:
        ok("projects.json url /projects/")
    if "sections" not in proj:
        fail("projects.json missing sections")
    else:
        ok("projects.json has sections")
    r_items = research.get("items") or []
    p_items = personal.get("items") or []
    if len(r_items) != 3:
        fail(f"research should have 3 items, got {len(r_items)}")
    else:
        ok("research 3 items")
    need = {
        "TencentCloud/TencentDB-Agent-Memory",
        "cobusgreyling/loop-engineering",
        "deepseek-ai/deepseek-harness",
    }
    got = {x.get("full_name") for x in r_items}
    if got != need:
        fail(f"research repos mismatch: {got}")
    else:
        ok("research repos match")
    for x in r_items:
        for k in ("full_name", "description", "html_url", "stargazers_count", "language", "updated_at"):
            if k not in x:
                fail(f"research item missing {k}: {x.get('full_name')}")
    if len(p_items) != 1:
        fail(f"personal should have 1 item, got {len(p_items)}")
    else:
        ok("personal 1 item")
    p_got = {x.get("full_name") for x in p_items}
    if p_got != {"chengguruchun/llm-trace-reuse"}:
        fail(f"personal repos mismatch: {p_got}")
    else:
        ok("personal repo is llm-trace-reuse")

    videos = load_json(ROOT / "api" / "videos.json")
    vhtml = (ROOT / "videos" / "index.html").read_text(encoding="utf-8")
    items = (videos or {}).get("items") or []
    if not videos:
        fail("api/videos.json missing or unreadable")
    else:
        ok(f"videos.json {len(items)} item(s)")

    # A card with no recording behind it must say so on both surfaces, or the
    # page advertises work that does not exist.
    for item in items:
        vid = item.get("id") or "<no id>"
        if f'id="{vid}"' not in vhtml:
            fail(f"videos page missing card for {vid}")
            continue
        planned = item.get("stage") == "planned"
        if not item.get("date") and not planned:
            fail(f"{vid} has no date and is not stage=planned")
        elif planned and item.get("date"):
            fail(f"{vid} is stage=planned but carries a date")
        else:
            ok(f"videos page has {vid} ({item.get('stage') or 'published'})")

    planned_ids = [i.get("id") for i in items if i.get("stage") == "planned"]
    for vid in planned_ids:
        card = re.search(
            rf'<article[^>]*id="{re.escape(vid)}".*?</article>', vhtml, re.DOTALL
        )
        if not card:
            continue
        if "video-frame--planned" not in card.group(0):
            fail(f"{vid} is planned but its frame still shows a play button")
        elif ">planned<" not in card.group(0):
            fail(f"{vid} is planned but the card shows no planned tag")
        else:
            ok(f"{vid} card marked planned")


def check_feeds_script() -> None:
    print("\n== Feeds script ==")
    src = (ROOT / "scripts" / "build_feeds.py").read_text(encoding="utf-8")
    if "rss_item_set_key" not in src and "unchanged" not in src:
        fail("build_feeds.py should skip rewrite when item set unchanged")
    else:
        ok("build_feeds.py has unchanged-item skip")


def check_live() -> None:
    print("\n== Live (optional) ==")
    paths = [
        "/SKILL.md",
        "/api/discover.json",
        "/api/catalog.json",
        "/api/projects-research.json",
        "/.well-known/agent-card.json",
    ]
    for path in paths:
        url = BASE + path
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "validate-lab"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                code = resp.status
            if 200 <= code < 300:
                ok(f"live {path} -> {code}")
            else:
                warn(f"live {path} -> {code}")
        except Exception as e:
            warn(f"live {path} failed: {e}")


DIST_SKILL = Path("dist/skills/ai-knowledge-lab/SKILL.md")


def frontmatter_description(text: str) -> str:
    m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return ""
    d = re.search(r"description: >-\n((?:[ \t]+.*\n)+)", m.group(1))
    if not d:
        return ""
    return " ".join(line.strip() for line in d.group(1).splitlines())


def check_distribution() -> None:
    """The skill only gets used if agents can find it and the beacon can report back."""
    print("\n== Distribution ==")
    dist = ROOT / DIST_SKILL
    if not dist.exists():
        fail(f"missing {DIST_SKILL}")
        return
    ok(str(DIST_SKILL))

    root_desc = frontmatter_description((ROOT / "SKILL.md").read_text(encoding="utf-8"))
    dist_desc = frontmatter_description(dist.read_text(encoding="utf-8"))
    if not root_desc or not dist_desc:
        fail("SKILL.md description frontmatter not parseable")
    elif root_desc != dist_desc:
        fail("dist skill description drifted from /SKILL.md — keep them identical")
    else:
        ok("skill descriptions in sync")

    if len(dist_desc) > 1024:
        fail(f"dist skill description {len(dist_desc)} chars (max 1024)")
    else:
        ok(f"description length {len(dist_desc)}")

    for rel, key in (("api/discover.json", "tools"), ("mcp/tools.json", "tools")):
        data = load_json(ROOT / rel)
        names = {t.get("name") for t in (data or {}).get(key, [])}
        if "lab_hello" in names:
            ok(f"{rel} exposes lab_hello")
        else:
            fail(f"{rel} missing lab_hello beacon")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "lab_hello" in skill:
        ok("SKILL.md documents the hello step")
    else:
        fail("SKILL.md does not tell agents to call lab_hello")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if "data-agent-hello" in home:
        ok("home page shows the handshake count")
    else:
        fail("home page missing data-agent-hello counter")


SEO_SKIP_DIRS = {".git", ".preview", ".local", ".pi", "node_modules", "__pycache__"}


def site_path_for(rel: str) -> str:
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def check_seo() -> None:
    """Every page must be indexable by search engines, not just readable by agents."""
    print("\n== SEO surfaces ==")
    for rel in ("sitemap.xml", "robots.txt", "assets/img/og-cover.png", "assets/img/og-cover.svg"):
        if (ROOT / rel).exists():
            ok(rel)
        else:
            fail(f"missing {rel} — run `python3 scripts/build_seo.py`")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8") if (ROOT / "sitemap.xml").exists() else ""
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").exists() else ""
    if f"Sitemap: {BASE}/sitemap.xml" in robots:
        ok("robots.txt points at sitemap")
    else:
        fail("robots.txt missing Sitemap directive")

    pages = [
        p
        for p in sorted(ROOT.rglob("*.html"))
        if not any(part in SEO_SKIP_DIRS for part in p.relative_to(ROOT).parts)
    ]
    if not pages:
        fail("no HTML pages found")
        return

    missing_meta: list[str] = []
    missing_from_sitemap: list[str] = []
    for p in pages:
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8", errors="ignore")
        needed = ('rel="canonical"', 'property="og:title"', 'application/ld+json')
        if not all(token in text for token in needed):
            missing_meta.append(rel)
        if f"<loc>{BASE}{site_path_for(rel)}</loc>" not in sitemap:
            missing_from_sitemap.append(rel)

    if missing_meta:
        fail(f"{len(missing_meta)} page(s) without canonical/OG/JSON-LD: {', '.join(missing_meta[:4])}")
    else:
        ok(f"canonical + OG + JSON-LD on {len(pages)} pages")

    if missing_from_sitemap:
        fail(f"{len(missing_from_sitemap)} page(s) absent from sitemap: {', '.join(missing_from_sitemap[:4])}")
    else:
        ok(f"sitemap covers {len(pages)} pages")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Also hit production URLs (soft warnings)")
    args = ap.parse_args()
    print(f"validate_lab root={ROOT}")
    check_agent_surfaces()
    check_scrub()
    check_index_coherence()
    check_hot_words()
    check_thoughts()
    check_projects()
    check_feeds_script()
    check_seo()
    check_distribution()
    if args.live:
        check_live()
    print()
    if FAIL:
        print(f"RESULT: {FAIL} FAIL, {WARN} WARN")
        sys.exit(1)
    print(f"RESULT: 0 FAIL, {WARN} WARN")
    sys.exit(0)


if __name__ == "__main__":
    main()
