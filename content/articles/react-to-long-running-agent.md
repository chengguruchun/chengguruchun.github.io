---
id: react-to-long-running-agent
type: Articles
title: 从 ReAct 到 Long-Running Agent：Harness 为什么开始成为 Agent 的第二增长曲线
date: 2026-09-28
thought_date: 2026-09-28
published_date: 2026-09-28
tags: [Agent, ReAct, Harness, Runtime, Long-Running Agent]
excerpt: ReAct 解决一步怎么走，Harness 让 Agent 能走很远，Runtime 让 Agent 能活很久。重新理解 2025 年以后长周期 Agent 的能力演进。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/react-to-long-running-agent.md
last_verified: 2026-09-28
cadence_days: 90
---

# 从 ReAct 到 Long-Running Agent：Harness 为什么开始成为 Agent 的第二增长曲线

这篇文章来自我最近对 ReAct、长周期 Agent、Harness 和 Agent Runtime 的连续讨论。一个越来越清晰的判断是：当任务从几分钟走向几小时、几天甚至更长时间以后，Agent 的问题已经不只是“模型够不够聪明”，而开始变成一个系统工程问题。

## 一、ReAct 解决的是“下一步做什么”

经典 ReAct 的核心非常简单：

```text
Thought
  ↓
Action
  ↓
Observation
  ↓
Thought
  ↓
Action
  ↓
Observation
  ↓
...
```

它解决的是一个局部决策问题：

```text
f(Context, Observation) → Next Action
```

也就是：**根据当前看到的世界，决定下一步做什么。**

例如，一个 Code Agent 读取项目、修改代码、运行测试、观察错误，再决定下一步修什么。这个循环已经足以让 LLM 从“生成答案”进入“行动”。

但 ReAct 有一个天然边界：它关注的是**当前循环**，而不是一个任务跨越几十、几百甚至几千次行动之后，系统还能不能持续保持正确的状态。

## 二、长周期 Agent 的问题不是“下一步”，而是“我现在在哪里”

假设一个 Agent 要花三天把一个老系统迁移到新的技术栈。

```text
Day 1
├─ 分析项目
├─ 修改依赖
├─ 修改 API
├─ 编译
└─ checkpoint

Day 2
├─ 恢复状态
├─ 继续 migration
├─ 测试
├─ 发现 23 个 failure
└─ checkpoint

Day 3
├─ 恢复
├─ 修剩余问题
├─ regression test
└─ verification
```

这里 ReAct 依然存在，但它只负责每一轮：

```text
Observation → Action
```

真正困难的是：

```text
昨天做到哪里？
哪些已经完成？
哪些失败过？
当前目标是什么？
哪些结果已经验证？
如果进程挂了怎么恢复？
如果 context 用完了怎么继续？
如果任务暂停两天，回来之后还能不能接上？
```

这已经从 **Action Loop** 变成了 **Task Lifecycle**。

## 三、所以 ReAct 与 Long-Running Agent 不是竞争关系

我更倾向于把它们理解成两层循环。

```text
Long-Running Agent
        │
        ├── Harness / Runtime
        │       │
        │       ├── Planning
        │       ├── State
        │       ├── Checkpoint
        │       ├── Verification
        │       ├── Recovery
        │       └── Context Management
        │
        └── ReAct Loop
                │
                ├── Reason
                ├── Act
                └── Observe
```

**ReAct 是内循环，Long-Running Runtime 是外循环。**

一个更简洁的表达是：

**ReAct 让 Agent 会“走一步”；Harness 让 Agent 能“走很远”；Runtime 让 Agent 能“活很久”。**

## 四、为什么 2025 年以后 Harness 开始变得重要

长周期 Agent 的实践开始暴露一个事实：单纯增加 context window，并不能自动得到可靠的长周期能力。

Anthropic 在 2025 年关于 long-running agents 的工程实践中，把问题拆成 initializer、增量执行、结构化 artifacts 和跨 session 的 context handoff；其核心目标正是让不同 session 的 Agent 能像“接班的工程师”一样继续工作。urlAnthropic：Effective harnesses for long-running agentshttps://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

到 2026 年，Anthropic 又进一步尝试 context reset、planner / generator / evaluator 等结构。一个重要观察是：当任务足够长时，**如何组织 Agent 的工作过程，本身就会显著影响最终结果**。urlAnthropic：Harness design for long-running application developmenthttps://www.anthropic.com/engineering/harness-design-long-running-apps

这就是我所说的 Harness 开始成为 Agent 的“第二增长曲线”：模型能力仍然重要，但系统如何把模型能力转化成持续、可验证、可恢复的任务执行能力，也开始成为独立的工程变量。

## 五、Harness 到底在补什么？

可以把它拆成几个很具体的能力。

问题Harness / Runtime 的对应能力
任务太长任务拆解、sprint、阶段性目标
Context 太大compaction、reset、structured handoff
不知道做到哪里State、progress、artifact
进程挂掉Checkpoint、Resume、Retry
模型说“完成了”Verification、Evaluator、Evidence
需要等待人Human-in-the-loop、Interrupt / Resume
任务跨越很长时间Durable Execution、Scheduler、Wake-up
执行有风险Sandbox、Guardrail、Policy
线上出了问题Tracing、Replay、Observability

这时可以看到，Harness 已经不只是一个 prompt wrapper。

## 六、Context Window ≠ Long-Horizon Capability

这是我觉得非常值得强调的一点。

```text
1M Context
   ≠
1M tokens 的有效工作记忆
   ≠
Long-Horizon Capability
```

