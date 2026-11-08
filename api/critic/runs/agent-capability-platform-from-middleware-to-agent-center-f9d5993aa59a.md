## 🤖 Critic Lab Report

Article: `articles/agent-capability-platform-from-middleware-to-agent-center.html`
Commit: `f9d5993aa59a9bc3a9b5021c50d99577fc456be9`
Model: `deepseek-chat`
Status: **needs_review**

This is a coherent design-model article that explicitly disclaims full production grounding, which is appropriate. Its main weaknesses are: (1) a central causal claim—that the 'interface-heavy public-service collection' problem is solved by declarative Definition—is asserted rather than shown; (2) several terms (skill/agent/workflow, outcome/evidence, 'technical barrier') are used at different granularities; and (3) the control-plane/runtime-plane split borrows K8s language while implicitly denying the comparison, without clarifying what the actual runtime contract is. The tool-design and risk-side questions in the review prompt are largely absent from this article, so I flag them as missing points rather than errors of this text.

## 1. Logic

- **HIGH** — Traditional middleware 'becomes an interface-heavy public-service collection' when domain boundaries and extension points are not done well; therefore a declarative Agent Definition with Registry + Runtime will avoid the same fate.
  - Issue: Circular/analogical reasoning. The article diagnoses a governance and adoption failure (teams route around the platform) but proposes a resource model as the remedy. Resource modeling does not by itself fix incentive, onboarding cost, or domain-boundary problems—the stated cause of the original failure.
  - Why it matters: The whole architecture justification rests on the analogy, but the analogy's failure mode is organizational/adoption, while the proposed fix is structural. If the platform is not easier to adopt, the resource model changes nothing.
  - Test / fix: State explicitly which part of the 'interface-heavy' problem the Definition model solves and which it does not. Add a falsifiable criterion, e.g. 'time-to-first-working-agent for a team without platform training' or 'percentage of teams that bypass the registered tools,' as the success metric.

- **HIGH** — 'Runtime is the platform's real technical barrier' (壁垒).
  - Issue: This is an overstated conclusion. The article gives no evidence that runtime is harder to build than, say, a good tool registry, policy engine, or evaluation harness, nor a definition of what 'barrier' means (engineering effort, correctness, cost?). A declarative Definition is also weakly useful without a rich registry and policy; these co-vary.
  - Why it matters: Over-prioritizing runtime in the V0.1 roadmap can lead teams to under-invest in Definition/Registry, which is where the article itself says the hard conceptual questions live. It can also cause teams to underestimate the policy and evaluation engine.
  - Test / fix: Reframe defensive claim as hypothesis: 'Runtime is the *hardest single component to make reliable* because of X (state, checkpoint, side-effect replay).' Give evidence, e.g. incident classes in existing agents, or a cost breakdown across components.

- **MEDIUM** — Tool = action capability (deterministic op), Skill = operational knowledge, Workflow = deterministic orchestration, Agent = goal-driven executor.
  - Issue: These are useful working definitions but not mutually exclusive. A Skill may contain a small workflow; a Workflow can call an Agent; an Agent can be used as a tool by another Agent. The article says they 'can be combined but not conflated'—which is a norm rather than a definitional test. No operational rule is given for classifying an ambiguous case.
  - Why it matters: If two teams classify the same capability differently (is 'refund policy' a Skill or a Workflow?), registry, versioning, and policy inheritance will be inconsistent.
  - Test / fix: Add a decision rule, e.g. 'if it needs model inference to choose a next step, it is agent/workflow; if it has an input-output contract and no model call, it is tool.' Test: classify three real examples in the article under the rule.

- **MEDIUM** — 'Agent Definition and Agent Run are two different objects'—Definition published/versioned, Run is an execution instance.
  - Issue: The distinction is sound but is applied only at run level. The article does not address how the Definition snapshot is pinned to a Run when a Definition changes mid-execution, nor how a long-running Run behaves after a hot-fix version is published. The 'immutable runtime config snapshot' is asserted, not defined as a contract.
  - Why it matters: Long-running and check-pointed runs are central to the article's value proposition (approvals, resume). Without snapshotting rules, resume-after-approval can silently change behavior.
  - Test / fix: Specify: does a Run bind to (Definition version, tool versions, model route) at start or at each step? Show how a checkpoint resumes against the pinned snapshot.

