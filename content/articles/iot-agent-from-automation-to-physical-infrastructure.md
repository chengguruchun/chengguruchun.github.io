---
id: iot-agent-from-automation-to-physical-infrastructure
type: Articles
title: IoT Agent 化：从自动化平台到 Physical Infrastructure
date: 2026-09-16
thought_date: 2026-09-16
published_date: 2026-09-16
tags: [Agent, IoT, Smart Home, Benchmark, MHS, Architecture, Physical AI]
excerpt: Agent 进入 IoT 后，真正变化的可能不是 MQTT 这类连接层，而是应用层被预先打包的确定性：联动、Workflow 和功能型 App 逐渐从主交互变成执行器、约束和兜底界面。与此同时，SMH-Bench、SimuHome 与 MHS 暗示了同一条路线：设备必须变得可描述、可发现、可验证、可安全执行。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/iot-agent-from-automation-to-physical-infrastructure.md
---

# IoT Agent 化：从自动化平台到 Physical Infrastructure

最近重新思考 IoT 平台，我越来越觉得，Agent 带来的变化并不是“给 IoT 平台加一个聊天入口”，而是会重新划分 IoT 技术栈中哪些东西是基础设施，哪些东西只是过去为了方便人类使用而预先打包好的产品形态。

我的核心判断可以先压缩成一句话：

> **契约留下，打包物被解包到运行时。**

MQTT、设备状态、物模型、能力描述、安全边界这些东西不会因为 Agent 出现而消失。相反，它们会变得更重要。真正可能被削弱的是把大量用户意图提前写死的联动、Workflow，以及围绕固定功能导航设计的 App。

## 1. 先看一个现实问题：Agent 到底有没有能力接管 IoT？

这件事不能只靠 Demo 判断。

最近出现的智能家居 Agent 基准已经在把问题从“模型会不会调用 API”推进到“模型能不能理解环境、处理状态、安排时间并验证结果”。

**SMH-Bench** 基于可执行、可验证的智能家居模拟环境，包含 1,100 个任务、7 个大类和 22 个细分类别，并覆盖不同复杂度的家庭环境；论文报告的主要困难集中在自动化调度、歧义处理和个性化推理等任务上。citeturn0academia38

**SimuHome** 则进一步把时间和环境状态放进模拟器：设备动作会持续影响温度、湿度等环境变量，并支持时间加速的 Workflow 调度。它提供了 600 个 benchmark episodes，覆盖状态查询、隐式意图理解、设备控制和 Workflow scheduling。citeturn0academia36turn0search37

这两个方向让我觉得很重要：

```text
过去：
自然语言 → API 调用是否正确？

现在：
自然语言
   ↓
理解用户真正目标
   ↓
理解当前环境状态
   ↓
选择能力
   ↓
执行
   ↓
观察现实变化
   ↓
验证目标是否达到
   ↓
必要时继续行动
```

也就是说，IoT Agent 的 benchmark 正在从 **instruction → action** 走向 **goal → environment → action → outcome**。

这和我之前对 Agent Loop 的理解其实是同一件事：**真正困难的不是调用工具，而是让行动进入现实世界以后还能形成反馈闭环。**

## 2. 因此，我开始重新看 IoT 的技术栈

传统 IoT 大致可以理解为：

```text
Device
  ↓
Link / Protocol
  ↓
Device Model / Capability
  ↓
Rule / Workflow / Scene
  ↓
App / Dashboard
  ↓
Human
```

Agent 进入以后，我认为这里会发生一个很有意思的变化：

```text
                     Agent
                       ↓
             Intent / Goal / Planning
                       ↓
          Capability / Tool / Policy
                       ↓
          Device Model / Physical Contract
                       ↓
             MQTT / Matter / Gateway
                       ↓
                Physical World
                       ↓
             State / Telemetry
                       ↓
                  Feedback
                       ↺
```

所以我现在不太愿意简单地说“应用层会消失”。更准确的说法是：**应用层中的“预先打包确定性”会被重新分配。**

## 3. 什么是“打包物”？

传统 IoT App 本质上做了一件非常有价值的事情：把设计者能够预想到的用户需求提前做成按钮、页面、场景和规则。

例如：

```text
“回家模式”
  → 打开客厅灯
  → 打开空调
  → 关闭安防
  → 拉开窗帘
```

