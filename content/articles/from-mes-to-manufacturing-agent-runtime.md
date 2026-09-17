---
id: from-mes-to-manufacturing-agent-runtime
type: Articles
title: 从 MES 到 Manufacturing Agent Runtime：当生产系统开始自己做决策
date: 2026-09-16
thought_date: 2026-09-16
published_date: 2026-09-16
tags: [Agent, Manufacturing, MES, Agent Runtime, Control Plane, Supply Chain, Decision Engineering]
stage: published
origin: joint
contribution: extension
thought_id: thought-mes-agent-runtime
excerpt: SHEIN 式制造的关键不是把 MES 加上一个 Copilot，而是把高频、动态、组合复杂的生产决策变成 Agent Runtime 的持续闭环。核心观点：不要替代岗位，要替代决策单元。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/from-mes-to-manufacturing-agent-runtime.md
last_verified: 2026-09-16
cadence_days: 90
---

# 从 MES 到 Manufacturing Agent Runtime：当生产系统开始自己做决策

这篇文章来自我对 SHEIN 式制造模式、MES 和 Agent Runtime 的连续思考。

这里并不是试图还原 SHEIN 的内部系统，而是把一种已经存在于数字化供应链中的业务闭环抽象出来，再问一个问题：**如果 Agent 真正进入制造系统，业务架构应该发生什么变化？**

我越来越觉得，答案不是「给 MES 加一个 AI Copilot」，也不是简单地给每个岗位配一个 Agent。

真正的变化可能是：

> **生产系统从“执行已经确定的流程”，逐渐变成“持续观察现实、做出决策、执行、验证并重新规划”的 Manufacturing Agent Runtime。**

而其中一个非常重要的设计原则是：

> **不要替代岗位，要替代决策单元。**


本文会区分三种表达：

- **已观察事实**：来自现有业务系统、生产实践或可复现数据的描述。
- **工程判断**：基于这些事实提出的架构判断或设计建议。
- **未来推测**：对行业和系统形态可能如何演化的假设。

后文的架构图和 Agent 分工主要属于工程判断，不等同于某一家企业已经采用的内部事实。

---

## 1. 传统 MES 与 Agent 化制造的区别

传统 MES 可以抽象成：

```text
订单
 ↓
生产计划
 ↓
排产
 ↓
工单
 ↓
生产
 ↓
质检
 ↓
入库
```

它解决的核心问题是：

> **如何把已经确定的生产计划数字化、透明化，并稳定执行。**

在本文的抽象中，MES 主要承担生产执行、过程追踪、状态记录和约束落地；跨订单、跨工厂、跨供应链的动态决策，通常还需要 APS、SCM、ERP 等系统共同参与。

但当制造模式变成高频、小批量、快速反馈时，问题开始变化：

```text
用户需求
   ↓
小批量测试
   ↓
真实销售反馈
   ↓
重新判断需求
   ↓
追加生产
   ↓
再次反馈
```

**已观察事实：** 在高频、小批量、快速反馈的制造模式中，需求、库存、产能和订单状态会持续变化，生产计划通常需要反复调整。

**工程判断：** 因此真正需要 Agent 化的，不是 MES 的所有功能，而是 MES 上方那些不断变化、需要重新组合资源的决策过程。

---

## 2. 为什么 SHEIN 式模式天然适合 Agent

如果把这种制造模式抽象掉具体公司的业务细节，会发现它具有几个非常典型的特征：

```text
大量 SKU
+
大量供应商
+
大量小订单
+
快速生产
+
快速市场反馈
+
快速重新生产
```

这意味着系统中的状态变化非常快。

一个订单表面上只是：

```text
生产 10,000 件
```

但真正的决策可能同时涉及：

```text
5 个供应商
20 条生产线
8 种材料
3 种工艺
不同质量水平
不同交期
不同价格
不同物流距离
当前库存
当前在制品
已有订单
机器状态
```

真正的问题变成：

```text
10,000 件
   ↓
怎么拆？
   ↓
给谁？
   ↓
什么时候做？
   ↓
用什么材料？
   ↓
走哪条产线？
   ↓
如果出现延迟怎么办？
```

这已经不是简单的 Workflow，而是：

> **Combinatorial Optimization + Dynamic Decision Making**

组合一多，规则数量会迅速膨胀；状态变化一快，固定流程又容易失效。

**工程判断：** 这正是 Agent 可能有价值的地方：不是“会聊天”，而是能够在巨大的可能性空间中生成、比较和调整方案。

---

## 3. Agent 化 MES：不是替代 MES，而是增加一个决策层

