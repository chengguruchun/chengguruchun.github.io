---
id: ai-native-software-language-aosl
type: Diverse Lab
title: AOSL：面向 AI-native 软件工程的语言与构建系统
date: 2026-10-09
thought_date: 2026-10-09
published_date: 2026-10-09
tags: [AI-Native, Software Language, DSL, Compiler, Semantic IR, Agent Runtime, Full-Stack]
excerpt: 从“教 AI 写传统代码”进一步走向“为 AI 重新设计软件描述方式”：提出 AOSL 的结构化 DSL、统一语义 IR、编译与 Runtime 混合执行、全栈生成、验证闭环与可验证原型方案。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/diverse/ai-native-software-language-aosl.md
last_verified: 2026-10-09
cadence_days: 90
---

# AOSL：面向 AI-native 软件工程的语言与构建系统

## 从教 AI 使用传统语言，到为 AI 重新设计软件语言

最近讨论 AI 辅助全栈开发时，我想到一个更进一步的问题：如果现有软件工程的语言体系并不是为 AI 设计的，我们是否可以建立一种新的、AI-native 的软件描述语言？

今天我们教 AI 理解 HTML、CSS、React、Java、API、npm、构建流水线和部署流程，本质上是在教 AI 适应人类为软件工程逐步形成的语言体系。AI 已经能生成大量代码，但生成代码不等于以较低成本、高可靠性地完成整个软件工程。

一个业务需求往往被分散到许多不同文件和抽象层：前端组件、样式、状态管理、API 契约、后端服务、数据库模型、权限规则、测试和部署配置。它们表达的其实是同一份业务意图，却需要 AI 在多个语言之间反复翻译，并自行维持一致性。

因此，我想探索的不是“再发明一种语法，让 AI 用它写代码”，而是：

> **让软件首先以 AI 能够稳定理解、修改、分析和验证的语义结构来描述，再由工具链将这些语义编译或执行为真正的软件。**

我暂时把这个方向称为 **AOSL（AI-native Oriented Software Language）**。这是一个工作名称，而不是现有行业标准。

核心假设是：AI-native 软件语言应该优先表达业务意图、系统约束、组件关系、执行行为和验证条件，再把这些信息映射到传统的软件实现。

## 一、AOSL 不只是一门 DSL，而是一套软件构建系统

我选择的设计方向是：

- **语言表达：结构化 DSL。** 自然语言可以作为入口，但不能成为系统唯一的事实来源。
- **执行方式：编译与 Runtime 混合。** 稳定、可确定的部分优先编译生成；动态决策、长周期任务和外部工具交互由 Runtime 执行。
- **第一阶段范围：全栈业务。** 不只生成 UI，还要让 UI、API、后端逻辑、权限和测试共享同一套业务语义。

整体可以拆成五个层次：

```text
用户需求 / AI 生成的结构化 DSL
              │
              ▼
       Semantic IR（语义中间表示）
              │
       ┌──────┴────────┐
       ▼               ▼
    Compiler       Agent Runtime
       │               │
       ▼               ▼
 React / Java      Workflow / Tools
 API / SQL        Checkpoint / Policy
       └──────┬────────┘
              ▼
       Verification & Feedback
              │
              └── 诊断 → 修改 → 重新验证
```

### 1. DSL：业务描述层

DSL 是人类和 AI 都可以读写的源文件，描述 Entity、View、Action、Policy、Workflow、Event、Constraint 和 Test 等业务原语。

### 2. Semantic IR：统一语义基准

IR 不应该只是 DSL 的 JSON 副本，而应是解析、引用解析、类型检查和语义分析之后的规范化模型。代码生成器、静态分析器、依赖图和验证器都应该使用同一份 IR，不能各自重新猜测 DSL 的含义。

### 3. Compiler：把稳定语义变成软件

Compiler 负责生成前端组件、API 契约、后端骨架、数据 Schema、迁移脚本和测试。它应当是确定性的：相同的 IR、相同的编译器版本和相同配置，应产生可解释、可复现的结果。

### 4. Agent Runtime：执行动态任务

Runtime 负责多步骤工作流、外部工具调用、超时、重试、Checkpoint、恢复、风险门控和人工审批。它不应该接管所有业务代码，只承接那些需要动态决策或持久化执行状态的部分。

### 5. Verification：以证据闭环，而不是以模型自评闭环

