## 🤖 Critic Lab Report

Article: `articles/problem-space-to-solution-space-agent-cognitive-loop.html`
Commit: `c7fcec89fe741a3a38659c5ab816490f3033bca2`
Model: `deepseek-chat`
Status: **needs_review**

The article offers a coherent engineering framing of the Agent problem as reducing semantic loss across a P0→P4 pipeline, with structured problem representation, active information gathering, tiered verification, and controlled experience-evolution. However, several core claims are over-generalized or under-specified: the data-processing-inequality justification does not actually bound what Agent-side action can recover; DDD is presented as a universal semantic anchor when it may not exist or may be the wrong source of truth; the verification layers conflate syntactic, semantic, and outcome correctness without addressing evaluator validity; and the self-evolution evaluation metrics lack operational definitions and failure modes. The 'Domain Object × Action = Tool' overlap that the reviewer asks about is not directly in this article—it appears to belong to a sibling article—but this article's DDD-anchoring claim implicitly relies on that mapping, so the review should flag the definitional ambiguity and parameter/tool consolidation risk in the sibling context while noting it is out of scope here.

## 1. Logic

- **HIGH** — 在单纯的串行处理链路中，数据处理不等式告诉我们：后续变换不会凭空增加关于原始 X 的信息。
  - Issue: The DPI applies to a Markov chain X → Y → Z. The article uses it as if the Agent's internal representation Z is always such a downstream transform, but an Agent that reads code, runs tests, or queries the user is not a deterministic function of Y alone—it introduces new observations that are conditioned on the world, not on Y. The article later acknowledges this, but the early section still frames the initial channel as lossy in a way that makes the DPI sound like a bound on what the Agent can recover, which it is not once the Agent has external actions.
  - Why it matters: If an engineer reads the DPI section as a law-like limit, they may under-invest in active information gathering because the formal framing appears to say the information is already lost. The article's own later claim (Agent can extend observations) is in tension with the strong initial framing.
  - Test / fix: Restate the DPI as applying only to the passive observation-to-internal-state path, and explicitly separate it from the active-sensing path where no DPI bound applies because new data is introduced. A concrete counterexample: a user saying 'optimize the order module' with no constraint on payment transactionality; a passive summarizer cannot recover the constraint, but an Agent reading the code can. That is not a violation of DPI; it is a different causal graph.

- **HIGH** — 在企业系统中，DDD 的领域模型、聚合边界、领域事件和业务不变量可以成为这样的锚点。
  - Issue: This is stated as a near-universal remedy, but many enterprise systems do not have clean DDD models; they have legacy schemas, undocumented services, implicit invariants, and stale documentation. Presenting DDD as the anchor without a boundary condition implies that the absence of DDD is a special case rather than a common one.
  - Why it matters: The feasibility of the entire 'semantic anchor' approach collapses if the anchor does not exist or is wrong. An Agent that trusts a stale DDD model may be worse than one that reads the code and tests. This materially affects the proposed architecture.
  - Test / fix: Add a boundary condition: the anchor must be verifiable against an executable source of truth (tests, schema, runtime logs) before the Agent treats it as ground truth. A concrete test: take a legacy order module where the DDD document says inventory is not reserved but the code reserves inventory; the Agent must flag the conflict rather than resolve it by preferring the document. Clarify whether DDD is a heuristic for systems that already maintain it or a recommendation to introduce it retroactively.

- **MEDIUM** — Agent 的价值不只是更聪明地推理，而是知道自己缺少什么信息、如何获得信息，以及新证据是否足以改变当前决策。
  - Issue: This is an aspirational characterization, not a demonstrated property. The article does not give a criterion for when an Agent 'knows what it is missing,' nor does it address the case where the Agent's uncertainty about its own uncertainty is miscalibrated. The claim is plausible but should be labeled as a design goal.
  - Why it matters: If treated as an achieved property, this can lead to over-trust in self-reported information gaps. LLM calibration on 'what I don't know' is a known weak point, and the article's own later section on verification does not connect back to the Agent's self-assessment of gaps.
  - Test / fix: Recast as a hypothesis: 'we hypothesize that an explicit Unknown field and a decision-value-ranked information-gathering loop improves task outcomes.' Add a test: compare an Agent with an explicit Unknown field against a baseline on a task where a critical constraint is omitted from the prompt; measure whether the Agent queries for it before proposing a solution.

