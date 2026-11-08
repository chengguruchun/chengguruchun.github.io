---
id: agent-capability-platform-from-middleware-to-agent-center
type: Articles
title: 从基础服务中台到 Agent 能力中台：让 Agent 成为可声明式构建的能力
date: 2026-11-08
thought_date: 2026-11-08
published_date: 2026-11-08
tags: [Agent, Agent Platform, Agent Runtime, Control Plane, Developer Platform, Kubernetes, PaaS, Tool Registry, Policy]
excerpt: 从传统基础服务中台出发，讨论 Agent 能力平台如何通过声明式 Definition、资源注册、动态装配与 Runtime 治理，让业务团队以配置和组合的方式构建不同类型的 Agent。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/agent-capability-platform-from-middleware-to-agent-center.md
last_verified: 2026-11-08
cadence_days: 90
---

# 从基础服务中台到 Agent 能力中台：让 Agent 成为可声明式构建的能力

我最近重新思考了一个问题：如果传统基础服务中台把 API、消息、认证、计量等公共能力沉淀出来，那么 AI Agent 时代，会不会出现一种新的中台——使用方不必理解 Agent 的内部实现，只需要配置少量参数、注册所需能力，就能创建各种 Agent？

我的判断是：**会，而且它不应该只是一个可视化 Workflow Builder，而应该是一套可声明、可组合、可运行、可治理的 Agent 能力平台。**

它要把模型、工具、Skill、Memory、权限和执行环境等复杂性沉淀到平台侧，让业务团队主要表达目标、能力需求和运行约束。

这篇文章从基础服务中台的经验出发，整理这个方向的架构设想。它是一个设计模型，不代表某个已经完整落地的产品。

## 一、从公共服务中台，到 Agent 能力中台

传统基础服务中台的价值，不只是把几个服务放到一起，而是把多个业务反复需要的能力抽象出来，形成统一的接入、治理和运营体系。

例如：

- API Gateway 统一处理认证、流量治理、路由和审计。
- 消息平台统一处理消息接入、订阅、投递和可靠性。
- 计量计费平台统一记录资源使用、核算用量和结算费用。
- 服务治理平台统一处理注册发现、限流、熔断和可观测性。

但传统中台也有一个常见问题：如果只把公共服务封装成接口，却没有做好领域边界、扩展点和接入体验，最终可能变成一个接口很多、接入很重、业务团队反而绕开的“公共服务集合”。

Agent 中台面临相同的问题，只是抽象对象发生了变化。

传统平台交付的是**可调用的技术服务**；Agent 能力平台要交付的是**可以被声明、组合和运行的智能体能力**。

使用方不应该每次都从头实现 Agent Loop、模型适配、工具调用、上下文拼装、状态管理、沙箱和执行追踪。平台应该提供这些公共能力，并允许业务侧通过配置表达差异。

可以把这种演进理解为：

~~~text
自己部署基础设施
      ↓
使用公共基础服务
      ↓
通过平台配置和组合能力
      ↓
声明 Agent 的目标、能力与约束
      ↓
平台装配并运行 Agent
~~~

这不是消灭开发，而是把重复的基础设施开发转化为平台能力，把真正有业务价值的差异留给业务团队。

## 二、Agent 中台不等于 Agent Builder

一个容易出现的误区，是把 Agent 中台理解成一个拖拽式编排器：选择模型、拖入几个工具、连几条线，最后生成一个 Agent。

可视化 Builder 是一种交互方式，但不是平台的核心。

如果底层仍然要求每个 Agent 自己实现运行循环、上下文管理、工具执行、权限校验和任务恢复，那么 Builder 只是减少了一部分配置工作，并没有真正降低 Agent 工程复杂度。

我更倾向于把平台拆成两个平面，以及一层基础设施：

~~~text
                  使用方 / 开发者
                         |
             Agent Console / Builder / API
                         |
                Agent Definition
                         |
          +--------------+--------------+
          |                             |
    Control Plane                 Runtime Plane
    控制面                         运行面
          |                             |
    Registry / Version             Agent Loop
    Config / Policy                Context Manager
    Model / Tool / Skill           Planner / Tool Executor
    Release / Rollout              Checkpoint / Approval
    Quota / Governance             Run State / Evaluation
          |                             |
          +--------------+--------------+
                         |
                 基础设施能力层
                         |
       LLM Gateway / MCP Gateway / CLI Hub
       Memory / Sandbox / Event / Observability
                         |
               Existing Business Services
