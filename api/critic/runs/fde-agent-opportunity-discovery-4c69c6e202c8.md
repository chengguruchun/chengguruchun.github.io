## 🤖 Critic Lab Report

Article: `articles/fde-agent-opportunity-discovery.html`
Commit: `4c69c6e202c84fc2f721ae23e03abb28a0f9f374`
Model: `deepseek-chat`
Status: **needs_review**

The article is a well-structured, explicitly hedged engineering hypothesis about FDE as a business-decision-modeling role, and it mostly labels its speculation appropriately. The main weaknesses are definitional looseness (Decision Unit is under-specified and risks collapsing domain boundaries into runtime/risk/verification boundaries), an unquantified cost inequality that is presented as decision-grade, and confidence-boundary claims (observation vs judgment vs speculation) that are not operationalized. Note: the git diff only changes a cache-busting version string on a script tag (article-actions.js?v=...-3 -> -4); it does not touch the article body, so the review targets the full text, not the diff. The reviewer prompt also asks about 'Domain Object × Action = Tool', which does not appear in this article — that framing belongs to a sibling article and should not be imported as if it were a claim here.

## 1. Logic

- **HIGH** — Decision Unit is defined by an attribute list (Trigger, Input/Context, Decision, Constraints, Action, Outcome, Feedback, Risk, Owner/Approver).
  - Issue: This is an attribute enumeration, not a boundary criterion. The list mixes domain semantics (Decision, Constraints) with runtime mechanics (Action, Feedback, Tools) and governance (Risk, Owner/Approver). Two analysts could draw different Decision Unit boundaries for the same process and both satisfy the list, so the unit is not falsifiable or comparable.
  - Why it matters: The whole article's value proposition rests on Decision Units being a stable, verifiable unit. If the boundary is analyst-dependent, the 'Agent Suitability' downstream comparison is not reproducible, and the open question about confirming boundaries is actually a definitional gap, not just a process gap.
  - Test / fix: Require a separate boundary test independent of the attribute list, e.g. 'a Decision Unit is the smallest set of states where one human/agent holds a single accountability and one verifiable Outcome closes the loop.' Test: give two engineers the same SOP and check whether they produce the same units and the same count; if not, the definition is under-specified.

- **HIGH** — Complexity is 'not six parallel labels but a judgment framework' with ten dimensions split into necessary conditions, risk penalties, and value sources.
  - Issue: The classification is asserted, then the table mixes the claims. The table's '作用' column labels 可观测性 and 可验证性 as '接近必要条件' but the surrounding prose also places 安全边界 and 治理难度 as necessary/penalty — these are neither consistently enumerated nor given thresholds. A 'necessary condition' that has no measurable gate is indistinguishable from a high-weight score.
  - Why it matters: If 可观测性/可验证性 are genuinely necessary, the assessment must be able to reject a case outright; if they are just heavily weighted, then a high-value case could still pass, which contradicts the stated framing and would mislead an FDE selling this to a client.
  - Test / fix: Add an explicit gate: 'if 可观测性 < X or 可验证性 < Y, the answer is No regardless of score' and show one case that is rejected by the gate despite high complexity/frequency. Also reconcile the ten-dimension list with the six-row table (four dimensions are missing from the table).

- **MEDIUM** — Agent 化值得做 ≈ (saved decision cost + speed + business benefit + coverage) > (model + integration + eval + monitoring + recovery + approval + explainability/governance costs).
  - Issue: This is framed as an inequality but every term is unquantified and some terms (coverage benefit, explainability cost) have no agreed unit. A pseudo-formula can create false rigor and be used to justify either verdict post hoc.
  - Why it matters: The article positions this as the 'most important question' in its final section, but a non-computable inequality cannot answer 'when does Workflow TCO exceed Agent Runtime TCO.' It also omits two large terms: the cost of the discovery/assessment itself and the cost of dual-running during migration.
  - Test / fix: Downgrade to a checklist labeled 'hypothesis, not formula,' or supply at least one worked estimate with explicit units and ranges showing how the verdict flips. Add discovery cost and dual-run/migration cost as terms.