生成结果需要经过编译、测试、契约检查、安全检查和必要的端到端验证。验证失败时，系统向 AI 返回结构化诊断；AI 可以提出修改，但修改必须重新经过确定性工具验证。

## 二、先定义业务原语，而不是模仿 React 或 Java

第一版我建议只定义八类核心原语。

| 原语 | 语义职责 | 典型产物 |
|---|---|---|
| `Entity` | 业务实体、字段、类型、不变量 | 数据模型、Schema |
| `View` | 页面结构、组件、数据绑定 | React 页面 |
| `Action` | 用户或系统可触发的业务操作 | API、命令处理器 |
| `Policy` | 权限、租户隔离、操作限制 | 授权检查、策略执行 |
| `Workflow` | 多步骤、分支、重试、审批 | Runtime 执行定义 |
| `Event` | 已发生的业务事实 | 事件类型、发布订阅契约 |
| `Constraint` | 系统必须满足的条件 | 静态检查、断言、测试 |
| `Test` | 业务验收和验证条件 | 测试用例、验证任务 |

这些原语不是互不相干的配置文件，而是构成一张语义关系图：

- View 引用 Entity，描述数据如何展示。
- View 中的操作引用 Action，而不是根据按钮文字猜测后端行为。
- Action 声明输入、输出、授权要求、状态变化和副作用。
- Policy 被 Action 和数据访问规则引用。
- Workflow 组合多个 Action，并描述失败与恢复。
- Event 描述已经发生的事实，供其他业务流程订阅。
- Constraint 约束以上各层。
- Test 为关键业务行为提供可执行的验收条件。

**不要让 AI 在 View 中自行推断后端行为，也不要让后端生成器根据按钮名称猜业务逻辑。跨层行为必须通过明确的语义引用连接。**

## 三、用一个全栈业务检验语言：多租户设备管理

第一版不应该只用 Todo 应用证明概念，而应选择一个包含页面、数据模型、权限和业务操作的真实业务切片。多租户设备管理是合适的起点。

下面是一个概念性的 AOSL v0.1 草案，并非已经定稿的标准语法：

```yaml
language: aosl/v0.1
module: device-management

entities:
  Device:
    identity: [tenant_id, id]
    fields:
      id: string
      tenant_id: TenantId
      name: string
      status:
        type: enum
        values: [online, offline, disabled]
    invariants:
      - tenant_id is required
      - name.length > 0

policies:
  device_operator:
    allow:
      - action: Device.disable
        when: >
          principal.tenant_id == resource.tenant_id
          && principal.role in ["admin", "operator"]

actions:
  Device.disable:
    input:
      device_id: DeviceId
    target: Device
    authorize: device_operator
    preconditions:
      - "target.status != 'disabled'"
    effects:
      - set: "target.status"
        value: disabled
    result:
      type: Device
    errors:
      - NOT_FOUND
      - FORBIDDEN
      - INVALID_STATE

views:
  DeviceList:
    route: /devices
    data: Device.list
    layout:
      type: table
      columns: [name, status]
    actions:
      - action: Device.disable
        label: 停用
        confirm: true
        visible_when: "row.status != 'disabled'"

tests:
  - id: reject_cross_tenant_access
    given:
      principal_tenant: tenant_a
      device_tenant: tenant_b
    when:
      action: Device.disable
    then:
      error: FORBIDDEN
      state_unchanged: true
```

这个示例把业务事实、UI 呈现、权限规则和验收要求放在同一模块里，但不把所有实现细节混成一个东西。

例如，`visible_when` 只决定按钮是否展示，绝不能成为授权边界。后端执行 Action 时，仍然必须独立校验身份、租户和权限。`effects` 描述业务语义，也不意味着编译器可以随意生成一段不可靠的数据库更新；它需要类型检查、事务规则和持久化适配器来落实。

### 语法需要区分三种表达

**声明式语义。** 例如 `authorize: device_operator`、`identity: [tenant_id, id]`。它们必须有明确的类型、引用规则和可检查的含义。

**受限表达式。** 例如 `row.status != 'disabled'`。需要独立的表达式语法、类型检查和受控求值，不能直接执行任意 JavaScript。

**外部实现与能力绑定。** 例如调用已有设备服务、数据库适配器或第三方 API。这些能力通过有类型的接口接入，而不是让 DSL 直接执行任意 Shell 命令。

