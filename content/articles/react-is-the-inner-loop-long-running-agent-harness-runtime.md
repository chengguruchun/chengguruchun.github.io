---
id: react-is-the-inner-loop-long-running-agent-harness-runtime
type: Articles
title: ReAct 只是内循环：长周期 Agent 为什么开始需要 Harness 与 Runtime
date: 2026-09-28
thought_date: 2026-09-28
published_date: 2026-09-28
tags: [Agent, ReAct, Harness, Runtime, Long-Running Agent, Loop Engineering]
excerpt: 从 ReAct 出发，区分 Action Loop、Task Loop 与 System Loop，理解 2025 年以后长周期 Agent 为什么越来越依赖 Harness、Durable Execution、Checkpoint、Verification 与 Runtime。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/react-is-the-inner-loop-long-running-agent-harness-runtime.md
last_verified: 2026-09-28
cadence_days: 90
---

# ReAct 只是内循环：长周期 Agent 为什么开始需要 Harness 与 Runtime

我最近越来越倾向于把 Agent 的 Loop 分成不同层次：ReAct 是最底层的 Action Loop；Harness 开始承担 Task Loop；Runtime 则承担更长生命周期的 System Loop。这样看，2025 年以后 Agent 的进步就不只是模型变强，而是“模型 × Harness × Runtime × Environment”共同变强。

## 一、ReAct 解决的其实是一个很局部的问题

ReAct 的核心非常清楚：

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
  ↺
```

它回答的是一个非常重要的问题：

**“根据我现在看到的世界，我下一步应该做什么？”**

因此 ReAct 是一个 **Action Loop**。它让模型不再一次性生成最终答案，而是可以通过工具行动、获得环境反馈，再决定下一步。

例如一个 Code Agent 可以这样工作：

```text
读取 pom.xml
   ↓
修改 dependency
   ↓
运行编译
   ↓
Observation：编译失败
   ↓
分析错误
   ↓
修改代码
   ↓
重新编译
```

这已经非常强了。但如果任务从十分钟变成三天，问题马上发生变化。

## 二、长周期 Agent 的问题不是“下一步”，而是“我现在在哪里”

假设一个任务需要连续工作三天：

```text
Day 1
分析项目 → 修改代码 → 测试 → checkpoint

Day 2
恢复状态 → 继续修改 → 发现新的失败 → checkpoint

Day 3
恢复状态 → 回归测试 → 验证结果 → 完成
```

这里真正困难的问题已经不是 ReAct 本身，而是：

```text
我完成了什么？
我还剩什么？
上一次为什么失败？
当前环境是什么状态？
哪些结果已经被验证？
如果进程挂掉，怎么继续？
如果 Context 换了，新的 Agent 怎么接班？
```

因此，长周期 Agent 的核心对象开始从 **Action** 变成 **State**。

## 三、我更愿意把 Agent Loop 分成三层

层次核心问题典型能力
Action Loop下一步做什么？ReAct、Tool Calling、Observation
Task Loop整个任务如何持续推进？Planning、Decomposition、Verification、Context Handoff
System Loop任务如何跨进程、跨时间稳定运行？Checkpoint、Resume、Retry、Scheduling、HITL、Observability

这样看，ReAct 并没有被长周期 Agent 淘汰。恰恰相反，它更像是长周期系统里面最核心的一层“内循环”。

```text
Long-Running Agent
        │
        ├── Harness / Task Loop
        │       └── ReAct / Action Loop
        │               └── Tool → Observation
        │
        └── Runtime / System Loop
                ├── State
                ├── Checkpoint
                ├── Resume
                ├── Retry
                └── Scheduling
```

## 四、所以 Harness 开始变得重要

2025 年 Anthropic 针对 long-running agents 的实践已经非常直接：仅仅让模型在多个 context window 中持续循环并不够。它需要 initializer、结构化 feature list、progress artifacts、git history、测试与 session handoff，让下一次 session 能够知道上一次发生了什么。

这里我觉得有一个重要的概念变化：

```text
Prompt
  ↓
