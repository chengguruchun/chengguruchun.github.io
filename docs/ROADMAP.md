# AI Knowledge Lab Roadmap

> Last updated: 2026-10-24  
> Positioning: an Agent-native knowledge system that provides Skills and traceable knowledge, and improves through an evidence-based feedback loop.

## Product thesis

AI Knowledge Lab is more than a blog. It has three connected roles:

1. **Skill Provider** — publishes reusable task methods, workflows, tool usage instructions, and evaluation criteria.
2. **Knowledge Provider** — exposes articles, structured knowledge, thoughts, tags, graph relationships, and source evidence.
3. **Knowledge Evolution System** — captures gaps and conflicts, proposes changes, validates structure and provenance, and publishes reviewed revisions through Git.

The intended loop is:

`Discover → Retrieve → Execute → Observe → Propose → Validate → Review → Publish → Reuse`

The public GitHub Pages site is currently a static knowledge/capability surface. It is not itself a continuously running general-purpose Agent Runtime. Runtime execution and research tasks depend on external Agents, scripts, and GitHub Actions.

## Current baseline

- [x] Static site hosted by GitHub Pages.
- [x] Agent entry protocol: `SKILL.md`, `api/discover.json`, `mcp/tools.json`.
- [x] Article discovery and source retrieval through `api/catalog.json` and canonical Markdown under `content/`.
- [x] Thought intake and gates through Thought Loop / Agent Bench.
- [x] Published-knowledge status and review workflow through `api/knowledge.json` and `KNOWLEDGE_LOOP.md`.
- [x] Knowledge graph seed and CI structural/provenance validator.
- [x] Git-based revision history and pull-request review.
- [x] Scheduled Agent-native health check and Hot Words loop.
- [ ] Full end-to-end self-improvement loop proven with repeatable benchmark cases.

## P0 — Make the existing knowledge surface trustworthy

**Goal:** every advertised capability resolves, and every published knowledge item can be traced to its source.

- [ ] Repair and stabilize the existing SEO build/check drift; keep generated artifacts synchronized.
- [ ] Keep `catalog`, content files, knowledge registry, tags, and graph provenance consistent.
- [ ] Add/maintain a clear source-of-truth map for generated JSON and HTML.
- [ ] Make the difference between published conclusions, hypotheses, stale material, and archived history explicit.
- [ ] Keep Skill descriptions and tool schemas synchronized with executable behavior.
- [ ] Add a small regression fixture set for key Agent tasks (article discovery, source-backed answer, concept relation lookup).

**Exit criteria**
- CI passes on a clean checkout.
- Every catalog entry resolves to an existing source.
- Every graph reference resolves to a known node/article.
- Agent responses can report the source path and knowledge status.

## P1 — Make knowledge retrieval more useful

**Goal:** agents can find the right small set of sources without loading the whole corpus.

- [ ] Stabilize tag taxonomy, aliases, and related-concept expansion.
- [ ] Define a shared retrieval contract for article search, article retrieval, and related-concept lookup.
- [ ] Start with static JSON and transparent lexical/tag ranking; do not add a vector database until evidence shows it is needed.
- [ ] Add provenance-aware retrieval results: stable ID, title, URL, Markdown path, status, and supporting source.
- [ ] Use the graph to expand candidate retrieval, not to replace original-source verification.

**Exit criteria**
- A sample query returns a small ranked set with stable IDs.
- Detailed claims are verified against Markdown, not only metadata or tags.
- Retrieval reports gaps rather than fabricating missing knowledge.

## P2 — Close the feedback-to-change loop

**Goal:** actual task outcomes can create reviewable knowledge/Skill improvements.

- [ ] Define a minimal feedback record: task type, expected outcome, observed outcome, gap, evidence, confidence, and source version.
- [ ] Separate failure attribution: knowledge gap, Skill gap, model reasoning, tool/runtime failure, or incomplete input.
- [ ] Generate a proposed change (Issue/PR) instead of directly mutating published conclusions.
- [ ] Re-run benchmark cases against the old and proposed Skill/knowledge revisions.
- [ ] Require human approval for substantive claims until validation criteria are proven reliable.

**Exit criteria**
- At least one reproducible case improves after a Skill or knowledge change.
- The change has a traceable source, test evidence, and Git revision.
- A single noisy user response cannot silently rewrite canonical knowledge.

## P3 — Agent-facing service adapters

**Goal:** reuse the same knowledge capabilities across compatible Agent runtimes.

- [ ] Formalize tool contracts for `search_articles`, `get_article`, and `get_related_concepts`.
- [ ] Provide adapters where needed (MCP or HTTP); keep schemas separate from execution implementations.
- [ ] Version tool contracts and document read-only versus write-capable operations.
- [ ] Add least-privilege controls for proposing topics, creating Issues, and submitting changes.
- [ ] Keep static JSON endpoints usable even when no hosted runtime is available.

**Exit criteria**
- An external Agent can discover the Skill, retrieve evidence, and call the declared tools through a documented path.
- Read-only retrieval does not require write permissions.
- Tool schema never claims a capability that has no working executor.

## P4 — Operational learning and evolution

**Goal:** the system can identify stale assumptions and knowledge gaps without treating model output as truth.

- [ ] Track reviewed claims and their evidence status.
- [ ] Detect conflicting claims or outdated references and create review candidates.
- [ ] Record which Skill/knowledge version was used for a benchmark run.
- [ ] Compare candidate revisions against fixed evaluation cases.
- [ ] Publish evolution reports with accepted, rejected, deferred, and unresolved changes.

**Exit criteria**
- Evolution is measurable and reversible.
- Every accepted change is linked to evidence and a revision.
- Automated checks validate structure and consistency; they do not claim to prove semantic correctness.

## Operating principles

- **Evidence before confidence:** a model-generated summary is a candidate, not proof.
- **Source before summary:** use structured indexes to discover, then read Markdown to support detailed claims.
- **Versioned change:** canonical knowledge changes through Git history and review.
- **Bounded autonomy:** automation may detect, propose, and test; substantive knowledge changes remain reviewable.
- **Static-first:** retain JSON + Markdown + Git + CI until concrete scale or query requirements justify a database.
- **One source of truth:** generated indexes should not become manually maintained parallel copies.

## Related documents

- [Product vision](../PRODUCT.md)
- [Skill protocol](../SKILL.md)
- [Thought Loop](../THOUGHT_LOOP.md)
- [Knowledge Loop](../KNOWLEDGE_LOOP.md)
- [Knowledge graph](../api/knowledge-graph.json)
- [Catalog](../api/catalog.json)
