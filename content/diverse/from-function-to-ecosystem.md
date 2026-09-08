---
id: from-function-to-ecosystem
type: Diverse Lab
title: 从函数到生态系统：重新理解大模型与 Agent
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Diverse, Physics, Ecology, LLM, Agent, Experiment, Complex Systems]
excerpt: 从我们关于科学实验、物理学、生态学与 Agent 的讨论出发：大模型需要用实验思维理解，Agent 则进一步进入环境、反馈与持续调整的问题。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/diverse/from-function-to-ecosystem.md
---

# 从函数到生态系统：重新理解大模型与 Agent

这篇文章不是在给 AI 套一个新的理论，而是把我们最近几次讨论串起来。

我们先讨论了一个很直接的问题：为什么使用大模型，越来越像做科学实验？后来又谈到：为什么物理学里的规律通常比较确定，而生态学面对的却是概率、多变量和复杂关系？再往后，这个问题自然进入了 Agent：当模型不再只是回答问题，而是开始调用工具、改变环境、获得反馈，系统就不再只是一个「输入 → 输出」的函数。

所以我现在更愿意把这几个问题放在一起看：**从函数，到实验，再到一个具有反馈关系的系统。**

## 一、为什么大模型不像传统函数

传统软件很容易形成这样的工程直觉：

```text
Input
  ↓
Deterministic Logic
  ↓
Output
```

但大模型并不是这么简单。

同一个问题，Prompt 的写法、上下文的位置、历史信息、模型版本、采样参数，都可能影响最终结果。

所以我们之前讨论「为什么一个提示词放在前面，模型似乎更容易记住」时，真正重要的并不是马上给出一个确定解释，而是把它当成一个可以验证的假设。

更准确的方式应该是：

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
```

也就是说，**不要把一次模型行为直接当成规律。**

## 二、为什么我越来越觉得应该用科学实验的方式使用大模型

我们讨论过一个很重要的变化：以前使用软件，通常是在调用确定的能力；现在使用大模型，很多时候是在观察一个概率系统在不同条件下的行为。

因此，如果我们发现一个 Prompt 有效，真正应该问的是：

> 是什么条件让它有效？

比如我们怀疑「某条规则放在 Prompt 前面更容易被模型遵循」，就可以固定其他条件，只改变规则的位置，然后重复实验。

这样得到的结论才有意义：

```text
条件 A → 成功率 X
条件 B → 成功率 Y
```

而不是直接得到：「Prompt 放前面一定更好。」

这也是我们讨论到的一个判断：**使用大模型，应该越来越接近科学实验的思维。**

## 三、物理学和生态学为什么给了我两种不同的感觉

我们后来又讨论了一个问题：为什么物理学给人的感觉往往比较确定，而生物学、生态学则更加概率化、多元化？

一个重要区别是，我们观察到的系统不同。

物理学经常试图寻找可以重复验证的稳定规律；生态系统则包含大量相互作用的个体、环境和反馈关系。

所以可以粗略地形成两种不同的观察方式：

```text
物理学
寻找稳定规律
     ↓
控制变量
     ↓
重复验证
```

以及：

```text
生态系统
多主体 + 多变量 + 相互作用
        ↓
      反馈
        ↓
    状态变化
        ↓
    下一轮行为
```

这并不是说物理学没有概率，也不是说生态学没有规律，而是面对复杂系统时，不能只期待一个简单、确定的输入输出关系。

## 四、这个区别为什么又回到了 Agent

如果只看一次 LLM 调用，我们仍然可以把它理解成：

```text
Prompt → Answer
```

但 Agent 不一样。

当 Agent 开始拥有 Tool、Memory，并且能够对外部环境产生影响以后，它的行为就变成了一个连续过程：

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
Next Action
 ↺
```

这也是我们讨论 Loop Engineering 时形成的一个核心理解：**Loop 不是把 Workflow 写得更复杂，而是让现实结果进入下一步决策。**

Workflow 更接近：

```text
A → B → C
```

Loop 更接近：

```text
Goal → Action → Observation → Gap → Adjustment
```

前者的路径基本已经知道；后者需要根据实际结果继续调整。

## 五、Agent 的复杂性开始来自环境和反馈

所以我现在不太愿意把 Agent 简单理解成「一个更强的模型」。真正让 Agent 复杂起来的，是它进入了一个环境。

例如我们讨论 IoT 和制造业时，Agent 并不是只生成一段文字，而可能需要：

```text
读取设备状态
     ↓
判断当前情况
     ↓
调用设备能力
     ↓
观察设备变化
     ↓
判断是否达到目标
     ↓
继续调整
```