原因很简单：长任务不是单纯把历史全部保存下来，而是要知道**什么状态值得保存、什么时候应该切换上下文、下一次 Agent 应该看到什么**。

因此一种更合理的模式是：

```text
ReAct
 ↓
Artifact / State
 ↓
Checkpoint
 ↓
Context Reset
 ↓
重新加载任务状态
 ↓
新的 ReAct
```

这和传统意义上的“一个 Agent 一直活着”很不一样。长周期 Agent 更像是：**Agent 可以不断更换，但任务状态必须连续。**

## 七、Verification：从“我做了”到“结果真的对了”

长任务还有一个问题：Agent 自己判断“完成”通常不够。

```text
LLM
 ↓
Action
 ↓
Environment
 ↓
Verification
 ↓
Evidence
 ↓
State Update
```

因此长周期 Agent 越来越需要独立的 evaluator、测试、真实环境反馈和结果证据。

这也解释了为什么 Code Agent 是一个很好的实验场：编译、测试、运行结果、Git diff 都可以形成比较明确的反馈。但在企业任务里，真正困难的是把“完成”定义成可验证的真实结果，而不是 Tool Call 成功。

## 八、Runtime 与 Harness 开始分层

随着系统走向生产，我越来越倾向于区分两个概念。

```text
Harness
├── Prompt
├── Tools
├── Skills
├── Agent Loop
├── Task Strategy
└── Domain-specific scaffolding

Runtime
├── Durable Execution
├── State / Checkpoint
├── Memory
├── Scheduling
├── HITL
├── Multi-tenancy
├── Auth / Policy
├── Sandbox
└── Observability
```

这个区分也正在出现在生产 Agent 基础设施的实践中。LangChain 在 2026 年对生产 Deep Agents 的总结中明确区分了 Harness 与 Runtime：Harness 负责 prompt、tools、skills 以及围绕模型的工作循环；Runtime 则负责 durable execution、memory、human-in-the-loop、observability、sandbox、scheduled jobs 等生产基础设施。urlLangChain：The Runtime Behind Production Deep Agentshttps://www.langchain.com/blog/runtime-behind-production-deep-agents

于是可以得到一个我比较喜欢的抽象：

```text
LLM
 ↓
Agent / ReAct
 ↓
Harness
 ↓
Runtime
 ↓
Environment
```

## 九、从 Action Loop 走向 State Loop

ReAct 的核心是：

```text
Reason → Act → Observe
```

长周期 Agent 的核心则逐渐变成：

```text
Goal
 ↓
State
 ↓
Plan
 ↓
Action
 ↓
Observation
 ↓
Verification
 ↓
State Update
 ↓
Checkpoint
 ↺
```

所以我会把这个变化称为：

**从 Action Loop 走向 State Loop。**

前者关心下一步行动；后者关心整个任务状态如何随着行动、环境反馈和验证结果持续演化。

## 十、再往前一步：Agent Runtime 开始像一个“操作系统”

如果 Agent 只有一次调用，那么 Runtime 很薄；如果 Agent 需要运行几天，甚至长期运行，那么 Runtime 就开始承担类似操作系统的职责：

```text
Process      → Agent
Scheduler    → Task / Wake-up
Memory       → State / Context
Filesystem   → Workspace / Artifact
Device       → Tool / External System
Isolation    → Sandbox
Supervisor   → Retry / Recovery / Policy
Observability→ Trace / Event / Evaluation
```

这也是为什么我之前一直觉得 Kubernetes、Actor Model、Agent Runtime 之间存在值得研究的结构性联系：它们并不是功能一一对应，而是在解决一个共同的问题——**如何让一个持续运行的计算实体，在复杂环境中保持状态、接受调度、处理失败，并不断趋向目标。**

## 十一、我对 Agent 能力演进的一个阶段性判断

如果把近几年的变化放在一起，我会这样描述：

```text
2023
LLM
 ↓
Prompt Engineering

2024
LLM
 ↓
Context Engineering

2025
LLM
 ↓
Tool Use
 ↓
ReAct / Agent Loop
 ↓
Harness Engineering

2026
LLM × Agent × Harness × Runtime × Environment
 ↓
Long-Running Agent
```

这不是说 Prompt、Context 或 ReAct 不重要，而是它们开始成为更大系统中的一层。

真正值得继续研究的问题变成：

```text
模型如何思考？
Agent 如何行动？
Harness 如何组织行动？
Runtime 如何保证行动持续？
Environment 如何提供真实反馈？
Verification 如何判断目标是否真的完成？
```

## 十二、最后：长周期 Agent 的核心，不是“让一个 Agent 活得更久”

我越来越觉得，这是一个容易被误解的问题。

长周期 Agent 并不一定意味着：

```text
让同一个 Agent
一直占着一个 Context
一直运行下去。
```

更合理的抽象可能是：

```text
让任务活得更久，
而不是让某一个 Context 活得更久。
```

Agent 可以重新启动，Context 可以被 reset，模型甚至可以更换；只要：

```text
Goal 不丢
State 不丢
Evidence 不丢
Checkpoint 不丢
Environment 状态可恢复
Verification 持续存在
```

那么任务就可以继续。

所以最后我想留下三个句子：

**ReAct 让 Agent 会走一步。**
**Harness 让 Agent 能走很远。**
**Runtime 让 Agent 能活很久。**

而真正的 Long-Running Agent，可能不是一个更大的 ReAct Loop，而是一个围绕 **State、Feedback、Verification 和 Recovery** 构建起来的持续计算系统。

## 参考

- [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

- [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

- [LangChain — The Runtime Behind Production Deep Agents](https://www.langchain.com/blog/runtime-behind-production-deep-agents)