第一版的表达式语言可以只支持布尔运算、比较、字段访问、集合判断和空值检查。任意循环、动态代码执行和复杂算法先通过有明确输入输出契约的实现模块承载，避免 DSL 很快变成另一种难以分析的通用语言。

### 类型系统要表达业务语义

除了 string、integer、enum 等基础类型，还可以逐步引入：

- `EntityRef<Device>`：指向设备的引用。
- `Principal`：当前经过认证的主体。
- `TenantId`：租户标识，不能与普通字符串随意混用。
- `Command<Device>`：请求执行一个业务操作。
- `Result<Device, DomainError>`：显式表示成功或业务失败。
- `Event<DeviceDisabled>`：已经发生的业务事件。

目标不是创造更多复杂类型，而是让 AI 容易混淆的概念变得可区分。例如，Device.disable 的输入可以是 DeviceId，但数据库查询必须使用当前可信身份绑定的 TenantId 限定范围。不能因为 AI 生成了一个看起来正确的查询，就认为租户隔离自然成立。

## 四、前端和后端统一的是业务语义，不是运行时

前端和后端的执行环境、故障模型和安全边界不同，因此我不建议强行把它们合并成同一套运行时。

但从业务角度看，它们经常只是同一个行为的不同部分。以“停用设备”为例：

1. **用户意图：** 停用一台设备。
2. **UI 语义：** 显示停用按钮；提交时显示处理中；成功后更新状态；失败时展示原因。
3. **业务语义：** 检查租户与角色权限，校验设备状态，执行停用并持久化结果。
4. **验证语义：** 未授权用户无法操作；重复请求不会产生错误状态；失败时系统能识别真实结果。

传统开发需要把这些要求翻译到不同语言中。AOSL 可以把它们表达为一个统一的 `Device.disable` 操作，再让不同生成器实现各自部分。

因此，我倾向于：**统一业务语义，允许不同执行环境采用不同实现。** 这比只统一 API 或 UI 组件更上一层，因为它统一的是跨层业务行为。

## 五、Compiler：从 DSL 到真正的软件

如果直接把 DSL 转成 React 和 Java，将来更换技术栈时就必须重新解释大量规则。多个生成器还可能对同一条业务规则产生不一致的理解。

所以编译器应该采用明确的流水线：

```text
DSL Source
   ↓
Parse：语法解析，生成 AST
   ↓
Resolve：名称解析，验证符号引用
   ↓
Type Check：类型、参数、返回值和表达式检查
   ↓
Semantic Analysis：权限、租户边界、副作用与依赖分析
   ↓
Build IR：生成规范化的 Semantic IR
   ↓
Plan：计算依赖图、生成顺序和受影响产物
   ↓
Generate：生成前端、API、后端骨架、迁移与测试
   ↓
Verify：编译、测试、契约与安全验证
```

其中最关键的是 **Semantic IR（语义中间表示）**。它应当是经过解析和验证的规范化模型，而不只是源 DSL 的 JSON 副本。

例如，一个 Action 的 IR 可以包含：

```json
{
  "kind": "Action",
  "id": "device-management.Device.disable",
  "input": {
    "device_id": {
      "type": "DeviceId",
      "required": true
    }
  },
  "target": {
    "entity": "Device",
    "identity": ["tenant_id", "id"]
  },
  "authorization": {
    "policy_ref": "device-management.device_operator",
    "enforcement": "server_required"
  },
  "execution": {
    "mode": "transactional",
    "effects": [
      {
        "operation": "set",
        "path": "Device.status",
        "value": "disabled"
      }
    ]
  },
  "errors": ["NOT_FOUND", "FORBIDDEN", "INVALID_STATE"],
  "provenance": {
    "source": "device-management.aosl",
    "symbol": "actions.Device.disable"
  }
}
```

`provenance` 非常值得提前设计。生成代码后，系统应该能回答：

- 这个 Java 方法由哪个业务声明生成？
- 哪个 UI 按钮引用了这个 Action？
- 修改权限规则会影响哪些文件和测试？
- 某次运行对应哪个 DSL 版本和实现版本？

这样，AI 的修改才具备可追踪性，而不只是对代码库进行一连串难以还原的文本编辑。

### 增量生成与代码所有权

不能每次都重新生成并覆盖整个项目。建议为产物明确所有权：

