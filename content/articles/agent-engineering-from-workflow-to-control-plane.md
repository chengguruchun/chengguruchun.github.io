---
id: agent-engineering-from-workflow-to-control-plane
type: Articles
title: Agent Engineering：从 Workflow 到 Loop，再到 Control Plane
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Agent, Workflow, Graph, Loop Engineering, Harness, Control Plane, Kubernetes, Runtime]
excerpt: Workflow、Graph、Loop 与 Harness 并不是互相替代，而是 Agent 系统在不同不确定性和治理尺度上的不同工程层。最终，Agent 会从一个调用模型的应用走向一个可调度、可评测、可持续收敛的运行时系统。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-engineering-from-workflow-to-control-plane.md
---

# Agent Engineering：从 Workflow 到 Loop，再到 Control Plane

过去几年，软件工程围绕 Workflow 建立了大量稳定系统：流程被拆解成步骤，步骤调用 API，API 驱动微服务，最终完成业务动作。

Agent 出现以后，一个常见误区是：把 LLM 放到 Workflow 前面，就认为完成了 Agent 化。

但我越来越觉得，真正的变化并不是「Workflow + LLM」，而是**软件系统开始需要处理路径不确定、目标不确定、结果需要验证，以及执行后还要继续调整的问题**。

于是 Workflow、Graph、Loop、Harness 和 Control Plane 开始逐渐形成一条完整的工程链。

## 一、Workflow 没有消失，它只是负责确定性的部分

Workflow 最擅长的问题，是路径已经比较明确：

```text
Step A → Step B → Step C → Step D
```

例如订单创建、库存扣减、支付、发货。这些业务流程的正确性应该继续由确定性服务保证。

Agent 并不需要重新实现这些能力。

更合理的结构是：

```text
Agent
  ↓
Tool / Capability
  ↓
Existing Business Services
```

所以 Agent 时代真正发生变化的，不是微服务消失，而是**微服务的能力开始以 Tool / Capability 的形式被 Agent 消费**。

过去 OpenAPI 主要解决「程序如何调用能力」；下一阶段更重要的问题是「Agent 如何发现、理解、授权、调用并验证能力」。

## 二、为什么 Workflow + LLM 还不够

假设任务是：

> 「帮我把这个新品上线，并尽可能提高转化率。」

它没有一条天然固定的路径。

Agent 可能需要：

1. 检查商品信息
2. 查询历史销售
3. 分析用户
4. 判断营销策略
5. 调用商品能力
6. 调用营销能力
7. 观察结果
8. 发现转化没有改善
9. 修改策略
10. 再次执行

因此真正的对象开始从：

```text
Workflow
```

变成：

```text
Goal → Action → Observation → Gap → Adjustment
```

这就是 Loop Engineering。

## 三、Graph、Workflow、Loop、Harness 是不同层，不是竞争关系

我现在更倾向于这样理解四者：

| 工程方式 | 主要解决的问题 | 核心假设 |
|---|---|---|
| Workflow | 确定性流程 | 路径基本已知 |
| Graph | 复杂任务结构 | 依赖关系可以显式表示 |
| Loop | 不确定路径与目标收敛 | 下一步取决于观察结果 |
| Harness | Agent Runtime | 上下文、工具、状态与生命周期需要被控制 |

它们可以同时存在。

一个复杂任务可以先由 Graph 组织，再由 Workflow 执行确定性步骤；遇到不确定性以后进入 Agent Loop；整个过程由 Harness 管理上下文、工具、状态和生命周期。

所以我不认为「Graph Engineering」会被「Loop Engineering」替代，也不认为 Agent 会把 Workflow 干掉。

它们处理的是不同类型的不确定性。

## 四、Loop Engineering 真正改变的是控制方式

传统软件通常是：

```text
人
 ↓
UI
 ↓
Workflow
 ↓
API
 ↓
Service
 ↓
Data
```

Agent 系统越来越接近：

