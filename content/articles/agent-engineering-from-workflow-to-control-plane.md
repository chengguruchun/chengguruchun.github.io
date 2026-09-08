---
id: agent-engineering-from-workflow-to-control-plane
type: Articles
title: Agent Engineering：从 Workflow 到 Loop，再到 Control Plane
date: 2026-09-08
thought_date: 2026-09-04
published_date: 2026-09-08
tags: [Agent, Workflow, Graph, Loop Engineering, Harness, Control Plane, Kubernetes, Runtime]
excerpt: 从我们关于 Workflow、Graph、Loop、Harness、微服务、Tool Gateway 与 Kubernetes 的讨论出发：Agent 化不是推倒原有软件，而是让系统的控制方式从调用函数逐渐走向目标、反馈与持续收敛。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-engineering-from-workflow-to-control-plane.md
---

# Agent Engineering：从 Workflow 到 Loop，再到 Control Plane

这篇文章整理的是我们最近关于 Agent Engineering 的一条思考线。

我们先讨论 Workflow、Graph、Loop 和 Harness 分别解决什么问题；然后把它和我过去做微服务、开发者平台时的经验联系起来；再进一步讨论 Tool Gateway、Kubernetes，以及未来 Agent 为什么可能需要一个 Control Plane。

核心并不是「Agent 会不会替代 Workflow」，而是：**当软件开始从执行确定的函数，转向完成一个目标时，系统的控制方式会发生什么变化？**

## 一、Workflow 没有消失

传统软件很擅长处理确定性的事情：

```text
人
 ↓
UI
 ↓
Workflow
 ↓
API
 ↓
微服务
 ↓
数据
```

订单、库存、支付、设备控制等能力，本身仍然需要确定性的软件来保证正确性。

所以 Agent 化并不意味着把原来的微服务和 Workflow 全部重写掉。

更合理的方式是：

```text
Agent
  ↓
Tool / Capability
  ↓
Existing Business Services
```

微服务继续负责确定性的业务能力；Agent 开始负责在目标下选择和组合这些能力。

## 二、为什么 Workflow + LLM 还不够

我们讨论 SaaS Agent 时举过一个例子：

> 「提高这个商品的销售。」

这不是一个天然固定的 Workflow。

Agent 可能需要先读取商品数据，再看销售历史和用户情况，然后选择营销能力；执行以后还要看结果，如果结果没有达到目标，再调整策略。

因此问题开始从：

```text
Step A → Step B → Step C
```

变成：

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

这就是我们后来反复讨论的 **Loop Engineering**。

## 三、Graph、Workflow、Loop、Harness 是不同东西

我们讨论下来，我更愿意这样区分：

| 工程方式 | 主要解决的问题 |
|---|---|
| Workflow | 已经知道路径的确定性流程 |
| Graph | 复杂任务中的结构和依赖 |
| Loop | 根据实际结果不断调整，直到目标逐渐收敛 |
| Harness | Agent 运行时的上下文、工具、状态和生命周期 |

所以它们不是互相替代的关系。

一个长任务可以有 Graph；Graph 中可以包含 Workflow；遇到不确定性以后进入 Agent Loop；Harness 负责让 Agent 能够稳定运行。

我们之前讨论「Graph Engineering、Loop Engineering、Harness Engineering」时，我越来越倾向于认为，真正属于 Agent 特性的，是 **Loop**：因为 Agent 面对的不是一条完全预先确定的路径，而是一个需要根据现实不断修正的过程。

## 四、Agent 真正改变的是软件的控制方式

传统软件更像是在问：

```text
调用什么函数？
调用哪个 API？
执行哪个 Workflow？
```

Agent 开始以后，问题逐渐变成：

```text
我要达到什么目标？
我现在是什么状态？
我有哪些能力可以使用？
现实发生了什么？
距离目标还有多远？
下一步应该怎么做？
```

所以我认为 Agent 化更深的一层变化，不是增加一个聊天 UI，而是：

> **软件控制方式从「调用函数」逐渐向「管理目标」移动。**

这也是为什么我们后来会自然地把 Agent 和 Kubernetes 联系起来。

## 五、Kubernetes 给 Agent 的真正启发：Reconcile

我不认为应该简单地把 Pod、Deployment 和 Agent 一一对应。

Kubernetes 真正值得借鉴的是它的控制思想：

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

Agent 也可以这样理解：

```text
Goal / Desired Outcome
          ↓
        Action
          ↓
       Reality
          ↓
     Observation
          ↓
          Gap
          ↓
      Adjustment
          ↺
```

二者的共同点是：**系统不是执行一次就结束，而是持续观察实际状态，并尝试缩小目标与现实之间的差距。**

但 Agent 的难点也更加明显：Kubernetes 的很多状态可以直接机器判断，而 Agent 的「完成」往往是语义性的。

例如：

```text
HTTP 200
Tool Call PASS
Workflow SUCCESS

       ≠

目标真的完成
```

所以 Agent 的 Actual State 不能只记录执行状态，还要尽可能接近真实结果。

## 六、Tool Gateway：从 OpenAPI 到 Agent Capability

我们还讨论了一个和我过去工作经历联系很紧的变化。