我更倾向于把业务架构设计成五层：

```text
                ┌──────────────────────────┐
                │     Business Control     │
                │       Control Plane      │
                └────────────┬─────────────┘
                             │
                    Goal / Constraint
                             │
                ┌────────────▼─────────────┐
                │      Agent Runtime       │
                │   Planning / Decision    │
                └────────────┬─────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
     Demand Agent       Production Agent    Supply Agent
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ↓
                ┌──────────────────────────┐
                │       MES / WMS / SCM    │
                │     Deterministic Layer  │
                └────────────┬─────────────┘
                             ↓
                ┌──────────────────────────┐
                │ Factory / Machine / IoT  │
                │ PLC / MQTT / Sensors     │
                └──────────────────────────┘
```

**工程判断：** 这里有一个重要原则：

> **Agent 不应该取代 MES。**

MES 仍然负责确定性执行、状态记录、工艺与生产过程管理；Agent 在其上方负责动态决策。

这和我之前对 Agent Control Plane / Runtime 的理解是一致的：

- Control Plane 管目标、约束、策略、审批与调度
- Agent Runtime 管执行、状态、规划与循环
- MES/WMS/SCM 继续作为确定性业务能力
- 工厂、机器和 IoT 是现实世界的执行面

---

## 4. 不应该先设计“岗位 Agent”，而应该先设计“决策 Agent”

一个很容易走偏的设计方式是：

```text
MES Agent
├── 查询 Agent
├── 修改 Agent
├── 数据 Agent
└── 报表 Agent
```

这其实只是 AI CRUD。

另一种看起来更自然的方式是：

```text
供应商经理 Agent
生产经理 Agent
仓库经理 Agent
```

但我觉得这依然不是最好的抽象。

因为一个岗位实际上包含很多不同类型的工作：

```text
Routine
Decision
Communication
Judgement
Responsibility
```

Agent 最先适合接管的是其中的：

```text
Routine + Decision
```

而责任、重大判断和高风险授权并不会因为 Agent 出现就自动消失。

所以更好的拆法是：

```text
Supplier Manager
├── 找供应商
├── 比较供应商
├── 判断交期
├── 监控质量
├── 处理异常
└── 调整订单

             ↓

Supplier Discovery Agent
Supplier Matching Agent
Supplier Monitoring Agent
Supplier Recovery Agent
```

也就是说：

> **不是替代一个职位，而是拆解一个职位中的决策单元。**

这会直接改变 Agent 产品的设计方式。

---

## 5. 哪些工作最值得 Agent 化？

我认为不能只看“这个岗位是不是重复劳动”，而应该同时看以下条件：

```text
决策频率
×
组合复杂度
×
随机性
×
反馈速度
×
可验证性
×
可观测性
×
可行动性
×
结果归因
×
权限可控性
×
经济价值
```

前五项描述问题本身是否适合动态决策，后五项决定 Agent 是否真的能被部署和治理。高复杂度只是必要线索，不是充分条件：如果状态不可观测、结果无法归因、没有可执行接口，或者错误成本与集成成本远高于收益，就不应该因为“复杂”而强行 Agent 化。

可以先形成一个简单的判断框架：

| 工作类型 | 随机性 | 组合复杂度 | 可验证性 | 更适合的形态 |
|---|---:|---:|---:|---|
| 数据录入 | 低 | 低 | 高 | Automation |
| 固定工艺流程 | 低 | 低 | 高 | Workflow |
| 生产排产 | 中 | 高 | 高 | Agent |
| 供应商匹配 | 高 | 高 | 中高 | Agent |
| 物料调度 | 高 | 高 | 高 | Agent |
| 异常恢复 | 高 | 高 | 中高 | Agent |
| 质量分析 | 中高 | 高 | 高 | Agent + Model |
| 需求预测 | 高 | 高 | 中 | Agent + Model |
| 新产品工艺设计 | 高 | 高 | 较低 | Human + Agent |
| 重大采购/安全决策 | 高 | 高 | 低 | Human + Agent |

这里会出现一个很有意思的结论：

> **最应该 Agent 化的，不一定是人数最多的岗位，而是“决策密度最高”的岗位。**

---

## 6. 随机性与组合复杂度，是两个非常重要的坐标轴

可以把制造任务放在一个二维空间里：

```text
                    Decision Complexity
                           ↑
                           │
        Human              │       Agent + Human
                           │
     战略决策              │       高风险异常
     重大采购              │       新产品
     安全                   │       重大质量
                           │
                           │
───────────────────────────┼────────────────────→ Randomness
                           │
     Workflow              │       Agent
                           │
     数据录入              │       排产
     固定审批              │       调度
     固定工艺              │       异常处理
                           │       供应商匹配
                           │       库存优化
```