这是一个非常好的产品设计，但它本质上是把一个常见意图**提前打包成一个确定性 Workflow**。

Agent 出现以后，用户可能直接说：

> “我刚回家，帮我把客厅调整成适合晚上休息的状态。”

Agent 可以根据时间、环境、设备状态、用户偏好和当前设备可用性，动态决定应该调用哪些能力。

因此：

- **联动不会凭空消失**，它可能成为 Agent 可以调用的确定性执行器；
- **Workflow 不一定消失**，反而可能成为 Agent 验证过后生成的高效执行路径；
- **App 也不会完全消失**，授权、危险操作、异常处理、设备配置和人工接管仍然需要明确界面。

真正可能被削弱的是：**为了覆盖大量可能的人类意图，而提前做出来的大量固定入口。**

所以我更愿意把这个变化叫做：

> **不是 Layer 消失，而是 Packaging 被解包。**

## 4. 为什么 MQTT 反而不会消失？

这里是我觉得最值得强调的一点。

如果 Agent 变得越来越强，它反而更需要一个确定性的执行面。

Agent 可以是不确定的：它可能选择不同的策略、不同的工具、不同的行动顺序。但最终它必须把决策落到一个能够被机器确定执行的接口上。

因此：

```text
Agent：不确定
   ↓
Capability Contract：确定
   ↓
Protocol / Link：确定
   ↓
Device：确定
   ↓
Physical World：真实反馈
```

MQTT、Matter、网关、设备状态同步、QoS、离线缓存等解决的是“消息怎么可靠地到达设备”的问题。Agent 并没有消灭这个问题。

相反，Agent 越像一个动态控制器，下面的确定性基础设施就越重要。

所以“Link 层还在”并不只是因为它比较底层，而是因为它承担了**确定性契约的一部分**。

## 5. 真正升值的可能是 Capability Contract

如果过去 Device Model 主要是给平台和 App 用的，那么 Agent 时代，它会逐渐变成 Agent 的 API。

Agent 不应该只知道：

```text
light_001
```

它需要知道：

```text
这是一个什么设备？
可以读什么？
可以写什么？
当前状态是什么？
哪些参数有范围限制？
需要什么权限？
哪些操作有风险？
执行以后如何验证？
```

因此我认为 IoT 平台真正重要的抽象会从 **Device** 向 **Capability + State + Constraint + Outcome** 演化。

这也是为什么最近看到 MHS（Model Hardware Standard）时，我觉得它和 IoT Agent 的方向非常契合。

## 6. MHS 更像“物理世界的 Capability Contract”

MHS 当前是一个面向科学研究和先进制造设备的研究预览。它的核心思路是：通过标准化 driver、设备描述、状态、能力以及安全边界，让 Agent 可以发现和操作物理设备；控制路径可以通过 MCP、CLI 或代码 API 来完成。citeturn0search6turn0search3

我觉得这里有一个很好的区分：

> **MHS 不负责规定消息怎么传，它更接近“这台机器是什么、能做什么、现在是什么状态、哪些事情不能做”的物理能力契约。**

可以把它理解成：

```text
MHS
├── Device Description
├── Capability
├── State
├── Constraint
├── Safety Boundary
└── Driver

        ↓
   MCP / CLI / API
        ↓
      Agent
```

而 MQTT / Matter 之类更偏向另一侧：

```text
“这条消息如何到达设备？”
“如何发现设备？”
“如何可靠传输？”
“如何在网络不稳定时运行？”
```

两者并不冲突。

从这个角度看，**MCP 可以理解为 Agent ↔ Software 的连接协议，而 MHS 更接近 Agent ↔ Physical Capability 的描述与执行基础。** MHS 官方也明确把两者定位为互补关系，而不是互相替代。citeturn0search4turn0search6

## 7. 于是 IoT 的技术栈可能重新分层

我现在更倾向于下面这个模型：