- **MEDIUM** — 执行者和验收者尽量解耦，避免模型用自己的解释证明自己的方案正确。
  - Issue: This is a strong architectural recommendation, but the article does not address the cost and feasibility of true decoupling. A separate verifier model can share the same priors, the same training data, and the same blind spots; independence is not guaranteed by using a different prompt or a different model instance. The article later mentions 'Judge 的能力' as a risk but does not reconcile it with the earlier 'decompose executor and verifier' recommendation.
  - Why it matters: If engineers believe that a separate verifier is independent by construction, they may over-trust it. The article's own L3 layer (independent Judge) inherits this problem.
  - Test / fix: Specify independence criteria: different model family, different evidence source, or deterministic oracle where possible. Add a concrete test: have two verifier models from different families evaluate the same failing action; measure agreement rate and false-positive rate against a human-labeled ground truth. If agreement is high on wrong answers, the decoupling is nominal.

- **LOW** — 只有在有明确训练数据、评估和发布流程时，才进一步讨论模型层面的学习。
  - Issue: This is a reasonable heuristic but stated as a necessary condition without justification. There may be cases where online learning or retrieval-augmented experience accumulation without a formal release process still produces measurable improvements, particularly in low-risk domains. The article elsewhere advocates for shadow evaluation and regression testing, which is a higher bar than 'training data, evaluation, and release process' for memory-based learning.
  - Why it matters: The claim could unnecessarily block lightweight memory-based improvement loops that are cheaper and safer than model updates.
  - Test / fix: Soften to 'model-level learning should be gated by a release process, but memory-level learning may be deployed with rollback and shadow evaluation.'

## 2. Counterexamples

- **HIGH** — Thesis: Structured intermediate problem representation with explicit Goal/Constraint/Unknown improves semantic preservation from problem to solution.
  - Counterexample: In a highly exploratory domain (e.g., early-stage product discovery), the 'true problem' is itself being discovered through action. Requiring a structured problem representation before acting can freeze a premature model and prevent the exploration that would reveal the real constraints. A concrete case: a user says 'make the checkout faster' and the real issue is that the payment provider is intermittently rejecting certain cards; a structured Goal/Constraint/Unknown model derived from the prompt might miss the provider issue entirely, while a direct diagnostic action (latency trace, provider error log) finds it immediately.
  - Boundary: The structured representation is most valuable when the cost of a wrong solution is high and the domain has stable, discoverable semantics. It is least valuable in exploratory or diagnostic tasks where the act of probing is itself the primary source of problem understanding.

- **MEDIUM** — Thesis: Active information gathering should be prioritized by decision value, not by indiscriminately loading all context.
  - Counterexample: In a time-sensitive incident response (e.g., production outage), the decision-value ranking of information may be wrong because the Agent does not yet know which information is decision-relevant. An Agent that spends 30 seconds ranking information sources before querying the error log may be slower than a simple heuristic that queries the highest-frequency diagnostic source first. The decision-value ranking itself requires a model of the decision, which may be the very thing that is missing.
  - Boundary: Decision-value-ranked information gathering is appropriate when the decision space is at least partially known; it can fail in novel incidents where the first action should be broad diagnostic observation rather than targeted query.

- **MEDIUM** — Thesis: A tiered verifier (L1-L4) with independent judges provides a reliable check on Agent actions.
  - Counterexample: A Judge model can be convinced by a plausible-sounding explanation even when the underlying action is wrong. Consider a code review scenario where the Agent claims a fix is correct because it added a test; the Judge sees the test and the explanation and gives a high score, but the test is tautological or the fix breaks a different invariant not covered by the test. The verifier's L3 semantic check can be gamed by the executor's output without any deception—just shared assumptions.
  - Boundary: Independent judges are more reliable when grounded in a deterministic oracle (e.g., property-based tests, schema constraints) than when they rely on LLM judgment of natural-language explanations.

- **MEDIUM** — Thesis: Memory should retain source, confidence, and applicability scope, and allow subsequent evidence to revise it.
  - Counterexample: In a multi-tenant SaaS environment, a validated experience from tenant A may be incorrectly applied to tenant B if the memory does not encode tenant-specific constraints. The memory schema proposed (source, confidence, scope) may be insufficient if 'scope' is not machine-checkable at retrieval time. A concrete failure: a procedural memory that 'retrying payment with exponential backoff works' is learned on a tenant whose payment provider supports idempotency, but applied to a tenant whose provider does not, causing duplicate charges.
  - Boundary: Memory revision and scope are feasible only if the scope predicate is computable from the current runtime context; otherwise, the memory system needs a retrieval-time guard that re-validates applicability.