最适合 Agent 的，不是简单的高随机性，而是：

> **高随机性 + 高组合复杂度 + 快速反馈 + 可验证结果 + 可观测、可执行且风险可控。**

可以把 Agent 化的经济边界粗略写成：

```text
可获得的决策收益
+ 响应速度收益
+ 反馈闭环收益
>
模型成本
+ 集成成本
+ 错误与补偿成本
+ 治理成本
```

这不是精确的财务模型，但可以提醒我们：规则很多并不自动意味着 Agent 更经济。

例如生产排程：

```text
订单
 ↓
供应商
 ↓
产能
 ↓
材料
 ↓
工艺
 ↓
交期
 ↓
质量
 ↓
成本
```

其中任何一个状态变化，都可能导致整个方案重新计算。

**工程判断：** 这比“固定流程自动化”更可能需要 Agent；如果约束足够明确、反馈周期足够短，也可能由优化器或 Workflow 更经济地解决。

---

## 7. Agent 最有价值的地方：处理异常，而不是正常流程

现实生产中，正常路径往往并不难。

真正昂贵的是异常：

```text
订单延迟
材料缺货
机器故障
质量下降
供应商拒单
物流延迟
需求突然上涨
```

传统 MES：

```text
正常路径
──────────────→
                ↓
              异常
                ↓
            人工处理
```

Agent Runtime：

```text
Normal
   ↓
Event
   ↓
Re-plan
   ↓
Execute
   ↓
Verify
   ↓
Continue
```

因此我甚至会认为：

> **Exception Agent 可能比“MES Copilot”更接近制造 Agent 的核心价值。**

例如某工厂突然延迟 6 小时：

```text
Production Agent
      ↓
发现延迟
      ↓
计算影响范围
      ↓
是否换工厂？
是否拆单？
是否加急？
是否调整批量？
      ↓
生成 Recovery Plan
      ↓
Simulation / Verification
      ↓
Execute
```

这已经不是 Workflow，而是一个持续运行的决策闭环。

---

## 8. Event Bus 会成为 Agent Manufacturing 的神经系统

如果 Agent 只是不断查询 MES：

```text
Agent
  ↓
查询 MES
  ↓
查询 MES
  ↓
查询 MES
```

整个系统会很重。

更自然的架构是 Event-driven：

```text
                    Event Bus
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 Demand Agent     Production Agent   Supply Agent
       │               │               │
       └───────────────┼───────────────┘
                       ↓
                    Decision
                       ↓
                    Action
                       ↓
                  Verification
                       ↓
                    New Event
```

事件可以是：

```text
DemandChanged
OrderCreated
MaterialDelayed
FactoryCapacityChanged
QualityDegraded
ShipmentDelayed
InventoryLow
```

于是制造系统形成一个循环：

> **Event → Agent → Action → Verification → Event**

但生产系统不能只靠事件触发和 Agent 自由协作。Runtime 还必须提供状态存储、事件溯源、幂等执行、任务优先级、权限审批、超时处理、补偿事务和决策审计，否则多个 Agent 可能重复执行、互相覆盖，甚至形成事件循环。事件总线负责传播变化，Control Plane 负责决定谁可以在什么条件下采取什么动作，Execution Plane 负责把获批动作可靠地落到业务系统。

这和 Agent Runtime 的 Loop Engineering 是同一个思想，只是执行对象从软件任务扩展到了现实生产。

---

## 9. Demand Agent：决定“应该生产多少”

Demand Agent 负责的不是简单报表，而是持续回答：

> **“现在到底应该生产多少？”**

它可以观察：

```text
销量
点击
收藏
搜索
转化率
库存
历史数据
季节
营销活动
```

然后产生一个带置信度和验证方式的判断：

```yaml
forecast: 3000
confidence: 0.83
verification:
  - future_sales
  - inventory_turnover
```

这里我特别倾向于保留一个原则：

> **Agent 的判断不仅要有结果，还应该有置信度和验证方式。**

因为预测本身不是事实。

真正重要的是后续反馈能否证明它。

---

## 10. Production Agent：决定“怎么生产”

假设需求是：

```text
3000 件
```

系统可能有：

```text
Factory A
capacity = 1000
quality = 96%
lead_time = 2 days

Factory B
capacity = 2000
quality = 94%
lead_time = 3 days

Factory C
capacity = 500
quality = 98%
lead_time = 1 day
```

Agent 可以生成候选方案：

```text
Plan #1
A 1000
B 1500
C 500
```

