---
title: "让 Agent 真正自我进化：用 Simulation、Replay 与 Evaluation 构建进化实验室"
description: "自进化不是不断增加 Agent、Skill 或 Prompt，而是在相同任务集与资源预算下证明能力提升。通过真实轨迹采集、模拟探索、流量回放、独立评估、版本晋级与回滚，形成可复现、可比较、可治理的 Agent 进化闭环。"
date: 2026-11-15
type: Articles
tags:
  - Agent
  - Self-Evolving Agent
  - Simulation
  - Replay
  - Evaluation
  - Evolution Lab
  - Agent Runtime
---

# 让 Agent 真正自我进化：用 Simulation、Replay 与 Evaluation 构建进化实验室

Agent 能力不断增加，不等于 Agent 正在进化。新增一个 Skill、切换一个模型、把单 Agent 改成 Multi-Agent，都只是发生了变化。只有当新版本在可比较的任务集合与资源预算下，持续取得更好的结果，并且没有引入不可接受的回归，才有理由称之为进化。

因此，自进化系统不能只让模型反思“哪里做得不好”，再让它自由修改 Prompt。它需要一套类似科学实验室的工程设施：从真实任务中采集经验，在隔离环境中探索候选策略，用历史流量和新生成场景进行验证，由独立评估器判断是否晋级，最后通过灰度发布与回滚控制风险。

> 自进化的核心不是让 Agent 不断变复杂，而是让它在相同任务集、相同资源预算和明确安全边界下，证明自己变得更好。

## 一、先定义什么叫“进化成功”

假设 V1 能完成一组订单分析任务。后来系统产生 V2：它增加了一个 Skill，调整了 Plan，并更换了部分工具调用策略。V2 的成功率从 80% 提升到 88%，但 Token 消耗增加 70%，平均延迟翻倍，而且数据分析类任务出现回归。它究竟是不是更好的版本？

答案不能只由单一成功率决定。我们需要先定义比较协议：

- **相同任务集：**基线版本和候选版本面对同一组任务，按任务类型分层统计，避免只在擅长的样本上获胜。
- **相同资源预算：**限制 Token、模型调用、工具调用、并发、执行时间和 Sandbox 配额。
- **相同验收标准：**任务成功、结果质量、业务不变量和安全要求必须使用同一套定义。
- **可解释的差异：**记录候选版本究竟改变了 Prompt、Bias、Plan、Skill、Tool Route，还是 Agent 拓扑。

评估目标适合采用“硬门槛 + 多目标优化”，而不是把所有指标简单加权成一个分数。权限、安全、资金正确性和关键业务不变量是硬门槛；通过门槛后，再比较任务质量、成本、延迟和稳定性。不能用更低的 Token 成本抵消一次越权，也不能用总体成功率掩盖关键任务类别的严重退化。

```text
进化判定
  1. 安全与业务不变量：必须通过
  2. 关键任务回归：不得超过容忍阈值
  3. 任务质量：达到目标或显著改善
  4. 资源预算：不超过约束
  5. 稳定性：多轮运行结果可接受
```

## 二、Evolution Lab：把自进化变成一套实验系统

我倾向于把这套能力称为 **Evolution Lab（进化实验室）**。它不是线上 Agent Runtime 的一部分执行逻辑，而是负责管理 Agent 能力变化的控制系统。线上 Runtime 负责完成业务任务；Evolution Lab 负责观察、提出候选、实验、评估和发布。

```text
                  Production Agent Runtime
                 真实任务 / Trace / Feedback
                            |
                            v
                     Experience Store
              任务快照 / 执行轨迹 / 失败案例
                            |
                            v
                  Evolution Orchestrator
             问题发现 / 实验调度 / 预算分配
                    +-------+--------+
                    v                v
             Strategy Generator  Scenario Generator
             候选策略生成          场景生成与扩展
                    +-------+--------+
                            v
                  Simulation + Sandbox
                     隔离探索与执行
                            |
                            v
                       Replay Engine
                   历史任务 / 环境重放
                            |
                            v
                    Evaluation Engine
                 质量 / 成本 / 安全 / 回归
                            |
                            v
                  Version & Promotion Gate
                  灰度发布 / 晋级 / 回滚
                            |
                            +------> Runtime
```

