---
id: saas-ecommerce-agent-thinking
type: Articles
title: SaaS 电商平台的 Agent 思考
date: 2026-09-07
thought_date: 2026-09-07
published_date: 2026-09-07
tags: [Agent, SaaS, E-commerce, Architecture, Loop Engineering]
excerpt: 从某电商 SaaS 平台出发：Agent 不是给业务系统加一个聊天入口，而是让软件从 API / Workflow 中心逐渐演化为 Goal / Capability / Feedback Loop 中心。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/saas-ecommerce-agent-thinking.md
---

# SaaS 电商平台的 Agent 思考

如果把某电商 SaaS 平台看成一个复杂的软件系统，那么 Agent 改造真正有意思的地方，并不是「增加几个 AI Agent」。更深一层的问题是：原来围绕 UI、API、Workflow 和微服务建立起来的软件，能不能逐渐变成一个围绕 Goal、Capability、Agent 和 Feedback Loop 运行的系统。

## 一、先不要把 Agent 理解成一个新的 UI

传统 SaaS 电商系统的基本路径是：**人 → UI → Workflow → API → 微服务 → 数据**。这套模型成立的前提，是人知道自己要做什么，也能够把目标拆成系统能够理解的操作。

Agent 出现以后，入口开始发生变化：

```text
[Interaction Model]
Traditional SaaS:
  - 人理解业务
  - 人拆解步骤
  - UI 驱动 Workflow
  - API 执行确定性动作


Agent-native SaaS:
  - 人给出 Goal
  - Agent 理解并拆解
  - 动态选择 Capability
  - 根据结果持续调整
```

因此，Agent 的价值不是简单地把「点击按钮」改成「说一句话」，而是把一部分**问题分解、能力选择和过程调整**从人转移给机器。

## 二、为什么「Workflow + LLM」还不够

最容易出现的第一代 Agent 改造，是把已有 Workflow 前面加一个 LLM：`User → LLM → Workflow → API → Result`。这仍然假设流程基本确定。Agent 真正不同的地方应该是：目标可以明确，而路径不一定明确。

> 「帮我把这个新品上线，并尽可能提高转化率。」

系统需要理解目标与约束，检查商品信息，读取历史销售与用户数据，判断需要调用哪些商品、营销和数据能力，执行策略，观察真实结果，并在目标与现实产生差距时继续调整。

所以 Agent 更接近：**Goal → Action → Observation → Gap → Adjustment → …**。这也是 Loop Engineering：重点不在「步骤是否全部跑完」，而在「结果是否越来越接近目标」。

## 三、原有的微服务不需要被推翻

商品、订单、库存、营销、客户、数据等微服务，本身并不是 Agent 时代的负担。它们已经积累了大量确定性的业务能力。真正需要变化的是这些能力的**暴露方式**。

```text
[From API Platform to Agent Capability Platform]
Business Services → API / OpenAPI → Tool Capability → Agent
```

过去 OpenAPI 平台解决的是「让程序能够调用内部能力」。下一阶段更值得建设的是「让 Agent 能发现、理解、授权并安全调用这些能力」。

## 四、Tool Gateway 可能成为新的基础设施层

如果每个 Agent 都直接连接几十甚至几百个业务服务，系统很快会失去治理能力。因此 Agent 与业务服务之间需要一个能力层：

```text
Agent
  ↓
Tool Gateway / Capability Gateway
  ↓
商品 Tool · 订单 Tool · 库存 Tool · 营销 Tool · 数据 Tool
  ↓
Existing Business Services
```

Gateway 不只是 API Proxy。它需要处理 **Capability Discovery、Contract、Tenant、Permission、Routing、Audit / Observability**。这样，原来的微服务继续负责**业务正确性**，Tool Gateway 负责**能力治理**，Agent 负责**目标驱动的决策**。

## 五、从单 Agent 到 Agent Control Plane

当 Agent 数量增加以后，新的问题会出现：任务如何调度？谁可以执行？预算是多少？什么时候需要人工审批？失败后如何恢复？怎样判断真的完成了？

```text
[Agent Control Plane]
Goal / Task → Control Plane → Scheduler → Agent Runtime
Runtime → Tools / Services → Environment → Observation ↻
```

Kubernetes 管的是「服务如何稳定运行」；Agent Control Plane 更关心「智能任务如何被分解、执行、验证并最终完成」。两者可以共享基础设施，但任务语义不是同一件事。

## 六、为什么 Kubernetes 的类比有价值

真正有价值的不是把 Pod 机械地对应成 Agent，而是借用 **Desired State → Actual State → Reconcile** 的系统心智。

```text
[Reconcile Mindset]
Desired State → Actual State → Gap → Reconcile ↻
Goal → Action → Observation → Gap → Adjustment ↻
```

但必须保持边界：K8s 的健康状态通常可以由探针、资源和副本状态检查；Agent 的完成状态经常是语义性的。工具调用成功、接口返回 200、模型自评通过，都不等于真实业务目标已经完成。

## 七、Agent 的真正难点是 Outcome，而不是 Action

传统 Workflow 容易定义成功：步骤全部 OK，Workflow 就 SUCCESS。Agent 则更容易出现：工具调用成功、Proxy Tests PASS、模型自评 PASS，但真实业务 Outcome 仍然未知。

这就是 **Proxy Metric ≠ Real Outcome**。如果平台只奖励「过程跑通」，就会不断优化出看起来完成、实际没有解决问题的 Agent。

因此，一个合理的任务对象至少需要区分：**Goal、Success Criteria、Evidence、Proxy Checks、Real Outcome**。完成声明必须有可核对的证据。

## 八、一个 SaaS 电商 Agent 平台可能长什么样

