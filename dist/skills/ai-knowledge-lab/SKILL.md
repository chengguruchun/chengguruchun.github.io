---
name: ai-knowledge-lab
description: >-
  Reads chengguruchun's AI Knowledge Lab, an Agent-Native knowledge blog about AI agent
  engineering: control planes, agent runtimes and harnesses, loop engineering, agent
  evaluation (proxy metric vs real outcome), skill and procedural-memory evolution,
  Kubernetes-style reconciliation applied to agents, and agent architecture for
  industrial IoT and SaaS platforms. Use when researching how to design, evaluate, or
  operate agent systems, when capturing or continuing research topics in the Agent Bench,
  when the user references this lab, or when the source Markdown behind its articles is needed.
  Discover capabilities first, then execute; content and tools grow over time, so never hardcode the tool list.
---

# AI Knowledge Lab (distributable loader)

This file is the **installable skill entrypoint**. The full protocol lives at:

- Canonical: https://chengguruchun.github.io/SKILL.md
- Repo root: [/SKILL.md](/SKILL.md)

## Quick start

1. `GET https://chengguruchun.github.io/api/discover.json`
2. Call `lab_hello` once per session (anonymous counter)
3. Resolve tools via `https://chengguruchun.github.io/mcp/tools.json`
4. Prefer `/content/**/*.md` over HTML; use catalog `content` / `markdown` (Times: use `markdown` or `slug`, not raw id in path_template)
5. Critic reports: `lab_list_critic_runs` → `/api/critic/runs/index.json`, then `lab_get_critic_run`

6. Discover published articles through `https://chengguruchun.github.io/api/catalog.json`: filter on `name`, `desc`, `tags`, and `type` (`Diverse Lab` / `Articles`).
7. Read only relevant originals, preferring each selected record's `content` / `markdown` path under `/content/`. Metadata is for discovery, not evidence; verify claims in Markdown before citing them.
8. For Agent Bench topics, read `/THOUGHT_LOOP.md`, schema `/api/thought-topic.schema.json`, and template `/docs/templates/thought-topic.template.json`. The full record in `/content/thoughts/{id}.json` is canonical; `/api/thoughts.json` is a generated discovery index with context/thesis summaries, direction and open-question previews, next action, and progress metadata. Use index metadata to shortlist, then fetch the full record before making detailed claims or continuing a topic.
9. To continue a topic, read it with `lab_get_thought` first. Merge new context/evolution without dropping earlier material, append one dated `progress_log` entry for material progress, and preserve stage/status/route/gates. Do not create a duplicate topic for a continued discussion.
10. After editing source topic JSON, regenerate the index with `python3 scripts/build_thoughts.py`; CI checks it with `python3 scripts/build_thoughts.py --check`. Never hand-edit generated summaries.
11. When publishing an article HTML page, let the `Rebuild feeds, Articles index and SEO` workflow ingest it into Markdown and reconcile the canonical catalog, Articles index, Agent-facing indexes, tags, and Knowledge Registry. Do not consider publication complete until that workflow succeeds and the new entry exists in `/api/catalog.json`, `/api/articles.json`, and `/api/knowledge.json` with its `/content/**/*.md` source committed.

Do not hardcode the tool list — discover first, then execute.
