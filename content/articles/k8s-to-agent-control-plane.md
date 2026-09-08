---
id: k8s-to-agent-control-plane
type: Articles
title: Kubernetes × Agent：从容器编排到目标收敛
date: 2026-09-06
thought_date: 2026-08-28
published_date: 2026-09-06
tags: [Agent, Kubernetes, Control Plane, Runtime, Loop Engineering]
stage: published
origin: joint
contribution: extension
thought_id: thought-k8s-agent-control-plane
excerpt: K8s 管服务如何稳定运行；Agent Control Plane 管智能任务如何被分解、执行、验证并完成。核心是 Desired State 与 Actual Outcome 的持续拟合。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/k8s-to-agent-control-plane.md
---

# Kubernetes × Agent：从容器编排到目标收敛

把 Agent 想成可调度单元，直觉来自同一类工程压力：生命周期、配额、失败重试、策略边界、可观测性。Kubernetes 已经把「声明期望 → 持续收敛」做成了基础设施常识。于是人们自然把 Pod、Job、Controller 的语言借过来，试图给智能任务同样的治理感。

共享的是 **reconcile 心智**：系统不断比较期望与现实，并采取行动缩小差距。失效的是把「健康检查通过」误当成「任务语义完成」。容器重启可以抹掉进程态；工具调用一旦对外部世界产生不可逆副作用，重启本身并不是修复。类比是操作脚手架，不是身份等同。

> K8s 管理的是「服务如何稳定运行」；Agent Control Plane 管理的是「智能任务如何被分解、执行、验证并最终完成」。

这两句话可以并排放着读。一边管的是可用性、副本、滚动发布；另一边管的是目标分解、工具轨迹、证据化完成。基础设施层仍然可以是 K8s；任务语义层需要另一套对象与闭环。

```text
┌─────────────────────┐   ┌──────────────────────────┐
│ Kubernetes          │   │ Agent Control Plane      │
│ Pod/Job/Net/GPU     │   │ Task/Policy/Approval     │
│ Secret/NS/HPA       │   │ Eval/Replay/Outcome      │
│ 服务如何稳定运行     │   │ 任务如何验证并完成         │
└─────────────────────┘   └──────────────────────────┘
```

并非每个 Agent 都需要完整 Control Plane。脚本式单次调用、人工紧盯的探索任务，常常用更轻的 runtime 就够。Control Plane 在任务可复用、要多人协作、要审批、要评测与回放、要跨会话收敛时才真正划算。

## 核心：目标与过程不断拟合

整篇的中心不是对象清单，而是一条拟合链：

```text
Desired State → Actual → Gap → Reconcile ↻
                │
                └─ 对应 Loop Engineering：
                   Goal → Action → Observation → Gap → Adjustment ↻
```

映射到 [Loop Engineering](../diverse/llm-scientific-experiment.md) 的运行时闭环。

K8s 的 Desired State 通常是可检查的：副本数、就绪探针、配置版本。Agent 的 Desired State 往往是语义目标：「把账单对平」「生成可合并的修复」「在预算内完成调研」。Actual 因此不能只停在进程绿、步骤绿；它必须携带可核对的 Outcome 证据。Gap 不是耻辱，而是下一轮调度与策略调整的输入。

把「过程跑完」当成「目标达成」，会系统性地奖励看起来像完成的轨迹——这与 Diverse Lab 里 **Proxy Metric ≠ Real Outcome** 是同一条警告。

## 选择性对象映射（脚手架，不是身份）

| K8s 侧直觉 | Agent Control Plane 侧 | 共享什么 | 何处断裂 |
|---|---|---|---|
| Pod | Runtime / Session | 生命周期、资源边界 | Agent 会话携带目标与记忆，不是纯容器进程 |
| Job | AgentTask | 有始有终的工作单元 | 成功判定是语义 Outcome，不是 exit code |
| Scheduler | Task / Runtime Scheduler | 排队、配额、亲和 | 还要考虑工具能力、审批门、评测成本 |
| ConfigMap | Policy / Prompt Pack | 可变配置 | Policy 约束的是行为与权限，不只是环境变量 |
| Secret | Credential / Tool Token | 敏感材料 | 常与工具网关、最小权限、审计绑定 |
| Namespace / RBAC | Tenant / Capability Scope | 隔离与授权 | 还要覆盖工具面与数据面 |
| Admission | Approval Gate | 变更前闸门 | 高风险工具调用需要人工或策略审批 |
| Controller | Task Controller | 持续 reconcile | 拉取的是 Outcome / Eval，而不只是 Ready |
| Trace / Event | Trace / Replay | 事后可叙述 | 需要可回放轨迹与证据包 |
| Rollout | Policy / Prompt Rollout | 渐进发布 | 发布对象是策略与评测门，而不只是镜像 |

这些映射的价值是让分布式系统工程师快速进入问题；危险是把「重启 Pod」的肌肉记忆搬到「重跑带副作用的工具链」上。对不可逆外部效应，正确动作往往是补偿、审批升级或停机，而不是盲目 reconcile 再试一次。

## Agent Control Plane 的一等对象

最小有用集合可以写成：

- **AgentTask**：目标、约束、预算、成功判定
- **Runtime**：执行会话、上下文、工具绑定
- **Policy**：允许/拒绝、速率、审批门槛
- **ToolCapability**：可调用能力与契约
- **Approval**：高风险动作的显式门
- **EvalRun**：对照评测与门禁
- **Replay**：轨迹回放与复盘
- **Outcome**：带证据的完成声明

控制器的工作是把 `status` 拉向 `spec`——但这里的「拉近」必须以 Outcome 为准。示意：