让模型知道“应该做什么”

Harness
  ↓
让模型知道“怎么持续做”
```

Harness 不只是一个 prompt wrapper。它开始决定：

- 给模型哪些工具和 Skills；

- Context 如何组织、压缩和重置；

- 任务如何拆分成可验证的工作单元；

- 每个 session 如何留下结构化状态；

- 什么时候必须验证，而不是相信模型说“完成了”；

- 多个 Agent 如何分工和交接。

2026 年 Anthropic 又进一步把 planner、generator、evaluator 组合起来，用结构化 handoff 和独立 evaluator 支撑多小时的自主开发。这说明 Harness 已经从“辅助模型”逐渐变成了 Agent 能力的一部分。

## 五、但 Harness 还不是 Runtime

这里是我觉得特别容易混淆的一层。

```text
Harness
= prompts + tools + skills + loop + task-specific logic

Runtime
= durable execution + state + memory + scheduling
  + retry + HITL + observability + sandbox + tenancy
```

一个 Harness 可以让 Agent 在某个任务上表现得更好；但当它进入生产环境以后，还会遇到完全不同的问题：

```text
进程挂了怎么办？
机器重启怎么办？
部署升级怎么办？
人三天以后才审批怎么办？
任务运行几个小时怎么办？
多个任务怎么并发？
状态保存在哪里？
谁有权限执行这个 Tool？
执行结果怎么追踪？
```

这已经不是 prompt engineering，而是典型的 Runtime Engineering。

LangChain 在 2026 年对生产 Agent Runtime 的总结也把 durable execution、memory、human-in-the-loop、multi-tenancy、observability、sandbox 和 scheduled jobs 等能力放到了 Harness 之下的 Runtime 层。

## 六、长周期 Agent 最关键的一个能力：Durable Execution

传统 HTTP 请求往往是：

```text
Request → Process → Response
```

而 Agent 可能是：

```text
Run
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
等待人工审批
 ↓
……三天后……
 ↓
Resume
 ↓
继续执行
```

因此，Agent Runtime 必须把“执行”从一个短生命周期进程中解耦出来。

这也是为什么 Checkpoint / Resume 越来越像 Agent Runtime 的基础原语：

```text
Action
 ↓
State Update
 ↓
Checkpoint
 ↓
Process Dies
 ↓
New Worker
 ↓
Restore State
 ↓
Continue
```

这时候，Agent 就开始有点像一个真正的长期计算实体，而不是一次 API request。

## 七、Context Window 变大，不等于任务 Horizon 变长

一个直觉很容易出现：

既然 Context 越来越大，那就把所有历史都塞进去，Agent 不就能做更长的任务了吗？

但我认为这是两个不同的问题。

```text
Context Window
     ≠
Task Horizon
```

Context window 解决的是“这一轮模型能看到多少信息”；Task Horizon 解决的是“系统能否跨越很多轮行动仍然保持正确的状态”。

因此长周期系统可能反而需要：

```text
工作一段时间
 ↓
保存 Artifact / State
 ↓
Context Reset
 ↓
加载必要状态
 ↓
新的 Agent Session
 ↓
继续工作
```

Anthropic 的 long-running agent 实践也显示，context compaction 并不能单独解决跨 session 的问题，结构化 artifacts、progress tracking 和 context reset 都可能成为 Harness 的重要组成部分。

## 八、Verification 把“我做完了”变成“结果真的成立”

长任务还有一个特殊问题：错误会累积。

```text
错误 1
 ↓
错误 2
 ↓
错误 3
 ↓
错误 4
 ↓
最后才发现整个方向错了
```

所以长周期 Agent 必须不断形成反馈闭环：

```text
Goal
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
 ↺