Simulation 负责寻找可能更好的路径；Replay 负责在可比较条件下重新执行；Evaluation 负责根据证据作出判断。提出方案的模型不应该同时成为唯一的裁判。

## 三、Simulation：主动探索新的解决路径

Replay 主要回答“新版本在已知任务上表现如何”，Simulation 则回答“是否存在我们还没有尝试过的解决方法”。Simulation 不应该只是把历史请求重新跑一遍，而应该是一个候选策略与场景的探索器。

### 1. Strategy Generator：生成候选策略

候选变更可以分层管理：

| 层级 | 变异对象 | 示例 |
|---|---|---|
| L1 参数与提示 | Prompt、Bias、模型参数 | 调整异常识别规则的表达、改变推理预算 |
| L2 能力组合 | Skill、Tool、知识与路由 | 新增订单分析 Skill，替换查询工具 |
| L3 执行策略 | Plan、重试、验证与委派 | 先查支付再查订单，增加独立 Verifier |
| L4 架构拓扑 | Agent 数量、角色与协作关系 | 单 Agent 改为订单 Agent、支付 Agent 与 Judge 协作 |

我建议采用 Strategy Mutation（策略变异）：从一个稳定版本出发，每次只修改一个主要变量，生成候选版本。这样实验结果才能归因。单变量实验找到有效改动后，再做组合实验，检查多个改动是否产生协同效应或相互抵消。

候选策略最好使用受约束的 Strategy DSL 表达，而不是允许模型任意改生产 Prompt、代码和工具权限。模型可以提出变更，DSL 描述变更，策略校验器检查允许的操作、资源预算和风险等级，Sandbox 才负责执行。

```text
CandidateStrategy
├── base_version
├── mutation_type
├── target
├── change_set
├── expected_effect
├── risk_level
├── resource_budget
└── rollback_to
```

### 2. Scenario Generator：主动生成测试场景

如果实验数据只有历史流量，系统很容易只学会处理过去出现过的问题。因此 Simulation 还需要主动扩展场景：

- **历史场景：**真实线上任务、典型成功路径和失败轨迹。
- **边界场景：**空数据、极值、并发、超时、重复请求、状态不一致。
- **对抗场景：**工具返回矛盾信息、上下文缺失、恶意输入、权限边界和异常依赖。
- **组合场景：**把多个已知故障组合起来，探索系统是否出现新的失效模式。

更重要的是 Failure-driven Exploration：让历史失败自动驱动下一轮场景生成。例如，曾经发生重复退款，系统就生成并发退款、超时后重试、重复事件投递、幂等键缺失等相关案例。新场景需要由规则、领域约束或人工抽样校验，避免生成器制造不真实、无法判定的测试数据。

### 3. Sandbox：保证探索不会污染真实世界

Simulation 的执行环境必须隔离。只读工具可以接测试环境；可写工具应使用 Mock、测试数据库或快照副本；发送消息、退款、转账、删除数据等外部副作用必须拦截或模拟。每个实验还需要独立身份、权限、网络边界、文件系统和资源配额。Agent 的探索自由度不能高于 Sandbox 的安全边界。

## 四、Replay：把真实经验变成可重复的实验样本

流量回放的价值不只是重发一次请求，而是让新旧版本在尽可能相同的条件下接受比较。采集对象应该是完整的任务轨迹，而不是只有 Request 和 Response。

```text
Task Trace
├── Task Goal / User Input
├── Context Snapshot
├── Memory & Knowledge Version
├── Prompt / Model / Parameters
├── Plan & State Transitions
├── Tool Calls & Tool Results
├── External Dependency Snapshot
├── Artifacts / State Changes
├── Final Output
└── Verification & User Feedback
```

轨迹记录需要同时考虑隐私和安全：敏感字段脱敏或令牌化，凭证不得进入回放数据集；对可写操作记录意图和结果，但回放时不重放真实副作用。每条样本还应带上来源、采集时间、任务类别、数据版本和适用范围。

