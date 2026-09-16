---
id: iot-agent-from-automation-to-physical-infrastructure-part-ii
type: Articles
title: IoT Agent 化：从自动化平台到 Physical Infrastructure（二）
date: 2026-09-16
thought_date: 2026-09-16
published_date: 2026-09-16
tags: [Agent, IoT, Physical AI, Architecture, Benchmark]
excerpt: 第一篇讨论“契约留下，打包物被解包到运行时”。这一篇继续往下追：当 Agent 真正进入物理世界，IoT 平台究竟应该提供什么？
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/iot-agent-from-automation-to-physical-infrastructure-part-ii.md
last_verified: 2026-09-16
cadence_days: 90
---

# IoT Agent 化：从自动化平台到 Physical Infrastructure（二）

## 一、上一篇之后，我重新确认了一件事

第一篇的核心判断是：Agent 不会消灭 IoT 基础设施。MQTT、Matter、设备能力描述、物模型、安全约束这些“契约”仍然存在；真正可能被解构的是为了服务人类而提前打包好的场景、联动和固定交互。

但这个判断还缺了一层：**Agent 到底凭什么能够在物理世界里完成任务？**

最近阅读 SimuHome，以及把它和 SMH-Bench、MHS 放在一起看之后，我觉得答案逐渐清楚了：**IoT 平台未来最重要的能力，不只是“连接设备”，而是给 Agent 一个可以观察、行动、验证和恢复的 Physical Runtime。**

## 二、SimuHome 把问题从 API 拉回了环境

传统智能家居 Agent 测试，很容易变成“用户说一句话，Agent 调一个 API”。但真实家庭不是 API 列表，而是一个持续变化的状态空间。

SimuHome 的价值就在这里：它让设备动作持续影响环境变量，并引入虚拟时间来测试未来调度和多步骤工作流。这样评价对象从“API 调得对不对”，变成了“行动之后环境有没有进入预期状态”。

**我的理解：**IoT Agent 的真正对象不是 Device API，而是 Environment State。

## 三、所以 IoT Agent 的闭环应该改变

```text
过去：
User → App → Rule → API → Device

Agent 时代：
Goal
  ↓
Observe State
  ↓
Plan
  ↓
Act
  ↓
Environment Changes
  ↓
Observe / Verify
  ↓
Re-plan / Recover
```

这和 Coding Agent 非常像。代码 Agent 写完代码不代表完成，必须编译、测试、检查结果；IoT Agent 发出 `turn_on` 也不代表任务完成，必须确认设备和环境真的发生了预期变化。

因此我越来越倾向于把 Agent 的成功定义为：**Target State 与 Actual State 的差距不断缩小。**

## 四、SMH-Bench 和 SimuHome 共同说明了什么？

如果把 benchmark 看成一面镜子，两个方向都在把 Smart Home Agent 从“工具调用题”变成“环境推理题”。SimuHome 强调时间动态、环境变量和 workflow；SMH-Bench 则进一步扩大任务覆盖和家庭规模，测试 Agent 在复杂环境中的 reasoning + action。

这意味着未来 benchmark 的关键指标可能也要发生变化：

- 不是只测 tool-call accuracy；

- 而要测目标状态是否达成；

- 失败之后能不能发现；

- 能不能根据反馈继续行动；

- 多步任务能不能最终收敛。

## 五、这也重新解释了“固定联动为什么可能被解构”

以前的平台需要提前告诉用户：当 A 发生时，如果 B，就执行 C。因为计算和交互成本很高，所以平台把常见意图预先打包成“场景”。

Agent 出现后，部分场景可以从**静态规则**变成**运行时策略**。

但这里有一个很重要的修正：**不是规则消失，而是规则的位置发生变化。**

安全边界、权限、设备约束、不可执行条件仍然应该是确定性的；Agent 可以负责在这些边界内部进行动态规划。

确定性约束层：
  “什么绝对不能做？”
  “什么条件下才能做？”