```text
Human Goal
    ↓
Agent
    ↓
Capability / Tool
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

过去人负责拆解任务，系统负责执行。

未来系统开始承担一部分「拆解、选择、观察、调整」的工作。

所以软件控制方式可能逐渐从：

> 「你要执行哪个功能？」

转向：

> 「你想达到什么结果？」

这可能是 Agent 化最深的一层变化。

## 五、Kubernetes 为什么会成为一个很好的类比

Kubernetes 真正值得借鉴的地方，不是 Pod 对应 Agent、Deployment 对应 AgentTask 这种机械映射。

真正值得借鉴的是：

```text
Desired State
      ↓
Actual State
      ↓
Gap
      ↓
Reconcile
      ↺
```

Agent 也可以表达成：

```text
Goal
 ↓
Action
 ↓
Observation
 ↓
Gap
 ↓
Adjustment
 ↺
```

二者共享的是 **Reconcile Mindset**。

但它们的完成语义完全不同。

Kubernetes 可以比较容易地检查：副本数、Ready、资源状态、配置版本。

Agent 的完成状态往往是语义性的：

> 「这个问题真的解决了吗？」

工具调用成功、HTTP 200、Workflow SUCCESS、模型自评 PASS，都不能直接回答这个问题。

所以 Agent 的 Actual State 必须逐渐从「执行状态」走向「Outcome 状态」。

## 六、Agent Control Plane 会在什么时候出现

当 Agent 只有一个、任务很短、风险很低时，一个 Runtime 足够。

但当系统开始拥有大量 Agent 和大量任务以后，治理问题一定会出现：

- 谁可以执行？
- 能调用哪些 Tool？
- 预算是多少？
- 什么时候必须审批？
- 失败以后怎么办？
- 怎样回放？
- 怎样评测？
- 怎样判断真正完成？
- 多个 Agent 如何协调？

于是需要一个类似 Kubernetes Control Plane 的控制面：

```text
                   Goal
                    ↓
          ┌──────────────────┐
          │ Agent Control    │
          │ Plane            │
          └────────┬─────────┘
                   ↓
          Task / Policy / Budget
                   ↓
             Agent Runtime
                   ↓
             Tool Gateway
                   ↓
        Services / Environment
                   ↓
              Observation
                   ↓
                Outcome
                   ↺
```

Control Plane 不负责替代 Agent，也不负责替代业务服务。

它负责的是**目标、任务、策略、调度、权限、审批、评测、回放和结果治理**。

## 七、Tool Gateway 是连接 Agent 与微服务的基础设施

如果每一个 Agent 都直接连接几十甚至几百个业务服务，系统很快会失去治理能力。

因此需要：

```text
Agent
  ↓
Tool Gateway
  ├── Capability Discovery
  ├── Schema / Contract
  ├── Tenant
  ├── Permission
  ├── Routing
  ├── Rate Limit
  ├── Audit
  └── Observability
  ↓
Business Services
```

这也是我过去做开发者平台时，对「OpenAPI 暴露能力」这件事重新理解后的一个变化：

**API Platform 解决程序调用能力；Tool Gateway 开始解决 Agent 使用能力。**

底层业务服务依然负责确定性正确性。

Agent 负责目标驱动的决策。

Gateway 负责能力治理。

Control Plane 负责全局任务治理。

## 八、真正难的不是 Action，而是 Outcome

传统 Workflow 很容易定义成功：步骤全部执行完成，Workflow 就 SUCCESS。

Agent 则不一样：

```text
Tool Call = PASS
API Test = PASS
Workflow = SUCCESS
Model Self-Eval = PASS

             ≠

