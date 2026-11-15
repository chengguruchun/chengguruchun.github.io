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
        "api/thought-topic.schema.json",
        "docs/templates/thought-topic.template.json",
        "content/thoughts/criteria.json",
        "THOUGHT_LOOP.md",
        "KNOWLEDGE_LOOP.md",
        "content/knowledge/criteria.json",
        "api/knowledge.json",
        "api/knowledge-criteria.json",
        "api/knowledge/runs/latest.json",
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
            "lab_continue_thought",
            "lab_thought_validate",
            "lab_thought_criteria",
            "lab_thought_judge",
            "lab_knowledge_status",
            "lab_knowledge_due",
            "lab_knowledge_criteria",
            "lab_knowledge_report",
            "lab_knowledge_review",
            "lab_knowledge_run_status",
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
            continuation = by.get("lab_continue_thought", {})
            cd = continuation.get("description") or ""
            if "progress_log" not in cd or "stage" not in cd:
                fail(f"{label} lab_continue_thought must document append-only progress and stage preservation")
            else:
                ok(f"{label} lab_continue_thought docs")


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

    # Agent-facing article metadata is an explicit contract, not just UI labels.
    article_indexes = (
        ("api/catalog.json", c_items),
        ("content/index.json", i_items),
        ("api/articles.json", (load_json(ROOT / "api" / "articles.json") or {}).get("items") or []),
        ("api/diverse-lab.json", (load_json(ROOT / "api" / "diverse-lab.json") or {}).get("items") or []),
    )
    expected_articles = [x.get("id") for x in c_items if x.get("type") == "Articles"]
    expected_diverse = [x.get("id") for x in c_items if x.get("type") == "Diverse Lab"]
    section_ids = {
        "api/articles.json": [x.get("id") for x in article_indexes[2][1]],
        "api/diverse-lab.json": [x.get("id") for x in article_indexes[3][1]],
    }
    if section_ids["api/articles.json"] != expected_articles:
        fail("api/articles.json IDs/order differ from catalog Articles")
    else:
        ok("api/articles.json matches catalog")
    if section_ids["api/diverse-lab.json"] != expected_diverse:
        fail("api/diverse-lab.json IDs/order differ from catalog Diverse Lab")
    else:
        ok("api/diverse-lab.json matches catalog")
    for label, rows in article_indexes:
        for item in rows:
            if item.get("type") not in ("Articles", "Diverse Lab"):
                continue
            eid = item.get("id") or "<missing-id>"
            if not str(item.get("name") or "").strip():
                fail(f"{label} {eid} missing name")
            if not str(item.get("desc") or "").strip():
                fail(f"{label} {eid} missing desc")
            if not str(item.get("url") or "").strip():
                fail(f"{label} {eid} missing url")
        ok(f"{label} agent metadata scanned")

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
        elif it.get("content") and src.exists():
            detail = load_json(src)
            if not isinstance(detail, dict):
                fail(f"thought source is not a JSON object: {it.get('content')}")
                detail = {}
            context = detail.get("context")
            evolution = detail.get("evolution")
            progress_log = detail.get("progress_log")
            if context is not None and not isinstance(context, dict):
                fail(f"thought {it.get('id')} context must be an object")
                context = {}
            if evolution is not None and not isinstance(evolution, dict):
                fail(f"thought {it.get('id')} evolution must be an object")
                evolution = {}
            if progress_log is not None and not isinstance(progress_log, list):
                fail(f"thought {it.get('id')} progress_log must be an array")
                progress_log = []
            context = context if isinstance(context, dict) else {}
            evolution = evolution if isinstance(evolution, dict) else {}
            progress_log = progress_log if isinstance(progress_log, list) else []
            directions = evolution.get("directions") or []
            if not isinstance(directions, list) or any(not isinstance(x, dict) for x in directions):
                fail(f"thought {it.get('id')} evolution.directions must be an array of objects")
                directions = []
            for entry in progress_log:
                if not isinstance(entry, dict) or not entry.get("date") or not (entry.get("summary") or entry.get("type")):
                    fail(f"thought {it.get('id')} progress_log entries need date and summary/type")
                    break
            summary = (
                context.get("problem_space")
                or context.get("original_observation")
                or context.get("trigger")
                or (detail.get("source") or {}).get("note")
                or detail.get("thought")
                or ""
            )
            summary = " ".join(str(summary).split())
            if len(summary) > 220:
                summary = summary[:217].rstrip() + "..."
            preview = [
                str(x.get("title") or x.get("id") or "").strip()
                for x in directions
                if x.get("title") or x.get("id")
            ][:6]
            actions = evolution.get("next_actions") or []
            next_step = actions[0] if isinstance(actions, list) and actions else ""
            if isinstance(next_step, dict):
                next_step = next_step.get("action") or next_step.get("title") or next_step.get("description") or ""
            if it.get("context_summary") != summary:
                fail(f"thought {it.get('id')} context_summary is out of sync with source")
            if it.get("evolution_preview") != preview:
                fail(f"thought {it.get('id')} evolution_preview is out of sync with source")
            thesis = detail.get("thesis") if isinstance(detail.get("thesis"), dict) else {}
            thesis_summary = thesis.get("core") or thesis.get("reframing") or thesis.get("key_question") or ""
            thesis_summary = " ".join(str(thesis_summary).split())
            if len(thesis_summary) > 220:
                thesis_summary = thesis_summary[:217].rstrip() + "..."
            questions = evolution.get("open_questions") or []
            questions_preview = [str(q).strip() for q in questions[:4] if str(q).strip()] if isinstance(questions, list) else []
            progress_count = len(progress_log)
            last = progress_log[-1] if progress_log and isinstance(progress_log[-1], dict) else {}
            last_progress = {key: str(last.get(key) or "").strip() for key in ("date", "type", "summary", "next") if last.get(key)}
            if it.get("next_step") != str(next_step).strip():
                fail(f"thought {it.get('id')} next_step is out of sync with source")
            if it.get("thesis_summary") != thesis_summary:
                fail(f"thought {it.get('id')} thesis_summary is out of sync with source")
            if it.get("open_questions_preview") != questions_preview:
                fail(f"thought {it.get('id')} open_questions_preview is out of sync with source")
            if it.get("progress_count") != progress_count or it.get("last_progress") != last_progress:
                fail(f"thought {it.get('id')} progress metadata is out of sync with source")
    if thoughts.get("criteria") != "/api/thoughts-criteria.json":
        fail("thoughts.json should point at thoughts-criteria.json")
    else:
        ok("thoughts.json has criteria pointer")
    notebook = thoughts.get("topic_notebook") or {}
    if notebook.get("schema") != "/api/thought-topic.schema.json" or notebook.get("template") != "/docs/templates/thought-topic.template.json":
        fail("thoughts.json topic_notebook schema/template pointers are missing or stale")
    elif notebook.get("sections") != ["context", "thesis", "evolution", "progress_log"] or not notebook.get("progress_policy") or not notebook.get("continuation_protocol"):
        fail("thoughts.json topic_notebook lifecycle contract is incomplete")
    elif notebook.get("index_fields") != ["context_summary", "thesis_summary", "evolution_preview", "open_questions_preview", "next_step", "progress_count", "last_progress"]:
        fail("thoughts.json topic_notebook index_fields contract is incomplete")
    else:
        ok("thoughts.json topic notebook schema/template/lifecycle/index contract")
    schema = load_json(ROOT / "api" / "thought-topic.schema.json")
    template = load_json(ROOT / "docs" / "templates" / "thought-topic.template.json")
    if not schema or not template:
        fail("thought topic schema/template missing")
    elif not isinstance(template.get("context"), dict) or not isinstance(template.get("evolution"), dict) or not isinstance(template.get("progress_log"), list):
        fail("thought topic template must include context, evolution, progress_log")
    else:
        for key in ("role_shift", "possible_org_forms", "boundary_conditions"):
            if not isinstance(template.get(key), list):
                fail(f"thought topic template must include {key} as an array")
        if not isinstance(template.get("proposed_model"), dict):
            fail("thought topic template must include proposed_model as an object")
        ok("thought topic schema and complete template")
    bench_js = (ROOT / "assets" / "js" / "bench-flow.js").read_text(encoding="utf-8")
    for field in ("role_shift", "possible_org_forms", "boundary_conditions", "proposed_model", "comparisons", "experiments", "evidence", "progress_log"):
        if field not in bench_js:
            fail(f"Bench renderer missing Topic field {field}")
    else:
        ok("Bench renderer covers canonical Topic research fields")
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
    if 'id="lab-knowledge"' not in bench:
        fail("bench page should mount the knowledge registry")
    else:
        ok("bench page has knowledge registry")
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
    if "知识生命周期" not in home or "lab_knowledge_report" not in home:
        fail("home should include the knowledge lifecycle in the Skill panel")
    else:
        ok("home Skill panel has knowledge lifecycle")
    if 'href="bench/"' not in home or ">Agent Bench<" not in home:
        fail("home nav should include Bench")
    else:
        ok("home nav has Bench")