Agent Runtime：
  “现在应该做什么？”
  “先做哪个？”
  “做完后是否达到目标？”

## 六、MHS 让我重新理解了“设备描述”

MHS 这类思路很重要，因为 Agent 并不应该直接面对杂乱的厂商协议。设备需要被描述成 Agent 可以理解的能力边界：它是什么、能读什么、能写什么、有什么安全限制。

因此我会把设备侧抽象成：

Device
  ├── Identity
  ├── Capabilities
  ├── State
  ├── Constraints
  ├── Safety Limits
  └── Driver / Link

其中 Driver / Link 负责“怎么送过去”；Capability Contract 负责“这台设备是什么、允许做什么”；State 负责“现在发生了什么”；Safety / Constraints 则负责“不能越过哪里”。

这也是为什么我现在不太认同“Agent 会把 IoT 底层吃掉”这种说法。恰恰相反，**Agent 越强，底层契约越重要。**

## 七、真正新增的可能是一层：Physical Runtime

传统 IoT 平台主要解决 Device Management、Connectivity、Rules、Dashboard。Agent 进入之后，需要新增一种运行时能力：

Physical Runtime
  ├── State Observation
  ├── Capability Discovery
  ├── Planning
  ├── Action Execution
  ├── Verification
  ├── Retry / Recovery
  ├── Checkpoint / Resume
  └── Audit / Safety

这和我之前对 Agent Runtime 的理解开始重合：它不是简单的“LLM + Tools”，而是一个持续运行的控制系统。

## 八、因此 App 也不是简单地“消失”

我之前说 App 可能消失，现在我会把这个说法修正得更准确。

**功能导航型 App 会被意图入口大量替代，但 App 本身不会消失。**

权限确认、危险操作确认、设备状态可视化、故障处理、人工接管，这些场景仍然需要确定性的 UI。

所以未来可能不是：

App → 消失

而是：

```text
App
  ↓
从“操作入口”
变成
“Observation / Approval / Fallback Interface”
```

## 九、最终的架构变化

如果把这些东西放在一起，我现在更愿意把 IoT Agent 平台理解成：

```text
┌────────────────────────────────────┐
│           Agent / Intent Layer     │
│        Goal · Planning · Reasoning  │
└──────────────────┬─────────────────┘
                   ↓
┌────────────────────────────────────┐
│          Physical Runtime          │
│ Observe · Act · Verify · Recover   │
└──────────────────┬─────────────────┘
                   ↓
┌────────────────────────────────────┐
│       Capability / Safety Contract │
│   Device Model · Schema · Limits   │
└──────────────────┬─────────────────┘
                   ↓
┌────────────────────────────────────┐
│       Link / Protocol / Gateway    │
│       MQTT · Matter · Edge         │
└──────────────────┬─────────────────┘
                   ↓
┌────────────────────────────────────┐
│        Physical Devices            │
└────────────────────────────────────┘
```

## 十、我的结论

所以第一篇的“Physical Infrastructure”这个词，我现在反而觉得还可以再往前推进一步。

未来的 IoT 平台可能不再只是“管理物理设备的云平台”，而是**Agent 操作物理世界的基础设施**。

它的底层仍然是 MQTT、Matter、网关、设备和物理世界；中间是能力契约、安全约束和状态；上面则出现 Physical Runtime，让 Agent 可以持续地：

**Observe → Plan → Act → Verify → Recover**

这可能是 IoT Agent 化真正值得关注的地方：**不是把 LLM 塞进 IoT 平台，而是把 IoT 平台从“自动化平台”重新定义成“Physical Runtime Infrastructure”。**

如果说传统 IoT 的核心问题是 **How to connect?**，那么 Agent 时代更重要的问题可能变成：**How to make the physical world converge toward a goal?**

而这也让我之前的一个判断变得更清晰：**Agent 正在从 Next API 走向 Next State。**
