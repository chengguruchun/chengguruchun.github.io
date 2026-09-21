---
id: spring-dubbo-deepseek-harness-runtime
type: Articles
title: 从 Spring、Dubbo 到 DeepSeek Harness：运行时架构为什么正在趋同
date: 2026-09-21
thought_date: 2026-09-21
published_date: 2026-09-21
tags: [Agent, Runtime, Spring, Dubbo, Harness]
excerpt: 从 Spring、Dubbo Service 到 DeepSeek Harness，观察依赖注入、Context、Event Bus、生命周期与运行时治理这些工程思想如何在 Agent 时代重新组合。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/spring-dubbo-deepseek-harness-runtime.md
last_verified: 2026-09-21
cadence_days: 90
---

# 从 Spring、Dubbo 到 DeepSeek Harness：运行时架构为什么正在趋同

如果把 Spring、Dubbo 和 DeepSeek Harness 放在同一张架构图里，我看到的并不是三个完全不同的世界，而是一条很有意思的工程演进线：**把复杂性不断下沉到 Runtime，让上层只面对稳定的抽象和契约。**不同之处在于，Spring 更偏向确定性的对象装配，Dubbo 更偏向确定性的服务调用，而 Harness 开始面对一个本质不同的问题：任务执行过程中，下一步到底应该做什么。

## 一、先把三个东西放在同一张图里

```text
Spring
  Object / Bean
       ↓
  Container Runtime
  DI / Context / Lifecycle
       ↓
  Business Code

Dubbo
  Service
       ↓
  Service Runtime
  Discovery / Routing / Protocol / Load Balance
       ↓
  Consumer / Provider

DeepSeek Harness / Agent Runtime
  Agent Task
       ↓
  Cognitive Runtime
  Context / Tools / Safety / Sandbox / Verification
       ↓
  Action → Observation → Next Decision
```

三个系统的管理对象不一样，但有一个共同的架构方向：

**上层表达“我要什么”，Runtime 负责解决“怎么提供、怎么运行、怎么治理”。**

## 二、共同的思想，其实比表面上的技术更重要

### 1. DI：把“依赖什么”与“怎么提供”分离

Spring 的依赖注入是最直观的例子。业务对象声明自己需要什么依赖，而容器负责创建、装配和管理具体实现。

```text
Business
   │
   ├── depends on → Interface
   │
   ↓
Spring Container
   │
   ├── Implementation A
   └── Implementation B
```

Agent Runtime 也出现了类似的问题。Agent 不应该把某个具体模型、工具或者执行环境硬编码进去，而应该依赖能力契约：

```text
Agent
  │
  ├── needs → LLM
  ├── needs → Tool
  ├── needs → Memory
  └── needs → Sandbox
          ↓
     Agent Runtime
          ↓
  Provider / Tool / Environment
```

因此可以把它理解成一种“能力注入”。模型厂商、工具实现、Sandbox 都可以被 Runtime 隔离在适配层后面。

### 2. Context：从对象上下文走向任务上下文

Spring 有 ApplicationContext；Agent Runtime 也必须有自己的 Context，只是 Context 的内容发生了变化。

传统 RuntimeAgent Runtime

Bean / ServiceAgent / Task
DependencyCapability / Tool / Model
Application ContextTask Context / Cognitive Context
ConfigurationPolicy / Goal / Constraint
Runtime StatePlan / Memory / Artifact / Observation

因此，Agent Context 并不只是 Prompt。它更像一个持续变化的运行时状态容器。

### 3. Event Bus：从系统事件走向认知事件

Event Bus 并不是 Agent 时代才出现的技术。传统系统早就使用事件来解耦模块、传播状态变化和驱动异步处理。

Agent Runtime 只是把事件的语义进一步扩展：

```text
TaskCreated
ToolCalled
ToolResult
ObservationReceived
VerificationFailed
PlanUpdated
HumanFeedback
RiskEscalated
TaskCompleted
```

因此 Agent 的执行过程本身就可以被看成一个 Event Stream。Runtime 通过事件驱动状态变化，而不是让所有组件互相直接调用。

## 三、真正的差异：Spring 是 Workflow，Harness 开始是动态决策

这里是我觉得最值得讨论的地方。

Spring 并不是严格意义上的 Workflow Engine，但从应用开发者的视角看，它通常服务于**相对确定的程序流程**：对象被创建、依赖被注入、方法被调用、事务被提交、生命周期被管理。

即使运行时很复杂，业务流程本身通常还是开发者预先定义的。

```text
Developer
    ↓
Fixed Program
    ↓
Spring Runtime
    ↓
Execution
```

Agent Harness 的结构则不同：

