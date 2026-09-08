---
id: agent-optimizer-experience-policy
type: Articles
title: Agent Optimizer：不训练模型，而是优化经验与策略
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Agent, Optimizer, Reinforcement Learning, Experience Memory, Evaluation, Policy]
excerpt: 从我们讨论 Local RL Optimizer、JitRL、EvoTest 与 GEPA 时形成的一条思路出发：Agent 变强不一定首先意味着修改模型权重，也可以通过经验记忆、轨迹检索、策略调整与工具调用方式的优化实现。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-optimizer-experience-policy.md
---

# Agent Optimizer：不训练模型，而是优化经验与策略

我们讨论 Agent 优化时，一个问题很快出现了：**Agent 变强，是不是一定要重新训练模型？**

我当时越来越倾向于认为，不一定。

如果把 Agent 看成一个持续运行的系统，那么除了模型本身，还有很多东西可以被优化：

```text
Model
 +
Experience
 +
Policy
 +
Tool Routine
 +
Evaluation
```

模型权重只是其中的一层。

## 一、把 Agent 和模型分开

传统理解很容易变成：

```text
模型变弱
 ↓
Fine-tuning / RL
 ↓
模型变强
```

但 Agent 实际运行的时候，还存在另一条路径：

```text
Task
 ↓
Agent
 ↓
Experience
 ↓
Retrieval / Reflection
 ↓
Policy Adjustment
 ↓
Next Action
```

这里并没有修改 LLM 的参数。

优化的是 Agent 如何利用已经发生过的经验，以及下一次面对类似任务时采取什么策略。

这也是我们讨论 **Local RL Optimizer** 时的一个重要方向：把优化器放在模型之外，让它优化策略，而不是直接修改 LLM weights。

## 二、经验本身可以成为 Agent 的“外部参数”

如果一次 Agent 执行产生了：

```text
Task
 ↓
Trajectory
 ↓
Outcome
 ↓
Critique
```

那么这条轨迹就不应该只是日志。

它可以变成下一次 Agent 决策时能够使用的经验。

因此我们讨论过一个很自然的结构：

```text
Task
 ↓
Task Fingerprint
 ↓
Case / Experience Memory
 ↓
Retrieve Related Trajectories
 ↓
Estimate Which Action Worked
 ↓
Agent
```

这里的 Memory 不一定要保存完整上下文，而可以保存与问题相关的案例、轨迹和反馈。

## 三、JitRL 给我的一个启发

我们讨论过 ICLR 2026 的 JitRL。

它让我注意到一个方向：**不改变模型梯度，也可以通过非参数化的经验记忆来估计行动的价值。**

核心思路可以粗略理解成：

```text
当前任务
   ↓
寻找相似历史轨迹
   ↓
比较历史 Action 的结果
   ↓
估计 Action Advantage
   ↓
帮助当前决策
```

这和传统 RL 的思路不同：传统路线通常需要把经验进一步变成参数更新；这里则可以把经验保留在模型之外。

它的意义不只是降低训练成本，而是让我开始把 Agent Optimizer 看成一个独立系统。

## 四、EvoTest 让我看到另一种可能

我们还讨论过 EvoTest 的 Actor / Evolver 双角色结构。

这里比较有意思的是：Agent 的一次执行可以成为下一次系统改进的输入。

可以抽象成：

```text
Actor
 ↓
执行任务
 ↓
Transcript
 ↓
Evolver
 ↓
分析问题
 ↓
修改 Prompt / State / Tool Routine
 ↓
下一轮 Actor
```

这和“重新训练一个模型”是不同的工程路径。

它优化的是 Agent 的行为程序：

- Prompt
- Persistent Memory
- State
- Tool Call Routine
- Execution Strategy

所以 Agent 本身开始具有一种可以持续演化的结构。

## 五、GEPA / Prompt Evolution 进一步说明了这一点

我们还聊过 DSPy 生态和 GEPA（Reflective Prompt Evolution）。

这里让我比较关注的不是某一个具体 benchmark，而是它体现出来的方向：

> **优化对象不一定是模型参数，也可以是模型周围的程序。**

如果把 Agent 看成：

```text
LLM
+
Prompt
+
Tools
+
Memory
+
Policy
+
Evaluation
```

那么真正需要优化的可能是整个行为程序，而不是只有 LLM。

这也是为什么我觉得“Agent Optimizer”应该成为一个独立的工程层。

## 六、但 Optimizer 有一个非常危险的问题

如果评价指标错了，Optimizer 会非常努力地把错误指标做高。

所以我们后来又讨论到一个问题：

```text
Proxy Metric ≠ Real Outcome
```

例如：

```text
API PASS
12 tests passed
outcome.ok = true

        ↓

用户：问题没有解决
```