然后交给确定性的工具验证：

```text
Cost
Lead Time
Quality
Risk
Capacity Constraint
Material Constraint
```

所以这里我不希望 LLM 自己“拍脑袋决定”。

更合理的链路是：

```text
LLM
 ↓
生成 Plan
 ↓
Simulator
 ↓
Constraint Checker
 ↓
Business Rules
 ↓
Optimizer
 ↓
Execute
```

> **Agent 是 Planner，而不是最终真相。**

---

## 11. Supplier Agent：从供应商管理走向供应商智能网络

传统系统中的供应商通常只是：

```text
供应商 A
供应商 B
供应商 C
```

系统记录供应商数据，但并不一定真正理解当前哪个供应商最适合哪个订单。

Agent 可以持续维护：

```text
capacity
quality
delivery
price
response speed
historical success
current workload
machine capability
```

于是问题从：

> “有哪些供应商？”

变成：

> “当前这个订单，在当前约束下，谁最适合生产？”

**未来推测：** 这时候供应商系统可能从 Supplier Management 逐渐变成 Supplier Intelligence Network。

---

## 12. 人机分工：风险越高，越需要 Approval Gate

Agent 并不是所有事情都应该自动执行。

例如：

```text
普通排产调整
        ↓
Agent 自动执行
```

而：

```text
重大质量事故
重大采购
重大供应商变更
安全相关操作
高额不可逆操作
        ↓
Agent Proposal
        ↓
Human Approval
        ↓
Execute
```

所以 Control Plane 中应该存在 Approval 这样的一级对象。

可以理解成：

```text
Low Risk
Agent → Execute

Medium Risk
Agent → Verify → Execute

High Risk
Agent → Proposal → Human Approval → Execute
```

这也是为什么“岗位是否被替代”不是最好的问题。

更好的问题是：

> **这个决策是否可以被机器稳定地验证？错误成本是多少？是否允许自动执行？**

---

## 13. Manufacturing Agent Runtime：最终业务架构

综合起来，我更倾向于下面这套架构：

```text
                         Business Goal
                              │
                              ↓
                    ┌──────────────────┐
                    │  Control Plane   │
                    │                  │
                    │ Demand           │
                    │ Production       │
                    │ Supply           │
                    │ Inventory        │
                    │ Policy           │
                    │ Approval         │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  Agent Runtime   │
                    │                  │
                    │ Planner          │
                    │ Executor         │
                    │ Verifier         │
                    │ Optimizer        │
                    │ Memory           │
                    └────────┬─────────┘
                             ↓
                         Event Bus
                             │
          ┌──────────────────┼──────────────────┐
          ↓                  ↓                  ↓
     Demand Agent      Production Agent    Supplier Agent
          ↓                  ↓                  ↓
     Inventory Agent    Quality Agent      Logistics Agent
          └──────────────────┼──────────────────┘
                             ↓
                    ┌──────────────────┐
                    │ Execution Plane  │
                    │                  │
                    │ MES              │
                    │ WMS              │
                    │ ERP              │
                    │ SCM              │
                    └────────┬─────────┘
                             ↓
                    Factory / IoT / PLC
                             │
                             ↓
                         Real World
                             │
                             └──── Event ────→
```

**工程判断：** 在这套目标架构中，MES 的位置发生了变化。

它仍然非常重要，但不再是整个业务决策系统的最高层。

它更像：

> **Execution Plane。**

而 Agent Runtime 成为：

> **Decision + Reconciliation Plane。**

---

## 14. K8s 类比：制造系统也可以拥有 Desired State

这和我之前思考 Kubernetes × Agent 的方向可以直接连接起来。

Kubernetes 的核心是：

```text
Desired State
      ↓
Actual State
      ↓
Gap
      ↓
Controller
      ↓
Action
      ↓
Actual State
      ↓
Gap
```

**工程判断：** 制造 Agent 可以使用类似的结构：

```text
Production Target
      ↓
Factory Reality
      ↓
Gap
      ↓
Agent Controller
      ↓
Re-plan
      ↓
Execute
      ↓
Verify
      ↓
Gap
```

例如：

```yaml
production:
  sku: A
  quantity: 3000
  deadline: 2026-09-20
  quality: "> 98%"
  cost: "< $5"
```

这不是一次性的生产计划，而可以被理解成一个 Desired State。

现实世界不断变化：

```text
Desired State
      ↓
Actual State
      ↓
Gap
      ↓
Reconcile ↻
```

因此制造 Agent 的核心能力之一，也可以理解为：

> **持续把现实生产状态向业务目标收敛。**

---

