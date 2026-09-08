---
id: from-function-to-ecosystem
type: Diverse Lab
title: 从函数到生态系统：重新理解大模型与 Agent
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Diverse, Physics, Ecology, LLM, Agent, Experiment, Complex Systems]
excerpt: 物理学给我们确定性规律，生态学提醒我们关系、反馈与概率；把两种心智放在一起，可以更准确地理解 LLM 为什么需要实验，也可以理解 Agent 为什么最终会走向环境与反馈闭环。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/diverse/from-function-to-ecosystem.md
---

# 从函数到生态系统：重新理解大模型与 Agent

我们习惯把软件系统理解成函数：给定输入，经过确定的逻辑，得到输出。

这个模型来自传统软件，也来自一种很强的工程直觉：只要把规则写清楚，系统就应该稳定地重复同一个结果。

但大模型出现以后，这个直觉开始出现裂缝。

我越来越觉得，理解这种裂缝，可以同时借用两种看起来距离很远的学科：**物理学与生态学**。

物理学帮助我们理解「规律」；生态学帮助我们理解「关系、反馈与适应」。而大模型与 Agent，恰好处在两者之间。

## 一、为什么大模型不像传统函数

传统程序通常可以近似成：

```text
Input
  ↓
Deterministic Logic
  ↓
Output
```

而一次大模型调用真正依赖的东西更多：

```text
Prompt + Context + History + Model + Tools + Decoding
                         ↓
                Conditional Distribution
                         ↓
                   One Sample
```

因此，同一个问题换一种上下文组织方式，结果可能改变；换一个示例，分布可能改变；换一个模型版本，行为可能改变；同一条件重复采样，也可能出现不同轨迹。

这并不意味着大模型「没有规律」。恰恰相反，它有规律，只是规律更多表现为**条件下的概率分布**，而不是简单的确定性映射。

所以真正值得问的问题不是：

> 「这一次为什么错了？」

而是：

> 「在什么条件下，它更容易正确？改变哪个变量，能够让成功概率提高？」

这就是科学实验思维进入 AI 工程的地方。

## 二、物理学给我们的启发：寻找可重复的规律

物理学最迷人的地方，是它不断尝试从复杂现象中寻找稳定关系。

工程师也天然喜欢这种思维：

- 控制变量
- 建立模型
- 测量结果
- 重复实验
- 寻找规律

因此，对于 LLM，一个好的工程方法不应该是不断试 Prompt，而应该逐渐变成：

```text
Hypothesis
    ↓
Experiment
    ↓
Observation
    ↓
Comparison
    ↓
Conclusion
    ↓
Next Hypothesis
```

比如我们怀疑「规则放在 Prompt 最前面更有效」，就应该固定模型、数据集和解码参数，只改变规则位置，然后重复采样。

结论也应该带边界：

> 在数据集 D、模型 M 和参数 Θ 下，条件 A 比条件 B 有更高的成功率。

而不是：

> 「这个 Prompt 永远更好。」

这也是为什么我认为 **Prompt Engineering 最终会逐渐长成 Experiment Engineering**。

## 三、但只用物理学的心智还不够

如果我们只用「输入 → 输出」去理解 Agent，很容易把 Agent 想成一个更大的函数。

但当系统开始拥有：

- Memory
- Tools
- Multiple Agents
- Environment
- Feedback
- External Side Effects
- Long-term State

事情开始发生变化。

Agent 不再只是回答一个问题，而是在一个环境里持续行动。

这时候，生态学的直觉开始变得有用了。

生态系统很少存在一个简单的：

```text
A → B
```

它更接近：

```text
A ↔ B
↑   ↓
C ↔ D
 \  /
 Environment
```

一个行为会改变环境，环境变化又会反过来影响下一步行为。

这与 Agent Loop 非常接近：

```text
Goal
 ↓
Action
 ↓
Environment
 ↓
Observation
 ↓
Gap
 ↓
Adjustment
 ↺
```

## 四、Agent 真正复杂的地方，是反馈而不是模型

单个 LLM 很强，但一个 Agent 系统真正变复杂的地方，往往不是模型本身，而是模型进入了一个反馈系统。

例如一个 Agent 要「降低工厂能源消耗」：

1. 读取设备数据
2. 判断当前状态
3. 调整设备
4. 观察功率变化
5. 发现温度又升高
6. 调整策略
7. 继续观察

