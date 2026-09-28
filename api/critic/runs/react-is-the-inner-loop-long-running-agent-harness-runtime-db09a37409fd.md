## 🤖 Critic Lab Report

Article: `articles/react-is-the-inner-loop-long-running-agent-harness-runtime.html`
Commit: `db09a37409fdfb0db392b8121ba80e573b3eb1c1`
Model: `deepseek-chat`
Status: **needs_review**

The article proposes a useful three-layer distinction (Action Loop / Task Loop / System Loop) mapping to ReAct / Harness / Runtime, and argues ReAct remains the inner loop of long-running agents while Harness and Runtime absorb higher-order concerns. The framing is coherent but rests on several unsupported jumps: ReAct is described as a pure 'action loop', while the Harness/Runtime boundary and the runtime-vs-risk-vs-verification boundary are not rigorously separated. The reference list contains many 2026-dated citations that cannot be verified without external lookup, and the article does not address tool/parameter explosion within Harness, nor the possibility that ReAct-style prompting is subsumed into the model rather than remaining a distinct architectural layer.

## 1. Logic

- **HIGH** — ReAct is defined narrowly as an 'Action Loop' answering only 'what should I do next?'
  - Issue: ReAct as originally formulated includes an internal reasoning trace that acts as a lightweight task-level controller (it supports multi-step reasoning, self-correction, and subgoal chaining). Demoting it to a pure action selector understates what the pattern already does.
  - Why it matters: If ReAct already handles some task-level planning via its thought tokens, then the Harness/Task Loop is a partial re-engineering of what ReAct already does, not a clean new layer. This weakens the claim that long-running agents need a categorically new layer.
  - Test / fix: Clarify which specific ReAct limitations (e.g., context persistence, state externalization, cross-session handoff) Harness addresses that ReAct's internal thought trace cannot. Show at least one concrete failure mode where ReAct's task-level reasoning is insufficient but is not merely a context-length problem.

- **HIGH** — Harness and Runtime are presented as clearly separable layers.
  - Issue: The boundary is asserted by enumeration, not by a principled criterion: Harness = prompts+tools+skills+loop+task logic; Runtime = durable execution+state+memory+scheduling+retry+HITL+observability+sandbox+tenancy. In practice, many systems (e.g., agent frameworks with built-in state stores) blur the two, and memory/state appear on both sides.
  - Why it matters: A boundary that shifts with implementation makes the three-layer model descriptive rather than analytical, weakening its explanatory power and its use as a design constraint.
  - Test / fix: Define a single discriminating criterion (e.g., 'concerns about correctness of task progress' vs. 'concerns about correctness of execution lifecycle'), then test whether the listed capabilities cleanly partition. Note where they overlap (state, memory, retry).

- **MEDIUM** — Agent Performance ≈ Model × Harness × Runtime × Environment × Feedback.
  - Issue: This multiplicative formulation is a rhetorical device, not an empirically grounded model. It implies non-substitutability and potential zero collapse, none of which is demonstrated. It also implies each factor is largely independent, which is questionable (Harness design and model capability interact).
  - Why it matters: Presenting an intuitive product as an equation can overstate rigor and may mislead readers into treating it as a causal decomposition.
  - Test / fix: Either present it clearly as a heuristic mental model with caveats, or replace it with a qualitative statement that performance depends jointly on model, scaffolding, runtime, and environment, with examples of interaction effects.

- **MEDIUM** — 'ReAct 没有过时，它只是被放进了更大的系统' followed by the layered diagram.
  - Issue: The placement of ReAct as a subcomponent of Harness, which is itself a subcomponent of Runtime, is asserted rather than derived. The diagram shows Harness and Runtime as siblings under Long-Running Agent, but the text sometimes implies Harness is contained within Runtime.
  - Why it matters: A layered model with inconsistent containment relationships is not usable as a design vocabulary.
  - Test / fix: Pick one containment topology and apply it consistently across sections 3, 5, 9, and 12.

- **MEDIUM** — '这是两个不同的问题' regarding Context Window vs. Task Horizon.
  - Issue: The distinction is directionally correct but does not explain the interaction: larger context can reduce the frequency of context resets, which directly affects how much Harness-level state management is needed. Treating them as strictly orthogonal understates the coupling.
  - Why it matters: If context window growth materially reduces state-management burden, then the relative weight of Harness vs. Runtime shifts over time, which is relevant to the article's own claim about scaffolding being removable.
  - Test / fix: Add a paragraph on the interaction: how does increasing context length change the required frequency of checkpoint/reset and the shape of Harness state artifacts?

