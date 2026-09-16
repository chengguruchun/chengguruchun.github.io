---
id: h-neurons-paper-reading
type: Diverse Lab
title: H-Neurons：幻觉可能藏在模型内部的稀疏神经元中
date: 2026-09-16
thought_date: 2026-09-16
published_date: 2026-09-16
tags: [Diverse, Interpretability, Hallucination, Agent Runtime, LLM]
excerpt: 从神经元层面理解 hallucination、over-compliance 与预训练起源，并思考内部风险信号如何进入 Agent Runtime。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/diverse/h-neurons-paper-reading.md
last_verified: 2026-09-16
cadence_days: 180
---

# H-Neurons：幻觉可能藏在模型内部的稀疏神经元中

**论文：***H-Neurons: On the Existence, Impact, and Origin of Hallucination-Associated Neurons in LLMs*，Cheng Gao 等，arXiv:2512.01797。论文从 identification、behavioral impact、origin 三个角度研究 hallucination-associated neurons。

## 1. 这篇论文真正问了什么？

过去我们通常从数据、训练目标、RLHF、解码策略等宏观角度解释幻觉。这篇论文反过来问：**如果把 LLM 打开到神经元层面，是否存在一小部分内部单元，它们的激活状态与 hallucination 稳定相关？**

作者把这类神经元称为 **H-Neurons**，并进一步追问两个问题：这些神经元只是“报警器”，还是会影响模型行为？它们是在 alignment 阶段产生，还是在 pre-training 阶段就已经存在？

## 2. 最核心的发现：非常少的神经元也能预测幻觉

论文发现，少于模型全部神经元 **0.1%** 的一个稀疏子集，就能够较可靠地预测 hallucination 的发生，并且在不同场景下具有较好的泛化能力。

这个结果有意思的地方不只是“0.1% 很少”，而是它暗示：**模型的某些复杂宏观行为，可能由非常稀疏的内部表征参与触发或调节。**

## 3. 作者怎么找到它们？

官方实现给出的流程大致是：多次采样模型回答 → 抽取事实性 token → 构造 balanced 的 truthful / hallucinated 样本 → 提取 neuron activations → 量化 neuron contribution → 用 sparse logistic regression 找到具有预测能力的神经元。

这里我觉得有一个很重要的实验思想：作者不是直接观察某个 neuron“看起来像在产生幻觉”，而是先把**可观察行为标签**建立起来，再反过来寻找内部 activation 与行为之间的关系。

## 4. 第二个发现：它不只是相关，还和“过度顺从”有关

论文进一步做了 controlled intervention。结果显示，对 H-Neurons 进行干预会影响模型的 **over-compliance** 行为，因此作者认为这些神经元与该行为存在因果联系，而不仅仅是一个相关性指标。

这里需要区分两件事情：论文的实验支持的是**在其设置下对这些神经元进行干预会改变行为**；这并不意味着已经找到了一个可以解释所有 hallucination 的“幻觉开关”。

## 5. 第三个发现：H-Neurons 可能在预训练阶段就形成

作者继续把这些神经元追溯到 pre-trained base model，发现它们在基础模型中仍具有 hallucination detection 的预测能力，因此论文认为这些与幻觉相关的内部机制可能在**预训练阶段**已经出现，而不是完全由 post-training alignment 引入。

这点对理解 LLM 很重要：我们今天看到的“模型行为”，可能不是 instruction tuning 或 system prompt 单独创造出来的，而是在更早的训练阶段已经形成了一些潜在的内部结构，后续训练只是改变它们的表达和使用方式。

## 6. 这和我之前对“大模型要像做科学实验一样使用”的想法有什么关系？

我之前有一个判断：面对 LLM，不能只把 prompt 当成“写得更好一点”，而应该更像做实验——提出假设、控制变量、观察结果、记录反馈。

H-Neurons 其实提供了一个更底层的版本：

```text
宏观行为
   ↓
定义可观察指标
   ↓
采样 / 对照
   ↓
提取内部 activation
   ↓
寻找相关结构
   ↓
干预
   ↓
观察行为是否改变
```

也就是说，LLM 的一些看似“玄学”的行为，可以逐渐被转化成**可测量、可干预、可复现的实验对象**。

## 7. 对 Agent Runtime 的启发

这篇论文让我重新思考 Agent Runtime 的“验证”应该放在哪里。

我们之前讨论 Agent 时，验证主要发生在外部世界：Code Agent 跑 test，IoT Agent 看设备状态，业务 Agent 看任务结果。但 H-Neurons 提醒我们：**模型内部也可能存在可以被观测的风险信号。**

因此未来 Agent Runtime 可能出现两类 feedback：

- **External feedback：**工具执行结果、测试结果、环境状态、用户确认。

- **Internal feedback：**模型 hidden state / activation 中与不可靠行为相关的信号。

于是 Agent 的可靠性闭环可能从：

```text
LLM → Tool → External Verify → Re-plan
```

进一步变成：

```text
LLM
 ↓
Internal Risk Signal
 ↓
Tool / Action
 ↓
External Verification
 ↓
Re-plan
```

但这里目前只能作为研究方向，不能把 H-Neurons 直接当成生产环境里的 hallucination detector。

## 8. 一个更深的思考：模型能力和 Harness 能力可能要分开

这篇论文让我想到我们之前讨论过的一个问题：**Agent 的可靠性究竟来自模型本身，还是来自 Runtime / Harness？**

H-Neurons 更偏向“模型内部机制”这一侧：模型本身可能存在与不可靠行为相关的稀疏结构。

而 Agent Runtime 则是另一侧：它可以通过 context engineering、tool feedback、verification、retry、checkpoint、memory 等机制，把模型内部的不确定性限制在一个可控的执行闭环里。

所以我现在更倾向于把 Agent reliability 看成：

```text
Reliability
= Model Internal Mechanism
+ Context / Harness
+ External Verification
+ Runtime Recovery
```

而不是单纯期待“换一个更强的模型”解决所有问题。

## 9. 需要保持的谨慎

这篇论文很有启发性，但它不应该被解读成“已经找到 hallucination 的根因”。论文研究的是特定模型、任务和实验设置下的神经元层现象；“预测幻觉”“因果影响 over-compliance”和“幻觉的完整机制”是三个不同层次的问题。

尤其是 **H-Neurons ≠ 一个通用的幻觉开关**。真正要走向工程应用，还需要验证跨模型、跨任务、跨领域的稳定性，以及干预是否会损害模型正常能力。

## 10. 我的总结

我认为 H-Neurons 最有价值的地方，是它提供了一条从**宏观行为 → 微观机制 → 干预验证**的研究路径。

过去我们说“LLM 会幻觉”，通常停留在行为层；这篇论文尝试继续往下追：

```text
为什么会产生这种行为？
        ↓
模型内部哪些 activation 与它相关？
        ↓
这些 activation 能否预测？
        ↓
干预它们会不会改变行为？
        ↓
这些结构什么时候形成？
```

这让我对 Agent 的一个判断更加明确：**未来 Agent engineering 不一定只是把模型包在更多工具和 workflow 外面，也可能逐渐进入“模型内部机制 + 外部 Runtime”共同设计的阶段。**

如果说 IoT Agent 的方向是从 **Next API → Next State**，那么 LLM reliability 的一个可能方向就是从 **Next Token → Next Internal State → Next Verified Outcome**。

## 参考

- [H-Neurons · arXiv](https://arxiv.org/abs/2512.01797)

- [H-Neurons · Official GitHub](https://github.com/thunlp/H-Neurons)