```

这也是我之前一直强调的 **verify → optimize**。真正可靠的 Agent，不应该仅仅记录“Tool Call 成功”，而应该尽可能记录“目标结果是否成立”。

于是 Evaluation 也开始进入 Harness：generator 负责产生结果，evaluator 负责判断结果。这比让同一个 Agent 自己宣布“完成”更容易形成独立反馈。Anthropic 2026 年的长周期应用实验就采用了 planner / generator / evaluator 的结构。

## 九、ReAct、Harness、Runtime 的边界可以这样理解

层核心问题一句话
ReAct下一步做什么？让 Agent 会“走一步”
Harness整个任务怎么推进？让 Agent 能“走很远”
Runtime任务怎么长期稳定运行？让 Agent 能“活很久”

我觉得这比简单讨论“ReAct 是否过时”更准确。

**ReAct 没有过时，它只是被放进了更大的系统。**

## 十、这也解释了为什么 2025 年以后 Harness 开始成为独立的工程对象

如果 Agent 只是一次 LLM + Tool Calling，模型能力自然是最大的变量。但当任务开始跨越多个 context、多个 session、多个 worker，甚至跨越几天以后，模型已经不是唯一变量。

```text
Agent Performance
        ≈
Model
× Harness
× Runtime
× Environment
× Feedback
```

2026 年的工程实践正在明显朝这个方向发展：Anthropic 持续研究 long-running harness，LangChain 则明确区分 harness 与 production runtime，并把 durable execution、memory、HITL、observability 等能力下沉到 runtime。

甚至可以看到一个很有意思的趋势：随着模型越来越强，Harness 中一些原本必要的“脚手架”可能会逐渐被删掉；反过来，模型无法稳定解决的问题，又会被 Runtime 或 Harness 显式工程化。Anthropic 也明确指出，Harness 中的假设会随着模型能力提升而过时，因此需要持续验证哪些组件真正有价值。

## 十一、我现在对 Agent Runtime 的一个更强理解

如果沿着这条线继续往下走，我觉得 Agent Runtime 的核心已经不是“帮 LLM 调工具”。

它更像是在管理一种新的长期计算实体：

```text
Goal
 ↓
Agent
 ↓
Action Loop / ReAct
 ↓
Environment
 ↓
Feedback
 ↓
State
 ↓
Checkpoint
 ↓
Resume / Replan
 ↺
```

因此我越来越愿意把它和传统系统中的 Process、Actor、Kubernetes Controller 放在一起思考。

它们的共同点不是“都能执行代码”，而是：

**它们都需要让一个持续变化的计算实体，在不确定的现实环境中保持自己的状态，并不断向某个目标推进。**

## 十二、最后：从 Action Loop 到 Lifecycle

如果把整个 Agent Engineering 再压缩一次，我现在会这样理解：

```text
ReAct
  ↓
Action Loop
  ↓
Harness
  ↓
Task Loop
  ↓
Runtime
  ↓
Lifecycle
  ↓
Environment
  ↓
Feedback
  ↺
```

所以，Agent 的下一阶段可能并不是简单地让 LLM “想得更久”，而是让系统能够：

- 把一个长期目标拆成可推进的状态；

- 让不同 session / Agent 之间可靠交接；

- 在失败后从 checkpoint 恢复，而不是重新开始；

- 用真实环境验证结果，而不是只看模型输出；

- 在必要时暂停、等待、重新唤醒；

- 让 Harness 随模型能力演进，而 Runtime 保持稳定的基础设施边界。

这也是我最近越来越关注 **Agent Runtime** 的原因：**ReAct 解决了 Agent 如何行动的问题，而 Runtime 开始解决 Agent 如何作为一个长期存在的计算实体运行的问题。**

## 参考

- Anthropic, *Effective harnesses for long-running agents*, 2025-11-26。

- Anthropic, *Harness design for long-running application development*, 2026-03-24。

- Anthropic, *Scaling Managed Agents: Decoupling the brain from the hands*, 2026-04-08。

- LangChain, *The Runtime Behind Production Deep Agents*, 2026-04-20。
