---
id: from-llm-to-agent-runtime
type: Articles
title: 从 LLM 到 Agent Runtime：当“预测下一个 Token”开始进入真实世界
date: 2026-09-21
thought_date: 2026-09-21
published_date: 2026-09-21
tags: [LLM, Runtime, Agent, Inference]
excerpt: 从模型推理、KV Cache、Inference Runtime、Tool、Environment 和 Feedback 出发，思考为什么 Agent Runtime 是模型能力进入真实世界之后的新一层。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/from-llm-to-agent-runtime.md
last_verified: 2026-09-21
cadence_days: 90
---

# 从 LLM 到 Agent Runtime：当“预测下一个 Token”开始进入真实世界

如果把 LLM 简化成“根据上下文预测下一个 Token”，那么 Agent 的出现其实提出了一个更大的问题：**这个“下一个 Token”如何变成一个真正的 Action？Action 执行以后，模型又如何知道现实世界发生了什么？**我越来越觉得（目前仍是假设），Agent Runtime 正是在填补模型与真实世界之间的这层空间。

## 一、从模型内部走出来

Transformer 解决的是信息如何在模型内部流动；Decoder-only LLM 通过 Causal Mask 和 Next Token Prediction 形成强大的生成能力。但模型输出的本质仍然是一段 token 序列。

```text
LLM
 ↓
Token
 ↓
文本 / Tool Call / Structured Output
```

当输出只是文本时，系统可以直接把它交给用户。但当输出变成“执行一个命令”“修改一个文件”“查询数据库”“部署一个服务”时，事情发生了变化。

此时系统必须回答：这个 Action 能不能执行？在哪里执行？权限够不够？风险有多高？执行结果是什么？失败怎么办？下一步要不要继续？

## 二、我开始意识到：Inference 其实已经是一套系统工程

在模型层面，我们经常讨论 TTFT、TPOT、KV Cache、PagedAttention、量化、Batching 等问题。这些技术解决的是：**如何让模型更快、更高效、更便宜地完成推理。**

但当模型变成 Agent 后，推理不再是一次简单的 request → response：

```text
User Goal
   ↓
LLM
   ↓
Decision
   ↓
Tool / Environment
   ↓
Observation
   ↓
LLM
   ↓
Next Decision
   ↓
...
```

模型调用开始形成一个 Loop。

这里值得先划一条边界：Inference Runtime 负责“这一层推理如何更快、更便宜”——TTFT、TPOT、KV Cache、Batching 都是它的领域；Agent Runtime 则负责“下一步是否应该发生、在哪里执行、结果是否被验证”。KV Cache 属于前者，Sandbox 属于后者。

## 三、Tool 是模型伸向世界的“手”

我现在更愿意把 Tool 理解成模型能力与现实世界之间的接口，而不是简单的“函数列表”。

```text
LLM Capability
      ↓
   Tool Contract
      ↓
   Tool Gateway
      ↓
External System
```

模型负责提出下一步，但 Tool 需要提供明确的契约：输入是什么、输出是什么、权限是什么、失败如何表示、是否可重试、是否有副作用。

这也是为什么我之前对 MCP、OpenAPI、Tool Gateway 的兴趣越来越强：**模型能力要真正进入企业系统，必须经过一层可治理的能力接口。**

## 四、Sandbox：从“能调用”变成“在哪里执行”

尤其是 Code Agent 出现以后，我越来越觉得 Sandbox 是 Runtime 的重要组成部分。

```text
LLM：我要修改代码
        ↓
Runtime：这是高风险 Action
        ↓
Sandbox：隔离环境
        ↓
Compile / Test / Run
        ↓
Result
        ↓
LLM：根据结果继续决策
```

这里出现了一个关键变化：模型不再只输出“答案”，而是提出一个需要在环境中验证的行动。

因此 Runtime 必须知道什么时候启动 Sandbox、使用什么权限、允许访问哪些资源，以及什么时候需要 Human Gate。

## 五、Verification 比“执行成功”更重要

执行完成并不等于任务完成。

一个 API 返回 200，不代表业务目标已经实现；代码编译成功，也不一定意味着用户的问题解决了。

当然，这也有边界：当任务结果本身可以被确定性校验时——比如一次带 checksum 的查询、schema 验证通过的取数——执行成功就是任务成功，额外的业务验证反而是浪费。Verification 之所以重要，是在结果有歧义、有副作用、或需要领域语义判断的时候。

```text
Action
  ↓
Execution
  ↓
Observation
  ↓
Verification
  ↓
┌───────────────┐
│ Correct?      │
└──────┬────────┘
   No  │  Yes
       │
   Replan       Done
```

所以我越来越倾向于把 Agent Loop 理解成**不断缩小 Expected Outcome 与 Actual Outcome 之间的 Gap**，而不是简单的“执行工具”。

