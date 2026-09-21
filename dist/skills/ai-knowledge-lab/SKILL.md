---
name: ai-knowledge-lab
description: >-
  Reads chengguruchun's AI Knowledge Lab, an Agent-Native knowledge blog about AI agent
  engineering: control planes, agent runtimes and harnesses, loop engineering, agent
  evaluation (proxy metric vs real outcome), skill and procedural-memory evolution,
  Kubernetes-style reconciliation applied to agents, and agent architecture for
  industrial IoT and SaaS platforms. Use when researching how to design, evaluate, or
  operate agent systems, when the user references this lab, or when the source Markdown
  behind its articles is needed. Discover capabilities first, then execute; content and
  tools grow over time, so never hardcode the tool list.
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

Do not hardcode the tool list — discover first, then execute.