- **MEDIUM** — The article repeatedly separates '已观察事实 / 工程判断 / 未来推测.'
  - Issue: The '已观察事实' items ('真实企业业务往往包含大量隐性约束...') are general characterizations without a stated observation basis, sample, or counter-check. The label performs work it hasn't earned, so it functions as rhetoric rather than epistemic hygiene.
  - Why it matters: The three-layer separation is the article's main credibility device. If 'fact' is not tied to any source or experience record, the labels become decorative and the reader cannot tell which parts are contestable.
  - Test / fix: Either attach a basis to each 'fact' (e.g. 'observed in N client engagements, examples: ...') or re-label them as 'widely reported working assumption.' Keep speculation labels as-is — those are honestly used.

## 2. Counterexamples

- **HIGH** — Thesis: The right first move is to decompose the business into Decision Units and then choose Workflow/Optimizer/Agent.
  - Counterexample: A stable, high-volume process with clear rules (e.g. tax calculation, ETL) where the existing Workflow already has acceptable TCO and full auditability. Here decomposition is unnecessary overhead, and the correct answer is 'don't decompose, don't Agent.' The article's own §6 acknowledges complex ≠ Agent but the headline workflow (Business Reality → Decision Units → Complexity Map → Suitability) still presumes decomposition is always the entry point.
  - Boundary: Decomposition earns its cost only when (a) the current workflow TCO is actually rising, or (b) a decision is currently made ad hoc/humanly and is a candidate for automation. Otherwise the assessment is a solution looking for a problem.

- **MEDIUM** — Thesis: FDE can lead the modeling of business decisions into Decision Units.
  - Counterexample: Regulated domains (nuclear, pharma GxP, financial controls) where the accountable decision owner is a qualified role with legal responsibility, not an FDE. The 'Owner/Approver' field in the Decision Unit implies the FDE can identify it, but authority to define the decision boundary sits with the domain/risk owner.
  - Boundary: FDE can facilitate and draft; validation and sign-off must be with the accountable role. The article gestures at this in §9 but the headline still says 'FDE 牵头', which in a compliance review reads as FDE owning the decision model.

- **MEDIUM** — Thesis: Agent Discovery can extract Decision Units and hidden decisions from logs/SOPs/ERP data.
  - Counterexample: Logs record what was executed, not the alternatives that were rejected or the judgment that was exercised implicitly. A human approving every order without recorded rationale yields an 'observation' of a routine, not a decision. Hidden decisions are precisely the ones with no trace.
  - Boundary: Discovery from logs will systematically under-detect informal judgment and over-detect formal workfow. It may recover the decision *shape* but not the constraints or the risk tolerance — those need domain-expert elicitation.

## 3. Novelty

- **potentially_distinctive** — Decision Unit as the minimal unit for Agent opportunity discovery.
  - Basis: Preliminary, no browsing. Task/decision decomposition is established in process mining and in classical decision analysis; the specific packaging as 'Decision Unit' with this attribute set for Agent suitability is a combination I have not verified elsewhere. Treat as a naming contribution, not a proven new concept.

- **common_combination** — Ten-dimension complexity framework partitioned into necessary conditions, risk penalties, and value sources.
  - Basis: Individual dimensions (observability, verifiability, error cost, interface maturity) are standard in automation/ML feasibility and safety engineering. The partition into necessary/penalty/value is a useful synthesis but not a novel mechanism.

- **potentially_distinctive** — FDE as 'business compiler' translating business language into a decision space.
  - Basis: The article correctly flags this as a metaphor. 'Compiler' framing for requirement-to-execution is used in other domains (e.g. intent compilers); its application to FDE role is evocative but unvalidated. Label as metaphor, which the article does.

- **unknown** — Agent Discovery Agent auto-generating a Complexity Map from enterprise data, validated by FDE + domain experts.
  - Basis: No external evidence gathered. This is explicitly speculation; nothing in the text establishes feasibility.

