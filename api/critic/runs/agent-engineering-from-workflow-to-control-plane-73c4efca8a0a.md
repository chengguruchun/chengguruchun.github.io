## 🤖 Critic Lab Report

Article: `articles/agent-engineering-from-workflow-to-control-plane.html`
Commit: `73c4efca8a0a0ad53c5d51d2dd94247d9f170f29`
Model: `deepseek-chat`
Status: **needs_review**

这篇稿子更像一张方向性的路线图，并未构成严密论证：把 Workflow、Graph、Loop、Harness、Gateway、Control Plane 这几层并列、逐层叠加的叙事有启发，但其中几处关键跳跃没有论证——尤其是「Agent 真正改变的是控制方式」「Tool Gateway 是能力的统一治理层」「Control Plane 会自然出现」这三条，更像是设计直觉而非已验证结论。此外，全文的核心追问（语义性的 Goal 如何判定完成）恰恰暴露了整条路线的最大漏洞：Control Plane 的说法在完成判定不可靠时会让系统带上危险的一厢情愿。本次 diff 只是资源版本号变化，无内容层面的引入。

## 1. Logic

- **HIGH** — 「真正属于 Agent 特性的，是 Loop」
  - Issue: 这是一个排他性断言，但文章没有论证 Graph、Harness 不是 Agent 特性。Graph 处理多步依赖、Harness 处理长周期生命周期，都可能是 Agent 区别于传统 Workflow 的关键特性。文章先并列四层，随后单点抬高 Loop，中间缺少为何 Loop 更「本质」的论证。
  - Why it matters: 若把 Loop 定为本质，读者会低估 Harness（状态、恢复、权限、可观测）与 Graph（结构约束、可验证节点）的工程价值，这与其后文中自己对语义性完成判定的担忧相互矛盾。
  - Test / fix: 给出一个可区分测试：一个只有 Graph+Harness、没有开放 Loop 的系统（如 DAG 上的条件重试），它是否仍是 Agent？如果答案是「是」，则 Loop 不是唯一特性，应改为「Loop 是 Agent 区别于传统 Workflow 的主要特征之一」。

- **HIGH** — 「HTTP 200 / Tool Call PASS / Workflow SUCCESS ≠ 目标真的完成，所以 Actual State 不能只记录执行状态」
  - Issue: 文章正确指出语义性完成是难点，但随后仍把 Control Plane 的 Reconcile 类比直接搬到 Agent 上，未说明在完成判定不可靠时 Reconcile 循环如何终止或如何避免震荡。K8s 的 Reconcile 依赖确定性、可观测的 status 字段；Agent 的 status 本身需要被判定，这是循环内的另一个循环。
  - Why it matters: 这是整篇文章最关键、也最没被解决的点。如果 Goal 完成判定由 LLM 给出，Control Plane 的「收敛」就建立在不可靠的观测上，可能无限重试、过早宣布成功或反复回滚，这比没有 Control Plane 更危险。
  - Test / fix: 把「完成判定」列为 Control Plane 的一等组件，并给出工程方案：多重校验（Proxy Metric + Real Outcome，与本站 agent-evaluation 一文呼应）、人工确认门、预算/步数上限、幂等 action 与可回滚。用一个具体反例测试：若 10 次 action 后 Judge 仍判「未完成」，Control Plane 应如何处理？文章没有答案。

- **MEDIUM** — 「当 Agent 数量、任务数量和能力数量不断增加以后，系统会自然出现更高一层的问题」→ 推出 Control Plane
  - Issue: 「自然出现」是模糊的因果主张。规模增长会带来协调成本，但不必然导致集中式 Control Plane；也可能通过协议、契约、去中心化的 Agent 间协商或现有编排层（如 Temporal、队列、事件总线）解决。文章把「问题存在」等同为「必然收敛到单一控制面」。
  - Why it matters: 这是全文最像「把工程直觉当规律」的地方。集中式 Control Plane 本身引入单点、状态存储、多租户隔离与权限扩散问题，这些在文中未被讨论。
  - Test / fix: 应改为假设句：「在 X 类场景下，集中式 Control Plane 可能优于去中心化协调」，并列出可观察条件（如需要全局任务状态、跨 Agent 权限统一、审计要求）。给出一个反例场景说明何时不需要 Control Plane。