| 产物类别 | 修改策略 |
|---|---|
| 完全生成的 DTO、类型、API 契约 | 重新生成并检查差异 |
| 生成的 UI 组件骨架 | 根据 DSL 增量更新 |
| 用户编写的业务扩展 | 保留，不得静默覆盖 |
| 外部系统适配器 | 通过稳定接口调用 |
| 测试和迁移脚本 | 生成后必须审查和验证 |

如果开发者直接修改生成的 Java 文件，下一次编译器可能覆盖修改。因此需要将生成文件与手写扩展分离，或者通过明确扩展点和合并策略管理变化。

**DSL 可以是受管控的业务事实来源，但不意味着所有源代码都必须由它生成。**

## 六、编译与 Runtime 的分工：按语义和风险，而不是按技术栈

如果全部编译成传统代码，AOSL 会很像模型驱动开发工具；如果全部通过 Runtime 解释执行，又会损失传统软件的类型检查、性能、调试能力和成熟工具链。

因此，分工应考虑业务语义的稳定程度、是否需要动态决策，以及运行时风险。

| 业务能力 | 推荐方式 | 原因 |
|---|---|---|
| UI 布局、静态类型、API 契约 | 编译生成 | 结构稳定，容易检查 |
| 常规 CRUD、数据映射 | 编译生成 | 行为明确，易于测试 |
| 权限策略 | 编译为检查，必要时由策略引擎求值 | 需要强制执行和审计 |
| 多步骤业务流程 | 编译成 Workflow，由 Runtime 执行 | 需要持久化状态、超时与恢复 |
| 动态选工具、多 Agent 协作 | Runtime | 需要根据观察结果决策 |
| 人工审批、延迟数天的任务 | Runtime | 需要等待、Checkpoint 和恢复 |
| 高风险操作 | 受约束的执行模块 + Runtime 治理 | 需要授权、审批、幂等与审计 |

一个关键区别是：**业务逻辑不等于 Agent 决策。**

权限校验、状态约束、幂等处理和数据持久化，应由确定性代码或受约束的执行模块承担。如果设备处于异常状态，需要查询诊断信息、选择恢复工具并在必要时请求人工审批，这部分才适合 Runtime 编排。

LLM 可以参与选择下一步做什么，但不能通过自由生成代码绕过业务约束。Runtime 每次调用工具前都要检查权限和输入；调用后要区分成功、失败、超时和结果未知。外部设备命令超时不代表设备没有执行操作，不能忽略重复副作用而简单重试。

### Workflow 示例

```yaml
workflows:
  DisableDeviceWorkflow:
    input:
      device_id: DeviceId
    steps:
      - id: authorize
        action: Device.authorize_disable
      - id: disable
        action: Device.disable
        after: authorize
        retry:
          max_attempts: 2
          on: [TRANSIENT_ERROR]
        timeout: 30s
      - id: verify
        action: Device.verify_disabled
        after: disable
      - id: audit
        action: Audit.record
        after: verify
    failure:
      on: [FORBIDDEN, INVALID_STATE]
      strategy: fail_fast
    checkpoint:
      after: [authorize, disable, verify]
```

这只是简化示例。真正实现时，需要明确每个步骤的持久化状态、幂等键、补偿动作和恢复策略。如果 disable 已成功，但 verify 超时，恢复时应该从 verify 继续，而不是盲目再次执行 disable。如果外部系统返回结果未知，应先查询真实状态，再决定下一步。

语言描述工作流语义，Runtime 提供可靠的执行机制。这正是长周期 Agent Runtime、Checkpoint、重试和事件驱动机制可以发挥作用的地方。

## 七、AI 参与编译器的哪个环节？

不应该让 LLM 取代编译器。传统编译器擅长确定性任务：解析、类型检查、引用解析和代码生成；LLM 擅长意图理解、发现缺失信息、复杂业务建模，以及基于诊断提出修复。

**AI 负责：**

- 把用户需求转换成 DSL 初稿；
- 发现需求歧义并提出澄清问题；
- 根据编译器诊断提出候选修改；
- 根据测试失败分析可能原因。

**确定性工具负责：**

- 语法和类型检查；
- 符号引用与依赖分析；
- 权限和租户约束检查；
- 代码生成与版本兼容性检查；
- 执行测试、保存结果和审计记录。

**Runtime 负责：**

- 工作流调度与持久化；
- 工具调用和执行状态管理；
- 风险门控与审批；
- 超时、重试、恢复和结果核验。

