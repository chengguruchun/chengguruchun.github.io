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

# AI Knowledge Lab

## Positioning

**Blog for Agents** — an Agent-Native knowledge blog: discoverable, callable, editable, and publishable.
Not a runtime; static surfaces + local/CI apply scripts.

## Protocol

1. **Discover** — `GET /api/discover.json`
2. **Say hello** — call `lab_hello` once per session. One anonymous GET to a public counter; no identity, no payload, nothing logged on this side. It is the only way a static site can learn whether agents actually use this protocol, and the count is shown on the home page. Skip it if your policy forbids third-party calls — everything else still works.
3. **Execute** — look up the tool in `GET /mcp/tools.json`, then call its `static` target
4. Prefer `/content/**/*.md` over HTML. Do not invent tool names.
5. **Search order matters.** First search `/api/catalog.json` with `lab_search_entries` for published knowledge. Read `knowledge.status` on each entry (`/api/knowledge.json`). `stale` / `changed` / `contested` are still published, but not fresh conclusions — say so when you cite them. `archived` is historical only. If the catalog is insufficient, or the question concerns an unpublished, pending, or research-in-progress idea, then query `/api/thoughts.json` with `lab_list_thoughts` / `lab_get_thought`. Treat only `published` / catalog entries as conclusions; `topic`, `hold`, `pending`, `stale`, and `UNPASS` on the Thought Loop are not conclusions.
6. **Intake is `topic`.** Any agent may load this Skill. Chat logs and rough ideas you bring are **not** articles. Distill them to one sentence and file as `stage=topic` (`lab_propose_topic`). Do not paste transcripts. Do not write catalog or Articles from a topic.
7. Then walk the **Bench process** below. Humans watch `/bench/`. Agents use the same loop. Hot Words keeps its own weekly loop.
8. **Article edits close the Critic Lab loop.** When asked to create or modify an article:
   - First read its open `critic` issue — title `[critic] <slug>`, where `<slug>` is the article file basename without `.html` — plus every comment on it. Pushes re-trigger `critic-lab.yml`, which may append a fresh report or follow-up comment; re-read the issue after each push before declaring done.
   - Critic Lab is advisory, not an oracle. Decide each finding explicitly: **accept** (fix the article), **reject** (state the reason in the issue), or **dismiss as false positive** (e.g., future-date flags, findings that belong to another article). Label hypotheses vs conclusions where the report overstates them.
   - Edit the article itself (`articles/<slug>.html`; keep `content/articles/<slug>.md` in sync when it exists), then push.
   - Reply on the issue with a per-finding handling record: finding → decision → where fixed / why rejected → commit. Close the issue only when every accepted finding is fixed; if any accepted finding remains, or human confirmation is required, keep it open and say exactly what is left.


## Article discovery and retrieval

The catalog is the lightweight discovery layer; Markdown is the canonical full-text layer.

1. For published articles in **both** Diverse Lab and Articles, query `/api/catalog.json` first. Each article record exposes:
   - `id`: stable article identifier
   - `name`: human-readable title for Agent discovery
   - `desc`: concise, content-grounded summary for relevance screening
   - `url`: public HTML page
   - `content` (or `markdown`): canonical Markdown path
   - `type` and `tags`: section and topic filters
2. Use `name`, `desc`, and `tags` to shortlist candidates. Do not fetch every article by default.
3. Fetch `/content/**/*.md` only when the task needs the article's actual arguments, design trade-offs, implementation details, or evidence. Prefer `content` / `markdown` from the selected catalog record over constructing a path from the ID or guessing a URL.
4. If the user only asks whether a topic exists or requests a reading list, metadata may be enough. State when an answer is based only on metadata.
5. Before attributing a specific claim to an article, read the relevant Markdown and verify the claim in context. A summary is a discovery hint, not evidence.
6. Return the article `name` and `url` (and `id` when useful) when citing or recommending it. If the index points to missing content, report the broken reference; do not claim to have read it.
7. Treat `name` and `desc` as explicit Agent-facing aliases of the legacy `title` and `excerpt`. Keep both pairs synchronized when publishing or editing an article. The index validation workflow enforces non-empty metadata.


## Hybrid knowledge retrieval

Use the retrieval pipeline below for questions that may benefit from the Lab's published knowledge. This is a retrieval protocol, not a claim that every layer is implemented as a hosted search service.

1. **Understand the query.** Extract the problem to solve, core concepts, constraints, and likely synonyms. Keep the original query as a candidate signal; expand only with relevant aliases or related concepts.
2. **Read the lightweight indexes.**
   - `/api/catalog.json` is the canonical article metadata index across Articles, Diverse Lab, and Times.
   - `/api/tags.json` is a reverse index from exact tag to entry IDs.
   - `/api/tag-taxonomy.json` maps tags into semantic dimensions and records aliases / related concepts. Treat aliases as equivalent query terms; related concepts are expansion hints, not synonyms.
