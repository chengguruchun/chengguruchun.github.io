---
name: ai-knowledge-lab
description: >-
  Open knowledge system by chengguruchun for AI Agents. Discover capabilities,
  then execute. Content and tools grow over time — never hardcode the tool list.
---

# AI Knowledge Lab

## Protocol

1. **Discover** — `GET /api/discover.json`
2. **Execute** — look up the tool in `GET /mcp/tools.json`, then call its `static` target
3. Prefer `/content/**/*.md` over HTML. Do not invent tool names.

Meta tools only: `lab_discover`, `lab_execute`.  
Add capabilities in `discover.json` + `tools.json`, not this file.

## Stable surfaces

| Path | Role |
|------|------|
| `/SKILL.md` | This protocol (rare changes) |
| `/api/discover.json` | Capability index (grows) |
| `/mcp/tools.json` | Full schemas (grows) |
| `/api/catalog.json` | Knowledge index |
| `/content/**/*.md` | Canonical knowledge |

Owner: chengguruchun · Hangzhou  
GitHub: https://github.com/chengguruchun · Mail: chengguruchun@163.com