def check_knowledge() -> None:
    print("\n== Knowledge loop ==")
    registry = load_json(ROOT / "api" / "knowledge.json")
    criteria = load_json(ROOT / "api" / "knowledge-criteria.json")
    src = load_json(ROOT / "content" / "knowledge" / "criteria.json")
    catalog = load_json(ROOT / "api" / "catalog.json")
    if not registry or not criteria or not src or not catalog:
        return
    if not criteria.get("prompt") or not criteria.get("version") or not criteria.get("axes"):
        fail("knowledge-criteria.json needs prompt, version, axes")
    elif criteria.get("version") != src.get("version"):
        fail("api/knowledge-criteria.json version != content/knowledge/criteria.json")
    else:
        ok(f"knowledge criteria v{criteria.get('version')}")
    items = registry.get("items") or []
    if len(items) < 1:
        fail("knowledge.json should list published Articles/Diverse")
    else:
        ok(f"knowledge {len(items)} items")
    ids = {x.get("id") for x in items if isinstance(x, dict)}
    for it in catalog.get("items") or []:
        if not isinstance(it, dict):
            continue
        if it.get("type") == "Times":
            if it.get("knowledge"):
                fail(f"Times {it.get('id')} must not carry knowledge")
            continue
        if it.get("type") in {"Articles", "Diverse Lab"}:
            if it.get("id") not in ids:
                fail(f"catalog {it.get('id')} missing from knowledge.json")
            kn = it.get("knowledge") or {}
            if kn.get("status") not in {"fresh", "stale", "changed", "contested", "archived"}:
                fail(f"catalog {it.get('id')} missing knowledge.status")
            elif not kn.get("last_verified") or not kn.get("next_review"):
                fail(f"catalog {it.get('id')} missing last_verified/next_review")
    ok("catalog knowledge fields scanned")
    if str(ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(ROOT / "scripts"))
    from knowledge_lib import page_parity_gaps

    gaps = page_parity_gaps()
    if gaps:
        fail("published HTML missing catalog/markdown: " + ", ".join(gaps[:6]))
    else:
        ok("published HTML has catalog + markdown")
    from knowledge_lib import bench_loop_gaps

    bench_gaps = bench_loop_gaps()
    if bench_gaps:
        fail("bench skipped Thought Loop gates: " + ", ".join(bench_gaps[:6]))
    else:
        ok("bench stays on the Thought Loop")
    loop = (ROOT / "KNOWLEDGE_LOOP.md").read_text(encoding="utf-8")
    if "过期不等于错误" not in loop or "lab_knowledge_report" not in loop:
        fail("KNOWLEDGE_LOOP.md should keep stale ≠ wrong and report-only agents")
    elif "url_fetch" not in loop or "arxiv_lookup" not in loop:
        fail("KNOWLEDGE_LOOP.md should document Observe url_fetch + arxiv_lookup")
    else:
        ok("KNOWLEDGE_LOOP.md stale ≠ wrong")
    rt = src.get("runtime") if isinstance(src.get("runtime"), dict) else {}
    tools = rt.get("tools") or []
    if "url_fetch" not in tools or "arxiv_lookup" not in tools:
        fail("knowledge criteria runtime.tools must include url_fetch and arxiv_lookup")
    elif not (ROOT / "scripts" / "knowledge_runtime.py").exists():
        fail("missing scripts/knowledge_runtime.py")
    else:
        ok("knowledge research runtime is fetch + arXiv")
    wf = ROOT / ".github" / "workflows" / "knowledge-weekly.yml"
    wf_text = wf.read_text(encoding="utf-8") if wf.exists() else ""
    if not wf.exists():
        fail("missing knowledge-weekly.yml")
    elif "knowledge_check.py" not in wf_text or "knowledge_verify.py" not in wf_text:
        fail("knowledge-weekly.yml should run knowledge_check.py and knowledge_verify.py")
    else:
        ok("knowledge weekly workflow")
    if "Never rewrite article bodies" not in (ROOT / "SKILL.md").read_text(encoding="utf-8"):
        fail("SKILL.md should keep knowledge reports from rewriting articles")
    else:
        ok("SKILL.md knowledge reports do not rewrite")


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
    if not p_items:
        fail("personal snapshot is empty")
    else:
        ok(f"personal {len(p_items)} item(s)")
    p_got = {x.get("full_name") for x in p_items}
    if "chengguruchun/llm-trace-reuse" not in p_got:
        fail("personal snapshot should keep llm-trace-reuse")
    else:
        ok("personal snapshot includes llm-trace-reuse")
    for x in p_items:
        for k in ("full_name", "description", "html_url"):
            if not x.get(k):
                fail(f"personal item missing {k}: {x.get('full_name')}")

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



