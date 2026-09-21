## 🤖 Critic Lab Report

Article: `articles/from-llm-to-agent-runtime.html`
Commit: `d88cf895990b7da8799e2f39c1f758e5da275cd4`
Model: `deepseek-chat`
Status: **needs_review**

The revision improves calibration by labeling several claims as hypotheses and adding boundaries for Verification and for the functional-stack framing. However, the central category distinction between Inference Runtime and Agent Runtime remains a made-up boundary without an operational test, the division of responsibilities (Context/Scheduling/Tool Routing/Sandbox/Checkpoint/Verification/Safety Gate/Observability) is a useful hypothesis rather than a derived framework, and the claim that Runtime should own verification/state/risk is still under-specified. The review finds no fatal flaw, but several claims should be reframed, tested, or bounded before the article is treated as more than exploratory thinking.

## 1. Logic

- **HIGH** — Inference Runtime 负责“这一层推理如何更快、更便宜”；Agent Runtime 负责“下一步是否应该发生、在哪里执行、结果是否被验证”。KV Cache 属于前者，Sandbox 属于后者。
  - Issue: The boundary is asserted rather than operationally defined. In practice, an inference server may handle tool-call scheduling, batching across turns, and cached state; an agent runtime may also optimize KV-cache reuse or prefill scheduling. The separation is a conceptual convenience, not an observed architectural fact.
  - Why it matters: If readers take this as a real architectural boundary, they may build separate systems where shared infrastructure is required, or miss performance interactions between agent planning and inference serving.
  - Test / fix: Define the boundary by a decision rule: e.g., a component belongs to Inference Runtime if it can be optimized without changing the external action sequence; it belongs to Agent Runtime if it changes which actions are attempted or whether they are allowed. Test with a concrete system: does the same batching/caching mechanism serve both loops, or does one loop invalidate the other's assumptions?

- **MEDIUM** — 真正的 Runtime 与 Workflow Engine 的区别，不在于“职责更多”，而在于它把验证、状态与风险当成一等公民。
  - Issue: This is circular unless 'first-class citizen' is defined. Workflow engines already handle state, retries, and sometimes validation; the difference may be degree and model-driven control flow, not kind.
  - Why it matters: Without a definition, the distinction is unfalsifiable and can be used to relabel any workflow engine as an agent runtime.
  - Test / fix: Provide a decision procedure: a system is an Agent Runtime if at least one of its next actions is selected non-deterministically from model output and verified against a runtime-owned outcome contract. Otherwise it is a Workflow Engine.

- **MEDIUM** — 验证退化为 schema 校验，甚至不需要 Checkpoint。
  - Issue: For a stateless read-only research agent, checkpointing is indeed unnecessary. But 'schema validation' is not equivalent to verification of outcome; a malicious or malformed read can still pass schema while returning wrong data.
  - Why it matters: For read-only agents, correctness often depends on source trust, freshness, and semantics, not just format. Over-reducing verification may create false confidence.
  - Test / fix: Add a row to the boundary table: when is schema validation sufficient? For example, when the task is purely formatting/transforming a trusted source with no semantic ambiguity. When source trust is low, verification must check provenance or content, not just schema.

- **MEDIUM** — Runtime 的约束是补充而不是替代模型层的防护——两者共同构成安全边界。
  - Issue: This is a reasonable claim, but the article does not explain the interaction. If runtime constraints are too weak, model-level refusals may be the only defense; if runtime constraints are strong, model-level refusals may be unnecessary. The '共同构成' phrasing hides a trade-off.
  - Why it matters: Practitioners may over-invest in one layer and under-invest in the other. The claim is true but not actionable without a model of failure modes and cost.
  - Test / fix: Add a failure-mode matrix: for each error class (prompt injection, tool misuse, hallucinated API, unsafe action), identify which layer can catch it, which layer can prevent it, and what the cost of false positives/negatives is.

## 2. Counterexamples

- **MEDIUM** — Thesis: Sandbox is mainly necessary for Code Agents; a read-only research agent can have a very thin runtime without a sandbox.
  - Counterexample: A read-only agent that queries internal APIs can still leak sensitive data through side channels, trigger rate limits, or be used for prompt injection that causes it to exfiltrate data. Sandboxing can be necessary even for read-only agents to enforce egress and data isolation.
  - Boundary: Sandbox necessity depends on whether actions can cause side effects, including information disclosure, not only on whether they modify code.

- **MEDIUM** — Thesis: When results can be deterministically verified (e.g., checksum query, schema validation), execution success is task success, so additional business verification is waste.
  - Counterexample: A checksummed query returns data whose provenance is untrusted or whose schema is valid but semantically wrong (e.g., stale cache, wrong tenant). Execution success does not entail task success if the source is not trustworthy.
  - Boundary: Deterministic verification is sufficient only when both format and provenance/semantics are trusted. Otherwise, verification must extend to source and context.