```text
User Goal
    ↓
Agent
    ↓
Reason
    ↓
Choose Action
    ↓
Observe Result
    ↓
Verify
    ↓
Should I continue?
   ↙       ↘
 Re-plan    Finish
    ↓
 Next Action
```

这里出现了一个 Spring 世界里并不核心的东西：**下一步并没有完全写死。**

Runtime 不只是执行流程，而是要承载一个持续的“目标 → 行动 → 观察 → 验证 → 决策”循环。

## 四、所以 Harness 更像“自主 AI 编排”

Workflow 的核心问题是：

```text
What are the predefined steps?
```

Agent Harness 的核心问题则更接近：

```text
Given the goal and current state,
what should happen next?
```

这两个问题看起来只差一点，架构上却完全不同。

Workflow 可以把大量逻辑提前编码；Agent Harness 必须允许 Runtime 在执行过程中根据 Observation、Verification 和 Policy 重新决定路径。

## 五、第二张图：从固定编排到动态编排

```text
Spring / Workflow
                       │
                 Predefined Flow
                       │
              ┌────────┴────────┐
              ↓                 ↓
           Step A             Step B
              ↓                 ↓
           Step C             Step D

             Agent Harness
                  │
                Goal
                  ↓
             Current State
                  ↓
             LLM Decision
                  ↓
        ┌─────────┼─────────┐
        ↓         ↓         ↓
      Tool      Sandbox    Agent
        │         │         │
        └─────────┼─────────┘
                  ↓
             Observation
                  ↓
             Verification
                  ↓
          ┌───────┴────────┐
          ↓                ↓
       Re-plan           Finish
```

**图 2：固定 Workflow 与动态 Agent Harness 的核心差异。**前者主要执行已经定义好的路径；后者需要不断根据实际结果重新计算下一步。

## 六、第三个变化：生命周期从“创建/销毁对象”变成“生成/复用/销毁能力”

这也是我觉得 Agent Runtime 很有意思的地方。

Spring 中，Bean 有明确的生命周期：创建、初始化、使用、销毁。Runtime 可以统一管理它。

到了 Agent 时代，Runtime 可能进一步管理“能力”的生命周期。

```text
Agent discovers capability gap
              ↓
       Generate / Load Skill
              ↓
       Validate in Sandbox
              ↓
            Execute
              ↓
          Observe Result
              ↓
        ┌─────┴─────┐
        ↓           ↓
      Reuse       Dispose
        ↓           ↓
     Cache /      Destroy
     Registry
```

例如一个 Code Agent 在执行任务时发现缺少某个转换能力，它可以生成一个临时插件或 Skill，在 Sandbox 中验证并使用。任务结束后，这个能力不一定永久存在：Runtime 可以根据复用价值、风险、成本和依赖关系决定缓存、升级或者销毁。

这里和 Spring 的生命周期思想是相似的，但管理对象已经从**“对象”扩展到了“动态能力”**。

## 七、可替代性：为什么“加一层”仍然是经典答案

计算机工程里有一个非常朴素、但长期有效的思想：**当系统出现一类变化时，加一层适配，把变化隔离起来。**

Spring 用容器隔离对象创建和依赖实现；Dubbo 用 RPC 抽象、代理、注册发现和协议层隔离服务调用细节；Agent Runtime 则可以用 Model Gateway、Tool Gateway、Provider Adapter 等隔离模型和能力提供方。

```text
Application
     │
Stable Contract
     │
Runtime / Adapter Layer
     │
┌────┼────────┬────────┐
↓    ↓        ↓        ↓
GPT Claude  DeepSeek  Local Model
```

这也是 Agent Runtime 真正重要的原因之一：**不要让上层 Agent 被某一家模型、工具或者执行环境绑定。**

## 八、但 Agent 的“替代性”比 Bean 更难

这里不能简单地说“模型都有统一接口，所以可以随便替换”。模型的 API 可以统一，但行为未必统一。

维度Spring BeanAgent Model / Capability

接口通常稳定可以标准化，但行为存在差异
执行确定性较强概率性、上下文相关
状态Runtime 管理Context + Memory + Task State
失败ExceptionRuntime / Tool / Semantic / Verification Failure
替换实现可替换模型可替换，但能力表现需要重新验证

所以真正的可替代性，不是“接口一样”这么简单，而是 Runtime 能否把不同提供方的差异吸收掉，并通过验证机制知道替换以后结果是否仍然满足目标。

## 九、Harness 的新核心：决策循环 + 验证

传统 Runtime 更多关注：

```text
Can I execute this?
```

Agent Runtime 还必须关注：

```text
Did this action move me closer to the goal?
```

因此它需要一个更完整的闭环：

```text
Goal
 ↓
Plan
 ↓
Action
 ↓
Observation
 ↓
Verification
 ↓
Gap Analysis
 ↓
Re-plan / Optimize
 ↓
Next Action
```

