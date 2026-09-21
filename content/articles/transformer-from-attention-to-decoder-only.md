---
id: transformer-from-attention-to-decoder-only
type: Articles
title: 从 Transformer 到 Decoder-only：我重新理解大语言模型是怎么“学会”的
date: 2026-09-21
thought_date: 2026-09-21
published_date: 2026-09-21
tags: [Agent, Transformer, LLM, Attention]
excerpt: 从一次关于 Transformer 的追问出发，重新理解 Self-Attention、Encoder-Decoder、Decoder-only，以及训练与推理到底有什么不同。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/transformer-from-attention-to-decoder-only.md
last_verified: 2026-09-21
cadence_days: 90
---

# 从 Transformer 到 Decoder-only：我重新理解大语言模型是怎么“学会”的

我原来试图把大模型理解成“训练时负责学习，线上时负责回答”的两个阶段。继续追问以后，我发现真正值得理解的不是“Encoder 负责训练、Decoder 负责推理”这样一个简单对应，而是：**同一套参数化模型，如何通过 Attention 学习 token 之间的关系，又如何在生成时把这种能力转化成一次次 Next Token Prediction。**

## 一、我为什么一直追问 Encoder 和 Decoder

最开始我的直觉很自然：Encoder 像一个阅读者，负责理解输入；Decoder 像一个写作者，负责按照顺序生成输出。经典 Transformer 的 Encoder-Decoder 结构确实非常适合用机器翻译来理解：Encoder 读取源语言，Decoder 根据已经生成的内容逐步产生目标语言。

但这个解释很快遇到了一个问题：今天我们熟悉的 GPT、Qwen、DeepSeek 等生成式大模型，为什么很多都不再保留完整的 Encoder-Decoder，而采用 Decoder-only？如果 Decoder 只是“生成”，它又是怎么学到语言、知识、代码以及各种世界规律的？更准确地说，Decoder-only 是在“开放域对话、指令跟随”这类任务上胜出的选择——机器翻译（T5、BART）、语音识别（Whisper）等场景里，Encoder-Decoder 至今仍然很常见。

这个问题最终把我带回了 Transformer 最核心的创新：**Self-Attention。**

## 二、Transformer 真正改变的，可能不是“神经网络”，而是 token 之间建立关系的方式

在更早的序列模型里，信息更倾向于沿着序列逐步传播。Transformer 则提供了一种不同的思路：对于一个 token，可以计算它与上下文中其他 token 的关系。

```text
Token A ─┐
Token B ─┼──→ Attention → 当前 token 的上下文表示
Token C ─┤
Token D ─┘
```

这意味着模型不必只能依赖“前一个 token 传过来的信息”，而可以直接建立更远距离的关联。Multi-Head Attention 又把这种关系拆成多个并行的“观察角度”，不同 head 可以学习不同类型的模式。

所以我现在更愿意这样理解 Transformer：**它把“序列处理”转化成了“关系计算”。**

## 三、Encoder 与 Decoder 的真正区别：Attention Mask，而不是“块的名字”

回到最初的直觉：Encoder 像一个阅读者，Decoder 像一个写作者。这个直觉在机器翻译里确实好用，但追问到机制层面，真正起作用的不是“它叫 Encoder 还是 Decoder”，而是 Attention 的 Mask 模式。

Encoder 使用**双向注意力**：每个位置都可以利用完整输入上下文，因此天然适合做表征学习、分类、匹配等任务。一个句子输入以后，每个 token 都可以结合整个句子的语境形成表示。

Decoder 则使用**因果注意力（Causal Mask）**。简单说，在预测当前位置时，模型不能看到未来 token：

```text
A B C D E
↑ ↑ ↑ ↑ ↑
每个位置只能使用它左侧已经出现的信息
```

这并不是说 Decoder 没有 Attention，而恰恰相反：**Attention 仍然是 Decoder 的核心，只是未来的信息被 mask 掉。**