- **LOW** — Verification / evaluator is placed within Harness.
  - Issue: Verification is downstream of the runtime and environment (it needs observed outcomes, not just model outputs). Assigning it exclusively to Harness conflates the source of verification signal (runtime/environment) with the component that consumes it.
  - Why it matters: Designers may implement verification artifacts only at the harness layer and miss that durable, trustworthy evidence must be produced and stored by the runtime.
  - Test / fix: Distinguish 'verification logic' (Harness) from 'verification evidence storage and retrieval' (Runtime). Give one concrete example where separating these matters.

## 2. Counterexamples

- **HIGH** — Thesis: Long-running agents require an explicit Harness/Task Loop distinct from ReAct.
  - Counterexample: Single-model agents that use very long context windows with native tool-use and no explicit task harness (e.g., research prototypes where the model itself replans within a 1M-token context) can complete multi-hour tasks without a separately engineered Harness layer. The task loop is implicit in the model.
  - Boundary: The Harness layer becomes architecturally necessary primarily when the task exceeds a single context window, requires human approval, or requires cross-process survival. Below those thresholds, Harness may collapse into prompt structure.

- **HIGH** — Thesis: Harness and Runtime are separable layers with distinct responsibilities.
  - Counterexample: A workflow engine (e.g., Temporal, Argo Workflows) provides durable execution, retry, and checkpointing without knowing anything about LLM prompts or tool selection. If an agent is expressed as activities in such an engine, the Runtime provides lifecycle, but the 'Harness' concept has no independent existence — it is just activity code.
  - Boundary: The two-layer distinction is most useful when there is a dedicated agent framework; it may be artificial when agents are expressed in general-purpose durable execution engines.

- **MEDIUM** — Thesis: Durable execution with checkpoint/resume is the key capability of long-running agents.
  - Counterexample: Some long-running tasks are better served by idempotent replay from the start (each attempt recomputes from inputs) than by checkpoint/resume. For tasks with cheap deterministic recomputation, checkpointing adds storage and versioning complexity without clear benefit.
  - Boundary: Durable execution is valuable when state is expensive to reconstruct (long tool calls, external side effects, human input). For cheap-to-recompute tasks, replay-from-start may be simpler and more robust.

- **MEDIUM** — Thesis: ReAct remains a stable inner loop across agent generations.
  - Counterexample: Modern reasoning models often internalize the Thought→Action→Observation pattern into a single generation with tool-use tokens, without exposing an explicit ReAct scaffold. In such systems, there is no distinct 'ReAct layer' — the pattern has been absorbed into the model.
  - Boundary: The 'ReAct as inner loop' framing is most accurate when the agent framework explicitly implements the loop; it may misdescribe systems built on models with native tool-use and internal reasoning.

- **MEDIUM** — Thesis: Harness should handle tool/skill selection, context organization, and verification.
  - Counterexample: A Harness that consolidates many tools into few general tools (to reduce selection errors) can push complexity into parameter space, causing parameter explosion and schema-versioning problems. This is a known tension in skill design that the article does not address.
  - Boundary: Tool consolidation helps when selection errors dominate; it hurts when parameter validation and schema evolution dominate. The boundary depends on tool call frequency, parameter diversity, and validation cost.

## 3. Novelty

- **common_combination** — ReAct is the innermost Action Loop; Harness is the Task Loop; Runtime is the System Loop.
  - Basis: The individual concepts (ReAct, harness, runtime concerns like durable execution) are established separately. The three-layer mapping is a useful pedagogical framing, but similar layerings appear in agent framework documentation and blog posts. Preliminary assessment without external browsing.

- **common_combination** — Agent Performance is best understood as Model × Harness × Runtime × Environment × Feedback.
  - Basis: 'Model times scaffolding' multiplicative framings have appeared in multiple agent-engineering discussions. The specific set of factors is plausible but the multiplicative form is not novel and is not empirically validated here.

- **established** — Long-running agents are best analogized to Process / Actor / Kubernetes Controller.
  - Basis: The Actor model and K8s controller analogies for agents are widely discussed; the article's knowledge lab contains a related piece ('从 Actor Model 到 Cognitive Actor'). Not novel.

- **established** — Context Window ≠ Task Horizon.
  - Basis: Common observation in long-context and agent literature; the distinction is frequently made. Not novel.

- **established** — Verification should record target-outcome validity, not just tool-call success.
  - Basis: This is a standard point in evaluation literature (proxy metric vs. real outcome); the article's own lab contains a related piece.

## 4. Facts

- **HIGH** — Anthropic, Effective harnesses for long-running agents, 2025-11-26.
  - Why verify: Dated 2025-11-26. Title, date, and content must be verified against the actual publication; some of the described artifact types (initializer, structured feature list, progress artifacts) may not match the source verbatim.
  - Preferred source: `primary`

