---
id: iot-agent-reconstruction
type: Articles
title: IoT 平台的 Agent 重构
date: 2026-09-07
thought_date: 2026-09-07
published_date: 2026-09-07
tags: [Agent, IoT, Architecture, Edge, Control Plane]
excerpt: 如果说传统 IoT 平台解决的是“设备如何被连接、管理和自动化”，那么 Agent 时代真正值得思考的问题是：设备、云边能力和智能决策，能不能共同组成一个可以围绕目标持续工作的运行系统？
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/iot-agent-reconstruction.md
---

# IoT 平台的 Agent 重构

## 1. IoT 的问题，比 SaaS 更接近“现实世界”

和纯软件 SaaS 相比，IoT 平台天然连接着物理世界：设备、传感器、网关、网络、边缘节点、云服务以及最终的业务系统。设备状态会变化，网络会抖动，数据会延迟，动作可能失败，现实世界也不会严格按照 Workflow 的预设运行。

因此，一个传统 IoT 平台通常围绕几件事构建：设备接入、设备管理、数据采集、规则引擎、消息处理、远程控制、告警和运维。它的核心是把**物理世界转换成软件可以理解和操作的对象**。

```text
传统 IoT

设备 → 网关 → IoT Platform → 规则 / Workflow → API / Command
  ↑                                      ↓
状态 / Telemetry ←─────────────── 执行动作
```

这个体系已经非常成熟，但它的默认交互方式仍然是“事件触发规则”或“用户发起操作”。Agent 带来的变化，是把问题从“发生了什么，然后执行哪条规则”，提升为“**我想达到什么结果，当前现实是什么，下一步应该做什么**”。

## 2. 这类 IoT 平台，Agent 不应该只是一个聊天入口

以某 IoT 平台为例，它已经拥有大量设备模型、设备能力、数据、场景自动化、用户与企业体系，以及连接硬件和云服务的基础设施。

如果只是增加一个“AI 助手”，让用户用自然语言创建场景，例如“晚上十点自动关灯”，这当然有价值，但它本质上仍然是把自然语言转换成已有的规则配置。

真正值得做的重构，是把现有 IoT 能力重新抽象成 Agent 可以理解、发现和组合的能力。

> **不是给 IoT 平台加一个 Agent，而是让 IoT 平台本身逐渐成为 Agent 可以工作的环境。**

## 3. 第一层变化：Device 不再只是“设备”，而是 Capability

传统 IoT 的核心抽象是 Device。Agent 更关心的是 Capability：这个环境里有什么能力？它可以读取什么？可以控制什么？执行之后会产生什么状态变化？

例如一盏智能灯，传统模型可能描述为设备 ID、在线状态、亮度、颜色和开关状态；面向 Agent，则应该进一步表达为“照明能力”“调节亮度能力”“设置色温能力”，以及这些能力的约束、权限、成本和预期结果。

```text
Device Model
      ↓
Capability Model
      ├── observe：读取温度 / 电量 / 状态
      ├── act：开关 / 调光 / 设置模式
      ├── compose：与其他设备形成场景
      └── verify：确认动作是否真正生效
```

这和之前讨论 SaaS 时的 OpenAPI → Tool 是类似的：**设备 API 不是 Agent 的最终抽象，Agent 需要的是带语义、约束和结果反馈的能力。**

## 4. 第二层变化：规则引擎不会消失，但 Agent 会站在它的上面

一个常见误区是认为 Agent 出现后，原来的规则引擎和 Workflow 都应该被替代。IoT 恰恰相反：确定性的规则非常适合继续运行在底层。

例如“温度超过 30℃ 就打开风扇”“门打开后 30 秒关闭照明”，这些逻辑不需要 LLM。它们应该保持低延迟、可预测、可验证。

Agent 更适合处理目标不明确、需要综合上下文、需要动态调整的任务。例如：

```text
目标：降低这个仓库的能源消耗，同时不要影响生产

Agent
  ↓
读取设备 / 电表 / 环境数据
  ↓
理解当前运行状态
  ↓
分析历史模式
  ↓
调用已有规则 / Workflow / Device Tools
  ↓
观察结果
  ↓
发现节能效果不足
  ↓
调整策略
  ↓
继续验证
```

因此，**Workflow 负责确定性执行，Agent 负责动态决策，IoT Runtime 负责连接现实世界。**

## 5. 第三层变化：IoT 需要自己的 Agent Control Plane

