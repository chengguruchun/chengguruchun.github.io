---
id: agent-runtime-model-learning-runtime
type: Bench
title: Agent Runtime Model：让 Runtime 本身成为可学习的系统
date: 2026-09-30
thought_date: 2026-09-30
published_date: 2026-09-30
tags: [Agent Runtime, Learning Runtime, Thought Experiment]
excerpt: 这不是一篇“已经定型”的架构文章，而是一个放进 Agent Bench 的思想实验：如果 Runtime 每天都在执行 Agent，它能不能像一个系统一样，从执行结果中学习自己的策略？
conclusion: false
stage: experiment
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/bench/agent-runtime-model-learning-runtime.md
note: Thought experiment on Agent Bench. Not a catalog conclusion.
---

# Agent Runtime Model：让 Runtime 本身成为可学习的系统

我们通常把 Agent 理解成“大模型 + Tools”。但当 Agent 真正进入复杂任务执行之后，一个新的问题出现了：大量关键决策并不是在解决任务本身，而是在决定“怎样运行这个 Agent”。这部分能力应该一直交给大模型吗？

## 一、从 Agent Model 到 Runtime Model

LLM 更擅长回答“下一步应该做什么”，而 Runtime 更关心“这一步应该怎样可靠地执行”。例如选择哪个工具、失败后是否重试、是否切换工具、是否需要人工确认、结果是否需要验证、什么时候保存 checkpoint，以及任务什么时候真正结束。

因此可以把职责进一步拆开：**LLM 负责解决任务，Agent Runtime 负责执行任务，而 Runtime Model 负责学习如何更好地运行 Agent。**

```text
LLM
 ↓
Agent Runtime
 ↓
Runtime Policies
 ↓
Execution
 ↓
Feedback
 └────────→ Runtime
```

## 二、为什么 Runtime 需要自己的 Model

如果每一次 Tool Routing、Retry、Verification 都重新调用一个大模型，会带来成本、延迟和稳定性问题。更重要的是，这些决策往往高度重复，并且具有明确的反馈信号，因此非常适合形成专门的 Policy。

Runtime Model 不需要成为另一个“万能 Agent”，更合理的方向可能是一组小型 Policy Models：Tool Router、Context Selector、Retry Policy、Risk Model、Verification Model、Cost Optimizer 和 Human Escalation Policy。

## 三、Runtime Model 学习的不是答案，而是执行策略

普通模型训练的数据通常是 Question → Answer。而 Runtime Model 更适合学习 Task → Trajectory → Outcome。

```text
Task Fingerprint
+ Context
+ Available Tools
+ Action
+ Observation
+ Failure / Recovery
+ Final Outcome
+ Cost / Latency
+ Human Feedback
```

这样积累下来的不只是“回答数据”，而是一套 Runtime Experience：什么任务适合什么工具，什么错误应该重试，什么结果需要验证，以及什么情况下应该让人类介入。

## 四、从 Feedback 到 Runtime Learning

```text
Task
  ↓
Trajectory
  ↓
Action / Observation
  ↓
Evidence
  ↓
Outcome / Reward
  ↓
Policy Dataset
  ↓
Runtime Model
  ↓
Better Execution
```

这里不一定需要修改基础大模型的参数。系统可以首先优化 Runtime Policy。例如某类任务使用 Tool A 的成功率只有 42%，而 Tool B 达到 91%，经过足够多的真实轨迹之后，Runtime Model 可以学习在类似任务中优先选择 Tool B。

这是一种不同于“训练一个更大的基础模型”的优化路径：**不一定先优化大脑，而是先优化大脑所在的操作系统。**

## 五、Verification 是 Runtime Model 的重要入口

Agent 说“任务完成”并不意味着任务真的完成。Runtime 可以比较 Expected Outcome、Actual Outcome 和 Evidence，再由 Verification Policy 判断是否可以结束。

```text
confidence > threshold  → finish
confidence < threshold  → verify
confidence very low      → re-plan / human
```

这与 Agent 的核心闭环非常接近：Expected → Actual → Gap → Optimize。Runtime Model 的价值就在于把这个闭环从一次性的 LLM 推理，逐渐变成可学习的执行策略。

## 六、最终可能形成 Runtime Policy Family

```text
Agent Runtime
│
├── Tool Router
├── Context Selector
├── Retry Policy
├── Risk Model
├── Verification Model
├── Cost Optimizer
└── Human Escalation Policy
```

因此未来的 Runtime Model 未必是一个模型，而更可能是一组围绕 Runtime 决策形成的 Policy Model Family。规则引擎负责确定性的边界，小模型负责高频策略判断，大模型负责复杂推理，而 Runtime 负责把它们组织成可靠的执行闭环。

## 七、为什么把它放进 Agent Bench

我更愿意先把这个想法放在 Bench，而不是直接把它当成一套成熟架构。因为真正需要验证的问题不是“这个架构图是否漂亮”，而是：

```text
同一类 Task
   ↓
记录多次 Trajectory
   ↓
比较 Tool / Retry / Verify 策略
   ↓
得到 Outcome 与 Cost
   ↓
更新 Runtime Policy
   ↓
再次执行
   ↓
是否真的变好？
```

如果没有这个闭环，“Learning Runtime”只是一个概念；如果能够在可重复的实验中观察到策略随着经验改善，它才开始成为一个真正可以工程化的 Runtime Model。

## 结语

如果基础模型是 Agent 的“大脑”，那么 Runtime 更像它所处的“操作系统”。而 Runtime Model 则可以被理解为这个操作系统中的学习型控制层。

所以我现在更倾向于把 Agent Bench 看成不只是模型评测场，而是**验证 Runtime 思想的实验台**：模型负责产生能力，Runtime 负责组织能力，而实验负责告诉我们 Runtime 的策略到底有没有变好。