- **MEDIUM** — Outcome and Evidence are needed to judge task completion ('模型返回成功 ≠ 完成任务').
  - Issue: 'Evidence' is introduced but never defined (schema? provenance? who validates?). The claim that Judge self-assessment is not sufficient is asserted without saying what external evidence would count or how it is verified.
  - Why it matters: Without a definition, 'evidence' becomes another unverified self-report. The K8s analogy (退出码) is also incomplete: process exit code is only one of several signals; many modern systems use condition/status plus events.
  - Test / fix: Define an evidence schema (source, timestamp, verifier, confidence) and give one concrete acceptance rule for the code-review agent (e.g. 'PR merged with no reverts within N days').

## 2. Counterexamples

- **HIGH** — Thesis: Most business teams can create Agents from templates plus a few parameters.
  - Counterexample: A regulated or safety-critical domain (payments, manufacturing line control, clinical ordering) cannot be safely expressed as small parameter overrides. The policy set, approval gates, evidence requirements, and test cases for each deployment variant differ materially, so 'fill in a few parameters' becomes 're-author policy + acceptance tests'—which requires engineering skill.
  - Boundary: Template-based creation is likely valid for read-only/analytic agents; it breaks where side effects are irreversible, regulated, or audited.

- **MEDIUM** — Thesis: Declarative Definition + Registry avoids the 'interface-heavy public-service collection' failure.
  - Counterexample: Earlier declarative resource models (e.g., OpenAPI-first internal catalogs, generic 'config-driven workflow engines') did not prevent bypass: teams wrote escape-hatch code because the declared contract was too coarse. Declarative models fail when the declaration language is insufficiently expressive for real variability, which pushes teams to shim code; the resulting system is heavier, not lighter.
  - Boundary: Holds when the declaration language covers ≥90% of real variation and has a clean Level-3 escape hatch.

- **MEDIUM** — Thesis: 'Agent Definition + Registry + Runtime + Policy + Evaluation' is sufficient skeleton.
  - Counterexample: A central piece—data/context management (retrieval corpora, memory sharing across agents, tenant isolation of memory)—is listed as a resource but never sized. Teams often fail because their agent retrieves wrong or stale context, not because Definition/Registry/Runtime are missing.
  - Boundary: Evaluation of this skeleton requires showing context/data layer complexity in the effort model.

- **LOW** — Thesis: Workflow and Agent should share a platform.
  - Counterexample: Mature workflow engines (Temporal, Camunda) and agent frameworks have different determinism assumptions, testing models, and failure modes (workflow replay determinism vs. LLM nondeterminism). Co-hosting may force compromises that weaken both.
  - Boundary: The article does suggest integration, not co-hosting—but does not say where they run relative to each other.

## 3. Novelty