所以 Encoder / Decoder 这两个名字，更多是原版 Transformer 论文为“翻译”任务留下的历史命名；真正决定行为差异的是 Mask 模式，而不是块的标签。理解了这一点，后面 Decoder-only 为什么能成为主流，就不再是意外。

## 四、我曾经把“预训练”和“推理”理解成 Encoder 与 Decoder 的切换

这是我在讨论过程中反复确认的地方。最初我的理解是：预训练时模型需要看到完整句子、学习前后关系，所以应该使用 Encoder；真正回答用户问题时，再切换到 Decoder，用掩码注意力预测下一个 token。

继续追问后，我发现这个模型不适用于今天主流的 Decoder-only LLM。

对于 Decoder-only LLM，**预训练阶段本身就使用 Causal Mask**。模型学习的目标就是：给定前面的 token，预测下一个 token。

因此更准确的图应该是：

```text
海量训练数据
     ↓
Decoder-only Transformer
+ Causal Mask
     ↓
Next Token Prediction（预训练）
     ↓
微调 + 强化学习（SFT、RLHF/DPO）
     ↓
得到可对话、可遵循指令的模型

真实用户输入
     ↓
同样的 Decoder-only 结构
+ Causal Mask
     ↓
逐步预测下一个 Token
     ↓
生成回答
```

这里补上了一个我原先忽略的环节：**后训练（对齐）**。预训练产出的基座模型并不会天然以“回答问题”的方式输出，真正让模型学会跟随指令、按用户期望组织回答的，是后续的微调与强化学习阶段（详见下一节）。所以“结构相同”是对的，但“同一份权重”并不完全成立——线上服务的 chat 模型通常是经过对齐的版本。

## 五、微调与强化学习：预训练模型是怎么“学会回答问题”的

如果只做预训练，模型学到的能力本质上是“续写”：给它一段文本，它接下去。预训练基座模型会补全句子、模仿风格，但它并不会自动以“回答用户问题”的方式组织输出——它可能继续提问、继续铺陈背景，甚至不理会指令。

让模型“会对话”主要靠两个阶段：

- **监督微调（SFT，Supervised Fine-Tuning）：**准备大量“指令 → 期望回答”的样本，让模型在这些真实回答上继续训练。这本质上是把“按用户指令作答”也变成一次 Next Token Prediction 的学习。微调之后，模型学会了回答的格式、语气，以及最基本的指令遵循。

- **强化学习（RLHF / DPO）：**光模仿样本还不够——样本无法穷尽所有情形，而且人工写的答案也不一定是最受欢迎的。强化学习阶段用奖励来优化行为：RLHF 先收集人类对多个回答的偏好来训练一个奖励模型，再用 PPO 等算法让模型生成更受偏好的输出；DPO 则直接利用偏好数据优化，不再需要单独的奖励模型。这个阶段在很大程度上决定了模型是否乐于助人、是否愿意承认不知道、是否更少输出有害内容。此外，面向推理的强化学习（用可验证的奖励来优化思考过程）也在进一步强化模型的推理能力。

所以今天“同一个 Decoder-only 结构”背后的完整链条是：**预训练学会语言与世界知识 → 监督微调学会跟随指令 → 强化学习优化行为偏好**。这也解释了文末那个问题的一半：模型能按用户意图组织回答、调用工具，并不完全是预训练的自然涌现——指令跟随和工具调用的格式，正是对齐阶段显式教给模型的。

## 六、那么训练和推理到底有什么不同？

结构可以相同，但计算过程并不相同。

训练时，完整的训练序列已经存在，因此 GPU 可以同时计算大量位置上的 next-token prediction。虽然每个位置仍然不能“偷看未来”，但不同位置的计算可以高度并行。这里的关键机制是 Teacher Forcing：训练时每个位置的前缀都来自真实数据，所以可以放心并行；即使某个位置预测错了，错误也不会进入下一轮训练输入。

