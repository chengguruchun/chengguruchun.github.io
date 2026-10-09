## 🤖 Critic Lab Report

Article: `articles/frontend-language-for-ai-assisted-development.html`
Commit: `9e4db1edb4f9b9c51e68c0d77a8244b0d365c66c`
Model: `deepseek-chat`
Status: **needs_review**

This is a solid, checklist-style terminology primer for AI-assisted frontend/full-stack work; the diff is a harmless heading renumber, but the article contains several boundary conflations (domain vs runtime/risk/verification), a few absolute claims ('lockfile is required', 'build success ≠ correct'), and unlabeled hypotheses about term-based compression reducing ambiguity. The article does not actually defend a 'Domain Object × Action = Tool' thesis here; if that framing is imported from elsewhere, its definitional vs. heuristic vs. universal status must be made explicit.

## 1. Logic

- **HIGH** — 前端术语是一套压缩歧义的工程语言
  - Issue: Terminology reduces ambiguity only when receiver and sender share the same operational semantics; the article treats naming (Modal vs Drawer) as if terms alone carry sufficient semantics. In practice a term is a pointer to a family of behaviors, not a specification.
  - Why it matters: If a reader treats vocabulary as sufficient specification, the result is the same failure mode the article warns about: the AI still fills in the gaps (which Modal implementation, focus trap, escape behavior, body scroll lock).
  - Test / fix: Test: give an AI only '用 Drawer 展示编辑' with no props/state/handlers and compare its output to the article's full eight-dimension spec. If the term-only version still requires most of the same clarifications, the claim overstates the compression.

- **HIGH** — The article's dimension table conflates domain boundaries with runtime/risk/verification boundaries (权限, 加载/错误状态, 验收, 回滚 are grouped as page-level '交互与状态' or '验收标准').
  - Issue: Authorization, secret handling, cache invalidation, and rollback are runtime/risk/verification concerns, not page-domain concerns. Listing them under 'the page says it' blurs who owns the boundary.
  - Why it matters: An AI agent given the table may treat permission checks and secret placement as frontend tasks, which is exactly the mistake the article elsewhere warns against ('只在前端隐藏按钮不构成真正的权限保护').
  - Test / fix: Split the table into (a) domain/UI contract (structure, layout, interactions, data shape) and (b) runtime/risk/verification contract (auth, secrets, environments, rollback, cache). Each row should name an owner (frontend / backend / infra / platform) and a verification method.

- **MEDIUM** — “安装冲突不应一律用强制参数压掉。”
  - Issue: Presented as an unconditional rule without the counter-case where a peer conflict is genuinely a benign annotation-only mismatch (common in tooling chains) and forced install is the pragmatic path.
  - Why it matters: Teams sometimes waste days on resolution when a documented override plus a pin would be correct. The rule as written suppresses a legitimate heuristic.
  - Test / fix: Add the qualifier: 'unless the conflict is annotation-only and both majors are known compatible; then record the override in the lockfile with a comment.'

- **MEDIUM** — “页面在本机能打开，只证明局部开发环境里的结果，不代表生产环境可用。”
  - Issue: True but too strong as a general rule: for purely static single-file pages with no env vars, this assertion is technically correct but pragmatically misleading because the article never gives the threshold where 'runs locally' does become sufficient evidence.
  - Why it matters: Without a threshold, readers can either dismiss the warning as boilerplate or over-invest in CI for a one-off page.
  - Test / fix: Add a decision rule: e.g., 'if the page reads env vars, secrets, remote APIs, or writes to persistent state, local success is not evidence; otherwise it is a weak but non-zero signal.'

- **LOW** — “术语提供相对稳定的概念边界。”
  - Issue: Conceptual boundaries of terms are not actually stable across ecosystems (Modal in various libraries has different a11y guarantees; Drawer semantics differ between MUI, Ant, and headless UI).
  - Why it matters: The compression value assumed by the article depends on this stability.
  - Test / fix: Either qualify ('stable within a project or design system') or provide one cross-framework counter-example.

## 2. Counterexamples