例如，AI 生成的 DSL 引用了不存在的 `device_operator` 策略。系统应该返回结构化诊断：

```text
E_POLICY_NOT_FOUND
Location: actions.Device.disable.authorize
Reference: device_operator
Available policies: device_reader, device_admin
```

AI 可以提出修复补丁，但编译器必须重新验证。如果修改会扩大权限、改变数据库约束或引入不可逆操作，还应触发额外风险检查或人工审批。

这样才形成可重复、可审计的 AI 开发闭环。

## 八、原型怎么做：先实现一个垂直切片

第一版不要实现通用平台，也不要同时支持多个技术栈。先验证：

> **一份结构化业务定义，能否一致地驱动 UI、API、后端逻辑和测试，并在业务规则变化后准确识别和验证所有受影响部分？**

建议第一版采用以下技术栈：

- **Compiler：TypeScript。** 实现 DSL 解析、类型模型、依赖图和代码生成，减少工具链复杂度。
- **Frontend：React + TypeScript。** 作为第一种 UI 生成目标，业务语义不绑定某个组件库。
- **Backend：Java + Spring Boot。** 验证企业后端集成，生成 DTO、API 契约、业务骨架和测试。
- **Database：PostgreSQL。** 验证实体、主键、租户边界、约束和数据库迁移。

选择 TypeScript 实现 Compiler，并不意味着 AOSL 最终只能支持 TypeScript。它只是原型阶段的工程取舍。后续增加 Java、Go 或其他目标生成器，才有助于证明语义模型真正独立于技术栈。

### 建议的仓库结构

```text
aosl/
├── examples/
│   └── device-management/
│       ├── app.aosl.yaml
│       ├── entities.aosl.yaml
│       ├── actions.aosl.yaml
│       ├── policies.aosl.yaml
│       ├── views.aosl.yaml
│       └── tests.aosl.yaml
├── packages/
│   ├── parser/
│   ├── type-system/
│   ├── semantic-ir/
│   ├── analyzer/
│   ├── compiler/
│   ├── generator-react/
│   ├── generator-java/
│   ├── generator-test/
│   └── runtime/
├── fixtures/
│   ├── valid/
│   ├── invalid/
│   └── expected-errors/
└── tests/
    ├── compiler/
    ├── semantic/
    ├── security/
    └── end-to-end/
```

早期可以把所有模块放在一个 TypeScript Monorepo 中，但不要为了目录完整而提前实现所有模块。先把解析、语义模型、校验、一个生成器和端到端测试跑通。

### 四个实现阶段

**阶段 1：DSL + Parser + Semantic IR**

- 定义 Entity、Action、Policy。
- 实现解析、名称解析和基础类型检查。
- 对不存在的字段、错误引用和非法类型返回稳定诊断码。

验收：合法输入能生成确定的 IR；非法输入被准确拒绝。

**阶段 2：React UI + API + 后端骨架**

- 根据 View 生成设备列表和详情页。
- 根据 Action 生成 API 契约和后端接口骨架。
- 根据 Policy 生成授权接口及对应测试。
- 为手写业务扩展定义稳定接口。

验收：生成的应用可以运行，页面操作真正到达后端，而不只是生成静态界面。

**阶段 3：验证器 + AI 修复**

- 自动执行编译、单元测试和端到端测试。
- 将失败转换为结构化诊断。
- 允许 AI 提交 DSL 补丁，并重新执行验证。
- 保存每次生成、修改和测试的版本记录。

验收：AI 不能仅凭自己宣称成功；必须有实际执行结果支持。

**阶段 4：持久化 Workflow + 风险治理**

- 支持多步骤任务、超时、重试和 Checkpoint。
- 引入工具注册、权限检查和人工审批。
- 明确未知执行结果、幂等键和恢复策略。

验收：进程重启后能够恢复工作流；失败恢复不会盲目重复不可逆操作。

这个顺序很重要。不要在 Compiler 还无法证明一个简单 Action 的类型和权限正确时，就急着实现复杂的多 Agent Runtime。

## 九、如何证明 AOSL 优于直接让 AI 写代码？

不能只用“代码生成成功率”作为指标，否则可能发现 AOSL 多了一层抽象，却没有真正减少开发成本。

建议建立三组对照实验：

- **A 组：** 直接让同一个模型根据需求生成全栈代码。
- **B 组：** 让同一个模型生成 AOSL DSL，再由 Compiler 生成代码。
- **C 组：** AOSL + Compiler + Runtime + 自动验证和修复闭环。

