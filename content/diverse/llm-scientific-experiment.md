---
id: llm-scientific-experiment
type: Diverse Lab
title: 大模型：用科学实验的方式使用
date: 2026-09-06
thought_date: 2026-09-02
published_date: 2026-09-06
tags: [Diverse, LLM, Experiment, Agent, Loop Engineering, Complex Systems]
stage: validated
origin: user
contribution: extension
thought_id: thought-scientific-experiment-agent
---

# 大模型：用科学实验的方式使用

## Question

为什么同一条规则，写在 Prompt 开头、中间或末尾，结果有时会差一截？为什么「上下文结构」在不少任务上，影响力并不亚于「措辞本身」？面对这种条件敏感，大模型更该被当成一段可调用的程序，还是一套需要假设、对照与评测的实验对象？

## My Thinking

工程习惯里，人们常把大模型近似成确定性函数：输入 Prompt，输出 Answer。这个近似有用，但不完整。

一次调用真正依赖的，通常是 Prompt、Context、Model、History，以及解码时的采样设置。即使把温度调到很低，输出仍可能随上下文组织、示例选择、工具描述与历史截断而漂移；温度高于零时，同输入多次采样还会叠加随机性。

更稳妥的对照是：

```
传统软件（常见工程假设）
Input → Deterministic Logic → Output

大模型调用（更贴近现实的描述）
Prompt + Context + Model + History + Decoding
        → Conditional Distribution
        → One Sample / One Trajectory
```

因此，高价值问题往往不是「为什么这一次错了」，而是「在哪些可陈述的条件下，正确率、稳定性与成本更优」。目标从「找到一句神奇 Prompt」，转向「估计并改善一组条件」。

说明边界：并非每次聊天都要上完整实验协议。代价高、可复用、要上线或要多人协作时，实验思维才真正划算。

### 把使用过程做成可对照的实验

承认条件敏感之后，用法就靠近实验科学，而不是靠感觉连改 Prompt：

1. 提出假设（Hypothesis）
2. 设计实验（Design）
3. 控制变量（Control Variables）
4. 运行足够样本（Run）
5. 记录结果（Record）
6. 对照比较（Compare）
7. 得出有范围的结论（Conclude）
8. 迭代改进（Iterate）

以「规则放置位置」为例。同一规则分别放在系统指令顶部、用户消息中段、输出前最后一句，或拆成多轮约束，记为实验 A–D。每次尽量只改位置这一类变量，并固定：模型版本、解码参数、评测集、成功判定。若解码仍有随机性，同一条件应重复采样，报告的是分布或区间，而不是单次运气。

建议至少记录：

- Success Rate（相对明确的成功判定）
- Error Type（失败如何分型）
- Cost / Latency
- Consistency（同条件多次采样的离散程度）

这时结论应写成：「在数据集 D、模型 M、参数 Θ 下，条件 A 的成功率为 x±…，相对基线 B 的增益为 …」——而不是「这条 Prompt 永远更好」。Prompt Engineering 由此长成 Experiment Engineering：可陈述、可对照、可复现（在供应商与模型版本不变的前提下尽可能复现）。

还要注意两类常见混淆：

- **解码随机性**：同输入多次采样不同。
- **条件敏感性**：换位置、示例或工具描述后分布平移。

二者都会造成「不稳定」，机制不同，对策也不同。

### 桥接到复杂系统：优化的是条件，不是单次答案

这与另一篇 Diverse Lab 笔记——[物理学 × 生态学](/diverse/physics-ecology-llm.html)——是同一条弧。偏物理的工程直觉喜欢「给定 A，得到 B」；偏生态与复杂系统的直觉更接近：A 提高 B 出现的概率。

单个 Chat 调用，还谈不上完整「生态系统」；但一旦把工具、记忆、多步轨迹、环境反馈叠上去，系统行为就更接近条件依赖的概率过程。此时优化对象通常不是某一次 Answer B，而是在约束、成本与延迟下的表现分布——可用 P(success | conditions) 来记，其中 success 必须被事先定义，且往往是多维的（正确、安全、成本、时延）。

把一次漂亮回答当成终局，等于用单次采样冒充稳定规律。