如果 Optimizer 只相信前面的信号，它就会把这个失败案例当成成功案例继续学习。

因此 Optimizer 不能只记录：

```text
reward = +1
```

而应该知道这个 reward 到底是什么证据产生的。

## 七、因此我把 Case Memory 想成 Optimizer 的第一层

我们讨论过一个比较实际的结构：

```text
Tier 1
Case / Experience Memory

Task
Critique
Trajectory
Outcome
Ground Truth Status
Cost
```

这些 Case 可以被向量化，用于寻找相似问题。

在它上面再放一个轻量的 Decision Layer：

```text
Case Memory
     ↓
Related Cases
     ↓
Decision Layer
     ↓
Prompt / Policy / Tool Routine
     ↓
Agent
```

这比一开始就重新训练一个模型更轻，也更容易观察到底是什么发生了变化。

这一层我先做成了一个很薄的实现：[llm-trace-reuse](https://github.com/chengguruchun/llm-trace-reuse)（站内：[Projects](/projects/)）。不改模型权重，只在任务开始时路由：命中 playbook 就走手册，能复用上次的 `preferred_path` 就不要重新规划。它还没有完整的 Ground Truth，所以 `outcome.ok` 仍然可能只是 Proxy。

## 八、Task Fingerprint 是连接经验与任务的关键

如果所有历史经验只是一个巨大的向量库，那么相似度本身并不足够。

我们讨论过 `task_fingerprint` 这个概念。

它不是简单的文本 embedding，而是试图描述：

```text
这是什么类型的问题？
什么失败模式？
需要什么能力？
过去什么策略有效？
```

这样 Optimizer 才能从：

```text
“和它长得像”
```

进一步走向：

```text
“它属于同一种问题，因此某种策略可能有效。”
```

## 九、Optimizer 真正优化的可能是“下一次怎么做”

这样重新看，Agent Optimizer 可以分成几层：

```text
                 Agent Optimizer
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   Experience       Policy          Tool Routine
     Memory        Adjustment         Tuning
        │               │               │
        └───────────────┼───────────────┘
                        ↓
                     Agent
                        ↓
                    Outcome
                        ↓
                   Evaluation
                        ↓
                     Memory
                        ↺
```

它优化的不是“模型知道多少”，而是：

> **面对一个任务，Agent 下一次应该怎么做。**

这和我们前面讨论的 Loop Engineering 是一致的。

## 十、为什么这条路线可能比重新训练更适合 Agent

Agent 的问题有一个特点：任务分布可能一直变化。

如果每遇到一种新情况都重新训练模型，周期和成本都很高，而且很难知道究竟是什么改变了模型行为。

如果把经验和策略外置：

```text
新问题
 ↓
执行
 ↓
得到经验
 ↓
验证结果
 ↓
写入 Case Memory
 ↓
下一次相似任务直接利用
```

那么 Agent 可以形成一种比较轻量的持续改进机制。

它不是让模型本身不断变化，而是让**模型周围的系统不断积累经验**。

## 十一、但这并不意味着“永远不要训练模型”

我并不认为经验记忆和策略优化可以替代模型训练。

更合理的理解是：它们处在不同层次。

```text
Model Training
    ↓
基础能力

Agent Optimizer
    ↓
任务策略
经验
工具使用方式
行为程序

Runtime / Control Plane
    ↓
执行与治理
```

模型负责提供通用能力；Optimizer 负责让 Agent 更会解决特定问题；Runtime 和 Control Plane 负责让整个系统稳定运行。

## 十二、最终形成一个持续学习的 Loop

如果把这些讨论放在一起，我现在更愿意把 Agent Optimizer 表达成：

```text
Goal
 ↓
Agent
 ↓
Action
 ↓
Environment
 ↓
Outcome
 ↓
Evaluation
 ↓
Experience
 ↓
Optimizer
 ↓
Policy / Memory / Tool Routine
 ↓
Next Agent
 ↺
```

这里最重要的不是“自动优化”四个字，而是中间多了一层：

> **经验不会只留在日志里，而是成为下一次决策的一部分。**

所以 Agent 的持续进化未必首先表现为模型参数发生变化，也可能表现为：

```text
经验越来越丰富
策略越来越稳定
工具调用越来越合理
失败模式越来越少
```

而整个系统真正需要解决的，仍然是我们前一篇文章里的那个问题：

> **Optimizer 到底应该相信什么结果？**

如果没有可靠的 Ground Truth，所谓“自动优化”很容易只是“自动把 Proxy Metric 做得更高”。评测怎么接到优化器，见 [Agent 的评价：Proxy Metric ≠ Real Outcome](/articles/agent-evaluation-proxy-vs-real-outcome.html)。
