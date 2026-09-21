---
id: agent-runtime-cognitive-actor
type: Articles
title: 从 Actor Model 到 Cognitive Actor：Claude Agent Teams 给 Agent Runtime 的启发
date: 2026-09-20
thought_date: 2026-09-20
published_date: 2026-09-20
tags: [Agent, Runtime, Akka, Actor Model]
excerpt: 从 Akka Actor、Mailbox、Supervisor、Sharding 出发，分析 Claude Agent Teams、多 Agent 通信与 Agent Runtime 的演化。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-runtime-cognitive-actor.md
last_verified: 2026-09-20
cadence_days: 90
---

# 从 Actor Model 到 Cognitive Actor：Claude Agent Teams 给 Agent Runtime 的启发

这不是“Claude Team = Akka + LLM”的结论，而是一种架构观察：当 Agent 从一次调用变成长期运行、可并行、可协作、有状态的计算实体时，系统自然会重新遇到 Actor Model 已经解决过的一些问题——消息、调度、生命周期、监督、状态和分布式路由。Agent 的特殊之处在于，它还增加了一层传统 Actor 没有的东西：**reasoning → action → observation → verification** 的认知闭环。

## 一、为什么我会想到 Akka

过去讨论 Multi-Agent，重点往往是 Prompt、Planner、Graph 和 Workflow。但当 Agent 开始并行执行、互相传递任务、持续运行几个小时甚至几天以后，问题就变成：谁负责调度？Agent 如何通信？状态在哪里？失败以后怎么办？任务如何恢复？多个 Agent 如何避免互相踩踏？这些已经更像分布式计算。