- **MEDIUM** — 「Tool Gateway 开始暴露 Agent 可理解、可治理的能力」
  - Issue: Capability Discovery、Tool Schema、Tenant、Permission、Routing、Observability 被平铺为「已讨论的核心问题」，但没有区分「能力发现（Agent 理解层面）」与「租户/权限/路由（运行时与安全层面）」。这些是不同层次的关注点，混在一层里会让 Gateway 变成什么都装的桶。
  - Why it matters: 若 Gateway 同时承担 schema 描述、授权、路由、审计，改动任何一层的风险都会外溢，且与 Control Plane 的职责重叠（Control Plane 也声称管权限与任务下发）。职责边界不清是这类架构最容易被批评的地方。
  - Test / fix: 显式画出三层：描述层（schema/capability）、策略层（tenant/permission/risk）、执行层（routing/observability）。并回答：授权决策归 Gateway 还是 Control Plane？二者冲突时谁优先？

- **MEDIUM** — 「Kubernetes 真正值得借鉴的是 Reconcile 思想」
  - Issue: 文章主动否认 Pod/Deployment 一一对应（这点可取），但 Reconcile 类比省略了 K8s 成立的前提：状态可由机器直接判定、控制器幂等、期望状态可声明。Agent 的 Goal 既非完全可声明也非完全可判定。类比被借用为修辞，而非被检验的假设。
  - Why it matters: 直接照搬 Reconcile 会掩盖 Agent 系统需要「判定器 + 预算 + 人工闸门」这一额外基础设施。
  - Test / fix: 列出 K8s Reconcile 成立的三个前提，逐条对照 Agent 场景哪些成立、哪些缺失，并把缺失项列为必须补齐的工程组件。

## 2. Counterexamples

- **HIGH** — Thesis: Loop 是 Agent 的本质特征，系统应围绕持续观察—调整构建
  - Counterexample: 客服问答、代码补全、单轮检索生成等高度确定的任务：一旦引入开放 Loop，反而增加延迟、成本与不确定性，且质量不如固定 Workflow。大量被部署的「Agent 产品」实际是固定 Graph 或单次调用。
  - Boundary: 对于路径确定、结果可机械判定的任务，Workflow/Graph 应作为默认，Loop 仅在目标语义化且可观测反馈存在时启用。

- **HIGH** — Thesis: Control Plane 会在规模扩大后自然出现并负责协调
  - Counterexample: 大规模多 Agent 系统也可用事件驱动、去中心化协商（如本站 gossip/consensus 一文讨论的集体认知）或现有工作流引擎（Temporal 类）协调，无需单一控制面；且当完成判定不可靠时，集中式 Reconcile 会放大错误决策（全局误判完成或全局重试风暴）。
  - Boundary: 当跨任务全局状态、统一审计、统一权限是硬需求时，Control Plane 更合理；当任务局部自洽、失败可隔离时，去中心化或分层协调可能更稳。

- **MEDIUM** — Thesis: Tool Gateway 应成为 Agent 与已有服务之间的统一能力层
  - Counterexample: 内部工具数量少、团队单一时，一个薄适配层或直接 Function Calling 即可；引入 Gateway 反而增加一跳延迟与部署负担。能力爆炸（数百个 Tool）时，若 Gateway 只做路由不做剪枝，Agent 的 Tool 选择准确率会下降，Gateway 反而放大了「Tool 过多」问题（见本站技能剪枝一文）。
  - Boundary: Gateway 的价值在能力多、多租户、需审计与权限隔离时成立；工具少时收益递减，能力多时必须配套检索/剪枝而非只做目录。

## 3. Novelty

- **common_combination** — 把 Workflow、Graph、Loop、Harness、Tool Gateway、Control Plane 串成一条从「调用函数」到「管理目标」的演进线
  - Basis: 各层概念在业界与本站多篇文章（ReAct 与 Harness、K8s×Agent、IoT Agent 等）中已分别出现；本篇的贡献是把它们排列成一条叙事，而非提出新机制。此为初步判断，未做外部检索。

- **established** — 用 K8s Reconcile 类比 Agent 的目标收敛
  - Basis: 控制循环/期望状态与现状对比是 K8s 既有核心思想，且与本站 k8s-to-agent-control-plane 一文重叠；类比本身常见。

- **potentially_distinctive** — 「Agent 化是让原软件变成 Agent 可工作的环境」而非重写
  - Basis: 该表述与「Agent-native 重写」的主流叙事相反，把重点放在既有系统的可工作性上，可能具有组合性价值；但其价值取决于能否给出可操作判据（什么算「可工作的环境」），目前仅停留在口号。

- **potentially_distinctive** — 语义性 Goal 的完成判定是 Agent 系统的核心未解问题
  - Basis: 作为全文收尾问题提出，方向对；但与本站 agent-evaluation-proxy-vs-real-outcome 一文明显重叠，需要说明增量。

## 4. Facts

