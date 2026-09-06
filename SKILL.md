---
name: ai-knowledge-lab
description: >-
  Blog for Agents by chengguruchun. Discover capabilities, then execute.
  Content and tools grow over time — never hardcode the tool list.
---

# AI Knowledge Lab

## Positioning

**Blog for Agents** — a personal knowledge blog that agents can discover and call.
Not a runtime; static surfaces + local/CI apply scripts.

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
| `/api/catalog.json` | Knowledge index (Articles, Diverse Lab, Times) |
| `/content/**/*.md` | Canonical knowledge |
| `/api/projects*.json` | Projects (research + personal) |
| `/api/videos.json` | Videos (page-only; not in catalog) |
| `/.well-known/agent-card.json` | Static Agent Card (documentation) |

Owner: chengguruchun · Hangzhou  
GitHub: https://github.com/chengguruchun · Mail: chengguruchun@163.com