- **HIGH** — Thesis: Names of components (Modal vs Drawer vs Popover) carry enough semantics for AI to implement correctly.
  - Counterexample: In MUI, Drawer can be a modal with focus trap; in Headless UI, Dialog and Popover are different primitives with different escape/focus semantics. Selecting a name does not determine behavior; props and state do.
  - Boundary: Framework/library-agnostic naming only holds when a design system fixes behavior per name. Outside that, the terminology claim under-specifies.

- **HIGH** — Thesis: Lockfile is the source of truth and should not be deleted to resolve conflicts.
  - Counterexample: Post-major-version migration, lockfiles can carry transitive pins that block required security patches; a deliberate regenerate + review of the diff is the standard remediation. Keeping the old lockfile in this case is the risk.
  - Boundary: The rule holds for routine installs; it does not hold during a planned dependency-tree migration where the lockfile itself is the artifact under change.

- **MEDIUM** — Thesis: '所有操作可实际使用' is a valid acceptance criterion.
  - Counterexample: In a mock-data-only build, 'all operations usable' can be satisfied by a mock server while real endpoints return 500. The criterion is satisfiable without proving the integration.
  - Boundary: Acceptance must distinguish mock-level behavior from end-to-end behavior with a real backend.

- **MEDIUM** — Thesis: 术语澄清 reduces ambiguity enough that AI can '制定计划'.
  - Counterexample: For domain-specific rules (e.g., 'editing user status must log to audit and trigger downstream recompute'), no frontend term captures the rule; the ambiguity is domain-level, not vocabulary-level.
  - Boundary: The terminology approach caps out at UI/engineering vocabulary and cannot cover business-rule ambiguity.

## 3. Novelty

- **common_combination** — Treating frontend terminology as a compression interface between humans and AI for spec-writing.
  - Basis: Spec-driven development, prompt engineering with structured output, and design-token/design-system practices already overlap heavily with this idea. The specific packaging as a Mandarin terminology handbook for full-stack AI-assisted development is a useful practical synthesis, but it is not a new mechanism from the text alone.

- **established** — Structuring AI requirements into 目标 / 约束 / 状态 / 验收 dimensions.
  - Basis: Common in requirements engineering, RFC templates, and structured prompt frameworks. The article presents it clearly but does not add a distinct mechanism.

- **potentially_distinctive** — The article's stance that vocabulary is more valuable than memorizing APIs.
  - Basis: As a prioritization heuristic for AI-assisted dev it is worth defending, but originality cannot be verified without scanning comparable material; also, this is a curriculum opinion, not a technical thesis.

- **unknown** — Implicit 'Domain Object × Action = Tool' framing (implied by the reviewer prompt; not stated in this article).
  - Basis: The article text does not define this. If it is imported from another piece, its status as definition vs. heuristic vs. universal claim is unverifiable from this file.

## 4. Facts

- **MEDIUM** — SemVer 的 MAJOR.MINOR.PATCH 分别对应不兼容变化、兼容功能增加和兼容修复。
  - Why verify: SemVer 2.0.0 defines this formally but ecosystem behavior (especially 0.x) diverges; ^1.2.3 behavior differs across npm, pnpm, and Yarn for pre-1.0 versions.
  - Preferred source: `primary`

- **HIGH** — 前端构建工具中的环境变量通常会被编译进公开资源，因此 Secret 不能放在前端变量里。
  - Why verify: True for Vite / CRA / Next.js client-side vars, but the rule has framework-specific exceptions (server-only env in Next.js server components, Cloudflare workers, etc.). Blanket statement risks over-generalization.
  - Preferred source: `official`

- **MEDIUM** — Tree Shaking：在静态分析可行时移除未使用的导出代码。
  - Why verify: Effectiveness depends heavily on module format, side-effect annotations in package.json, and the bundler. The 'when static analysis allows' clause is correct but the practical limitations differ across Vite/esbuild/webpack/Rollup.
  - Preferred source: `official`

- **LOW** — Package Manager 例如 npm、pnpm、Yarn.
  - Why verify: Fine, but the list omits Bun and Deno; version-sensitive.
  - Preferred source: `multiple_independent`