~~~

**Control Plane 负责定义和管理 Agent；Runtime Plane 负责真正执行 Agent。**

控制面不应该直接承担每一次模型推理和工具调用。它维护期望配置、资源引用、版本和策略，再将一个不可变的运行配置交给 Runtime。

运行面根据配置启动执行实例，管理每次 Run 的状态、步骤、工具调用、Checkpoint 和结果。

底层基础设施继续提供模型访问、工具接入、执行隔离、记忆存储、事件通信和观测能力。

## 三、核心抽象：Agent Definition

如果平台要让使用方通过配置创建 Agent，就必须先回答一个问题：

**用什么结构描述一个 Agent？**

我倾向于设计一个声明式的 Agent Definition。它不是简单的 Prompt 配置，而是描述 Agent 的身份、目标、依赖能力、运行策略和安全约束。

例如，创建一个代码审查 Agent：

~~~yaml
apiVersion: agent.platform/v1
kind: Agent

metadata:
  name: code-review-agent
  version: 1.0.0
  tenant: team-a

spec:
  description: 代码审查 Agent

  model:
    group: coding-model
    temperature: 0.2

  instructions:
    system: |
      你是一个代码审查专家。
      检查代码质量、安全性和潜在 Bug。

  tools:
    - name: git.diff
      version: 1.2.0
    - name: git.read_file
      version: 1.0.0
    - name: ci.run_test
      version: 2.1.0

  skills:
    - java-code-review
    - security-review

  memory:
    profile: project-memory
    scope: project

  runtime:
    profile: sandbox-python
    max_steps: 20
    timeout: 300s
    checkpoint: true

  policy:
    ref: code-review-readonly
    approval:
      required_for:
        - ci.run_test
~~~

这里的重点不是 YAML 语法，而是**声明式资源模型**。

使用方声明“我要什么”，平台负责解析和装配：

1. 校验 Definition 的 Schema 和字段约束。
2. 解析模型、工具、Skill、Memory 和 Runtime Profile 的引用。
3. 检查租户、用户和 Agent 的授权关系。
4. 校验工具版本、参数 Schema 和策略兼容性。
5. 生成可执行的 Runtime 配置快照。
6. 发布 Agent 版本，并允许后续创建执行实例。

实际平台还需要区分敏感信息和普通配置。API Key、数据库凭证等不应该明文写入 Definition，而应引用 Secret 或 Credential ID。

## 四、资源化：把 Agent 依赖的能力变成一等对象

Agent Definition 只是入口。要让它真正可组合，平台还需要一套资源注册和发现机制。

我认为至少需要以下资源：

| 资源 | 职责 | 示例 |
|---|---|---|
| Model | 模型能力与调用配置 | coding-model、reasoning-model |
| Tool | 可执行的原子能力 | git.diff、order.query |
| Skill | 专业知识、指令和操作方法 | Java Review、SQL Tuning |
| Memory Profile | 记忆策略与存储范围 | user-memory、project-memory |
| Runtime Profile | 执行环境与资源约束 | sandbox-python、browser-runtime |
| Policy | 权限、审批和风险规则 | read-only、finance-approval |
| Workflow | 确定性步骤编排 | 发布流程、订单审批 |
| Agent | 目标、依赖和运行约束的组合 | Code Review Agent |

这些资源需要有统一的注册、版本、状态、权限和生命周期管理。

这里有几个概念必须区分清楚：

- **Tool 是动作能力**：它定义输入输出契约，并最终执行一个确定性操作。
- **Skill 是操作知识**：它帮助模型理解某类任务应该如何处理，通常包含指令、流程知识、示例和约束。
- **Workflow 是确定性编排**：路径和步骤大体预先定义，适合业务规则明确的流程。
- **Agent 是目标驱动的执行主体**：它在约束下根据上下文、观察结果和反馈动态选择下一步。