def check_visit_counters() -> None:
    """Every articles|diverse HTML page (except index) must ship the visit counter."""
    print("\n== Visit counters ==")
    missing: list[str] = []
    checked = 0
    for folder in ("articles", "diverse"):
        d = ROOT / folder
        if not d.is_dir():
            fail(f"missing dir {folder}/")
            continue
        for p in sorted(d.glob("*.html")):
            if p.name == "index.html":
                continue
            checked += 1
            rel = p.relative_to(ROOT).as_posix()
            body = p.read_text(encoding="utf-8", errors="ignore")
            has_js = "assets/js/visits.js" in body
            has_attrs = ("data-visits-site" in body and "data-visits-page" in body) or (
                "footer-visits" in body
            )
            if not (has_js and has_attrs):
                bits = []
                if not has_js:
                    bits.append("visits.js")
                if not has_attrs:
                    bits.append("data-visits-* / footer-visits")
                missing.append(f"{rel} (missing {', '.join(bits)})")
    if missing:
        fail(
            f"{len(missing)}/{checked} articles|diverse page(s) missing visit counter: "
            + "; ".join(missing[:6])
            + ("…" if len(missing) > 6 else "")
        )
    else:
        ok(f"visit counters on {checked} articles|diverse pages")


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
        # Google Search Console verification tokens use an .html suffix but
        # are plain-text ownership proofs, not indexable site pages.
        and not (
            len(p.relative_to(ROOT).parts) == 1
            and re.fullmatch(r"google[0-9a-f]+\.html", p.name, re.IGNORECASE)
        )
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
    check_knowledge()
    check_projects()
    check_feeds_script()
    check_visit_counters()
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