### 三种回放模式

| 模式 | 执行方式 | 主要用途 |
|---|---|---|
| Deterministic Replay | 固定模型输出、工具结果和事件顺序 | 验证状态机、执行链路、重试与恢复逻辑 |
| Model Replay | 固定输入和上下文，重新调用模型 | 比较 Prompt、模型和策略变化 |
| Environment Replay | 在模拟环境中重新执行历史任务 | 验证新策略面对状态变化、故障和依赖波动时的表现 |

固定输入不代表模型输出确定。模型服务、采样、工具版本和外部环境都可能带来波动。因此 Model Replay 应多次运行，报告均值、方差、置信区间和失败分布；Deterministic Replay 则用于定位执行逻辑是否正确。三种模式不能混成一个“回放成功率”。

## 五、Evaluation：独立判断候选版本是否值得晋级

评估引擎应与策略生成器解耦。它至少要覆盖任务结果、过程质量、资源效率、稳定性和安全性。确定性指标优先使用代码和规则计算；开放式结果可以使用独立 Judge，但要保留评分依据，并用人工抽样校准 Judge 的偏差。

| 维度 | 关注指标 | 评估方式 |
|---|---|---|
| 任务质量 | 完成率、正确率、结果完整性 | 断言、业务验收、独立 Judge |
| 过程质量 | 工具选择、无效步骤、重试次数 | Trace 分析、规则检查 |
| 资源效率 | Token、成本、延迟、工具调用 | Runtime 指标 |
| 稳定性 | 多轮方差、超时率、失败分布 | 重复实验与分层统计 |
| 安全性 | 越权、危险副作用、约束违反 | 策略门禁、沙箱审计、测试 |

评估还要防止“基准刷分”。可以将数据集拆成探索集、验证集和保留测试集：探索集用于发现方向，验证集用于筛选候选，保留集尽量不参与策略生成，只用于最终晋级检查。线上新流量持续补充数据，但需要版本化，不能让候选方案反复针对同一批测试样本过拟合。

对于多目标指标，可以使用 Pareto 比较：如果某候选版本质量更高、成本不增加，通常更有吸引力；如果质量提升但成本显著增加，则需要明确业务预算和收益阈值，而不是用一个随意的综合分数掩盖取舍。

## 六、Evolution Orchestrator：决定何时进化、进化什么

进化调度器监听线上信号，识别值得研究的问题，并决定是否启动实验：

- 某类任务失败率持续升高；
- 用户反馈集中指向同一种结果缺陷；
- 线上出现新的任务类型或新的工具失败模式；
- 成本、延迟或资源消耗出现异常趋势；
- 现有策略在特定场景下长期需要人工介入。

调度器随后创建实验、分配预算、选择数据集、生成候选策略、安排回放与评估，并管理实验状态。它相当于进化系统的 Control Plane；Simulation 和 Replay 则是被调度的执行能力。

## 七、版本晋级与回滚：进化必须可撤销

候选版本通过离线实验，不代表可以直接成为生产版本。建议采用逐级晋级：

```text
Candidate
   ↓
Simulation Passed
   ↓
Replay Evaluation Passed
   ↓
Staging / Integration Test
   ↓
Canary Release
   ↓
Production
   ↓
Continuous Monitoring
```

灰度期间要持续观察真实任务成功率、关键业务指标、成本、延迟和安全事件。触发回归阈值时，自动停止扩量并回滚到上一稳定版本；高风险变更仍应要求人工审批。

回滚对象不能只有 Prompt。一个 Agent 版本应绑定完整的依赖清单：

```json
{
  "agent_version": "v2",
  "model_version": "model-01",
  "prompt_version": "prompt-02",
  "skill_versions": {"order_analysis": "v3"},
  "tool_registry_version": "tools-v5",
  "policy_version": "policy-v2",
  "knowledge_snapshot": "knowledge-v8",
  "evaluation_report": "eval-2026-001"
}
```