Akka 的 Actor Model 给出了一个简洁抽象：Actor 拥有自己的状态和行为，通过 Mailbox 接收消息，由执行环境负责调度；Actor 之间通过消息而不是直接调用协作，并通过 supervision 处理失败。[Akka Actor Model](https://doc.akka.io/libraries/akka-core/current/typed/guide/actors-intro.html)

## 二、Claude Agent Teams 为什么让我重新看到这个模型

Anthropic 的并行 Agent 实践展示了一个明显趋势：多个 Claude 实例可以并行工作在一个复杂目标上，而不是所有事情都由一个中心 Agent 串行完成。在公开的 C Compiler 实验中，16 个 Agent 并行推进一个 Rust C Compiler；运行 harness 使用任务锁、共享代码库、Git 同步和持续测试协调工作，而且没有依赖一个中央 Orchestrator。[Anthropic：Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)

```text
Goal
                     ↓
              ┌────────────┐
              │Agent Runtime│
              └──────┬─────┘
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Agent A     Agent B     Agent C
          ↕           ↕           ↕
       Message      Task       Artifact
```

这让我更愿意把 Multi-Agent 看成一种**分布式自治计算**，而不是“把几个 LLM 串起来”。

## 三、Actor 与 Agent：相似，但不是一回事

Actor SystemAgent RuntimeActorAgent / Cognitive ActorMailboxSemantic MailboxMessageTask / Event / Semantic MessageBehaviorReasoning + Policy + ToolsStateContext + Memory + Task StateDispatcherCognitive SchedulerSupervisorFailure + Semantic + Security SupervisorCluster ShardingAgent ShardingPersistenceCognitive Checkpoint但不要因此把二者等同。Actor 的 Behavior 通常是确定性的程序逻辑；Agent 的 Behavior 是概率性的认知过程：

```text
Actor
message → behavior → state update

Agent
message → context → reasoning → plan → action
       → observation → verification → next decision
```

所以我更愿意使用一个新的词：**Cognitive Actor**。

## 四、Mailbox 正在变成 Semantic Mailbox

Akka 的 Mailbox 可以理解为消息队列。Agent 的消息却往往是一个带意图和约束的任务：

```text
{ intent, context, constraints, priority,
  deadline, risk, artifacts, expected_outcome }
```

因此 Agent Runtime 的消息系统可能不应该只做 FIFO，而应该理解优先级、依赖、风险和语义相关性。消息也不只包括 Task，还包括 Event、Result、Verification Feedback 和 Human Instruction。

## 五、从 Dispatcher 到 Cognitive Scheduler

Akka Dispatcher 主要解决“哪个 Actor 获得执行机会”。Agent Runtime 的 Scheduler 则要决定“哪个 Agent、在什么时间、使用什么模型和多少计算预算继续推理”。

```text
Cognitive Scheduler
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   Model Router    Compute Router    Tool Router
        │               │               │
      LLMs            Sandbox          MCP/API
```

因此资源不再只有 CPU、Memory、Thread，还包括 Token Budget、Context Window、Model Capability、Tool QPS、Latency、Cost 和 Risk。Agent Runtime 调度的实际上是**推理机会**。

## 六、Supervisor：从 Exception Recovery 到 Decision Recovery

Akka 的 supervision 可以 restart、stop、resume 或 escalate。Agent 的 failure 却至少包括：

```text
Runtime Failure      → retry / restart
Tool Failure         → retry / fallback
Semantic Failure     → critique / replan
Verification Failure→ optimize / re-execute
Security Failure     → block / escalate
```

因此 Agent Supervisor 的职责可能从“进程活着没有”升级成“决策是否还在正确轨道上”。**传统 Supervisor 解决 Failure Recovery；Agent Supervisor 还需要解决 Decision Recovery。**

## 七、Router：从负载均衡到 Capability + Risk Routing

传统 Router 可以把消息分发到不同 Actor。Agent Runtime 的 Router 还需要判断能力、风险和环境：

```text
Task → Capability Router → Agent
                       ↓
                 Security Gate
                       ↓
                   Execution
```

“修改生产数据库”不是简单的 Database Capability，而是一个带有生产环境、高风险和权限约束的任务。因此路由不再只是“谁空闲”，而是“谁具备能力、谁被允许执行、在哪个环境执行”。

## 八、Sharding：Agent 会不会成为有身份的计算实体

Akka Cluster Sharding 的重要思想是：调用方只需要知道逻辑 Entity ID，不需要知道 Actor 当前位于哪个节点。系统负责把有状态 Actor 分布到 Cluster 中。[Akka Cluster Sharding](https://doc.akka.io/libraries/akka-core/current/typed/cluster-sharding.html)

```text
AgentId → Agent Router → Shard → Runtime Node
                                  ↓
                           Context / Memory
```

如果这个思想迁移到 Agent，一个长期运行的 Agent 可以拥有自己的 Identity、Memory、Task State、Permission 和 Artifact，甚至可以被暂时挂起，然后因为新消息恢复运行。**微服务更像无状态能力；Agent 更可能成为有身份、有状态、有生命周期的计算实体。**

## 九、Persistence：保存的不只是 State，而是 Cognitive Trajectory

Agent 需要保存的可能是：

```text
Goal
Current Plan
Completed / Pending Steps
Context / Memory References
Artifacts
Verification Results
Failure History
```

于是长任务可以：

```text
Day 1 → checkpoint → suspend → Day 3 → restore → resume
```

Agent Persistence 不只是“保存对象”，而是保存一个可以继续行动的**认知轨迹**。

## 十、Backpressure：Agent 也会出现“认知过载”

一个 Agent 可能不断 spawn Agent、调用工具、消耗 Token 和启动 Sandbox：

```text
Agent → spawn → Agent → spawn → Agent → …
```

所以 Runtime 需要类似 Admission Control 的机制：

```text
Agent Spawn Request
        ↓
Admission Control
        ↓
Token Budget / Concurrency / Tool Quota / Sandbox Quota
        ↓
Allow / Delay / Reject
```

Agent 的自治并不意味着无限制自治。

## 十一、Agent 之间到底应该怎么通信？

我更倾向于把 Multi-Agent Communication 看成三个层次：

```text
Agent Communication
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 Direct Message     Event / MQ      Shared State
       │               │               │
    Actor/A2A       Kafka/EventBus   Task Board/Git
```

### 1. Direct Message

适合即时协作。A 可以直接把任务、上下文和结果交给 B。Google 的 A2A 方向正是在解决 Agent 间 capability discovery、task lifecycle、message、artifact 和长任务状态同步。[Google：A2A](https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/)

### 2. Event / MQ

适合解耦和广播。Event 表达“发生了什么”，而不一定表达“你现在必须替我做什么”。

### 3. Shared State

适合长期协作。Task Board、Git Repository、Artifact Store、Database 和 Workspace 都可以成为多个 Agent 共同观察和修改的外部事实源。Anthropic 的 C Compiler 实验中，任务锁、共享代码库、Git 同步和测试就是这种思路的实际例子。

所以成熟的 Agent Team 很可能不是“只用 Message”，而是：

```text
Direct Message + Event Bus + Shared Workspace + Task State + Artifacts
```

## 十二、为什么“共享世界”可能比“共享上下文”更重要

如果 Agent A 把全部上下文塞给 B，系统会越来越依赖 Prompt 和 Context Window：

```text
A → huge context → B → huge context → C
```

另一种思路是让 Agent 共享一个可验证的外部世界：

```text
Shared World
        /      |       \
      A        B        C
      |        |        |
    Task     Code     Artifact
    State    State      State
```

Agent 不需要知道其他 Agent 的全部思考过程，只需要知道当前世界状态和自己负责的任务。**共享事实，而不是共享全部执行过程。**这可能是大规模 Agent Team 更重要的基础。

## 十三、MCP 与 A2A：两张不同的网络

```text
Agent
  ├── MCP → Tool / Data / Context
  └── A2A → Agent / Task / Artifact
```

可以把它理解为两张网络：

```text
Capability Network
Agent → Tool / Data / Service

Agent Network
Agent ↔ Agent
```

两张网络最终都需要进入 Runtime 的统一治理：Identity、Permission、Routing、Observability、Policy 和 Cost。

## 十四、从 K8s、Akka 到 Agent Runtime

```text
Agent Runtime
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   Infrastructure     Actor        Cognitive
        │             Model           │
       K8s            Akka            LLM
        │              │              │
   Compute /        Message /      Reasoning /
   Scheduling       State          Planning
   Sandbox          Supervision    Context
   Network          Sharding       Tools
```

Kubernetes 更关心 **Where does it run?**；Actor Model 更关心 **How does a stateful concurrent entity communicate and survive?**；Agent Runtime 新增的问题是 **What should the cognitive entity do next?**

因此 Agent Runtime 更像三者的结合，而不是某一个 Agent Framework 的升级版。

## 十五、我的一个假设：Agent Runtime 可能是一种 Cognitive Actor System

```text
Cognitive Actor
 ├── Identity
 ├── Goal
 ├── Context
 ├── Memory
 ├── Policy
 ├── Tools
 ├── Mailbox
 ├── Environment
 ├── Verification
 └── Lifecycle
```

它拥有自己的身份，可以接收消息，可以改变状态，可以调用能力，可以观察现实，可以验证结果，可以失败、恢复、暂停和继续。

Agent Team 则是这些 Cognitive Actors 组成的动态系统：

```text
Goal
 ↓
Agent Runtime
 ↓
┌─────────┬─────────┬─────────┐
Agent A ↔ Agent B ↔ Agent C
└─────────┴─────────┴─────────┘
          ↓
     Shared World
          ↓
 Observation → Verification → Cognitive State → Next Action
```

所以我现在更愿意提出一个开放假设：

**Agent Runtime 可能不是 Workflow Engine 的下一版，而是 Cognitive Actor System 的早期形态。**

Workflow 的基本单位是步骤，Actor 的基本单位是自治计算实体，而 Agent 的基本单位可能是**能够在环境中持续进行认知闭环的自治计算实体**。

## 开放问题

- Agent 的 Mailbox 是否需要真正的语义调度，而不是简单 FIFO？

- Agent Supervisor 如何区分 Runtime Failure 与 Semantic Failure？

- Agent Sharding 是否会成为 Long-running Agent 的基础设施能力？

- 共享 Workspace 是否会比共享 Context 更适合大规模 Agent Team？

- Runtime 如何统一控制 Token、Model、Tool 和 Sandbox 的资源预算？

- Agent 的 Identity、Permission 和 Memory 是否会成为新的基础设施原语？

## 参考

- [Akka — Actor Model](https://doc.akka.io/libraries/akka-core/current/typed/guide/actors-intro.html)

- [Akka — Cluster Sharding](https://doc.akka.io/libraries/akka-core/current/typed/cluster-sharding.html)

- [Anthropic — Building a C compiler with a team of parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler)

- [Google — Agent2Agent Protocol](https://developers.googleblog.com/a2a-a-new-era-of-agent-interoperability/)
