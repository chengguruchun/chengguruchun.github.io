---
id: llm-scientific-experiment
type: Diverse Lab
title: 大模型：用科学实验的方式使用
date: 2026-09-06
thought_date: 2026-09-02
published_date: 2026-09-06
tags: [Diverse, LLM, Experiment, Agent, Loop Engineering, Complex Systems]
---

# 大模型：用科学实验的方式使用

## Question

为什么同一条规则，写在 Prompt 开头、中间或末尾，结果会差一截？为什么「上下文结构」经常比「措辞本身」更决定成败？大模型究竟更像一段可调用的程序，还是一套需要假设、对照与评测的实验系统？

## My Thinking

很多人把大模型当成确定性函数：输入 Prompt，输出 Answer。现实不是这样。真正进入推理的，往往是 Prompt、Context、Model、History、Sampling 叠在一起，再经过概率采样，才落到一次输出。

传统软件：

```
Input → Deterministic Logic → Output
```

大模型使用：

```
Prompt + Context + Model + History + Sampling
        → Probability
        → Output
```

因此，关键问题要从「为什么错了」换成「在什么条件下更容易正确」。不是在调试一条公式，而是在标定一套条件分布。

### 把使用过程做成科学实验

一旦承认输出是概率性的，正确用法就接近实验科学：

1. 提出假设（Hypothesis）
2. 设计实验（Design）
3. 控制变量（Control Variables）
4. 运行（Run）
5. 记录结果（Record）
6. 对照比较（Compare）
7. 得出结论（Conclude）
8. 迭代改进（Iterate）

一个典型例子：规则放置位置。同一规则分别放在系统指令顶部、用户消息中段、输出前最后一句、以及拆成多轮约束——记为实验 A–D。每次固定模型、温度、样本集，记录：

- Success Rate
- Error Type
- Cost
- Latency
- Consistency（同输入多次采样的稳定度）

这时你得到的不是「这条 Prompt 对不对」，而是「在哪些变量组合下，正确概率更高」。Prompt Engineering 开始长成 Experiment Engineering。

### 桥接到复杂系统：不是 Answer B，而是 P(correct)

这与另一篇 Diverse Lab 笔记——[物理学 × 生态学](/diverse/physics-ecology-llm.html)——是同一条弧。物理直觉喜欢「给定 A，得到 B」；生态与复杂系统更诚实：A 提高 B 出现的概率。

大模型落在概率性复杂系统这一侧。你优化的对象，不是单次 Answer B，而是在约束、成本与延迟下的 P(correct)。把一次漂亮回答当成终局，等于用单次采样冒充定律。

### Proxy Metric ≠ Real Outcome

实验还有第二个陷阱：代理指标不等于真实结果。

测试集全绿，用户问题仍然没解决；格式校验通过，业务目标没有推进；自洽评分很高，Held-out 一塌糊涂。评测必须至少拉三条线：

- User Feedback（真实任务是否完成）
- Held-out（未参与调参的样本）
- Ground Truth（可核对的事实或可执行断言）

否则你只是在优化「看起来像对」的分布，而不是「真正做对」的分布。

### 从单次回答到 Loop Engineering

当系统开始带着目标行动，单轮 Prompt→Answer 不够用了。更完整的闭环是：

```
Goal → Action → Observation → Gap → Adjustment
```

这就是 Loop Engineering：把反馈写进运行时，而不是写进一次性措辞。Gap 不是情绪，而是下一轮策略的输入。

在这条路上，会出现 Agent Optimizer：不必然先训权重，而是用经验轨迹（trajectory）优化外层策略——何时检索、何时调用工具、何时停、如何改写下一轮假设。模型权重可以固定；变的是策略、记忆、评测与环境交互协议。

### 五层方法论

把上面压缩成可迁移的五层：

1. **LLM ≠ deterministic function.** 先承认概率与条件依赖。
2. **Prompt Engineering → Experiment Engineering.** 假设、对照、记录、复现。
3. **Output → Evaluation → Real Outcome.** 代理指标必须对齐真实结果。
4. **Execute → Feedback → Gap → Improve → Execute Again.** 闭环，而不是单次调用。
5. **Model → Agent → Runtime → Multi-Agent → Environment → Feedback → Evolution.** 尺度拉大后，工程对象变成复杂系统本身。

### 一份可复用的实验模板

每次认真用大模型前，先写短模板：

- **问题**：要解决什么
- **目标**：成功长什么样
- **已知 / 未知**：边界与假设前提
- **假设**：改变什么会提高正确率
- **基线**：当前最好方案
- **实验**：变量、对照、样本量
- **工具**：检索、代码、评测器、日志
- **指标**：Success / Error / Cost / Latency / Consistency + 真实结果
- **反例**：故意找会翻车的输入
- **复现**：种子、版本、温度、上下文快照
- **沉淀**：结论写回策略库，而不是散落在聊天记录里

工具与角色分工往往比「再写一句更妙的 Prompt」更有效：假设提出者、评测器、反方审稿人、执行者分开，比单角色自嗨更能压住自我证明偏差。

<blockquote>
<p>使用大模型不是在调用一个确定性的函数，而是在做一种概率性的科学实验：提出假设、控制变量、观察结果、验证反馈，然后不断迭代。</p>
</blockquote>

<blockquote>
<p>当 Agent 开始具备目标、行动、记忆和反馈之后，面对的就不再只是 Prompt Engineering，而是一种新的 Complex System Engineering。</p>
</blockquote>

## Open Questions

- 哪些指标真正逼近 Real Outcome，哪些只是好看的 Proxy，会系统性地奖励「看起来像对」？
- 闭环越强，Reward Hacking 的空间越大——如何防止评测器与 Agent 合谋？
- 什么规模的任务值得上完整实验开销；什么时候一条强基线 Prompt 就够？
- Policy Optimizer 如何保持诚实：在优化外层策略时，怎样避免只拟合评测分布？
- Experiment Engineering 与 Complex System Engineering 的分界在哪里：何时该停在对照实验，何时必须设计环境、反馈与演化？