当 Agent 数量增加以后，真正困难的问题会从“怎么调用模型”变成“怎么管理大量 Agent 任务”。这时 Kubernetes 的思想会再次出现。

```text
IoT Agent Control Plane

                    Business Goal
                         ↓
                ┌─────────────────┐
                │ Agent Control    │
                │ Plane            │
                └────────┬────────┘
                         ↓
                  Task / Scheduler
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
     Device Agent    Energy Agent   Maintenance Agent
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                   Tool Gateway
                         ↓
             IoT / Cloud / Edge Services
                         ↓
                   Physical World
                         ↓
                    Observation
                         ↓
                   Reconciliation
```

Control Plane 的职责不是执行每一个动作，而是管理目标、任务、策略、权限、Agent 生命周期、状态、调度、观测和结果。Agent Runtime 则负责真正的推理和工具调用。

这和 Kubernetes 的类比非常自然：K8s 让“Desired State → Actual State”不断收敛；Agent 系统则让“Desired Outcome → Actual Outcome”不断收敛。

## 6. IoT 的 Agent Loop，比 SaaS 更重要

IoT 最大的特殊性在于：Agent 的动作会进入物理世界，而物理世界会反过来告诉 Agent“你到底做没做到”。

```text
Goal
  ↓
Plan / Action
  ↓
Tool / Device
  ↓
Physical Environment
  ↓
Observation / Telemetry
  ↓
Gap
  ↓
Next Action
  ↺
```

例如 Agent 下发“降低空调功率”的命令，并不意味着任务已经完成。它还需要观察功率、电流、温度和设备状态，判断目标是否真正达到。

所以 IoT Agent 的核心能力不是“会调用设备 API”，而是**能根据现实反馈持续修正行动**。

## 7. 从“设备自动化”走向“环境自动化”

传统 IoT 往往以单个设备或单条规则为中心。Agent 会推动抽象层级上移：用户不再需要知道具体要控制哪些设备，而是提出环境目标。

```text
传统：
“打开客厅灯 → 设置亮度 60% → 打开空调 24℃”

Agent：
“把客厅调整到适合晚间阅读的状态”
        ↓
Agent 理解环境
        ↓
灯光 + 空调 + 窗帘 + 传感器
        ↓
执行 → 观察 → 调整
```

这意味着 IoT 平台的竞争壁垒也可能从“连接了多少设备”逐渐转向“**能不能让这些设备作为一个环境被理解和操作**”。

## 8. 云、边、端不会被 Agent 抹平

Agent 架构也不能简单理解为“把所有事情交给云端大模型”。IoT 对实时性、可靠性和网络条件有严格要求。

- **端 / Device：**负责真实世界的感知与执行。
- **Edge：**负责低延迟、本地闭环、协议适配和断网情况下的基本运行。
- **Cloud：**负责全局上下文、跨设备分析、模型推理、长期记忆和复杂任务编排。
- **Agent Control Plane：**负责目标、任务、策略、调度和治理。

因此未来更合理的形态不是“Cloud Agent 替代 IoT Runtime”，而是**Agent 与 IoT Runtime 分层协作**。

## 9. Tool Gateway 是 IoT Agent 化的关键基础设施

如果每一个 Agent 都直接调用设备服务、用户服务、场景服务、数据服务，系统很快会失控。和 SaaS 一样，IoT 也需要 Tool Gateway。

```text
Agent
  ↓
Tool Gateway
  ├── Device Tools
  ├── Scene / Automation Tools
  ├── Telemetry / Data Tools
  ├── User / Tenant Tools
  ├── Edge Tools
  └── Operations Tools
        ↓
IoT Platform Services
        ↓
Devices / Edge / Cloud
```

Gateway 负责能力发现、Tool Schema、认证、租户、权限、路由、限流、审计和可观测性。这样 Agent 不需要知道底层微服务如何实现，只需要理解“我有哪些能力可以完成目标”。

## 10. 多租户与权限，在 Agent 时代会变得更重要

IoT 平台通常天然存在企业、项目、用户、设备等层级。Agent 一旦获得设备控制能力，权限边界就不能只停留在传统 API Token 层面。

未来需要回答的不只是“这个用户能不能调用 API”，还包括“这个 Agent 在这个任务上下文中，是否允许控制这批设备”“它能读取什么数据”“哪些动作必须人工确认”。

因此 Agent Identity、Tenant Context、Capability Permission、Policy 和 Audit Log，会成为 IoT Agent Platform 的基础设施，而不是外围功能。