它们可以组合，但不能混成同一种资源。

例如，一个客服 Agent 可以组合订单查询 Tool、退款政策 Skill、用户 Memory Profile、客服权限 Policy 和一个具备 Checkpoint 的 Runtime Profile。

## 五、运行时装配：配置如何变成真正运行的 Agent

当 Agent 被创建并发布后，平台需要把声明转化成一次真实执行。

我设想的运行链路是：

~~~text
POST /agents/{agent_id}/runs
              |
              v
        Agent API / Gateway
              |
              v
        Resolve Definition
              |
       +------+------+
       |             |
   Resolve Model  Resolve Tools
       |             |
   Resolve Skill  Resolve Policy
       |             |
       +------+------+
              |
       Build Runtime Context
              |
       Start Agent Run
              |
      Agent Loop / Planner
              |
       Tool Executor
              |
      Observation / Feedback
              |
       Checkpoint / Evaluate
              |
       Result / Run Trace
~~~

使用方不需要知道平台内部到底使用哪一种 Agent 框架，也不需要自己维护每个工具的协议适配。

例如统一执行接口可以是：

~~~http
POST /api/v1/agents/code-review-agent/runs
Content-Type: application/json
Authorization: Bearer <token>
~~~

~~~json
{
  "input": {
    "repository": "project-a",
    "branch": "feature/login"
  },
  "metadata": {
    "request_id": "req-10001"
  }
}
~~~

平台返回一个执行实例：

~~~json
{
  "run_id": "run-10001",
  "agent_id": "code-review-agent",
  "version": "1.0.0",
  "status": "running"
}
~~~

后续可以通过 Run API 查询状态、获取执行轨迹、等待人工审批或读取最终结果。

需要注意：Agent Definition 和 Agent Run 是两个不同的对象。

- Definition 描述“这个 Agent 应该是什么”。
- Run 描述“这个 Agent 在某次输入下实际做了什么”。

Definition 是可发布、可版本化的资源；Run 是有生命周期的执行实例。一次 Agent 发布可以对应大量独立 Run。

## 六、Runtime 才是平台真正的技术壁垒

配置页面和 YAML 规范并不难，真正困难的是平台能否稳定运行各种 Agent。

我认为 Runtime 至少要具备以下能力。

### 1. 动态能力装配

启动时根据 Definition 加载模型、工具、Skill、Memory 和 Policy。

工具不应该被写死在 Agent 代码中。Runtime 通过 Tool Registry 发现能力，再由 Tool Gateway 或对应执行器完成调用。

同时需要考虑工具版本锁定和 Schema 兼容。不能因为某个 Tool 更新了参数，就让已经发布的 Agent 在没有验证的情况下发生行为变化。

### 2. 状态管理与可恢复执行

每次执行都需要可追踪的状态模型：

~~~text
Agent Run
  ├── Step 1: 分析任务
  ├── Step 2: 生成计划
  ├── Step 3: 调用 Git Tool
  ├── Step 4: 调用 CI Tool
  ├── Step 5: Judge 评估
  └── Step 6: 输出结果
~~~

至少要记录 Run、Step、Tool Call、事件和 Checkpoint。

这让平台能够支持暂停、恢复、重试、超时、取消和人工介入。对外部工具产生副作用的步骤，不能简单地在失败后无条件重放；还要结合幂等键、执行记录和补偿策略。

### 3. 权限与安全治理

“Agent 注册了一个工具”不等于“Agent 可以在任何情况下调用这个工具”。

至少要有三层判断：

- **注册阶段**：这个 Agent 是否被允许引用该工具？
- **运行阶段**：当前租户、用户和任务是否拥有对应能力？
- **执行阶段**：本次具体参数、资源范围和操作风险是否符合策略？

高风险操作需要支持审批门。例如查询订单可以自动执行，退款、删除数据、设备控制或生产发布则可能要求额外授权或人工确认。

工具权限应当遵循最小权限，并结合 Sandbox 限制文件系统、网络、进程和资源访问。

### 4. 可观测性与成本治理

传统 API 平台关注请求、响应、延迟和错误率；Agent 平台还要关注任务级执行过程。

例如：