三组使用相同业务需求、相同模型和相同执行环境，记录：

| 指标 | 要验证的问题 |
|---|---|
| 首次通过率 | 一次生成后有多少任务通过编译和验收 |
| 业务正确率 | 功能是否符合预期，而不只是能运行 |
| 安全缺陷数 | 是否出现越权、跨租户访问或状态不一致 |
| 迭代修改成本 | 修改一项业务规则需要变更多少内容 |
| 回归缺陷率 | 修改后是否破坏原有功能 |
| 人工介入次数 | 需要多少次澄清、修复或审批 |
| 生成与验证耗时 | 端到端时间及模型调用成本 |

测试集至少覆盖正常业务、边界条件、权限、错误处理和需求变更。

例如，先生成设备列表，再新增一个只允许管理员执行的“删除设备”操作。观察系统能否同步更新 UI、API、后端授权、审计逻辑和测试，并确保普通用户无法绕过 UI 直接调用接口。

再把设备唯一键从 `id` 改为 `(tenant_id, id)`。编译器应该识别相关查询、数据约束和测试受到影响，而不是只改一处声明就认为完成。

**只有当 AOSL 在跨层一致性、修改成本和可验证性方面体现出可重复的优势，它才真正具有独立存在的价值。**

## 十、三个更深层的问题

### 1. 谁拥有最终的业务事实？

如果 DSL 写着设备状态必须是 disabled，而设备实际上没有响应停用命令，DSL、数据库和真实设备之间发生冲突，谁才是最终事实来源？

语义模型需要区分：

- 期望状态；
- 已持久化的业务状态；
- 外部设备报告的观测状态；
- 尚未确认的执行结果。

对普通 CRUD 应用，这可能不是主要矛盾；对 IoT、长周期 Agent 和外部工具调用，却非常关键。

### 2. 如何避免 DSL 变成另一种复杂编程语言？

如果每个新需求都增加一个特殊字段、一种表达式或一个新的运行时分支，AOSL 最终会变成另一个难以维护的框架。

每个新语法特性都应回答三个问题：

1. 它是否表达了已有语言难以清楚表达的语义？
2. 它能否被类型检查、静态分析或运行时验证？
3. 它是否可以通过明确的扩展接口实现，而不必成为语言内置能力？

如果只是某个生成器需要的模板参数，就不应轻易提升为语言核心语法。

### 3. 如何让 AI 持续修改软件，又不破坏一致性？

这涉及语义依赖图、增量编译、差异生成、版本迁移和回归测试。

我认为 AOSL 最有价值的能力之一，是让 AI 修改的单位从“代码文件”变成“业务语义变更”。

例如，AI 不只是报告修改了三个 Java 文件和两个 React 文件，而是提出一个可审查的业务变更：

```text
Change: Restrict Device.disable to administrators

Affected semantics:
- Policy: device_operator
- Action: Device.disable
- View: DeviceList
- Tests: authorization and tenant isolation

Required verification:
- Type checking
- Authorization tests
- Cross-tenant tests
- End-to-end regression tests
```

编译器根据语义依赖图计算影响范围，AI 提出修改，验证器检查受影响部分，最后形成可追踪的变更集。这比“AI 能写更多代码”更接近软件生产方式的变化。

## 十一、最终判断：AOSL 应该是什么？

我建议把第一版目标收敛为：

> **AOSL v0.1：一种结构化的全栈业务描述语言，以及围绕它建立的语义 IR、代码生成器和自动验证闭环。**

先不追求通用语言，不追求多模型协作，也不追求立即替代现有框架。

先证明一件事：一个业务语义模型可以一致地生成 UI、API、后端骨架和测试，并且可以安全、可追踪地演化。等这个基础成立后，再逐渐加入 Workflow、Runtime、Agent 工具调用、长周期任务和动态执行策略。

我尤其看好它与你之前关注的 Agent Runtime 的结合：

**AOSL 负责描述业务世界；Compiler 负责把稳定语义变成软件；Runtime 负责在真实环境中执行、观察、恢复和验证。**

三者组合起来，才可能形成真正区别于传统代码生成工具的 AI-native 软件工程体系。

这仍然是一个待验证的架构假设，而不是成熟的标准答案。但它值得通过一个小而完整的全栈原型来检验。