推理时，未来 token 并不存在。模型先生成一个 token，把它加入上下文，再生成下一个 token。因此生成过程天然具有自回归特征，而且每一步的前缀来自模型自己的采样——一旦某个 token 生成偏了，错误会进入下一轮输入并被放大，这就是 Exposure Bias：

```text
A → 预测 B
A B → 预测 C
A B C → 预测 D
A B C D → 预测 E
```

所以真正重要的区别不是“训练使用 Encoder、推理使用 Decoder”，而是：

**训练是在已知序列上并行学习 Next Token Prediction；推理是在未知未来上逐步执行 Next Token Prediction。**

## 七、“训练集 → 真实问题”这个类比，我为什么仍然觉得有价值

严格来说，用户线上请求不能直接等同于机器学习意义上的 test set。真正的测试集通常是独立保留的数据，用于评估泛化能力。

但我的原始直觉仍然有价值：模型在训练阶段从历史数据中形成参数化能力，部署以后面对的是新的、真实的上下文，需要验证这种能力能否泛化到真实问题。

因此我更愿意把它表达成：

```text
训练：从历史数据中学习规律
        ↓
参数：把学习结果压缩进模型
        ↓
推理：在新的上下文中调用这些能力
        ↓
真实结果：检验泛化是否成立
```

这也为我后面理解 Agent 打下了一个很重要的基础：**模型拥有能力，不等于系统已经完成任务。**

## 八、从“Attention”继续往下追：为什么长 Context 仍然会成为问题？

我在讨论中又遇到了一个新的疑问：既然 Attention 可以建立 token 之间的关系，为什么长上下文里仍然会出现信息利用不充分的问题？为什么重要信息的位置、上下文组织方式，会影响模型表现？

这让我意识到，“Context Window 很长”和“模型能有效利用所有 Context”不是一回事。Attention 是关系计算机制，但并不意味着每条信息都会被同等有效地利用。

这也正好连接到了我一直在研究的 Context Engineering：真正的工程问题开始从“模型有多大的窗口”，转向“哪些信息应该进入上下文、如何组织、什么时候更新，以及哪些信息应该交给外部系统”。

## 九、我现在对 Transformer 和 LLM 的一个阶段性理解

如果把今天的理解压缩成几句话：

- **Transformer 的核心突破：**用 Self-Attention 高效建立 token 之间的关系。

- **Encoder：**更适合利用完整输入上下文形成表征。

- **Decoder：**通过 Causal Mask 保持自回归生成。

- **Decoder-only LLM：**把大量能力统一到 Next Token Prediction 这个训练目标上。

- **训练：**已知序列上的并行学习。

- **推理：**未知未来上的自回归生成。

- **后训练：**微调（SFT）+ 强化学习（RLHF/DPO），让模型从“会续写”变成“会回答”。

以上是我目前的阶段性理解，其中几处表述需要标明边界：比如“Decoder-only 更优”应限定在开放域对话 / 指令跟随这类任务上；又比如“训练并行、推理自回归”的区分，在推测解码、chunked prefill 等工程优化下会变得模糊——并行度是工程后果，不是定义。

而最让我感兴趣的是最后一步：如果 LLM 的基本动作仍然是“预测下一个 Token”，为什么它已经可以表现出复杂的推理、规划和工具使用能力？这个问题一半的答案在模型内部——正如第 5 节所说，微调与强化学习让模型学会遵循指令、按任务组织输出；另一半才轮到模型之外的系统去回答。

这个问题把我自然带到了下一篇文章。

## 下一步：模型之外发生了什么？

如果说 Transformer 解决的是“模型如何处理信息”，LLM 解决的是“根据上下文生成下一步”，那么当模型真正进入现实系统之后，还需要解决另一个问题：

**生成出来的下一步，如何真正作用于世界，并获得反馈？**

这就从 Model 走向了 Inference Runtime、Tool、Environment、Verification 和 Agent Runtime。