- **MEDIUM** — 发表 2026-09-04 / 更新 2026-09-08
  - Why verify: 未来日期，可能是排版占位或时区/模板错误，影响读者对时效性的信任。
  - Preferred source: `official`

- **LOW** — 本次 diff 仅改 article-actions.js 版本号 v=20261023-3
  - Why verify: 版本号内含未来日期，需确认是否为缓存键约定而非笔误；不影响正文但影响可维护性。
  - Preferred source: `primary`

- **LOW** — OpenAPI 暴露程序可调用能力、Tool Gateway 暴露 Agent 可理解能力
  - Why verify: 属定性对比，非数值；但若作为论点，应对照具体 schema/协议（如 MCP 类工具描述约定）说明差异，否则易被视为空泛二分。
  - Preferred source: `multiple_independent`

## 5. Missing Points

- **HIGH** — 完成判定（Judge）的工程实现与失败模式
  - Why it matters: 全文自己提出这是核心未解问题，却未给出任何机制；不补这一点，Control Plane 的整条叙事在逻辑上是悬空的。

- **HIGH** — Control Plane 与 Tool Gateway 的职责边界及权限冲突仲裁
  - Why it matters: 两者都声称管任务、授权与状态，若不划清，实现时会出现双重鉴权、状态不一致、审计归属不明。

- **HIGH** — 成本、延迟与步数预算（budget/termination）
  - Why it matters: Loop 与 Reconcile 默认持续运行，没有预算与上限的循环在工程上不可部署；K8s 类比掩盖了 Agent 每步都有真实成本这一点。

- **MEDIUM** — 幂等性、回滚与副作用隔离
  - Why it matters: IoT 与制造业场景中 Action 改变真实世界，失败重试可能造成物理损失；Control Plane 若不做幂等与补偿设计，Reconcile 会变成危险的重试器。

- **MEDIUM** — 关于「Domain Object × Action = Tool」的定位（用户在评审关注点中特别提出）
  - Why it matters: 本文未直接讨论该式，但 Tool Gateway 层的刻画实际依赖它。应区分：这是建模定义（域对象上加动作生成工具）、工程启发式（有助于 schema 组织与发现），还是普适主张（所有工具都必须如此）。若为普适主张，需回应参数膨胀问题——同一域对象上的多个动作常共享参数前缀，合并成一个大工具会导致参数组合爆炸与选择歧义；若为启发式，则应说明何时拆分为原子工具更优。

- **MEDIUM** — 区分「域边界」与「运行时/风险/验证边界」（用户评审关注点）
  - Why it matters: 文章把 Capability Discovery、Tenant、Permission、Routing、Observability 并为一层，实际混入了三种不同边界：领域能力边界、运行时执行边界、风险与合规边界。验证往往属于风险边界而非域边界（如支付动作需额外审批而不改变域定义）。不区分会导致按域切分工具时漏掉跨域的风险校验。

- **LOW** — 多 Agent 协作失败模式（共识、冲突、回滚）
  - Why it matters: 文中「多个 Agent 怎么协作」仅列为一问，未展开；本站已有 gossip/consensus 文章可衔接，但需说明 Control Plane 与协商式协作的分工。

## 6. Recommended Changes

- 把「真正属于 Agent 特性的是 Loop」改为可证伪的假设，并补一个「只有 Graph+Harness、无开放 Loop 也属 Agent」的判定测试。
- 将「完成判定」提升为 Control Plane 的一等组件，给出多重校验、预算上限、人工闸门、幂等与回滚的具体设计，回应文中自己提出的语义性完成问题。
- 把「规模扩大后自然出现 Control Plane」改写为条件性主张，列出何时需要集中控制面、何时去中心化或复用现有编排更优，并承认其单点与权限扩散代价。
- 显式区分三层职责：能力描述层（Tool Gateway）、运行时控制层（Control Plane）、风险/验证层；明确授权与审计归谁，冲突时如何仲裁。
- 单独补一节讨论「Domain Object × Action = Tool」的定位：注明是定义、启发式还是普适主张，并分析工具合并导致的参数膨胀与选择歧义，给出拆分判据。
- 明确区分域边界（业务能力划分）与运行时/风险/验证边界（执行、权限、审批、可观测），说明验证通常跨越域边界，不能仅按域切分工具。
- 核对文首发表/更新时间与脚本版本号中的未来日期，避免时间敏感信息损害可信度；如为占位请标注。
- 在收尾处标注哪些是待验证假设（如 Control Plane 的必要性、Gateway 作为统一层），与本站 agent-evaluation、k8s×agent、技能剪枝等文交叉引用并说明本文增量。

Evidence level: `E1`

> Critic Lab is advisory. It does not modify the article or decide whether a finding should be accepted.