- 每个 Run 的模型调用次数和 Token 消耗。
- 每个 Step 的耗时、重试次数和状态。
- 每次 Tool Call 的参数摘要、执行结果和权限决策。
- 上下文长度、检索结果和模型路由。
- 任务完成率、人工接管率和真实业务结果。

这样才能把 Agent 的成本、质量和稳定性纳入平台治理。

### 5. 评估与反馈闭环

模型返回成功，不等于 Agent 完成任务。

平台需要区分过程指标和真实结果：

| 过程指标 | 真实结果 |
|---|---|
| 模型调用成功 | 任务目标是否达成 |
| Tool Call 返回 200 | 业务状态是否正确变更 |
| Workflow 执行完成 | 用户是否接受结果 |
| Judge 自评通过 | 是否有外部证据验证 |

Agent 平台应允许为不同 Agent 配置评估器、验收规则和反馈入口。否则只能知道 Agent 跑了多少次，却不知道它到底有没有用。

## 七、Control Plane 与 Runtime Plane 的职责边界

两层不是简单的服务拆分，而是生命周期和职责的拆分。

| 领域 | Control Plane | Runtime Plane |
|---|---|---|
| Agent | 定义、注册、版本、发布 | 加载 Definition、执行 Run |
| Model | 模型目录、路由策略 | 发起推理请求 |
| Tool | 注册、Schema、授权 | 发现、调用、处理结果 |
| Skill | 版本、发布、依赖 | 加载到上下文 |
| Memory | Profile、范围、策略 | 检索、写入、上下文组装 |
| Policy | 策略定义和审批规则 | 每次执行前做决策 |
| Runtime | Runtime Profile、资源配额 | Loop、状态、Checkpoint |
| Evaluation | 评估规范和门禁 | 执行评估、收集证据 |

这里可以借鉴 Kubernetes 的声明式资源和控制面思想，但不能把 Agent 简单等同于 Pod 或 Job。

Kubernetes 管理的是服务和计算资源的期望状态；Agent 平台还要管理目标、工具授权、语义结果、执行轨迹和人工审批。

更重要的是，Agent 的任务结果往往不是一个简单的进程退出码。平台需要用 Outcome 和 Evidence 判断任务是否真正完成。

## 八、产品形态：不同使用方，不同抽象层级

平台不应该要求所有人都理解底层资源。

我会设计三级使用体验：

**Level 1：模板化创建**

普通业务人员从模板市场选择客服、研发、运维、数据分析等 Agent，只填写业务参数、数据源和少量权限配置。

**Level 2：组件化组合**

开发团队自主选择模型、Tool、Skill、Memory、Policy 和 Runtime Profile，形成自己的 Agent Definition。

**Level 3：自定义 Runtime**

高级开发者可以接入自定义 Agent Loop、框架、执行器、Hook 或专用沙箱，同时仍然使用平台提供的模型网关、工具治理、权限、计量和观测能力。

这三级体验共享同一套资源模型和运行基础设施，而不是做三套彼此割裂的产品。

模板本身也不应该只是一个 Prompt。一个可复用的 Agent Template 应当包含经过验证的 Definition、依赖资源、权限默认值、评估用例和发布说明。

## 九、平台建设的演进路线

我不建议一开始就建设一个大而全的可视化 Agent Builder。更合理的是先把资源模型和 Runtime 做扎实。

| 阶段 | 建设重点 | 可交付结果 |
|---|---|---|
| V0.1 | Agent Definition、Registry、单 Agent Runtime | 能够通过配置创建和运行 Agent |
| V0.2 | Tool / Skill Registry、动态装配 | 能够复用和组合能力 |
| V0.3 | Policy、Sandbox、Checkpoint、Approval | 能够安全、可靠地运行 |
| V0.4 | Trace、Evaluation、Usage Metering | 能够度量质量、成本和效果 |
| V0.5 | Template、Marketplace、Multi-Agent | 能够规模化复用和协作 |

第一阶段最重要的不是支持多少种 Agent 框架，而是打通一条完整链路：

~~~text
定义 Agent
   ↓
注册并校验
   ↓
解析资源依赖
   ↓
生成 Runtime 配置
   ↓