## 11. Agent 的评价指标也要改变

如果只统计“Tool 调用了多少次”“Workflow 成功多少次”，很容易产生代理指标与真实结果之间的偏差。

IoT 更应该关注 Outcome：设备是否真的达到目标？环境是否改善？故障是否减少？能源是否下降？用户是否满意？

```text
Proxy Metrics
  ├── Tool call success
  ├── API PASS
  └── Workflow completed

                ≠

Real Outcome
  ├── Physical state changed
  ├── Target actually reached
  ├── No unintended side effects
  └── User / business goal satisfied
```

这也意味着 Agent 平台需要保存任务轨迹、观察结果、失败原因、人工反馈以及最终 Ground Truth，形成可持续优化的 Case Memory，而不是只保存聊天记录。

## 12. 这类平台真正值得重构的地方

如果把上面的思路放在这类 IoT 平台上，我认为重点并不是重新做一个“超级 Agent”，而是逐步建立一套 Agent-native Infrastructure：

- 把 Device Model 向 Capability Model 演化；
- 把已有 IoT API / OpenAPI 暴露成有语义的 Tools；
- 建立 Tool Gateway，统一权限、租户、路由和审计；
- 建立 Agent Runtime，承载推理、计划、工具调用和 Loop；
- 建立 Agent Control Plane，管理 Goal、Task、Policy、Scheduler 和状态；
- 让 Workflow / Rule Engine 成为 Agent 可以调用的确定性执行层；
- 把 Telemetry 从“监控数据”升级成 Agent 的 Observation；
- 把最终业务结果作为 Agent 的 Outcome，而不是只看 API 是否成功。

## 13. 最终形态：IoT 平台变成一个 Agent 可以工作的世界

从这个角度看，IoT Agent 重构和 SaaS Agent 重构其实是一条相同的技术路线，只是 IoT 多了一层物理世界。

```text
                    Goal
                      ↓
               Agent Control Plane
                      ↓
                Agent Runtime
                      ↓
                 Tool Gateway
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      Cloud          Edge         Devices
        └─────────────┼─────────────┘
                      ↓
              Physical Environment
                      ↓
                 Observation
                      ↓
                    Gap
                      ↓
                     Loop
```

所以，IoT 的 Agent 化并不是把 LLM 塞进设备平台，而是把整个系统的控制方式，从**“事件 → 规则 → 动作”**逐渐扩展成**“目标 → Agent → 能力 → 环境 → 反馈 → 再行动”**。

> **最终的问题不是“这类平台应该做哪些 Agent”，而是“这类平台应该把 IoT 平台改造成什么样的基础设施，才能让未来各种 Agent 都可以在上面工作”。**

如果 SaaS 的 Agent 化，是让软件从 API / Workflow 中逐渐走向 Goal / Agent / Outcome，那么 IoT 的 Agent 化更进一步：它是在让**数字世界与物理世界共同进入一个可被 Agent 持续感知、决策、执行和校正的闭环**。

## 14. 商业视角：IoT 平台怕的不是重构，而是绕过

如果把 SaaS 和 IoT 放在一起看，IoT 平台其实比 SaaS 平台更危险，但它的护城河也更硬。

危险在于「智能外移」：当用户说「帮我关灯、调温」，理解意图的是 Alexa、Siri 或某个助手层的 LLM，执行连接的是 IoT 平台——它会慢慢退化成一条只收连接费的哑管道，高毛利层被助手层吃掉。

硬也硬在这里：模组、认证、制造供应链、数十万 SKU 的设备库，这是物理地板，LLM 造不出来。

所以 IoT 平台的活路很清晰：把自己暴露成所有 LLM Agent 调用物理世界的入口——无论是 MCP 还是设备动作 API——从「被配置的平台」变成「Agent 的物理世界工具层」。这恰好就是第 9 节说的 Tool Gateway，只不过这类平台要把这个 Gateway 做成整个行业的物理入口，而不是自己平台内部的一个组件。

收费上，也会从「设备订阅」走向「动作 / 效果分成」。而这一条能不能走通，最终还是落到组织：技术弱、氛围差的组织，连「成为 Agent 物理入口」这道硬工程门都接不住，只能守着模组 / 供应链那块硬件地板，慢慢变成低毛利的连接商。

> **一句话：SaaS 平台怕被「重做」，IoT 平台怕被「绕过」。前者拼组织能不能交付，后者拼能不能把自己焊死在「Agent 的物理世界入口」上。**