## 六、为什么 Agent Runtime 不能只是一个 Orchestrator

如果 Runtime 只是把 LLM、Tool、Memory 串起来，它更像一个 Workflow Engine。

下面这份职责清单更像是我的**工作假设**，而不是一份放之四海皆准的定稿要求：

- **Context：**管理当前任务真正需要的信息。

- **Scheduling：**决定什么时候继续推理、调用什么模型、消耗多少预算。

- **Tool Routing：**根据能力、权限、风险选择工具。

- **Sandbox：**提供隔离的执行环境。

- **Checkpoint：**保存任务状态，支持 Resume。

- **Verification：**判断行动结果是否真的满足目标。

- **Safety Gate：**在执行高风险 Action 前进行拦截或人工确认。

- **Observability：**记录 reasoning/action/tool/result 的完整链路。

需要说明的是，这些职责的“必要性”并不相同：其中一部分跨 Agent 类型都成立（比如 Observability，对调试和审计几乎总是必须的）；另一部分则取决于场景（Sandbox 主要对 Code Agent 必要，Checkpoint 主要对长任务必要，Safety Gate 在只读场景里会退化为简单的限流）。一个只读研究 Agent——查询公开 API、汇总、返回文本——的 Runtime 可以非常薄：没有 Sandbox，验证退化为 schema 校验，甚至不需要 Checkpoint。

所以更准确的说法是：Runtime 具体要承担什么，取决于 Agent 的动作是否可变、是否有副作用、是否长时间运行。真正的 Runtime 与 Workflow Engine 的区别，不在于“职责更多”，而在于它把**验证、状态与风险**当成一等公民。

## 七、从“模型错误”走向“系统错误”

在单轮 Chat 中，错误通常表现为模型回答错了。

Agent 系统里的错误则可能发生在很多地方：

```text
Model Error
Tool Error
Context Error
Routing Error
Permission Error
Environment Error
Verification Error
Human Feedback Error
```

因此 Agent 的可靠性不能只靠换一个更强的模型解决。

这也是我最近一直在想的一件事（目前仍是假设）：**Agent 的安全与正确性，应该逐步从“模型自己判断”转向“Runtime 在每一个关键 Action 上提供外部约束和验证”。更准确地说，Runtime 的约束是补充而不是替代模型层的防护——两者共同构成安全边界。**

## 八、模型只负责“下一步”，Runtime 负责“下一步是否真的发生”

如果把整个系统压缩成一句话，我现在会这样描述：

```text
LLM
负责：What should happen next?

Runtime
负责：Can it happen? Where? With what permission?
How should it execute? Did it really work?
What should happen after the result?
```

这让我重新理解了 Agent Runtime 的位置。

它不是 LLM 的一个简单包装层，也不是传统 Workflow 的换皮版本。它更像是一个**连接认知与执行的运行环境**。

## 九、从模型到 Runtime：我更愿意把它看作一层功能栈，而不是一条历史线

```text
Transformer（以 Self-Attention 为核心机制）
  ↓
LLM
  ↓
Inference Runtime
  ↓
Tool
  ↓
Environment
  ↓
Feedback
  ↓
Verification
  ↓
Agent Runtime
```

需要说明的是，这更像一层**功能栈**，而不是一条历史演化线：Attention 作为一种机制早于 Transformer 出现，Transformer 的贡献是把 Attention 变成核心并让它可并行；Tool、Environment 也完全可以独立于 LLM 存在——几十年前的专家系统就有工具调用和验证循环。每一层都可以单独存在或省略，是否叠加取决于你要解决的问题。

如果按依赖关系读：Transformer 让模型能够更好地理解和关联信息；LLM 把这些能力压缩进参数；Inference Runtime 让推理变得高效；Tool 让模型获得行动接口；Environment 提供真实执行空间；Feedback 和 Verification 则让系统知道行动是否有效。

最终，Agent 才不再只是“会回答问题的模型”，而成为一个能够持续感知、行动、观察和修正的系统。

## 十、我下一步更想研究的问题

如果这个方向成立，那么下一步的问题就不再只是“哪个 Agent Framework 更好”，而是：

- Runtime 的最小原语到底是什么？

- Agent 是否应该成为一种有生命周期、有状态的计算实体？

- Context、Memory 和 Checkpoint 如何分层？

- Risk Gate 应该位于 Model、Tool 还是 Runtime？

- Verification 能不能形成统一的 Outcome Contract？

- 多个 Agent 协作时，Runtime 是否会越来越像 Actor System？

这也是我最近从 Transformer 一直研究到 Agent Runtime 的原因：**我越来越不想只理解模型“怎么想”，而是想理解一个 AI 系统“怎么真正工作”。**以上这些方向目前都还是假设，尚未经过系统验证。