```yaml
apiVersion: agent.lab/v1
kind: AgentTask
metadata:
  name: reconcile-invoice-gap
spec:
  goal: "对平 Q3 发票与收款差额，输出可审计说明"
  successCriteria:
    - type: evidence
      require: ["diff_report", "source_refs"]
  budget:
    maxSteps: 40
    maxCostUSD: 8
  policyRef: finance-tools-strict
  runtimeClass: tool-augmented
status:
  phase: Running
  steps: 12
  lastObservation: "3 笔差额候选待核验"
  outcome:
    complete: false
    evidenceRefs: []
  conditions:
    - type: ProxyChecksPassed
      status: "True"
    - type: RealOutcomeVerified
      status: "False"
```

`ProxyChecksPassed=True` 而 `RealOutcomeVerified=False`，正是 Control Plane 必须显式表达的状态：过程健康 ≠ 语义完成。完成需要证据，不是只需要过程绿灯。

## 本质差异：可检查健康 vs 语义结果

K8s 擅长把世界压成可探针的信号：存活、就绪、资源压力。Agent 系统的关键失败常常发生在探针全绿之后——答案格式正确、工具调用成功、自评很高，但任务并未在真实世界上完成。

因此：

- **Health / Proxy**：步骤执行、schema 校验、单元断言、模型自评
- **Real Outcome**：外部可核对事实、业务状态变更、held-out 评测、人类验收

Proxy 可用，但必须登记 gap。否则优化器会学会 Reward Hacking：把轨迹修得像成功。这与 [用科学实验的方式使用大模型](../diverse/llm-scientific-experiment.md) 中的评测纪律一致；也与 [物理学 × 生态学](../diverse/physics-ecology-llm.md) 中「条件提高概率，而不是一次性保证结果」的复杂系统直觉一致。

## 分层：谁拥有什么职责

```text
┌─────────────────────────────────────────────┐
│ Agent Control Plane                         │
│ Task · Scheduler · Registry · Policy · Eval │
└──────────────────────┬──────────────────────┘
                       ↓
┌─────────────────────────────────────────────┐
│ Agent Runtime / Orchestrator                │
│ Plan-Act-Observe · 状态 · 子 Agent 协调      │
└──────────────┬───────────────┬──────────────┘
               ↓               ↓
┌──────────────────────┐ ┌────────────────────┐
│ Provider Gateway     │ │ Tool Gateway       │
│ 模型路由/预算/限流    │ │ 鉴权/审批/审计/沙箱 │
└──────────┬───────────┘ └─────────┬──────────┘
           └───────────┬───────────┘
                       ↓
              Models · Biz Systems
                       ↓
         Evaluator · Trace · Replay · Feedback
```

角色分工：

- **Policy Optimizer**：在约束下选择路径与策略（何时检索、调用、停止、升级审批）
- **Runtime**：执行选定动作，维护会话态
- **Gateway**：强制工具契约、鉴权、配额与审计
- **Sandbox**：隔离副作用面
- **Evaluator**：判断 Proxy 与（尽可能）Real Outcome
- **Controller**：根据 Gap 重调度、重试策略或停机

K8s 可以继续承载 Runtime / Sandbox 的进程与网络；Agent Control Plane 拥有任务语义、策略门与完成判定。Agent 并不替代微服务：既有服务应通过 Tool Gateway 被调用，而不是被「再实现一遍成 Agent」。

## 三条环：Execute / Eval / Learn

```text
Execute (秒–分钟)   Eval (小时–天)        Learn (天–周)
Goal→Act→Obs→Gap    Trajectory→Gate       Evidence→Policy
把当前任务做完       哪条路径更好           下次自动选更好路径
```

1. **Execute Loop**：Goal → Action → Observation → Gap → Adjustment（在线收敛）
2. **Eval Loop**：轨迹与 Outcome → 评测门禁 → 通过/阻断发布（对照与防回归）
3. **Learn Loop**：失败模式与成功证据 → 策略/提示/路由更新 → 小流量验证（离线或准在线改进）

三条环转速不同。把 Learn 偷塞进每一次 Execute，容易过拟合当前任务；把 Eval 省掉，Execute 会在虚假成功上空转。

## 落地判断

```text
K8s（基础设施）
   ↓
Agent Control Plane（任务语义）
   ↓
Agent Runtime（执行闭环）
   ↓
确定性微服务 ←Tool Gateway→ 概率性 Agent 服务
```

- **K8s 保管基础设施**：节点、网络、配额、容器生命周期
- **Agent Control Plane 保管任务语义**：目标、分解、审批、证据化完成
- **微服务仍是能力提供者**：经 Tool Gateway 接入，保留清晰契约
- **类比用于沟通，证据用于完成**：重启不是万能药；不可逆工具效应需要补偿与门禁

本文先把「为何需要另一套控制面」与「拟合什么」立住。

> 容器编排回答「如何让服务按期望运行」；Agent 控制面回答「如何让智能任务按期望收敛到可验证的完成」。二者叠合，而不是互相取代。

## 开放问题

- 哪些 Outcome 可以机器核对，哪些必须保留人类验收，才能避免 Proxy 垄断成功定义？
- 对不可逆工具效应，默认的补偿、熔断与审批升级协议应写成怎样的一等对象？
- Eval Loop 与 Execute Loop 如何隔离，才能降低执行器与评测器合谋？
- 多租户下，ToolCapability 与数据面权限如何像 RBAC 一样可审计，却不把每次调用都拖成工单？
- 何时该上完整 Agent Control Plane，何时一条强约束的 Runtime 会话就足够？