## 4. Facts

- **MEDIUM** — Publication date 2026-09-17 and the article is written in present/future tense about FDE roles and 'Agent Discovery.'
  - Why verify: Any claim about current industry practice ('FDE 可能承担重要牵头角色') is time-sensitive; a 2026 date means the 'current' baseline may have shifted. Verify whether FDE role descriptions referenced are from a specific vendor/consultancy or general.
  - Preferred source: `primary`

- **LOW** — Example table uses '核电安全控制 不应直接采用自主 Agent.'
  - Why verify: This is a normative safety claim. It is plausible, but safety-critical autonomous control has its own regulatory literature; the article should not present it as an engineering conclusion without acknowledging applicable standards (e.g. IEC 61508/61511 class) if it wants to be citable.
  - Preferred source: `official`

- **LOW** — Script version string change (-3 to -4) in the diff.
  - Why verify: Appears to be a cache-busting version bump with no content change; confirm the deployed asset matches, otherwise readers may get stale JS, which is not an article claim but is the only actual change.
  - Preferred source: `primary`

## 5. Missing Points

- **HIGH** — No operational definition of 'Workflow Total Cost' vs 'Agent Runtime Total Cost.', nor a time horizon for 'long-term total cost.'
  - Why it matters: §7 and the open questions both depend on this comparison; without a horizon (e.g. 2-year TCO including maintenance, re-eval, model drift) the comparison is undefined and the FDE cannot defend a recommendation.

- **HIGH** — No treatment of how to handle a Decision Unit that is partly automatable and partly not — the boundary between domain scope and runtime/verification scope is underspecified.
  - Why it matters: This is the core review question: runtime/risk/verification boundaries can get conflated with domain boundaries when drawing Decision Units. A unit may be domain-coherent but unobservable, or runtime-observable but cross-domain. The article needs an explicit rule for when a domain-aligned unit must be split for runtime/risk reasons (or vice versa).

- **MEDIUM** — No mention of parameter/tool-surface explosion when consolidating decisions into fewer, larger units.
  - Why it matters: If Decision Units are drawn coarsely to preserve domain coherence, the tools/params inside grow and the suitability assessment should penalize it. The ten dimensions include interface maturity but not 'tool parameter cardinality' or 'decision-space size per unit,' which is exactly where consolidation pressure shows up.

- **MEDIUM** — No baseline measurement protocol for the 'saved manual decision cost' term.
  - Why it matters: Value sourcing (frequency, manual cost) is the positive side of the inequality; without a measurement method (time-and-motion, ticket sampling, human-in-loop latency) the FDE's value estimate is a guess.

- **LOW** — No discussion of who owns the Decision Unit catalog and how it is versioned as the business changes.
  - Why it matters: If decisions are the unit, they drift; an unversioned catalog will silently invalidate the suitability assessment over time.

## 6. Recommended Changes

- Replace the Decision Unit attribute list with an explicit boundary criterion plus a reproducibility test (two analysts produce the same units).
- Make the necessary-condition claim operational: define measurable gates for 可观测性 and 可验证性 that can reject a case, and show a rejected example.
- Demote the §7 inequality to a labeled hypothesis/checklist, or add a worked numeric example with units and ranges (including discovery and migration/dual-run costs).
- Clarify the domain-vs-runtime/risk/verification boundary: give a rule for when a domain-coherent decision must be split because it is unobservable, or merged despite spanning functions.
- Add a short section on parameter/tool-surface growth under consolidation as a penalized dimension.
- Attach a basis (experience record or source) to each '已观察事实' or relabel as working assumption.
- Soften 'FDE 牵头' to 'FDE leads the modeling workstream; decision ownership and sign-off sit with the accountable role.'
- State a TCO time horizon and a minimal measurement protocol for manual decision cost.
- Keep all speculation labels; add 'metaphor' tag explicitly to 'business compiler' (already implied).

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