## 3. Novelty

- **common_combination** — The five-space P0→P4 loss channel and the framing of Agent failure as primarily a problem-understanding failure.
  - Basis: The decomposition of a task into problem space, solution space, and execution feedback is widely used in requirements engineering, cognitive systems, and recent Agent literature (e.g., outer-loop vs inner-loop distinctions). The specific five-space labeling is a useful packaging but not a new theoretical contribution. The article does not claim originality here; it presents the framing as a lens.

- **potentially_distinctive** — Intermediate Problem Representation with an explicit Unknown field and versioning.
  - Basis: Structured task representation is common, but explicitly modeling Unknown as a first-class field with evidence-backed versioning and connecting it to active information gathering is a practical combination that is less commonly formalized. Without browsing, this is a preliminary assessment; the novelty is in the engineering discipline of treating unconfirmed assumptions as tracked entities rather than in the concept of a problem schema itself.

- **common_combination** — DDD domain model, aggregates, and invariants as semantic anchors for Agent problem representation.
  - Basis: The intersection of DDD and AI Agents is an active area in internal engineering blogs and vendor discussions. The article's specific claim—using invariants as constraints on Agent actions—is a natural application of DDD but not a novel definition. The boundary between 'semantic anchor' and 'source of truth' is where the original contribution could lie, but the article does not sharpen that distinction.

- **common_combination** — Tiered verifier (L1-L4) with evidence-bearing verification results.
  - Basis: Layered validation (syntax→semantics→outcome) is standard in compiler design and CI/CD. The application to Agent actions and the insistence on evidence provenance is a sensible engineering pattern, but the tiering itself is not new. The fingerprinting of errors/strategies/states is a potentially distinctive operational detail.

- **established** — Three-layer self-evolving Agent architecture (Execution Runtime / Evaluation & Simulation / Evolution & Memory) with shadow evaluation and rollback.
  - Basis: This resembles established ML production architecture (training/eval/serving) and control-plane patterns. The article's contribution is the mapping to Agent skill/policy evolution, but the three-layer structure and the gating of new strategies on offline evaluation and shadow runs are well-known heuristics.

## 4. Facts

- **MEDIUM** — CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing (arXiv:2305.11738) and Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv:2303.11366).
  - Why verify: The arXiv identifiers and titles are specific and attributed. They should be checked against the primary source to confirm the titles and that the descriptions in the article match the papers' actual claims. The article uses them as representative, which is acceptable, but the IDs must be correct.
  - Preferred source: `primary`

- **MEDIUM** — 数据处理不等式 tells us that subsequent transforms do not increase information about the original X in a serial chain.
  - Why verify: The DPI is a theorem with precise conditions (Markov chain, appropriate information measure). The article's use is a loose analogy, and the article itself notes it is not a direct proof of Agent correctness. The preferred source is the primary information-theory literature (e.g., Cover & Thomas) or a standard reference, not a Wikipedia link alone.
  - Preferred source: `primary`

- **LOW** — CRITIC '强调通过外部工具和反馈检查模型生成内容' and Reflexion '强调把语言化反馈写入经验'.
  - Why verify: These are compressed characterizations. CRITIC does use tool-interactive critiquing, but the article's description may flatten the details (e.g., CRITIC's specific reliance on external tool feedback vs. self-correction without tools). Reflexion's verbal reinforcement is more nuanced than '写入经验'; it uses self-reflection as a form of episodic memory, but the mechanism is specific to the paper. The characterizations are plausible but should be checked against the abstracts.
  - Preferred source: `primary`

- **LOW** — The weblog references 'articles/agent-runtime-cognitive-actor.html' and 'diverse/ai-native-software-language-aosl.html' as related.
  - Why verify: These are internal cross-references. The links are relative and should resolve. If the AOSL article is under a different path or has a different slug, the link may be broken. This is a site-maintenance fact, not a theoretical claim.
  - Preferred source: `primary`

## 5. Missing Points

- **HIGH** — Operational definition and measurement strategy for the proposed evaluation metrics (Requirement Coverage, Constraint Preservation, Assumption Accuracy, etc.).
  - Why it matters: The metrics are presented as the way to judge progress, but without operational definitions and measurement methods they risk becoming vanity metrics. For example, 'Requirement Coverage' requires a mapping from natural-language requirements to structured fields, which is itself an LLM judgment task with its own error rate. 'Assumption Accuracy' requires knowing which assumptions were validated, which may only be known retrospectively. The article should discuss the proxy-vs-outcome problem for these metrics.