启动 Run
   ↓
执行 Tool
   ↓
记录状态与结果
~~~

这条链路跑通以后，再逐步增加复杂能力。

## 十、几个需要提前想清楚的架构边界

### 1. 不要把所有业务逻辑搬到平台

平台应该提供通用运行能力和治理能力，业务团队仍然拥有领域知识、业务规则和业务服务。

例如订单退款 Agent 可以调用订单服务和退款服务，但订单状态机、退款规则和资金一致性仍然应该由对应业务域负责。

**平台管理能力的使用方式，业务域管理能力本身的正确性。**

### 2. 不要把 Workflow 和 Agent 对立起来

确定性流程仍然适合 Workflow。Agent 更适合处理目标不明确、需要动态判断和反馈调整的部分。

一个真实业务系统完全可以是：

~~~text
Workflow
  ├── 确定性校验
  ├── Agent 动态分析
  ├── 人工审批
  └── 确定性执行
~~~

Agent 中台应该同时支持 Workflow 与 Agent，而不是强制把所有流程 Agent 化。

### 3. 不要让配置自由度超过治理能力

配置越灵活，组合空间越大，兼容性和安全问题也越复杂。

所以需要 Schema 校验、资源版本锁定、依赖检查、策略校验、发布审批、灰度和回滚。默认配置应当安全，复杂配置逐步向高级用户开放。

### 4. 不要让 Runtime 被单一框架绑定

平台可以先支持一种主流 Runtime，但资源模型和平台协议不应该与某个框架的内部对象深度耦合。

不同团队可能使用不同语言和 Agent 框架。平台应通过统一的 Definition、Tool 协议、事件模型和执行接口，保留多 Runtime Adapter 的扩展空间。

## 十一、从基础服务中台到 Agent 中台：能力如何迁移

如果把传统基础服务中台的经验映射到 Agent 平台，会看到很多熟悉的基础设施问题：

| 传统基础服务中台 | Agent 能力平台 |
|---|---|
| API Gateway | LLM Gateway / Agent API |
| 服务注册发现 | Agent / Tool / Skill Registry |
| 消息网关 | Agent Event Gateway |
| API 权限 | Tool Permission / Agent Policy |
| 服务执行容器 | Agent Runtime / Sandbox |
| 配置中心 | Agent Definition / Config |
| 服务版本管理 | Agent Definition Version |
| 调用链追踪 | Agent Run Trace |
| 计量计费 | Token / Tool Usage Metering |
| 服务治理 | Run Governance / Evaluation |

这不是说两者完全相同。传统服务调用的输入和执行路径通常更确定，而 Agent 运行中包含模型决策、动态工具选择和多轮反馈。

因此 Agent 平台不仅要继承 API、消息、租户、权限、计量和可观测性等基础设施能力，还要增加任务状态、上下文、Checkpoint、语义评估和人工审批。

我过去在基础服务中台接触到的 API Gateway、消息网关、计量计费等经验，可以迁移到 Agent 平台的基础设施层；而 Agent Definition、动态装配和 Runtime 治理，是需要进一步建立的新抽象。

## 结语：从提供公共服务，到交付可组合的智能体能力

我现在更倾向于这样定义 Agent 中台：

> **Agent 能力中台是一套以声明式 Agent Definition 为入口，以 Registry 为资源目录，以 Runtime 为执行核心，以 Policy、Evaluation 和 Observability 为治理手段的可组合智能体平台。**

它的目标不是替每个业务团队写 Agent，而是让业务团队不必重复建设 Agent 的底层运行基础设施。

使用方只描述目标、选择能力、配置约束；平台负责资源解析、动态装配、执行治理和结果追踪。

如果把传统基础服务中台看作 Infrastructure as a Service，那么 Agent 能力中台可以进一步走向 Agent as a Service。

但我认为真正值得关注的，不是“零代码创建 Agent”这个表面体验，而是平台是否建立了一套稳定的资源模型和运行时契约。

**Agent Definition 描述期望，Registry 管理能力，Runtime 负责执行，Policy 约束行为，Evaluation 验证结果。**

这五个部分，可能构成 Agent 能力中台最重要的骨架。