- **HIGH** — Anthropic, Harness design for long-running application development, 2026-03-24.
  - Why verify: Dated 2026-03-24 and forward-referenced; date, existence, and the planner/generator/evaluator claim must be verified directly.
  - Preferred source: `primary`

- **HIGH** — Anthropic, Scaling Managed Agents: Decoupling the brain from the hands, 2026-04-08.
  - Why verify: Same as above; verify the source exists and supports the claims attributed to it (context compaction limits, harness assumptions aging out).
  - Preferred source: `primary`

- **HIGH** — LangChain, The Runtime Behind Production Deep Agents, 2026-04-20, and its list of Runtime capabilities (durable execution, memory, HITL, multi-tenancy, observability, sandbox, scheduled jobs).
  - Why verify: Date and content list must be checked against the actual LangChain publication; the article uses this as a load-bearing citation for the Harness/Runtime split.
  - Preferred source: `primary`

- **MEDIUM** — References contain literal citation artifacts 'citeturn0search1' etc.
  - Why verify: These look like unresolved citation markers, not reader-facing citations. They should be replaced with real links or removed before publication.
  - Preferred source: `official`

- **MEDIUM** — Publication date listed as 2026-09-28 while citing sources dated up to 2026-04-20.
  - Why verify: Confirm the dates are intentionally in the future and internally consistent; otherwise adjust to the actual writing date.
  - Preferred source: `official`

## 5. Missing Points

- **HIGH** — Tool/skill design tradeoffs inside Harness: consolidation vs. parameter explosion.
  - Why it matters: If Harness decides which tools and skills to expose, it must confront the same tradeoff agent designers already face: fewer general tools reduce selection error but push complexity into parameter schemas, versioning, and validation. Without this, the Harness layer looks like a clean abstraction when it is actually where a known hard problem lives.

- **HIGH** — Separation of runtime boundary from risk/verification boundary.
  - Why it matters: Durable execution, sandboxing, permission checks, and verification evidence are often conflated under 'Runtime', but they answer different questions (liveness, isolation, authorization, correctness). Conflating them makes it hard to reason about which failures are infrastructure failures and which are policy failures.

- **MEDIUM** — Interaction between context-window growth and Harness/Runtime requirements.
  - Why it matters: As context windows grow, the required frequency of checkpoint/reset and the shape of Harness state artifacts change. Discussing them as orthogonal leaves the reader without guidance on when the Harness layer can be simplified.

- **MEDIUM** — Idempotency and side-effect semantics for tools invoked across sessions.
  - Why it matters: Resume after process death can re-execute a tool with external side effects (payments, deployments). This is a first-class Runtime concern that the article's decision tree does not surface.

- **MEDIUM** — Cost, latency, and observability tradeoffs of durable execution.
  - Why it matters: Checkpointing every step is not free; agents may checkpoint only at coarse-grained safe points. The article presents checkpoint/resume as a primitive without discussing its granularity, latency, or storage design.

- **MEDIUM** — Evaluation of whether Harness scaffolding is still needed as models improve.
  - Why it matters: The article asserts a trend of scaffolding being removable, then pivots to 'Harness needs continuous validation.' It does not give a method for deciding which scaffolding is removable — a gap that makes the claim operational only in the abstract.

- **LOW** — Security/permission model for tools in a multi-tenant runtime.
  - Why it matters: Multi-tenancy is listed as a Runtime concern, but its implications for tool authorization, sandboxing, and data isolation are not developed; these materially affect feasibility.

## 6. Recommended Changes

- Replace unresolved citation artifacts 'cite turn0searchN' with real links, and verify each referenced source's exact title, date, and claims before publication.
- Clarify the Harness vs. Runtime boundary using a single discriminating criterion, and state where 'state' and 'memory' live in each.
- Reframe 'Agent Performance ≈ Model × Harness × Runtime × Environment × Feedback' explicitly as a heuristic, not a model, with at least one interaction example.
- Add a subsection on tool/skill design within Harness, explicitly addressing tool consolidation vs. parameter explosion and schema/versioning costs.
- Separate runtime concerns (liveness, durability) from risk/verification concerns (authorization, sandboxing, correctness evidence) even if both sit 'below' Harness.
- Discuss the interaction between larger context windows and the required frequency/shape of context reset and checkpoints.
- Add a boundary condition: when idempotent replay is preferable to checkpoint/resume, and note side-effect semantics for resumed tool calls.
- Align containment topology across the three diagrams (sections 3, 5, 9, 12) — pick one and apply consistently.
- Soften or scaffold the 'ReAct is only an action loop' framing by acknowledging ReAct's internal thought trace already does some task-level reasoning.
- Add a short method for deciding which Harness scaffolding can be removed as models improve, rather than only asserting the trend.
- Label the three-loop model as a hypothesis or mental model, not a derived architecture, and invite falsification.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