这也是我认为 Harness 与普通 Workflow 最根本的差别之一：**验证不是流程末尾的一个 check，而是驱动下一次决策的输入。**

## 十、热更新也会变得不同

传统系统的热更新通常是在不中断服务的情况下替换代码、配置或者实例。

Agent Runtime 的热更新可能更接近：

```text
Running Agent
     ↓
Context / Policy Update
     ↓
Tool / Skill Update
     ↓
Runtime Re-evaluates
     ↓
Continue from Current State
```

因为 Agent 是一个持续运行的决策过程，所以真正有价值的热更新不是简单“替换进程”，而是**不中断任务地改变它接下来可以使用的能力、策略和上下文**。

## 十一、把三者放到一条演进线上

```text
Runtime Complexity
                     ↑
                     │
                     │                  Agent Runtime
                     │               ┌─────────────────┐
                     │               │ Dynamic Decision│
                     │               │ Context         │
                     │               │ Tools           │
                     │               │ Verification    │
                     │               │ Recovery        │
                     │               └─────────────────┘
                     │
                     │        Dubbo Service Runtime
                     │      ┌─────────────────────┐
                     │      │ Discovery / Routing │
                     │      │ Protocol / LB       │
                     │      └─────────────────────┘
                     │
                     │  Spring Container
                     │ ┌────────────────────────┐
                     │ │ DI / Context / Lifecycle│
                     │ └────────────────────────┘
                     └────────────────────────────────→
                           Managed Entity

                     Object → Service → Agent Task
```

**图 1：从 Object → Service → Agent Task 的运行时演进。**这里并不是说 Spring 必然“进化成” Dubbo，更不是说 Dubbo 必然“进化成” Agent Runtime，而是三类系统在解决不同问题时，出现了越来越相似的 Runtime 抽象。

## 十二、我的判断：不是思想变高级了，而是管理对象变了

如果把很多 AI Agent 的架构术语拆开，我反而觉得没有那么神秘。

- DI → 能力注入

- Context → 任务与认知状态管理

- Event Bus → 执行事件与反馈传播

- Lifecycle → Agent / Skill / Sandbox 生命周期

- Adapter → Model / Tool / Provider 适配

- Scheduler → Agent / Model / Compute 调度

- Supervisor → 失败恢复 + 决策恢复

- Hot Reload → 动态更新 Context、Policy、Skill

这些思想并不是突然出现的。变化的是：**Runtime 开始管理一个会自主决策、会改变执行路径、会生成临时能力的计算实体。**

## 十三、最终的架构抽象

```text
User Goal
                       ↓
                 ┌───────────┐
                 │   Agent   │
                 │ Reasoning │
                 └─────┬─────┘
                       ↓
              ┌──────────────────┐
              │   Agent Runtime  │
              │                  │
              │ Context          │
              │ DI / Capability  │
              │ Scheduler        │
              │ Event Bus        │
              │ Safety / Policy  │
              │ Sandbox          │
              │ Verification     │
              │ Lifecycle        │
              │ Recovery         │
              └───────┬──────────┘
                      ↓
       ┌──────────────┼───────────────┐
       ↓              ↓               ↓
    Model          Tools           Agents
       ↓              ↓               ↓
   Provider       Gateway         Runtime
       │              │               │
       └──────────────┼───────────────┘
                      ↓
                 Environment
                      ↓
                 Observation
                      ↓
                 Verification
                      ↓
                  Next State
```

如果一定要用一句话概括，我会这样描述：

**Spring 管对象，Dubbo 管服务，而 Agent Runtime / Harness 开始管理“会自己决定下一步做什么的任务”。**

## 十四、开放问题

- Agent Runtime 是否最终会形成类似 Spring Container 的统一基础抽象？

- Model、Tool、Skill 是否会像 Bean 一样拥有标准生命周期和依赖关系？

- Agent 的动态 Skill 是否应该由 Runtime 自动回收？

- 如何判断一个替换后的模型仍然满足原来的 Capability Contract？

- Verification 是否会成为 Agent Runtime 像 Transaction、Retry 一样的基础原语？

- 当 Agent 可以动态生成能力时，Runtime 的安全边界应该放在哪里？

我现在更倾向于把 Agent Runtime 看成一种**“动态软件系统运行时”**。它继承了过去几十年基础软件里的很多工程实践，但因为管理对象从 Object、Service 变成了 Agent Task，Runtime 第一次必须把**决策、反馈、验证和动态能力生命周期**纳入基础设施本身。

这可能才是 Spring、Dubbo 与 Agent Harness 真正有意思的连接点：**技术形式在变，Runtime 把复杂性吸收掉的思想没有变。**