- **common_combination** — Agent 能力中台 = declarative Definition + Registry + Runtime Plane + Policy + Evaluation
  - Basis: Each component has established precedent (K8s CRD/control plane, service registries, runtime sandboxes, policy engines, eval harnesses). The composition is coherent but no claim in this article is established as novel, and this is a preliminary assessment without external browsing. (Note: the review prompt's 'Domain Object × Action = Tool' framing belongs to a sibling article, not this text; this article only says 'Tool = action capability'.)

- **established** — Control Plane / Runtime Plane split for agents
  - Basis: Directly modeled on Kubernetes and prior agent-runtime articles in this lab (k8s-to-agent-control-plane, agent-engineering-from-workflow-to-control-plane).

- **potentially_distinctive** — Tool / Skill / Workflow / Agent as distinct resource classes
  - Basis: The four-way distinction is proposed as a design model. It is similar to skill/tool distinctions used elsewhere, but the explicit norm that they should not be conflated, plus shared registry semantics, is a distinctive articulation in this body of work. Unverified against production systems.

- **unknown** — Runtime as locus of the real '壁垒'
  - Basis: No comparative evidence in the article; the claim is plausible but unsubstantiated in either direction.

## 4. Facts

- **MEDIUM** — Kubernetes manages 'expected state of services and compute resources'; agents need more (goal, tool authorization, semantic outcome, evidence).
  - Why verify: This characterization of K8s is a simplification. Controllers also manage observed state, conditions, and events; some systems embed workflow/evidence semantics in operators. The contrast may be overstated.
  - Preferred source: `official`

- **MEDIUM** — MCP Gateway / CLI Hub as infrastructure layer components (used as a normalized list).
  - Why verify: MCP and 'CLI hub' are moving targets with versioned behavior; the article treats them as stable categories. Any protocol-level claim should be pinned to a spec version.
  - Preferred source: `official`

- **MEDIUM** — Article metadata shows publication date 2026-11-08 (both in text and JSON-LD).
  - Why verify: Future-dated publication dates can be a build or backdating issue; if the site is meant to reflect real-time knowledge, this signals a metadata pipeline problem. Check build scripts/build_seo.py and article source front-matter.
  - Preferred source: `primary`

- **LOW** — Runtime needs to support pause, resume, retry, timeout, cancel, human intervention, idempotency keys, compensation.
  - Why verify: These are standard distributed-systems requirements, but the article does not cite where they are satisfied in production agent platforms. No source is given; keep as engineering heuristics.
  - Preferred source: `multiple_independent`

## 5. Missing Points

- **HIGH** — Tool parameter explosion under a 'Domain Object × Action = Tool' model is not addressed—and the article adopts 'Tool = atomic action' without specifying how parameters are bounded.
  - Why it matters: If every action on an aggregate domain object is its own tool, tools multiply non-linearly and their parameter schemas expand; if consolidated into 'domain-object tool + action parameter,' prompt selection accuracy degrades. The article needs an explicit boundary: how many tools, how much parameter space, and where to split. This is a known failure mode in tool-use agents.

- **HIGH** — Domain boundaries are conflated with runtime/risk boundaries in the policy discussion.
  - Why it matters: The article says 'platform manages how capabilities are used; business domain manages correctness' but does not say where ownership of policy (who can do what, when) sits. A tool owned by refund domain may enforce its own rules, while a platform policy also gates it—double ownership can lead to ambiguous enforcement and drift. The article should distinguish: domain boundary = ownership of capability and its state invariants; runtime boundary = execution isolation; risk boundary = approval and least privilege. Mixing them causes tools to be redesignated for governance reasons.

- **HIGH** — Verification boundary: what 'Evidence' is, who produces it, and where acceptance is enforced is not defined.
  - Why it matters: Without it, the Evaluation layer is another process metric. Boundary between 'platform verifies' and 'business domain verifies' (e.g., payments reconciliation must be owned by the ledger, not the agent platform) is missing.

- **MEDIUM** — Level-3 'Custom Runtime' (custom loop, hooks, sandbox) is claimed to share resources and infra, but the ABI/contract between the platform and a custom runtime is unspecified. How custom runtimes emit events, checkpoint state, and receive policy decisions is the crux of whether the resource model holds.
  - Why it matters: If the contract is not specified, Level-3 is effectively 'off-platform,' and the article's claim that the three levels share one model collapses.

- **MEDIUM** — Cost and latency implications of multi-round agent execution under platform governance are absent from sizing; token masking or summarization of tool results for policy decisions is not discussed.
  - Why it matters: Policy checks per parameter require inspecting payloads; large payloads mean cost and latency at the gate, which can push teams to bypass.

- **MEDIUM** — No discussion of failure modes specific to declarative platforms: schema evolution in published Definitions, backward compatibility of tool schemas, and rollback.
  - Why it matters: The article says 'do not let a tool update silently change behavior' but offers no version pin strategy. A concrete policy (pin major, allow patch, required re-verification) is needed.

- **LOW** — 'Agent as a Service' is used loosely to position beyond IaaS; no distinction from existing PaaS/serverless or from 'AI middleware' vendors.
  - Why it matters: It is a marketing-laden phrase without a precise definition in the text; the article itself later argues no-code is not the point. It should define what is actually delivered as a service (runtime? governance? both?).

## 6. Recommended Changes

- Reframe the 'interface-heavy public-service collection' failure mode and the Definition-based fix as hypotheses, and add an adoption metric as the test.
- Downgrade 'Runtime is the real 壁垒' to a hypothesis with a concrete claim about which reliability properties make it hard (state, checkpoint, side-effect replay).
- Define operational rules that distinguish Tool / Skill / Workflow / Agent (e.g., 'contains model inference to choose next step' as a test).
- Add a tool-granularity section: parameter explosion vs. prompt-selection accuracy; propose an explicit boundary (tool count, aggregate-object + action parameter) with a concrete example.
- Separate domain boundary (state invariants, capability ownership), runtime boundary (isolation), and risk boundary (approval/permission), and state who enforces each in the refund example.
- Define the Evidence schema and acceptance owner; mark 'evidence vs. self-report' as hypothesis pending examples.
- Specify the pinned snapshot semantics for Run/Checkpoint across published version changes (pin at start vs. per step).
- Specify the contract/ABI for Level-3 custom runtimes (events, checkpoint, policy callbacks) so the 'one shared model' claim can be tested.
- Check the future-dated publication timestamp (2026-11-08) in front matter and JSON-LD; confirm it reflects the intended build state.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