这里已经不是「Prompt → Answer」的问题。

它变成：

```text
Goal
 ↓
Policy
 ↓
Action
 ↓
Environment
 ↓
Observation
 ↓
Outcome
 ↓
Policy Adjustment
 ↺
```

Agent 的能力因此越来越像一种**环境中的适应能力**。

## 五、概率性并不等于不可工程化

这是我觉得最容易产生误解的一点。

「概率性」并不意味着「不可控」。

天气是概率性的，但气象学仍然可以工作；生态系统高度复杂，但生态学仍然可以研究；金融市场充满噪声，但统计模型仍然可以提供有价值的预测。

工程目标发生了变化：

```text
确定性系统：
Input → Output

概率性系统：
Conditions → Distribution → Outcome
```

因此评价 Agent 时，也应该从「这次回答对不对」逐渐走向：

- Success Rate
- Error Distribution
- Cost
- Latency
- Consistency
- Held-out Performance
- Real Outcome

一次漂亮的回答只是一个样本。

真正值得沉淀的是**在什么条件下，系统更可靠**。

## 六、Proxy Metric 不等于真实结果

复杂系统还有一个危险：我们很容易把代理指标当成真实目标。

例如：

```text
Tool Call = PASS
API Test = PASS
Workflow = SUCCESS
Model Self-Eval = PASS

          ≠

Real Outcome = SUCCESS
```

一个 Agent 可以把所有测试跑绿，却没有真正解决用户的问题。

这和科学实验中的「测量指标是否真的代表研究对象」是同一个问题。

所以我越来越倾向于把任务结果拆成三层：

1. **Proxy**：过程是否正常
2. **Evidence**：是否存在可以核对的证据
3. **Outcome**：真实目标是否完成

当 Ground Truth 缺失时，可以使用 Proxy，但必须记录它与真实结果之间的 gap。

## 七、从 Experiment Engineering 走向 Loop Engineering

科学实验解决的是「如何知道什么条件更好」。

Agent Loop 进一步解决的是「知道以后，系统如何自己调整」。

所以两者其实是一条连续的路线：

```text
Experiment Engineering
        ↓
Evaluation
        ↓
Policy / Strategy
        ↓
Agent Loop
        ↓
Environment Feedback
        ↓
Next Experiment
```

这也是我理解 Loop Engineering 的方式。

它不是把 Workflow 写得更复杂，而是让**现实结果成为下一步行动的输入**。

Workflow 更像：

```text
Step A → Step B → Step C
```

Loop 更像：

```text
Goal → Action → Observation → Gap → Next Action
```

前者假设路径基本知道；后者承认路径需要在运行过程中被发现。

## 八、最终会从模型工程走向环境工程

如果继续往前推，我认为 Agent Engineering 的对象会不断扩大：

```text
Model
  ↓
Prompt
  ↓
Agent
  ↓
Runtime
  ↓
Multi-Agent
  ↓
Environment
  ↓
Feedback
  ↓
Evolution
```

模型仍然重要，但它只是系统中的一个参与者。

真正决定系统长期能力的，是模型如何与工具、记忆、其他 Agent 和环境发生关系，以及这些关系能不能形成稳定的反馈闭环。

这也是为什么我越来越喜欢把 Agent 和生态系统放在一起思考。

不是说 Agent 就是生态系统，而是它们共享一种重要的工程心智：**系统的行为来自参与者、环境和反馈之间的持续互动。**

## 九、我现在更愿意这样理解 AI 工程

如果把这几次思考压缩成一句话：

> **物理学提醒我们寻找规律，生态学提醒我们观察关系，科学实验告诉我们如何验证，而 Agent Engineering 要把这些东西变成可以运行的反馈系统。**

所以未来 AI 工程可能不只是「模型工程」。

它会同时包含：

- **Model Engineering**：让模型更强
- **Experiment Engineering**：知道什么条件更有效
- **Agent Engineering**：让系统能够行动
- **Loop Engineering**：让系统根据现实反馈调整
- **Environment Engineering**：让 Agent 在一个可观测、可调用、可验证的世界里工作

到了这个阶段，我们真正构建的已经不只是一个 AI 应用。

而是一个能够**观察、行动、反馈、修正和演化的系统**。

> 从函数到实验，从实验到循环，从循环到生态系统。
>
> 这可能是理解下一代 AI 系统的一条重要路径。