- **LOW** — Thesis: Each layer in the functional stack can exist independently or be omitted; stacking depends on the problem you solve.
  - Counterexample: In practice, the layers interact: a tool contract may require sandbox capabilities; a sandbox may require checkpointing; observability of one layer may be insufficient without the others. Independent existence is possible in theory, but engineering cost and coupling may make certain combinations near-mandatory.
  - Boundary: Independence is a property of the concept, not of an implementation. The article should distinguish conceptual separability from practical coupling.

## 3. Novelty

- **common_combination** — The article distinguishes Inference Runtime from Agent Runtime and assigns KV Cache to the former, Sandbox to the latter.
  - Basis: Local overlap with other articles (agent-runtime-cognitive-actor, k8s-to-agent-control-plane, spring-dubbo-deepseek-harness-runtime) suggests this lab has been developing runtime analogies. The specific framing is a useful synthesis, but not obviously new as a category distinction.

- **established** — Runtime responsibilities: Context, Scheduling, Tool Routing, Sandbox, Checkpoint, Verification, Safety Gate, Observability.
  - Basis: These are common concerns in agent frameworks and workflow engines. The list is a reasonable taxonomy, but not a novel contribution.

- **potentially_distinctive** — Agent loop as closing the gap between Expected Outcome and Actual Outcome.
  - Basis: The framing is a control-theoretic reframing of agent loops. It may be distinctive in this lab's context, but the underlying idea (discrepancy reduction) is common in control theory and cognitive architectures. Needs external review.

- **common_combination** — Runtime should treat verification, state, and risk as first-class citizens, not just orchestration.
  - Basis: This echoes existing work on trustworthy agents and runtime safety, but the specific combination with the four-layer stack is a local synthesis.

## 4. Facts

- **MEDIUM** — Attention 作为一种机制早于 Transformer 出现；Transformer 的贡献是把 Attention 变成核心并让它可并行。
  - Why verify: This is a historical claim about the origin and contribution of attention mechanisms. It is generally correct, but the phrasing 'let it be parallelizable' may oversimplify the role of multi-head attention, positional encoding, and residual connections.
  - Preferred source: `primary`

- **LOW** — TTFT, TPOT, KV Cache, PagedAttention, quantization, batching are inference-runtime concerns.
  - Why verify: These are established, but the exact set and attribution may change as systems evolve (e.g., speculative decoding, continuous batching). No primary source needed for general concepts, but the article should avoid treating the list as exhaustive.
  - Preferred source: `multiple_independent`

- **LOW** — 几十年前的专家系统就有工具调用和验证循环。
  - Why verify: This is broadly true but historically nuanced. Expert systems often had rule-based inference, not tool calling in the modern sense; they did have verification and explanation subsystems. The claim should be softened or given a concrete example.
  - Preferred source: `primary`

## 5. Missing Points

- **HIGH** — The article lacks a cost model for verification, checkpointing, and sandboxing. These have latency, storage, and compute overhead that may make the proposed runtime impractical for real-time or high-throughput agents.
  - Why it matters: Engineering heuristics fail when costs are ignored. A runtime that verifies every action may be too slow; one that never verifies may be unsafe. The article should discuss the trade-off and suggest cost-aware policies.

- **HIGH** — The interaction between Runtime and Model-level safety is not specified. The article says they are complementary, but not how to allocate responsibility or resolve conflicts.
  - Why it matters: Without allocation, teams may build duplicated or conflicting safety mechanisms, or assume the other layer handles a failure mode. A decision framework is needed.

- **MEDIUM** — The 'Outcome Contract' is mentioned as a future question but not defined. It is a critical missing primitive for verification.
  - Why it matters: If verification is to be first-class, the contract must define what constitutes success, who owns it, and how it is updated. Without it, verification is ad hoc.

- **MEDIUM** — The article does not discuss multi-agent runtimes or concurrent state, despite mentioning Actor System in the questions. Checkpointing and verification become much harder in concurrent/actor settings.
  - Why it matters: Many real agent deployments are multi-agent. Ignoring concurrency may make the runtime design incomplete.

## 6. Recommended Changes

- Replace the Inference Runtime vs Agent Runtime boundary with an operational decision rule and test it against a concrete system (e.g., a code agent with KV-cache reuse).
- Define 'first-class citizen' for verification, state, and risk: specify what runtime must do, what it may delegate, and how it decides.
- Add a cost/latency model for verification, sandboxing, and checkpointing; propose when to skip each based on task properties (side effects, ambiguity, duration).
- Clarify the interaction between runtime constraints and model-level safety with a failure-mode allocation matrix.
- Define or at least sketch the 'Outcome Contract' primitive rather than leaving it as an open question.
- Add a concrete counterexample or boundary for read-only agents: when schema validation is insufficient (e.g., untrusted provenance).
- Reframe the functional stack as conceptual separability vs practical coupling; avoid implying that layers can always be omitted without consequence.
- Label the Agent Runtime responsibility list explicitly as a hypothesis with unknowns, and note that the list may be incomplete or overlap.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