## 15. 但制造世界比 K8s 更复杂：重试不等于重启

这里也必须小心 K8s 类比。

K8s 可以重启 Pod，但生产系统里的动作可能产生不可逆副作用。

例如：

```text
已经发货
已经采购
已经投料
已经生产
已经付款
```

这时如果 Agent 发现目标没有达成，不能简单地：

```text
retry()
```

而可能需要：

```text
补偿
审批升级
重新排产
回滚业务状态
停止执行
```

所以：

> **Manufacturing Agent 的 Reconciliation 必须理解业务副作用。**

这也是 Agent Control Plane 和普通基础设施 Control Plane 的一个重要区别。

---

## 16. 三条环：Execute / Eval / Learn

如果再往前推一步，我会把 Manufacturing Agent Runtime 看成三个不同速度的 Loop：

```text
Execute Loop
秒 → 小时
Goal → Plan → Act → Observe → Adjust

Eval Loop
小时 → 天
Trajectory → Outcome → Evaluation → Gate

Learn Loop
天 → 周
Evidence → Policy → Optimization → Rollout
```

对应到制造：

### Execute Loop

当前订单怎么完成？

```text
Goal
 ↓
Plan
 ↓
Execute
 ↓
Observe
 ↓
Adjust
```

### Eval Loop

这次方案到底有没有真的成功？

```text
计划
 ↓
实际生产结果
 ↓
成本 / 交期 / 质量
 ↓
评估
```

### Learn Loop

下一次怎么做得更好？

```text
历史轨迹
 ↓
失败模式
 ↓
成功模式
 ↓
策略更新
 ↓
小流量验证
```

这和 Agent 系统中的 Execute / Eval / Learn 三环是一致的。

---

## 17. 最后真正值得讨论的，不是“AI 替代多少人”

如果只从岗位出发，我们很容易得到一个简单但不够有用的问题：

> “生产经理会不会被 Agent 替代？”

我觉得更有架构意义的问题应该是：

> **生产经理今天到底在做哪些决策？哪些决策可以被结构化？哪些决策可以被验证？哪些决策的组合空间正在爆炸？哪些决策的反馈周期足够短？**

于是岗位会逐渐被拆成：

```text
岗位
 ↓
工作
 ↓
决策单元
 ↓
Decision Agent
 ↓
Policy
 ↓
Tool
 ↓
Verification
```

这会让 Agent 的边界变得清晰。

Agent 不一定直接“替代一个人”，而可能先替代一个人的一部分决策循环。

然后随着验证能力越来越强，这些决策循环逐渐扩大。

---

## 18. 我的一个暂时结论

如果把 SHEIN 式制造模式抽象成一个系统，我会这样描述：

> **它本质上是一个高频反馈的制造控制系统。**

而 Agent 化之后：

```text
Agent
= Manufacturing Decision Controller

MES
= Execution System

Event Bus
= Nervous System

IoT
= Sensors

Factory
= Actuators

Control Plane
= Business Goal + Policy + Scheduling

Agent Runtime
= Observe → Decide → Act → Verify → Reconcile
```

这里的 Controller 指制造业务的动态决策控制层，而不是 PLC、DCS 或安全联锁意义上的实时设备控制器。实时控制和安全边界仍应由确定性的工业控制系统负责。

因此未来的 Manufacturing Agent 不应该只是：

```text
MES + LLM
```

更可能是：

```text
MES
+
Event System
+
Agent Runtime
+
Optimization
+
Verification
+
Human Approval
```

而我目前最想保留的一个判断是：

> **不要替代岗位，要替代决策单元。**

因为真正决定 Agent 是否有价值的，不是“它像不像一个人”，而是：

> **它能不能在高频、随机、组合复杂的现实环境中，持续做出决策，并通过真实结果验证自己，再进入下一轮。**

**未来推测：** 这也许才是从传统 MES 走向 Manufacturing Agent Runtime 的一条可能路径。

---

## 开放问题

- 哪些制造决策的反馈周期足够短，可以形成真正的 Agent Loop？
- 排产、供应商匹配、库存、物流之间的 Agent 应该独立运行，还是共享一个 Planner？
- 什么样的 Simulator / Constraint Checker 才能成为 Agent 的“现实世界测试”？
- 哪些 Outcome 可以机器验证，哪些必须保留人工验收？
- 当一个 Agent 可以处理越来越大的决策空间时，岗位边界会如何重新组织？
- Manufacturing Agent Runtime 是否最终会像 Kubernetes 一样形成自己的 Control Plane、Runtime、Scheduler、Policy、Event 与 Reconciliation 体系？