- **LOW** — 参考：CSDN · Dontla、MDN、React 文档、Vue 文档.
  - Why verify: CSDN blog as a primary reference is weak; readers cannot tell which points map to which source. Claim credibility suffers.
  - Preferred source: `primary`

- **LOW** — 发表 2026-10-09 作者 chengguruchun.
  - Why verify: Publication date appears to be in the future relative to typical review context. May be a typo or intentional.
  - Preferred source: `official`

## 5. Missing Points

- **HIGH** — No treatment of accessibility verification beyond a passing mention of Semantic HTML.
  - Why it matters: If 'good' pages are a core deliverable, keyboard navigation, focus management, ARIA roles, and screen-reader behavior are exactly the requirements AI most often skips and the ones users actually notice. It is also a verifiable acceptance dimension, which the article otherwise values highly.

- **HIGH** — No explicit separation of domain vs. runtime vs. risk vs. verification boundaries anywhere in the requirements template.
  - Why it matters: This is the strongest conceptual gap: permissions, secrets, errors, rollback, and cache invalidation are treated as page-level items. Without a boundary map, the AI agent will happily put a JWT in a frontend var and call a frontend-only permission check 'authorization'.

- **MEDIUM** — Parameter/state explosion when reusable components are consolidated (e.g., one DataTable that handles pagination, sorting, filtering, selection, and column config).
  - Why it matters: The article emphasizes 'component reuse' as an unqualified good, but reuse across divergent use cases drives prop bloat, boolean flags, and conditional rendering, which makes AI-generated code harder to verify, not easier.

- **MEDIUM** — Observability and error-contract for the frontend (e.g., where client errors surface, what a 4xx vs. 5xx should show, how errors attach to trace IDs).
  - Why it matters: 'Error State' is listed as a UI concept but not as an operational one. Production incidents often come from untyped error objects; a requirement template should specify the error contract.

- **MEDIUM** — Internationalization, timezone, and locale handling.
  - Why it matters: For 'user management' pages, timestamps, date filters, and numeric formatting are frequent sources of mismatch between human intent and model output. The example page in §11 uses 创建时间 without any locale/timezone constraint.

- **MEDIUM** — State management ownership boundary (server-state vs client-state) is named but not distinguished.
  - Why it matters: Whether pagination state lives in URL, React Query cache, or Redux changes what 'correct' means for back/refresh/deep-link. The article says 'URL 参数还原筛选条件' but does not connect it to a state-ownership rule.

- **LOW** — Explicit acknowledgement that the piece is an opinion/curriculum, not a validated method.
  - Why it matters: The prose reads as a normative handbook; readers may import it as a standard without knowing it is an evolving hypothesis. A one-line hedge would preserve the article's stance while reducing over-application.

## 6. Recommended Changes

- Add a two-column boundary map that separates (domain contract) from (runtime/risk/verification contract), and assign an owner and verification method to each row. This directly addresses the strongest logical weakness.
- Qualify the terminology-compression claim as a hypothesis: 'terms reduce but do not eliminate underspecification; behavior-bearing props and states remain required.' Add a one-line contrast example across two libraries (e.g., how a Dialog behaves differently in two React ecosystems).
- Reframe reusable components as having a cost: add a short note about prop explosion and when duplication is preferable to over-generalization (the 'rule of three' heuristic or similar).
- Add accessibility as a first-class acceptance dimension in §11, with concrete checks (keyboard path, focus visible, screen reader role).
- Soften the lockfile and force-install rules into 'default heuristic + documented exception' phrasing, including the dependency-migration case.
- Specify the error contract for the frontend: how 4xx vs. 5xx surface, whether errors carry trace IDs, and where user-facing strings come from.
- Explicitly label the 12-step pipeline and the requirements table as a proposed pattern, not a standard, and add a short 'when this fails' section to keep it an engineering heuristic.
- If the article is intended to defend 'Domain Object × Action = Tool', state it explicitly and classify it: definition, heuristic, or universal claim. Currently the file does not contain that thesis, so any connection from the reviewer prompt must be made by the author or dropped.

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