```text
┌──────────────────────────────────────────┐
│ Agent / Intent / Goal / Planning         │  ← 新的动态决策层
├──────────────────────────────────────────┤
│ Tool / Capability / Policy / Verification│  ← Agent-facing layer
├──────────────────────────────────────────┤
│ Device Contract / MHS / Device Model    │  ← 物理能力契约
├──────────────────────────────────────────┤
│ MQTT / Matter / Gateway / Edge           │  ← 连接与运行基础设施
├──────────────────────────────────────────┤
│ Sensor / Actuator / Device               │  ← 物理世界
└──────────────────────────────────────────┘

        ↑
   Feedback / Telemetry
        │
        └────────────── Agent Loop
```

而原来处在中间的：

```text
Scene
Workflow
Automation
App Navigation
固定联动
```

不会全部消失，而是逐渐变成三种东西：

1. **确定性执行器**：把已经验证过的动作快速执行；
2. **约束与安全层**：保证 Agent 不越界；
3. **人工兜底界面**：危险操作、授权、异常处理仍然需要显式控制。

## 8. 这其实改变了 IoT 平台的产品定位

传统 IoT 平台更像：

> **连接设备 + 管理设备 + 配置自动化。**

Agent-native IoT 平台更像：

> **把物理世界变成一个 Agent 可以发现、理解、调用、观察和持续控制的 Runtime。**

于是平台真正需要建设的东西也会变化：

- Device Model → Capability Model；
- API → Tool；
- Telemetry → Observation；
- Rule → Constraint / Deterministic Executor；
- Workflow → Verified Execution Path；
- App → Intent UI + Authorization + Human Override；
- Device Management → Capability Discovery；
- Automation → Goal-driven Loop；
- Monitoring → Outcome Verification。

## 9. Benchmark 和 MHS，其实指向的是同一个问题

这是我觉得最有意思的地方。

表面上看，SMH-Bench / SimuHome 是在测“Agent 到底有多聪明”；MHS 是在定义“硬件怎么被 Agent 理解”。

但它们其实在解决同一个系统问题：

> **Agent 能不能可靠地把语言中的目标，落到一个真实、受约束、可观察的物理世界中？**

Benchmark 在测：

```text
Agent
  ↓
能不能理解？
能不能规划？
能不能行动？
能不能处理时间？
能不能验证？
```

MHS / Device Contract 在解决：

```text
Physical World
  ↓
能不能被发现？
能不能被描述？
能不能知道能力？
能不能知道边界？
能不能安全执行？
```

两边最终会在 Runtime 汇合：

```text
          Agent Capability
                 ↓
        ┌─────────────────┐
        │   Agent Runtime │
        └────────┬────────┘
                 ↓
      Capability / Tool Layer
                 ↓
        Device Contract
                 ↓
       MQTT / Matter / Edge
                 ↓
        Physical Environment
                 ↓
          Observation
                 ↺
```

## 10. 最终，我更愿意把它叫做 Physical Infrastructure

如果这个方向成立，那么未来 IoT 平台最重要的变化可能不是“多了多少 AI 功能”，而是它从一个**设备自动化平台**逐渐变成一个**Physical Infrastructure for Agents**。

它提供的不是一堆预先设计好的按钮，而是：

```text
What exists?
      ↓
What can it do?
      ↓
What is its current state?
      ↓
What is allowed?
      ↓
What can I safely execute?
      ↓
Did the physical world actually change?
      ↓
Did the goal actually happen?
```

这和 Kubernetes 给软件世界提供 Runtime 的思路有一点相似：底层负责提供稳定、可观测、可调度的执行基础，上层的智能系统负责不断把目标和现实状态拉近。

所以我现在对 IoT Agent 化的一个更明确判断是：

> **Agent 不会消灭 IoT 的基础设施。恰恰相反，它会让 IoT 从“给人使用的设备平台”，进一步变成“给 Agent 使用的物理基础设施”。**

而真正可能被 Agent 解构的，不是 MQTT，也不是设备能力本身，而是过去为了让人类操作方便而提前打包好的那一层确定性。

**契约留下，打包物解包；连接留下，决策上移；规则留下，但越来越像执行器和约束；App 留下，但越来越像授权、配置和人工接管。**

### 参考

- SMH-Bench：Benchmarking LLM Agents for Environment-Grounded Reasoning and Action in Smart Homes（arXiv, 2026）
- SimuHome：A Temporal- and Environment-Aware Benchmark for Smart Home LLM Agents（ICLR 2026）
- Model Hardware Standard（MHS）Research Preview（Anthropic, 2026）