### Proxy Metric ≠ Real Outcome

实验还有第二个陷阱：代理指标不等于真实结果。

测试集全绿，用户问题仍可能未解决；格式校验通过，业务目标未必推进；模型自评很高，Held-out 可能一塌糊涂。可用的评测至少要意识到三条线：

- **User / Task Outcome**：真实任务是否完成
- **Held-out**：未参与调参与选型的样本
- **Ground Truth / Executable Checks**：可核对事实或可执行断言（若存在）

现实里 Ground Truth 常常缺失。这时仍可用 Proxy，但必须显式记录 gap：proxy_success 与 perceived_real_outcome 是否一致。否则系统会优化「看起来像对」的分布，甚至学会 Reward Hacking。

### 从单次回答到 Loop Engineering

当系统开始带着目标行动，单轮 Prompt → Answer 往往不够。更完整的闭环是：

```
Goal → Action → Observation → Gap → Adjustment
```

这就是 Loop Engineering：把反馈写进运行时，而不是只写进一次性措辞。Gap 不是耻辱，而是下一轮策略的输入。

一个自然延伸是外层策略优化（Agent / Policy Optimizer）：不必然先改模型权重，而是用轨迹（trajectory）与真实结果，调整何时检索、何时调用工具、何时停止、如何改写下一轮假设。权重可以固定；变的是策略、记忆、评测与环境交互协议。这是否有效，仍要用对照实验证明，而不是用叙事证明。

### 五层方法论

把上面压缩成可迁移的五层（第 5 层是尺度放大后的工程对象，不是每条任务的必经之路）：

1. **先承认条件依赖与概率性。** LLM 不宜默认成确定性函数。
2. **Prompt Engineering → Experiment Engineering。** 假设、对照、记录、有范围的结论。
3. **Output → Evaluation → Real Outcome。** Proxy 必须能解释与真实结果的差距。
4. **Execute → Feedback → Gap → Improve → Execute Again。** 闭环优先于单次调用。
5. **Model → Agent → Runtime → Multi-Agent → Environment → Feedback → Evolution。** 参与者与反馈变多后，才更接近 Complex System Engineering。

### 一份可复用的实验模板

对高风险、可复用或要上线的任务，先写短模板：

- **问题**：要解决什么
- **目标**：成功长什么样（可判定）
- **已知 / 未知**：边界与前提
- **假设**：改变什么可能改善目标分布
- **基线**：当前最好方案（必须先有）
- **实验**：变量、对照、样本量、是否只改一个因素
- **工具**：检索、代码、评测器、日志、回放
- **指标**：Success / Error / Cost / Latency / Consistency + 真实结果（或 proxy + gap）
- **反例**：故意找会翻车的输入
- **复现**：模型版本、解码参数、上下文快照、数据版本
- **沉淀**：结论写回策略库，而不是散落在聊天记录里

工具与角色分工往往比「再写一句更妙的 Prompt」更能压偏差：假设提出者、执行者、评测器、反方审稿人分开，可降低自我证明。

<blockquote>
<p>在需要可靠结果的场景里，使用大模型更接近做一种概率性的科学实验：提出假设、控制变量、观察结果、验证反馈，然后在可陈述的条件下迭代——而不是把一次采样当成确定性函数的返回值。</p>
</blockquote>

<blockquote>
<p>当系统开始具备目标、行动、记忆与反馈，工程对象就容易从 Prompt Engineering 扩展到 Loop Engineering；参与者与环境互动足够复杂时，才会逼近 Complex System Engineering。</p>
</blockquote>

## Open Questions

- 哪些指标真正逼近 Real Outcome，哪些只是好看的 Proxy，会系统性地奖励「看起来像对」？
- 闭环越强，Reward Hacking 的空间越大——评测器与执行器如何隔离，才能降低合谋？
- 什么规模的任务值得上完整实验开销；什么时候一条强基线 Prompt 就够？
- 外层策略优化如何保持诚实：怎样避免只拟合评测分布，而在真实任务上失效？
- Experiment Engineering 与 Complex System Engineering 的分界在哪里：何时该停在对照实验，何时必须设计环境、反馈与演化？
