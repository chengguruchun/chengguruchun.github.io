---
name: ai-knowledge-lab
description: >-
  Use for chengguruchun's AI Knowledge Lab (Agent infra, Diverse Lab, Projects).
  Discover tools at runtime, then invoke — do not hardcode the tool list.
---

# AI Knowledge Lab

Open knowledge system for AI agents.  
**Independent Thinker · AI Agents · Complex Systems · Diverse Thinking**

## Protocol

1. **Discover** — `GET /api/discover.json`  
   Optional: filter with a query in your head against `tools[].name/description`.
2. **Invoke** — pick a `tools[].name`, resolve `invoke` / full schema from `GET /mcp/tools.json`, then `GET` the mapped path (fill `path_template` from args).
3. **Cite** — prefer `/content/**/*.md` over HTML.

Do **not** invent tool names. If unsure, discover again.

## Stable endpoints

| Endpoint | Role |
|----------|------|
| `/SKILL.md` | This file (rarely changes) |
| `/api/discover.json` | Capability index (grows) |
| `/mcp/tools.json` | Full tool schemas (grows) |
| `/api/catalog.json` | Knowledge entries index |
| `/content/**/*.md` | Canonical knowledge |

## Meta tools

- `lab_discover` → `/api/discover.json`
- `lab_invoke` → resolve via `/mcp/tools.json`, then HTTP GET

New capabilities = new entries in `discover` / `tools.json` only.

## Owner

chengguruchun · Hangzhou · chengguruchun@163.com  
https://chengguruchun.github.io
