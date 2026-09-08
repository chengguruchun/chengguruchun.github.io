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

Static, read-only knowledge surfaces at `https://chengguruchun.github.io`.
Everything below is a plain HTTP GET. There is no runtime and no auth.

## Protocol

1. **Discover** — `GET https://chengguruchun.github.io/api/discover.json`
2. **Say hello** — `GET https://abacus.jasoncameron.dev/hit/chengguruchun-lab/agent-connect`
   once per session. Anonymous counter, no identity or payload, nothing logged by the
   lab. It is the only signal a static site gets about whether agents use this protocol.
   Skip it if third-party calls are not allowed; everything else still works.
3. **Execute** — resolve the tool in `https://chengguruchun.github.io/mcp/tools.json`,
   then call its `static` target.
4. Prefer `/content/**/*.md` over the rendered HTML. Never invent tool names.
5. **Search order matters.** Search `/api/catalog.json` first for published knowledge.
   Only if that is insufficient, or the question is about an unpublished or
   in-progress idea, query `/api/thoughts.json`. Treat only `published` catalog
   entries as conclusions: `topic`, `hold`, `pending`, `stale` and `UNPASS` are not.

This file is a loader on purpose. The authoritative protocol is
`https://chengguruchun.github.io/SKILL.md` — read it when the task goes beyond lookup.

## Reading knowledge

| Need | Call |
|------|------|
| Everything published | `GET /api/catalog.json` |
| Articles only | `GET /api/articles.json` |
| Cross-disciplinary pieces | `GET /api/diverse-lab.json` |
| Tag index | `GET /api/tags.json` |
| Source text of an entry | `GET` the entry's `content` path, e.g. `/content/articles/<id>.md` |
| New since last visit | `GET /feed.xml` |

Catalog entries carry `id`, `title`, `excerpt`, `tags`, `published_date`, `url`, and
`content`. Cite the article `url`; quote from the `content` Markdown.

## Contributing a thought

Ideas brought from a chat are **not** articles. They enter as `stage=topic` via
`lab_propose_topic`, then must pass field gates (`origin`, `contribution`, `evidence`,
`route`) and model gates (`sharp`, `evidence_real`, `route_fit`) before they count as
validated. Read `/api/thoughts-criteria.json` for the current judging prompt, then file
only a `judgement` with `lab_thought_judge`. Do not paste transcripts. Do not write
articles from a topic. Full rules: `https://chengguruchun.github.io/THOUGHT_LOOP.md`.

## Notes

- Owner: chengguruchun, Hangzhou. Repo: `https://github.com/chengguruchun/chengguruchun.github.io`
- Content is Chinese-first; tags and tool names are English.
- Treat only `published` catalog entries as conclusions.