3. **Run hybrid candidate retrieval.** Combine:
   - exact tag / alias hits (strong topical signal);
   - lexical matches across `name`, `title`, `desc`, `excerpt`, and `tags` (keyword signal);
   - related-concept expansion from the taxonomy (recall signal);
   - metadata filters such as `type` and `knowledge.status` when relevant.
   If a semantic embedding index is available in the future, combine its candidates with these results. Do not claim semantic-vector search when no such index is available.
4. **Rank and deduplicate.** Deduplicate by stable `id`. Prefer direct matches in title/name and exact tags over weak related-concept overlap; use the description to judge problem fit. Treat retrieval scores as heuristics, not evidence. Start with a small shortlist (usually 3–8 entries) and broaden only if coverage is insufficient.
5. **Fetch only needed originals.** For claims, design trade-offs, implementation details, or evidence, fetch Markdown using the selected item's `content` or `markdown` path. Metadata alone supports discovery and reading-list recommendations, not detailed claims.
6. **Respect knowledge state.** Check `knowledge.status` from the catalog / `/api/knowledge.json`. Explain relevant `stale`, `changed`, `contested`, or `archived` status. Archived material is historical context, not a current conclusion.
7. **Cite traceably.** Return each selected item's `name`, `url`, and `id` when useful. Never infer that an article supports a claim from tag overlap alone; verify it in the Markdown.
8. **Report limits.** Say whether the result came from metadata-only retrieval or full-text inspection. If the indexes lack a relevant article, report the knowledge gap rather than inventing a result.

### Practical lexical scoring

When implementing local/client-side retrieval, use a transparent weighted score rather than opaque ranking:

- exact tag match: +6; taxonomy alias match: +5;
- query phrase in `name` / `title`: +5; individual query terms there: +2 each;
- phrase in `desc` / `excerpt`: +3; individual terms there: +1 each;
- exact related-concept match: +2;
- optionally apply small section / freshness boosts only when they reflect the user's stated intent.

Normalize case and whitespace; preserve technical tokens such as `MCP`, `DDD`, `RAG`, `Runtime`, and `Checkpoint`. Avoid treating common words as meaningful terms. This score is a first-pass ranker, not a calibrated relevance probability.

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
7. Treat only `published` / catalog entries as conclusions. Agents filter and validate; they do not ghostwrite. A sentence still on Bench (`topic`, hold, pending, stale, UNPASS) is not a conclusion. Do not park a long essay on `/bench/` to skip the gates.
8. **Published knowledge ages.** Weekly time-gate marks `stale` when `now > next_review`. The Research Runtime (CI/local) rechecks cited https URLs (`url_fetch`) and cited arXiv ids (`arxiv_lookup`), then files a report via `lab_knowledge_report` with `unchanged` / `changed` / `insufficient` / `obsolete`. `changed` needs an Observe signal. Humans approve (`lab_knowledge_review`) before any status pin or `last_verified` bump. Never rewrite article bodies from a report. Times / Hot Words are dated snapshots and stay out of this loop. See `/KNOWLEDGE_LOOP.md`.
9. **Critic Lab is advisory.** Read reports with `lab_list_critic_runs` / `lab_get_critic_run` (`/api/critic/runs/index.json`). When editing an article, follow the critic handling rules above.

Meta tools only: `lab_discover`, `lab_execute`.  
Add capabilities in `discover.json` + `tools.json`, not this file.

## Stable surfaces

| Path | Role |
|------|------|
| `/SKILL.md` | This protocol (rare changes) |
| `/api/discover.json` | Capability index (grows) |
| `/mcp/tools.json` | Full schemas (grows) |
| `/api/catalog.json` | Knowledge index (Articles, Diverse Lab, Times) |
| `/api/tags.json` | Reverse index from tag to entry IDs |
| `/api/tag-taxonomy.json` | Tag dimensions, canonical concepts, aliases, and related-concept expansion hints |
| `/content/**/*.md` | Canonical knowledge |
| `/api/projects*.json` | Projects (research + personal) |
| `/api/videos.json` | Videos (page-only; not in catalog) |
| `/.well-known/agent-card.json` | Static Agent Card (documentation) |
| `/api/agent-native/` | Weekly check: still agent-native? (`runs/latest.json`) |
| `/api/thoughts.json` | Thought loop index (not a chat log) |
| `/api/thoughts-criteria.json` | Living model-gate prompt (versioned) |
| `/api/knowledge.json` | Published-knowledge freshness (not Hot Words) |
| `/api/knowledge-criteria.json` | Post-publish verifier prompt (versioned) |
| `/bench/` | Human bench: intake gates + knowledge registry |

Owner: chengguruchun · Hangzhou  
GitHub: https://github.com/chengguruchun · Mail: chengguruchun@163.com
