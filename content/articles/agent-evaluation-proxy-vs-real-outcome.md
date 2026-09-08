---
id: agent-evaluation-proxy-vs-real-outcome
type: Articles
title: Agent 的评价：Proxy Metric ≠ Real Outcome
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Agent, Evaluation, Outcome, Ground Truth, Feedback, Loop Engineering]
excerpt: 从我们讨论 Agent 评价时遇到的一个具体矛盾出发：测试、API 状态和 outcome.ok 都可能是 PASS，但用户仍然认为问题没有解决。Agent 的评价最终必须回到真实 Outcome。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-evaluation-proxy-vs-real-outcome.md
---

# Agent 的评价：Proxy Metric ≠ Real Outcome

我们讨论 Agent 优化时，遇到过一个很直接的问题：**一个 Agent 的测试全部通过，是否意味着它真的把事情做好了？**

答案并不一定是。

我当时看到过这样一种情况：

```text
outcome.ok = true
12 tests passed
API PASS
multi-style PASS

        ↓

用户反馈：
「覆盖问题也没有修正」
```

这让我意识到，Agent 的评价不能只看系统内部已经定义好的指标。

## 一、Proxy Metric 很容易看起来像结果

传统软件里，很多执行结果本身就比较接近最终结果：

```text
HTTP 200
单元测试 PASS
API PASS
Workflow SUCCESS
```

这些信号当然重要，因为它们说明系统至少完成了某些预期动作。

但 Agent 做的事情越来越接近开放目标以后，情况发生了变化。

例如一个 Agent 修改代码，测试通过了，并不自动证明用户的问题解决了；一个 Agent 调整配置，API 返回成功，也不自动证明业务结果已经改善。

所以需要把两个概念分开：

```text
Proxy Metric
    ↓
「过程看起来成功」

Real Outcome
    ↓
「目标实际上被完成」
```

两者可能一致，也可能发生偏差。

## 二、为什么 Agent 更容易出现这种偏差

Agent 的任务通常不是单纯执行一个函数，而是：

```text
Goal
 ↓
Plan / Action
 ↓
Tool
 ↓
Environment
 ↓
Observation
 ↓
Adjustment
```

因此 Agent 的成功标准天然有两层。

第一层是：**Action 有没有正确执行。**

第二层是：**Action 有没有让环境朝目标移动。**

如果只测第一层，Agent 很容易学会优化一个代理指标，而不是优化真正的目标。

这和我们讨论 Kubernetes × Agent 时的想法是一致的：Kubernetes 很擅长判断资源状态，但 Agent 面对的 Actual State 往往不是一个简单的机器状态，而可能是语义性的 Outcome。

## 三、一个更重要的字段：Ground Truth Status

因此我们讨论 Agent Optimizer 时，我提出过把真实结果状态显式记录下来，而不是只保存一个 `ok=true`。

例如：

```text
Ground Truth Status
├── test_verified
├── user_confirmed
└── unverified
```

它表达的是：

- `test_verified`：测试或自动校验已经证明结果满足要求。
- `user_confirmed`：用户明确确认问题已经解决。
- `unverified`：系统还没有足够证据判断真实结果。

这比简单的：

```text
outcome.ok = true
```

更诚实。

因为 `ok` 很可能只表示某个代理检查通过，而不是最终目标已经完成。

## 四、Proxy Metric 与 Real Outcome 的 Divergence

如果两个信号发生冲突，我认为不应该简单地把用户反馈覆盖掉测试结果，也不能反过来认为用户反馈一定是错误的。

应该把这种冲突本身记录下来：

```text
Proxy Metric
      ↓
    PASS
      │
      │  ≠
      ↓
Real Outcome
      ↓
User Confirmed: FAIL

=> divergence_flag = true
```

因此我们讨论过一个很简单但重要的字段：

```text
divergence_flag
```

它不是为了告诉系统“谁对谁错”，而是告诉 Optimizer：**这里出现了评价体系与真实反馈之间的偏差，不能直接把这条轨迹当成成功案例学习。**

## 五、Held-out Test 为什么重要

如果 Agent 自己生成的测试就是它最终优化的测试，那么很容易出现一个问题：

```text
训练 / 优化
    ↓
Visible Tests
    ↓
全部通过
```

但这并不能证明它在没有见过的场景里仍然有效。

所以我们讨论时，我特别强调了要区分：

```text
Visible Tests
      ↓
Proxy Signal

Held-out Tests
      ↓
Independent Signal

User Feedback
      ↓
Real-world Signal
```

至少要让 Optimizer 知道，这三个信号不是同一个东西。

## 六、评价体系本身也应该成为 Agent Runtime 的一部分

如果 Agent 未来真的变成一个持续运行的系统，那么 Evaluation 就不能只是任务结束以后的一张报表。

它应该进入 Loop：

```text
Goal
 ↓
Agent
 ↓
Action
 ↓
Environment
 ↓
Observation
 ↓
Evaluation
 ↓
Gap
 ↓
Next Action
 ↺
```

这里 Evaluation 的作用不是单纯打分，而是回答：

> **现在的结果，离真正目标还有多远？**

这也是为什么我越来越觉得 Agent 的核心问题不是“能不能调用更多 Tool”，而是“能不能知道自己到底有没有完成”。

## 七、这会直接影响 Agent Optimizer

如果评价信号本身不可靠，Optimizer 越聪明，问题可能反而越严重。

因为它会非常有效地优化错误目标：

```text
错误 Proxy
    ↓
Optimizer
    ↓
更强的策略
    ↓
更高的 Proxy 分数
    ↓
更大的 Real Outcome 偏差
```

所以 Agent Optimizer 的第一步不是“怎么优化”，而是先回答：

```text
这个成功信号是真的吗？
```

这也是我后来把下面几个字段放到一起考虑的原因：

```text
task_fingerprint

ground_truth_status

divergence_flag

cost
```

其中 `task_fingerprint` 用来知道这是什么类型的问题；`ground_truth_status` 表示结果被什么程度的证据验证；`divergence_flag` 表示 Proxy 与真实结果是否发生冲突；`cost` 则记录得到这个结果付出了多少 Token、调用次数和 detour。

## 八、我现在更愿意这样理解 Agent Evaluation

传统软件的评价经常可以接近：

```text
Function
 ↓
Expected Output
 ↓
PASS / FAIL
```

Agent 更像：

```text
Goal
 ↓
Agent
 ↓
Action
 ↓
Environment
 ↓
Observed Outcome
 ↓
Ground Truth
```

因此：

> **Agent Evaluation 不是给 Agent 一个分数，而是建立 Proxy Metric 与 Real Outcome 之间的对应关系。**

如果两者长期一致，Proxy 才值得信任；如果两者出现偏差，就应该优先研究这个偏差，而不是继续提高 Proxy 分数。

最终，Agent 真正需要优化的不是：

> “我通过了多少测试？”

而是：

> **“我是否真的解决了用户要解决的问题？”**

这也是 Agent 从 Workflow 走向 Loop 以后，一个必须面对的问题。

一个正在用的薄实现是 [llm-trace-reuse](https://github.com/chengguruchun/llm-trace-reuse)（站内：[Projects](/projects/)）：复用 `preferred_path` 之前，仍然要先问这条轨迹的成功信号是不是真的。优化器怎么用这些经验，见 [Agent Optimizer](/articles/agent-optimizer-experience-policy.html)。
