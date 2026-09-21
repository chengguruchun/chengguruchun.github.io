## 🤖 Critic Lab Report

Article: `articles/domain-driven-agent-tool-design.html`
Commit: `c7cca1ee14d9f76c04fbafdedee24fda88cbc84c`
Model: `deepseek-chat`
Status: **needs_review**

The article reframes agent tool design as a domain-driven matrix (domain objects × actions), which is a useful engineering heuristic, but the core equation and several claims are stronger than the evidence supports. The most important risks are that tool consolidation trades naming explosion for parameter/action-space explosion, that domain boundaries are conflated with permission/runtime/verification boundaries, and that the framework quietly assumes a stable, well-modeled domain. The added visits.js footer is a separate, low-risk tracking change unrelated to the thesis.

## 1. Logic

- **HIGH** — 领域对象 × 动作 = 工具
  - Issue: Presented as an equation/identity but functions as a design heuristic. It is unclear whether a tool must be exactly one cell or whether merged cells are also 'the tool'. If merged cells count, the equation is not a definition; if not, the article's own consolidation step contradicts it.
  - Why it matters: If readers treat it as a definition, they will reject merged tools or over-generate cells. If it is a heuristic, it needs success criteria and failure modes.
  - Test / fix: Label it explicitly as a heuristic/lens, and define the output as either a cell or a merged action-group. Add a concrete rule: when to keep separate cells vs merge (e.g., same risk profile, same schema, same permission).

- **MEDIUM** — 动作推导降级为完备性校验
  - Issue: The claim that action-first design is 'the hidden flaw' overstates a sequencing preference. Action primitives are one valid decomposition axis; domain objects are another. Neither is universally first. For infrastructure agents (e.g., file system, shell, network), action/primitive-first is often the natural starting point because the domain objects are generic or runtime-defined.
  - Why it matters: Turning a heuristic into a ranked universal rule can mislead designers of platform/infra agents.
  - Test / fix: Scope the claim: 'for business/domain agents, start from domain objects; for infrastructure/runtime agents, action primitives may be the correct starting point.' Add a decision criterion.

- **MEDIUM** — 同动作合并是防止工具爆炸的关键闸
  - Issue: The article treats consolidation as the solution but does not analyze the cost side. Merging create_pr/review_pr/merge_pr into one tool with an action parameter moves complexity from tool selection to parameter selection. If the LLM must choose the correct action enum and supply action-specific parameters, error modes can worsen.
  - Why it matters: Tool count and parameter-space complexity are two different failure surfaces. Optimizing one can degrade the other.
  - Test / fix: Run an A/B evaluation: N separate tools vs one merged tool with action enum, on the same eval set. Measure tool-selection accuracy, parameter-filling accuracy, and end-to-end task success. Report the crossover point.

- **MEDIUM** — 边界 = 领域边界，天然框定「该管 / 不该管」
  - Issue: This conflates three distinct boundaries: (1) domain ownership (which objects), (2) permission/risk boundary (read vs write vs execute), (3) verification boundary (what output can be trusted/checked). The article later says '权限按风险分级', which contradicts the earlier claim that domain boundary naturally frames should/shouldn't manage.
  - Why it matters: If designers rely on domain boundaries for safety, they may miss risk-based and verification-based constraints. Domain-appropriate actions can still be dangerous or unverifiable.
  - Test / fix: Separate the axes explicitly: domain object × action (what), risk class (who may do it), verification mode (how to trust the result). Show that a single cell can carry different risk/verification levels.

- **LOW** — 长尾能力不进主列表 / MCP 长尾挂载
  - Issue: The article does not explain how the agent discovers and selects long-tail tools if they are not in the main list. Retrieval-based tool selection, dynamic loading, or capability manifests are implied but not specified.
  - Why it matters: Without a discovery mechanism, long-tail tools are effectively unavailable, weakening the completeness argument.
  - Test / fix: Describe a concrete long-tail discovery mechanism (e.g., vector retrieval over tool descriptions, hierarchical namespaces) and its failure modes.

## 2. Counterexamples

- **HIGH** — Thesis: Merging tools with an action parameter prevents tool explosion
  - Counterexample: A merged 'database操作' tool with action=create|read|update|delete|migrate|backup requires very different parameters and permissions per action. The LLM may select the correct action but hallucinate parameters for that action, producing a higher-severity failure than picking the wrong tool from a small list.
  - Boundary: Consolidation helps when actions share parameter schema and risk profile; it hurts when actions have divergent schemas, permissions, or verification needs.

- **HIGH** — Thesis: Domain-driven design naturally prevents over-privileged agents
  - Counterexample: A 'customer support' agent's domain object is 'Customer', and an action 'update' is domain-appropriate. But updating PII, refunding money, or changing account status are all 'update Customer' with very different risk. Domain boundary alone does not prevent unauthorized or unsafe actions.
  - Boundary: Domain boundary is necessary but not sufficient; permission and verification boundaries must be layered on top.

- **MEDIUM** — Thesis: Pure action-first design produces an indistinguishable skeleton across agents
  - Counterexample: A 'code review agent' and a 'customer service agent' may both start with Read/Write/Bash/Ask at the primitive layer, but the action-first method can include domain-specific actions like 'post_review_comment' or 'issue_refund' as first-class primitives. The article's characterization of action-first as only generic primitives is a straw man unless the method is explicitly restricted to generic primitives.
  - Boundary: The critique applies only to a narrow version of action-first that forbids domain-specific action naming.

- **MEDIUM** — Thesis: 领域对象 × 动作 gives a stable tool list
  - Counterexample: In a code review agent, the 'Diff' object may be represented as a file, a patch, a commit range, or a PR diff depending on the runtime. The same domain object has multiple runtime representations, so the matrix row is ambiguous unless representation is fixed. This can cause both duplicate tools and integration errors.
  - Boundary: The matrix assumes a stable runtime representation for each domain object; without it, the same object spawns multiple tools.