- **HIGH** — Cost and latency budget for the active information gathering and verification loops.
  - Why it matters: Every additional query, test run, or verifier call adds latency and cost. The article mentions budgets in the Controller section but does not connect the budget to the decision of which information to gather or which verification tier to invoke. A concrete engineering detail: how does the system decide to stop gathering information when the marginal value of a query is low? The decision-value ranking is mentioned but not made operational.

- **MEDIUM** — Mapping from verification failure types to recovery actions (RETRY vs REPLAN) and the risk of misclassification.
  - Why it matters: The article states that local implementation errors should RETRY and goal/strategy errors should REPLAN, but it does not provide a classifier for distinguishing them. A failure can be ambiguous: a test failure could be a local bug or a symptom of a wrong problem model. Misclassifying a REPLAN-worthy failure as RETRY leads to repeated failures; the article mentions error fingerprints but not how they drive the state transition decision. This is a material gap for feasibility.

- **MEDIUM** — Interplay between structured problem representation and exploration in open-ended tasks.
  - Why it matters: The article assumes that the problem representation should be built before the solution, but in exploratory debugging or discovery, the action itself is the primary means of refining the problem model. The article should discuss when the representation is a gate versus a living document, and whether there is a risk of over-structuring early. This is a key boundary condition for the proposed architecture.

- **MEDIUM** — Source-of-truth conflicts between DDD model, code, tests, and user statements.
  - Why it matters: The article advocates DDD as a semantic anchor but does not address what happens when the DDD model, the code, the schema, and the user disagree. In practice, these conflicts are common. The Agent needs a conflict-resolution policy that is evidence-based and traceable, or it will default to whichever source it finds first. This is both a missing point and a potential counterexample to the semantic-anchor claim.

- **LOW** — The sibling-article overlap: 'Domain Object × Action = Tool' as a definition, heuristic, or universal claim, and the risk of parameter explosion from tool consolidation.
  - Why it matters: The reviewer asks about this, but this article does not contain the formula. However, this article's DDD-anchoring claim is closely related: if tools are derived from domain objects and actions, then tool consolidation (fewer, more general tools) may reduce the number of domain-anchored checks and make the problem representation less precise. Conversely, too many domain-object × action combinations can cause parameter explosion and tool-selection ambiguity. The article should at least cross-reference the sibling article and note that the semantic-anchor approach depends on how tools are mapped to domain concepts. At present, the article treats DDD as an anchor without discussing the tool-mapping layer that connects it to actions.

## 6. Recommended Changes

- Reframe the data-processing-inequality section: clearly separate the passive information-loss bound from the active-sensing loop, and state explicitly that DPI does not limit what an Agent can recover through observation. Use a causal-graph or Markov-chain diagram that shows the active path as an extension of the graph rather than a violation.
- Add a boundary condition for DDD semantic anchors: they are valid only when verifiable against an executable source of truth (tests, schema, runtime logs), and the Agent must flag conflicts between sources rather than preferring the model. Introduce a 'source-of-truth conflict' state in the Controller.
- Label the 'Agent knows what it is missing' claim as a design hypothesis and connect it to calibration testing. Provide a concrete experiment: measure whether an explicit Unknown field reduces late-discovery rate compared to a baseline, and report false-confidence cases.
- Add operational definitions for the evaluation metrics in Section 8, including who or what judges each metric, the error rate of that judgment, and how the metrics relate to cost. Reconcile these with the proxy-vs-outcome problem discussed in the sibling evaluation article.
- Discuss the differentiation between RETRY and REPLAN more concretely, including a classification heuristic based on error fingerprints and state-change evidence. Add a failure mode: repeated RETRY on an ambiguous failure.
- Add a paragraph on when the structured problem representation should be a gate versus a living document, and whether there is a cost to premature over-structuring in exploratory tasks. This is a boundary condition for the architecture.
- Cross-reference the sibling article on Domain Object × Action = Tool and clarify whether that mapping is a definition, a heuristic, or a system-specific design. Note the risk that tool consolidation can reduce the granularity of domain-anchored verification and that domain-object × action proliferation can cause parameter explosion; the article should not treat the semantic-anchor approach as independent of that trade-off.
- Soften the claim that model-level learning 'only' happens with training data and release processes; acknowledge that memory-level learning can be deployed with rollback and shadow evaluation, which is a different gate.

Evidence level: `E2`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