```text
                    Business Goal
                          │
                          ▼
                ┌──────────────────┐
                │  Agent Control   │
                │      Plane       │
                └────────┬─────────┘
                         │
              Task / Policy / Budget
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Product Agent   Marketing Agent  Service Agent
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                ┌──────────────────┐
                │  Tool Gateway    │
                └────────┬─────────┘
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    商品服务           订单服务           营销服务
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                    Real World
```

Control Plane 管理 Goal、Task、Policy、Budget、Approval、Eval、Replay、Outcome；Runtime 负责执行；Tool Gateway 管理能力发现、权限、租户、路由和审计；Business Services 继续提供可靠的确定性能力；Evaluation / Feedback 判断 Agent 是否真的解决问题。

## 九、Workflow、Graph、Loop 并不是互相替代

| 机制 | 适合解决的问题 | 核心假设 |
|---|---|---|
| Workflow | 确定性业务流程 | 路径基本已知 |
| Graph | 复杂任务结构 | 任务可以表示成有结构的依赖 |
| Loop | 目标与现实持续拟合 | 下一步取决于观察结果 |
| Harness | Agent Runtime 本身 | 需要控制上下文、工具、状态和生命周期 |

成熟的 SaaS Agent 系统很可能同时使用它们：**Graph 组织复杂任务，Workflow 执行确定性步骤，Agent Loop 处理不确定性，Harness 负责运行时治理。**

## 十、真正的改造路径可能是渐进式的

1. **API → Tool**：把已有业务能力变成可发现、可描述、可授权的 Agent Capability。
2. **Workflow → Agent-assisted Workflow**：先让 Agent 负责理解、参数补全和异常处理。
3. **Workflow → Goal-driven Loop**：对于路径不确定的任务，让 Agent 根据观察结果动态选择下一步。
4. **单 Agent → 多 Agent**：把不同领域的能力和责任拆开。
5. **Agent Runtime → Control Plane**：统一任务、策略、调度、审批、评测和回放。
6. **过程指标 → Outcome 指标**：最终让真实业务结果成为最重要的反馈信号。

## 十一、我认为最值得关注的变化

如果这条路线成立，那么 SaaS 电商平台最深的变化可能不是「多了一个 AI 助手」，而是**软件系统的控制方式发生了变化**。

过去，业务系统主要回答：*「你要执行哪个功能？」*。未来，系统越来越需要回答：*「你想达到什么结果？」*

这意味着 SaaS 的核心抽象可能逐渐从：

```text
Page → API → Workflow → Service
```

转向：

```text
Goal → Agent → Capability → Environment → Outcome → Feedback
```

而这并不意味着 UI、API、Workflow 和微服务消失。它们会成为更底层、更可靠的执行基础设施。真正上移的是**决策和目标管理**。

## 十二、最后：Agent 改造真正改造的是什么

回到这类 SaaS 电商平台，我认为最值得改造的不是某一个业务页面，也不是先做一个「万能电商 Agent」。更合理的顺序是：

- 先把已有业务能力变成 Agent 可理解、可授权、可审计的 Capability；
- 再建立统一的 Tool Gateway，让能力从业务服务中解耦出来；
- 然后建设 Agent Runtime，让 Agent 能够可靠执行；
- 当任务规模上升后，再建设类似 Kubernetes Control Plane 的任务治理层；
- 最后用真实业务 Outcome 建立反馈闭环，让 Agent 的优化目标从「调用成功」转向「问题解决」。

所以我更愿意把这次变化称为：

> **不是给 SaaS 加 Agent，而是让 SaaS 逐渐成为一个 Agent 可以工作的环境。**

当这个环境成熟之后，Agent 不再只是一个孤立的智能应用，而会成为 SaaS 平台上的一种新的计算单元。传统微服务提供能力，Agent 负责决策，Control Plane 负责治理，Feedback Loop 负责让系统不断逼近真实目标。

这可能才是 SaaS 电商平台真正值得思考的 Agent 化方向。

## 十三、技术之外：商业与组织才是真正的变量

前面的路线回答的是「怎么搭」。但还有一个更尖锐的商业问题：LLM 会不会直接把这类 SaaS 取代掉？

我的判断是：不是「取代」，而是「分层重构」。LLM 与 Agent 会重构掉这类平台的上三层——配置后台、策略模板、交互界面；但下两层反而更值钱：支付与交易牌照、微信 / 抖音 / 线下收银的生态合同、沉淀的交易数据与风控对账，以及合规（三级分销、资金清结算）。这些东西，LLM 造不出来。

顺着这个判断，收费模型会从「订阅」滑向「混合 / 效果制」：高频刚需走订阅（锁住成本），低频高价值走按量或 GMV 分成。纯 token 收费在 SMB 场景有一个死穴——账单不可预测，商家最怕这个。

再深一层，Agent 能不能「自治经营店铺」？会来，但会长期停在 L2–L3：小额高频让 Agent 自决，大额、定价、退款政策必须人拍板。天花板不是技术，而是「谁背锅」——算商家的，商家不敢放权；算平台的，平台不敢给无上限自治。而一旦自治真的成立，收费会越过 token，直接跳到按 GMV 抽成、按效果付费——这才是真正动了订阅制的根。

还有一个容易被忽视的风险：千 Agent 同面。当所有 Agent 的信号同源，它们会收敛到同一套最优策略，集体打折压价，商家的利润会被自己的 Agent 卷没。

所以最终胜负手不是模型，是组织。能跑通 Harness → Optimizer → Evaluator 自进化循环的组织，能把这场重构变成产品；组织接不住的，只能守住底层 commodity，眼睁睁看着上层被别人吃掉。

> **这类平台不会被 LLM 取代，但会被迫从「卖工具」重构成「托管经营 + 效果分成」——身价取决于它敢不敢、能不能为 Agent 自治的后果兜底。**