这样才能避免只回滚了 Prompt，却仍然使用新 Skill、新工具定义或新知识快照的“半回滚”状态。版本清单、实验数据、评估报告和发布记录应该能够互相追溯。

## 八、知识沉淀与策略进化要分开

一次实验通过，不意味着所有实验过程都应该写进知识库。建议区分两类资产：

- **Knowledge：**领域事实、工具说明、失败案例、经过验证的经验、适用范围和反例。它描述系统知道什么。
- **Policy / Strategy：**何时选择哪个工具、如何组织 Plan、何时重试、何时委派、何时请求人工审批。它描述系统如何行动。

知识可以为策略生成提供依据，但知识本身也要有来源、置信度、版本和有效范围。策略可以频繁实验，但只有通过评估的候选才进入稳定版本。失败轨迹可以进入经验库，却不能未经验证就升级为通用 Skill。

完整的进化循环是：真实任务产生经验，经验帮助发现问题，Simulation 探索候选策略，Replay 提供可比较证据，Evaluation 决定是否晋级，发布后的新结果再成为下一轮经验。

## 九、从小闭环开始：Evolution Lab 的落地路线

不建议一开始就做自动修改架构、自动创建 Multi-Agent 的完整系统。先选择一个任务边界清晰、结果可判定、风险可隔离的场景，例如订单异常分析或退款资格判断。

| 阶段 | 建设内容 | 验收目标 |
|---|---|---|
| MVP | Trace 采集、数据脱敏、固定工具结果、基线回放 | 同一批任务可稳定复现和比较 |
| 阶段二 | 候选 Prompt / Plan 变异、独立评估、资源预算 | 能证明一个局部策略变更是否有效 |
| 阶段三 | 失败驱动场景生成、Sandbox、环境回放 | 能发现历史流量未覆盖的边界问题 |
| 阶段四 | Skill / Tool Route 进化、灰度与自动回滚 | 形成从实验到生产的治理闭环 |
| 阶段五 | Agent 拓扑与协作策略实验 | 在明确收益和风险边界下验证架构级进化 |

第一阶段最重要的不是让系统自动产生很多候选，而是先保证“同一任务、同一环境、同一标准”能够被可靠比较。没有可信的测量，自动优化只会更快地放大错误。

## 十、开放问题：进化系统本身也需要被评估

- **探索边界：**Strategy DSL 应允许模型修改哪些对象？哪些变更必须人工审批？
- **实验归因：**如何处理模型非确定性、工具版本变化和多个变量之间的交互作用？
- **数据治理：**如何脱敏真实流量，同时保留回放所需的语义和状态？
- **评估可信度：**如何避免 Judge 偏差、合成场景失真和测试集过拟合？
- **资源经济性：**何时值得启动实验？探索成本是否低于预期收益？
- **架构进化：**什么证据足以支持从单 Agent 转为 Multi-Agent，而不是仅仅增加协作复杂度？

这些问题说明，自进化并不是一个“让模型自己改自己”的开关，而是一套有实验设计、有质量度量、有权限边界、有版本治理的工程体系。

> 真正的自进化，不是 Agent 学会了更多技能，而是它能够提出改变、验证改变、解释改变带来的收益，并在改变失败时安全地回到已知可靠的状态。

## 延伸阅读

- [从问题空间到解决空间：大模型时代的认知闭环与自我进化](https://chengguruchun.github.io/articles/problem-space-to-solution-space-agent-cognitive-loop.html) —— 从问题建模、语义保持和反馈修正理解 Agent 如何减少问题域到解决域的信息损耗。
- [从 Actor Model 到 Cognitive Actor：Claude Agent Teams 给 Agent Runtime 的启发](https://chengguruchun.github.io/articles/agent-runtime-cognitive-actor.html) —— 从执行实体、调度、监督和生命周期理解 Agent Runtime。
- [Agent 化会改变哪些软件工程定律？从 Harness 到架构反馈闭环](https://chengguruchun.github.io/diverse/agent-engineering-laws-harness-architecture-feedback.html) —— 从架构反馈与 Runtime 优化的角度延伸自进化系统。