Real Outcome = SUCCESS
```

这也是我最近越来越关注的 **Proxy Metric ≠ Real Outcome**。

如果系统只优化代理指标，最终可能得到一个「看起来非常会完成任务」的 Agent，却没有真正解决问题。

因此一个 AgentTask 更合理的结构应该至少包含：

- Goal
- Success Criteria
- Evidence
- Proxy Checks
- Real Outcome

完成不是一个布尔值，而应该是一份带证据的声明。

## 九、Execute、Eval、Learn 应该是三条不同速度的环

Agent 系统如果要长期进化，我认为至少需要三条环：

```text
Execute Loop
Goal → Act → Observe → Gap

Eval Loop
Trajectory → Evaluate → Gate

Learn Loop
Evidence → Strategy Update → Experiment
```

它们的时间尺度不同。

Execute 关注当前任务能不能完成；Eval 关注这条策略是否值得继续使用；Learn 关注下一次是不是可以更好。

如果把 Learn 混进每一次 Execute，很容易过拟合当前任务；如果没有 Eval，系统会在错误策略上持续自我强化。

这和科学实验式使用大模型的思路是连起来的：**先定义目标，再实验、评测、记录，然后才允许策略进入下一轮。**

## 十、从微服务到 Agent Runtime，不是推倒重来

如果今天一个大型 SaaS 或 IoT 平台已经有大量微服务，我不认为正确路线是全部重写成 Agent。

更现实的演进应该是：

```text
API
 ↓
Tool / Capability
 ↓
Agent-assisted Workflow
 ↓
Goal-driven Loop
 ↓
Multi-Agent
 ↓
Agent Runtime
 ↓
Agent Control Plane
 ↓
Outcome Platform
```

每一步都可以独立产生价值。

已有商品、订单、库存、营销、设备、用户、数据服务继续存在。

改变的是：**系统的上层控制方式逐渐从调用函数，移动到管理目标。**

## 十一、最终的 Agent 平台可能更像一个分布式系统

如果继续把这个方向往前推，我越来越觉得未来 Agent 不会只是一个「LLM Application」。

它可能更像一种新的分布式运行时：

```text
                Control Plane
                     ↓
          ┌──────────┼──────────┐
          ↓          ↓          ↓
       Agent A    Agent B    Agent C
          ↓          ↓          ↓
       Runtime    Runtime    Runtime
          └──────────┼──────────┘
                     ↓
                Tool Gateway
                     ↓
          Existing Services / World
                     ↓
              Observation / Outcome
                     ↺
```

这也是为什么 Kubernetes 会成为一个自然的类比对象。

不是因为 Agent 是 Pod。

而是因为两者都需要面对：

- 生命周期
- 调度
- 资源
- 权限
- 故障
- 状态
- 观测
- 重试
- 治理
- 持续收敛

只是 Agent 多了一个非常关键的东西：**目标是语义性的，环境是开放的，结果需要验证。**

## 十二、我现在对 Agent Engineering 的一句话定义

如果把最近这些思考压缩成一句话，我会这样写：

> **Agent Engineering 不是让模型学会调用更多工具，而是把一个原本由人拆解、由 Workflow 执行的软件系统，逐渐变成一个能够理解 Goal、选择 Capability、观察 Environment、验证 Outcome，并通过 Loop 持续收敛的运行时系统。**

Workflow 负责确定性。

Graph 负责复杂结构。

Loop 负责不确定性。

Harness 负责运行时。

Tool Gateway 负责能力治理。

Control Plane 负责任务治理。

Evaluation / Feedback 负责真实结果。

而 Kubernetes 继续负责最底层的基础设施。

最终，Agent 不一定替代软件系统。

更可能发生的是：**软件系统开始变成 Agent 可以工作的环境。**

## 开放问题

- 什么规模的 Agent 系统才真正需要 Control Plane？
- Outcome 如何机器验证，而不是继续依赖 Proxy Metric？
- Tool Gateway 与传统 API Gateway 的边界会如何变化？
- Agent Runtime 的状态应该像容器一样可替换，还是应该成为持久对象？
- Execute / Eval / Learn 三条环如何避免互相污染？
- 多 Agent 系统什么时候真的比单 Agent 更有价值？