这时候，模型只是其中的一部分。

工具、设备、数据、环境和反馈共同决定了系统最后的行为。

所以 Agent 和生态系统之间真正值得类比的地方，不是「Agent 就是生态系统」，而是：

> **系统的行为开始来自参与者、环境和反馈之间的持续互动。**

## 六、概率性不代表不能工程化

这也是我们讨论中我比较在意的一点。

大模型具有概率性，并不意味着工程师只能接受「它有时候就是这样」。恰恰相反，概率性意味着我们需要换一种工程方式。

从：

```text
Input → Output
```

逐渐变成：

```text
Conditions → Behavior Distribution → Outcome
```

因此，与其只看某一次回答，不如记录：

- 什么条件下成功
- 什么条件下失败
- 失败是什么类型
- 改变了什么之后发生变化
- 是否可以在新的任务上复现

一次成功只是一个样本。

真正有价值的是找到**成功和失败背后的条件与规律**。

## 七、Proxy Metric 不等于真实结果

我们在讨论 Agent 优化时还碰到过一个很实际的问题：**测试通过，不代表用户的问题真的解决了。**

例如：

```text
API PASS
Test PASS
Workflow SUCCESS

       ≠

用户真正的问题已经解决
```

这就是 Proxy Metric 和 Real Outcome 的区别。

如果一个 Agent 的评测只看 API 是否调用成功、测试是否通过，它可能会越来越擅长「通过测试」，但不一定越来越擅长解决真实问题。

所以我们后来讨论 Agent Optimizer 时，特别强调了几个东西：

```text
Task Fingerprint
Ground Truth Status
Divergence Flag
Cost
```

尤其要区分：

```text
Test Verified
User Confirmed
Unverified
```

这其实和科学实验的思维又连起来了：**测量指标必须尽可能接近我们真正想知道的东西。**

## 八、从实验，到 Loop

到这里，我觉得几件事情已经连起来了。

科学实验解决的是：

> 怎样知道什么条件更有效？

Loop Engineering 解决的是：

> 当现实结果和目标存在差距时，系统下一步怎么调整？

所以它们可以连接成：

```text
Hypothesis
    ↓
Experiment
    ↓
Observation
    ↓
Evaluation
    ↓
Strategy
    ↓
Agent Action
    ↓
Environment Feedback
    ↓
Next Action / Next Experiment
```

这也是我现在理解 Agent 的一个重要变化：**Agent 不只是生成 Action，而是要面对 Action 产生的真实结果。**

## 九、从「函数」到「关系」

如果把这几次讨论再往前推一步，我觉得我们真正改变的可能不是某一个模型，而是理解软件系统的方式。

传统软件很容易从函数出发：

```text
调用什么函数？
调用哪个 API？
执行哪个 Workflow？
```

Agent 开始以后，问题逐渐变成：

```text
我要达到什么目标？
我现在在哪里？
我能使用什么能力？
现实发生了什么？
距离目标还有多远？
下一步应该怎么做？
```

这也是为什么我们后来会把 Agent 和 Kubernetes 联系起来。

Kubernetes 最值得借鉴的并不是「Pod 对应 Agent」，而是它背后的 **Desired State → Actual State → Reconcile** 思维。

Agent 也可以理解成：

```text
Goal / Desired Outcome
          ↓
       Action
          ↓
   Actual Environment
          ↓
      Observation
          ↓
          Gap
          ↓
      Adjustment
          ↺
```

这里已经不再只是函数调用，而是一个持续的关系和反馈系统。

## 十、我现在更愿意这样理解这条路线

如果把我们最近关于 LLM、物理学、生态学、科学实验、Agent 和 Loop 的讨论压缩起来，我会得到这样一条路线：

```text
传统软件
   ↓
函数 / API
   ↓
Workflow
   ↓
LLM
   ↓
实验与评测
   ↓
Agent
   ↓
Loop
   ↓
环境与反馈
```

这并不是说后面的东西会把前面的东西全部替代。

我们讨论 SaaS、IoT 和制造业时也一直在强调：**原来的微服务、Workflow、规则系统并不需要被推倒重来。**

它们依然负责确定性的事情。

变化的是上层的控制方式：从「调用哪个函数」，逐渐走向「如何让系统达到目标」。

所以我现在更愿意把 Agent 理解成一种新的系统控制方式，而不只是一个新的 AI UI。

> 从函数到实验，从实验到循环，再从循环进入环境。
>
> 这可能是我目前理解大模型和 Agent 的一条比较自然的思考路径。