- **LOW** — Thesis: Tool descriptions of 3–4 sentences improve selection
  - Counterexample: For a tool with a large action enum, 3–4 sentences may be insufficient to disambiguate all actions. Conversely, for a simple read tool, long descriptions add context bloat. Description length is task- and action-space-dependent.
  - Boundary: The description guideline is not universal; it interacts with tool granularity.

## 3. Novelty

- **common_combination** — 领域对象 × 动作 = 工具 as a design lens
  - Basis: Domain-driven design and CRUD/resource-action matrices are well-established. Combining them for agent tool design is a useful packaging but not a new primitive. Preliminary assessment without external browsing.

- **potentially_distinctive** — Action derivation as completeness check rather than starting point
  - Basis: The specific inversion (domain-first, action-as-checklist) is a practical framing that may be distinctive in the agent-tool context, though it parallels established DDD sequencing. Needs comparison to existing agent tool taxonomy literature.

- **established** — Same-action merging as the key anti-explosion gate
  - Basis: API design and tool consolidation for LLM function-calling is widely discussed; merging similar operations into one tool with an action parameter is a common pattern.

- **unknown** — Long-tail MCP/Skill mounting outside the main list
  - Basis: The article asserts a pattern but provides no mechanism or evidence. Novelty cannot be assessed without knowing the intended retrieval/loading architecture.

## 4. Facts

- **MEDIUM** — Claude Code 的 46 个内置 tool；14 个需提示、32 个免提示
  - Why verify: Tool count and permission split are version-sensitive and may change across releases. The article presents them as stable facts.
  - Preferred source: `primary`

- **MEDIUM** — Bash 内置只读命令集免提示
  - Why verify: Permission behavior depends on Claude Code configuration and version; it may not be a fixed built-in read-only set.
  - Preferred source: `primary`

- **MEDIUM** — Cursor 9 个 MCP 撑大上下文
  - Why verify: This is a personal anecdote and context-window impact depends on model, MCP implementation, and tool description length. Presented without measurement.
  - Preferred source: `multiple_independent`

- **LOW** — 工具描述写 3–4 句 / 返回只留高信号字段
  - Why verify: This is presented as a general performance rule but is likely model- and task-dependent. No benchmark cited.
  - Preferred source: `multiple_independent`

- **LOW** — e2b 沙箱对应「执行」动作类别里的代码执行细分子类
  - Why verify: e2b is a specific product with its own architecture; mapping it to a single matrix cell may understate its scope (filesystem, networking, lifecycle).
  - Preferred source: `primary`

- **LOW** — 新增 visits.js 页脚访问统计
  - Why verify: Tracking script behavior, privacy implications, and whether it fails gracefully are not described.
  - Preferred source: `primary`

## 5. Missing Points

- **HIGH** — Parameter explosion from action consolidation
  - Why it matters: Merging tools moves complexity into the action enum and parameter schema. If the schema becomes a union of all action-specific parameters, the LLM may hallucinate irrelevant or wrong parameters. Tool count reduction is not the same as complexity reduction.

- **HIGH** — Permission/risk boundary vs domain boundary
  - Why it matters: Domain-appropriate actions can be high-risk. A matrix cell needs a risk annotation (read/write/execute/external side effect) independent of the domain object. Without this, the framework can produce unsafe agents.

- **HIGH** — Verification boundary for action outcomes
  - Why it matters: Agents need to verify that an action succeeded and produced the intended effect. Some actions are cheap to verify (read), others expensive or impossible (send_email, merge_pr). The matrix does not capture verifiability, which affects tool design (e.g., need for dry-run, idempotency, confirmation).

- **MEDIUM** — Runtime representation of domain objects
  - Why it matters: The same domain object may have multiple runtime representations, causing duplicate tools and integration bugs. The matrix assumes a canonical representation that must be specified.

- **MEDIUM** — Failure modes of domain modeling
  - Why it matters: If the domain model is wrong or incomplete, the entire tool set inherits the error. The article acknowledges boundary errors are costly but does not propose how to validate the domain model before tool generation.

- **MEDIUM** — Cost of matrix maintenance
  - Why it matters: As domain objects and actions grow, the matrix can become large. The article does not discuss how to keep the matrix coherent, versioned, or pruned.

- **LOW** — Evaluation methodology for tool design
  - Why it matters: The article makes performance claims (description quality, consolidation) but does not define how to measure success. A concrete eval loop would strengthen the hypothesis.

- **LOW** — Interaction with prompt/context budget
  - Why it matters: Even a well-consolidated tool list consumes context. The article mentions context bloat but does not connect the matrix to prompt budgeting or dynamic tool loading.

## 6. Recommended Changes

- Label '领域对象 × 动作 = 工具' explicitly as a heuristic/lens, not a definition or universal law, and add scope conditions (business agents vs infra agents).
- Add a dedicated section on consolidation costs: parameter-space growth, action-enum disambiguation, and when to keep tools separate.
- Separate domain boundary from permission/risk and verification boundaries; annotate each matrix cell with risk class and verification mode.
- Replace or qualify strong claims like '天然框定该管/不该管' with a layered boundary model.
- Provide a concrete long-tail discovery mechanism (retrieval, namespaces, dynamic loading) instead of asserting '长尾不进主列表'.
- Add a small evaluation protocol (A/B test separate vs merged tools, measure selection/parameter/end-to-end accuracy) to support the consolidation claim.
- Mark version-sensitive Claude Code/Cursor numbers with dates and sources, or soften to 'as of a given release'.
- Clarify the visits.js footer addition separately; it is unrelated to the article thesis and may need privacy/performance review.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
