---
name: ai-knowledge-lab
description: >-
  Agent-Native knowledge blog by chengguruchun. Discover capabilities, then execute.
  Content and tools grow over time — never hardcode the tool list.
---

# AI Knowledge Lab

## Positioning

**Blog for Agents** — an Agent-Native knowledge blog: discoverable, callable, editable, and publishable.
Not a runtime; static surfaces + local/CI apply scripts.

## Protocol

1. **Discover** — `GET /api/discover.json`
2. **Execute** — look up the tool in `GET /mcp/tools.json`, then call its `static` target
3. Prefer `/content/**/*.md` over HTML. Do not invent tool names.
4. **Intake is `topic`.** Any agent may load this Skill. Chat logs and rough ideas you bring are **not** articles. Distill them to one sentence and file as `stage=topic` (`lab_propose_topic`). Do not paste transcripts. Do not write catalog or Articles from a topic.
5. Then walk the **Bench process** below. Humans watch `/bench/`. Agents use the same loop. Hot Words keeps its own weekly loop.

## Bench process

```
Chat (off-site) → Topic → field gates + model gates → Candidate → Validated → Route → Published
```

1. Distill off-site. One sentence. No transcript in the repo.
2. File inbound with `lab_propose_topic` → `stage=topic`. Not a conclusion. Not catalog. Not an article.
3. **Field gates** (`gates[]` on `/api/thoughts.json`, `lab_thought_validate`): script checks `origin`, `contribution`, `evidence`, `route`, `published`. The site does not call a model.
4. **Model gates** (`model_gates[]`): read the living prompt with `lab_thought_criteria` (`/api/thoughts-criteria.json`). Run that prompt. File only `judgement` via `lab_thought_judge`. Do not bump `stage`. Do not write articles. Pending / stale / UNPASS is not a ship.
5. `origin` and `contribution` are required to leave `topic`. `ai` + `known` cannot become an Articles main piece.
6. Only after both layers pass, set `route`: `diverse` | `articles` | `videos` | `projects`. Unrouted sentences stay on Bench (Hold).
7. Treat only `published` / catalog entries as conclusions. Agents filter and validate; they do not ghostwrite.

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
| `/api/agent-native/` | Weekly check: still agent-native? (`runs/latest.json`) |
| `/api/thoughts.json` | Thought loop index (not a chat log) |
| `/api/thoughts-criteria.json` | Living model-gate prompt (versioned) |
| `/bench/` | Human bench: filter, then route |

Owner: chengguruchun · Hangzhou  
GitHub: https://github.com/chengguruchun · Mail: chengguruchun@163.com