过去开发者平台做的一件核心事情，是把内部能力通过 OpenAPI 暴露出来，让其他程序能够调用。

进入 Agent 时代，这层能力仍然存在，但问题变了：

> 不只是「程序怎么调用 API」，而是「Agent 怎么发现、理解、授权和使用能力」。

因此可以形成：

```text
Agent
  ↓
Tool Gateway
  ↓
Product Tool
Order Tool
Inventory Tool
Marketing Tool
Data Tool
  ↓
Existing Services
```

Tool Gateway 不应该重新实现业务逻辑，而应该成为 Agent 和已有服务之间的能力层。

我们讨论过它需要解决的核心问题包括：

- Capability Discovery
- Tool Schema
- Tenant
- Permission
- Routing
- Observability

这也是我对原来「开发者平台」这类基础设施重新理解后的一个方向：**OpenAPI 暴露的是程序可调用的能力，Tool Gateway 开始暴露 Agent 可理解、可治理的能力。**

## 七、为什么未来 Agent 可能会走向 Control Plane

我们之前有一个很直观的判断：未来的 Agent 可能还是微服务式的，然后像 Kubernetes 一样存在一个 Control Plane，负责下发任务，Agent Runtime 负责完成任务，再通过实际结果去拟合目标和现实之间的差距。

如果只有一个 Agent，这种架构可能没有必要。

但当 Agent 数量、任务数量和能力数量不断增加以后，系统会自然出现更高一层的问题：

```text
任务怎么下发？
Agent 怎么选择？
Tool 怎么授权？
任务现在是什么状态？
结果怎么判断？
失败以后怎么处理？
多个 Agent 怎么协作？
```

于是可以得到一个更接近 Kubernetes 的结构：

```text
              Control Plane
                    ↓
             Desired Goal
                    ↓
             Agent Runtime
                    ↓
              Tool Gateway
                    ↓
        Existing Services / World
                    ↓
             Observation
                    ↓
                 Outcome
                    ↺
```

这里 Control Plane 不是替代 Agent，也不是替代微服务。

它更像整个 Agent 系统的控制面。

## 八、IoT 让这个问题更加明显

我们讨论 IoT 时，这个模型变得更加直观。

SaaS Agent 处理的是数字世界；IoT Agent 还要面对真实设备和物理环境。

例如：

```text
Goal
 ↓
Agent
 ↓
Device Capability
 ↓
Physical World
 ↓
Telemetry
 ↓
Observation
 ↓
Gap
 ↓
Next Action
```

这里最大的变化是：Agent 的 Action 会真的改变环境，而环境又会给 Agent 返回新的状态。

因此 IoT Agent 不是简单地「给设备平台加一个聊天框」，而是从：

```text
Event → Rule → Action
```

逐渐走向：

```text
Goal → Agent → Capability → Environment → Feedback → Next Action
```

但原来的规则和 Workflow 依然有价值。

例如温度超过阈值以后打开风扇，这种确定性的规则并不需要 Agent 来替代。

Agent 更适合处理需要上下文、判断和调整的目标。

## 九、制造业为什么更难

我们也讨论过制造业里的 Agent。

制造业的问题不是「没有 API」，而是流程非常复杂，很多系统又是历史形成的单体或强耦合系统。

所以如果直接告诉企业：

> 「我们给你做一个 Agent。」

老板很难看到为什么值得付钱。

反过来，如果从基础设施和目标出发，问题就变成：

```text
企业已有系统
      ↓
Capability / Tool
      ↓
Agent Runtime
      ↓
Goal
      ↓
Outcome
```

这样 Agent 并不是要求企业推倒重来，而是逐渐进入已有生产系统。

这也是为什么我越来越觉得，Agent 真正的价值可能不只是「一个 Agent 产品」，而是**让原来的软件和生产环境逐渐变成 Agent 可以工作的环境。**

## 十、Agent 化不是重写微服务

把 SaaS、IoT 和制造业放在一起看，我现在更倾向于这样理解演进过程：

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
Control Plane
```

这不是一次性迁移。

原来的微服务继续存在；Workflow 继续存在；规则引擎继续存在。

只是它们从「用户直接操作的系统」，逐渐变成「Agent 可以调用和工作的环境」。

## 十一、我现在对 Agent Engineering 的理解

如果把这几次讨论压缩成一句话：

> **Agent Engineering 不是给软件系统加一个 LLM，而是让系统从执行预先定义的路径，逐渐变成围绕 Goal、Capability、Environment 和 Feedback 持续解决问题。**

所以：

```text
Workflow → 确定性的执行
Graph    → 复杂任务的结构
Loop     → 目标与现实之间的持续收敛
Harness  → Agent 的运行环境
Tool     → Agent 可以使用的能力
Gateway  → 能力的统一治理
Control Plane → 多 Agent / 多任务的控制
```

而 Kubernetes 给我的启发，是 **Reconcile**：

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

未来 Agent 系统可能会越来越像一个分布式系统，而不只是一个 LLM Application。

但这里最值得继续研究的问题仍然是：

> **当目标是语义性的，系统到底怎样知道「真的完成了」？**

这可能比「怎么调用更多 Tool」更加重要。
