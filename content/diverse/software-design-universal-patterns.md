---
id: software-design-universal-patterns
type: Diverse Lab
title: 软件工程的隐形语法：从“加一层”到“广进严出”
date: 2026-09-23
thought_date: 2026-09-23
published_date: 2026-09-23
tags: [Diverse, Software Design, Architecture, Complex Systems, Design Patterns]
excerpt: 把软件工程里反复出现的设计思想放在一起：间接层、分而治之、粗到精、缓存、批处理、异步、隔离、一致性、反馈与控制，以及它们背后的共同结构。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/diverse/software-design-universal-patterns.md
last_verified: 2026-09-23
cadence_days: 180
---

# 软件工程的隐形语法：从“加一层”到“广进严出”

我最近连续想到两个软件工程里的“万能句式”。一个是：**“没有什么是加一层不能解决的，如果有，就加两层。”**另一个是：**“广进严出。”**前者强调间接层、抽象与解耦，后者强调粗到精、多级过滤与逐级收敛。把它们放在一起看，我越来越觉得，软件工程里大量看似不同的模式，本质上都在做同一件事：**把一个难以直接处理的问题，转换成一组更容易控制的问题。**

所以这不是一份“设计模式大全”。我更想做一张**软件工程底层思想地图**：同一个思想在数据库、操作系统、分布式系统、搜索、编译器、机器学习和 Agent Runtime 中，会以完全不同的名字重新出现。

## 一、第一性原理：软件设计其实是在“改变问题的形状”

面对一个复杂问题，工程师通常不会直接硬解，而会先问：能不能隔离？能不能拆开？能不能先粗筛？能不能把昂贵决策推迟？能不能提前计算？能不能复用？能不能把失败限制在局部？能不能从反馈中继续修正？

```text
原问题
  ↓
抽象 / 拆分 / 隔离 / 过滤 / 延迟 / 复用 / 复制 / 反馈
  ↓
更小、更局部、更可预测的问题
  ↓
组合
  ↓
系统
```

因此，很多架构技巧真正改变的不是业务本身，而是**问题的边界、成本、时序、信息量和失败传播范围**。

## 二、增加间接层：不要让两个东西直接耦合

**Any problem in computer science can be solved by another level of indirection.**

核心不是“多加一层”，而是：**让变化的一方不要直接碰稳定的一方。**

思想典型实现解决什么
抽象Interface / API实现变化适配Adapter / Wrapper接口不兼容代理Proxy访问控制、增强、远程化门面Facade隐藏子系统复杂度网关Gateway统一入口、路由、鉴权Sidecar旁路进程把治理与业务解耦Service Mesh通信层把服务治理下沉防腐层Anti-Corruption Layer隔离外部领域模型

DNS、虚拟内存、文件系统、容器、对象存储，也都可以从这个角度理解：**用一个稳定的逻辑接口承接底层不断变化的现实。**

注：Hyrum's Law 提醒我们，抽象并不等于真正隐藏。**当足够多用户使用一个 API 时，所有可观察行为最终都可能被某些用户依赖。**因此“契约”既是边界，也是长期演化中的事实。

## 三、分而治之：把一个复杂问题拆成多个局部问题

如果“加一层”是在增加边界，那么“分而治之”是在增加边界的数量。

```text
复杂问题
   ↓
┌────┬────┬────┐
 A    B    C    D
└────┴────┴────┘
   ↓
组合结果
```

- 模块、包、函数：拆软件。

- 微服务、领域边界：拆服务与业务。

- 分片、分区：拆数据。

- MapReduce：拆计算。

- Actor：拆并发状态。

- Multi-Agent：拆决策主体。

真正被降低的是**局部复杂度**，而不是代码行数。

## 四、关注点分离：一个东西不要同时承担太多维度

单一职责、AOP、MVC、Hexagonal Architecture、Clean Architecture、Control Plane / Data Plane，都可以看作关注点分离的不同实现。

```text
业务逻辑
  │
  ├── 数据访问
  ├── 权限
  ├── 日志
  ├── 事务
  ├── 网络
  └── 监控
```

其中 Control Plane / Data Plane 特别有意思：**决策与执行往往具有不同的变化速度。**这也是 Kubernetes、Service Mesh 和 Agent Runtime 都容易出现“控制面”的原因。

## 五、广进严出：粗到精、逐级收敛

```text
全量输入 → 粗筛 → 候选集 → 精排 → 验证 → 最终结果
```

搜索的“召回 → 粗排 → 精排 → 重排”、RAG 的“检索 → rerank → generation”、编译器的“词法 → 语法 → 语义 → 优化 → 代码生成”，都在做同一件事：

**让便宜的阶段处理更多，让昂贵的阶段只处理少量候选。**

场景粗到精
搜索/推荐召回 → 粗排 → 精排 → 重排RAG查询理解 → 多路召回 → Rerank → 生成视觉候选区域 → 分类 → 精细定位搜索算法Branch → Bound → Prune安全粗拦截 → 身份 → 权限 → 风险检查

**Bloom Filter 是这个思想非常漂亮的例子：**先用极低成本判断“绝大概率不存在”，允许可控的 False Positive，把少量误判留给后级验证，换取数量级的空间和性能收益。它不是追求每一级都正确，而是追求**整条漏斗的总体成本可控**。

## 六、缓存与预计算：把未来的问题提前解决

缓存的本质不是 Redis，而是：**如果一个结果未来大概率还会被需要，就不要每次重新计算。**

CDN、物化视图、索引、编译产物、KV Cache、Memory，都可以放在这个思想下。它是典型的**空间换时间**。与之相反，懒加载、分页、流式处理则是**时间换空间**：只在真正需要时计算。

## 七、批处理与摊销：不要只复用结果，也要复用一次操作的固定成本

这是我觉得值得单独拿出来的一类，因为它和缓存很像，却不是同一件事。

**Cache 是复用“已经算过的结果”；Batching 是让多个工作单元共同承担一次固定开销。**

例子摊销的成本
数据库批量写入网络往返、事务提交Group Commit日志刷盘Batch API请求调度、连接与协议开销LLM Batch InferenceGPU 调度与计算资源Vectorized Execution逐条解释/函数调用开销连接复用/多路复用连接建立与管理成本

因此可以把它抽象成：

```text
单个任务：固定成本 + 单位成本
多个任务：一次固定成本 + N × 单位成本
```

Batch 的代价也很明显：需要等待攒批，会引入延迟，并可能增加尾延迟。于是它和实时性之间形成了典型的工程权衡。

## 八、异步化：把“现在必须完成”改成“最终完成”

队列、Event Bus、Pub/Sub、Kafka、任务系统，本质是在时间维度上增加一个间接层：生产者不再必须等待消费者。

```text
同步：A ─────→ B ─────→ C
             等待

异步：A → Queue → B → C
```

它把生产与消费解耦，并提供缓冲、削峰、重试、回放等能力。

## 九、背压与限流：系统不能无限接受工作

异步以后马上出现一个问题：Producer 可能比 Consumer 快。于是限流、背压、Admission Control、优先级、采样和丢弃策略出现了。

核心思想是：**不要让系统承诺它无法承担的工作量。**

在 Agent 系统中，它有非常直接的映射：**token budget、rate limit、并发上限、tool quota、context budget** 都是智能执行系统里的背压机制。

## 十、超时、重试、幂等、补偿：失败不是例外，而是正常路径

只讲 Retry 而不讲 Timeout，其实少了一半。没有超时，就没有明确的失败边界；没有幂等，重试就可能制造更多副作用。

机制解决的问题
Timeout限制一次等待的最长时间Deadline限制整个请求链路的总预算TTL限制状态/数据的有效生命周期Lease让临时占有权自动过期Retry + Backoff应对瞬时失败Idempotency让重复执行不产生重复副作用Compensation无法回滚时用业务动作修复

可以把它看成一个失败闭环：

```text
限制等待 → 发现失败 → 重试 → 防止重复副作用 → 无法恢复 → 补偿
```

## 十一、隔离：把故障限制在一个舱室里

线程池隔离、Bulkhead、Sandbox、Container、Tenant Isolation、Circuit Breaker，本质都在控制**故障传播半径**。

优秀的系统不是假设“不会坏”，而是设计成“坏了也不要全部一起坏”。

## 十二、降级与优雅失败：不是所有功能都值得同等保护

Fallback、Graceful Degradation、Read-only Mode、Partial Result、Feature Flag 都是在做优先级管理。

核心问题是：**当资源不足或依赖失败时，系统应该保住什么？**

## 十三、冗余与复制：用更多资源换可用性、吞吐和恢复能力

副本、Replica、主从、多活、备份、纠删码，都可以看作冗余。

但复制马上带来一个问题：**多个副本之间谁说了算？**

于是从 Replication 自然走向一致性协议。

## 十四、一致性与共识：多个观察者如何得到一个共同状态

版本号、乐观锁、向量时钟解决的是不同程度的冲突识别；CRDT 通过数据结构设计降低冲突；而在需要多个节点对某个日志/状态顺序形成一致意见时，就进入共识协议。

**Raft、Paxos** 可以看成“多个副本如何在故障存在时，对一件事情形成可接受的共同决定”的经典答案。

因此“复制”与“一致性”并不是两个孤立知识点，而是一条连续的设计链：**复制 → 冲突 → 顺序 → 共识 → 一致状态。**

## 十五、版本化、事件溯源与 Checkpoint：不要只保存现在，也保存如何到达现在

Version、MVCC、Event Sourcing、Snapshot、Checkpoint、Replay 都在解决类似问题：**状态变化之后，我们还能不能知道它从哪里来、能不能回到过去、能不能继续执行？**

这也是长运行 Agent 必须面对的问题：一个任务运行七天之后，如果中间失败，系统不能只剩一个“当前状态”，而需要能够 Resume、Replay、检查轨迹。

## 十六、声明式：描述“想要什么”，把“怎么做到”交给系统

命令式告诉系统一步一步做什么；声明式描述 Desired State，让控制器不断把 Actual State 拉向目标。

```text
Desired State
      ↓
   Controller
      ↓
Actual State
      ↓
   Observe
      ↺
```

Kubernetes 是经典例子。Agent Runtime 也越来越接近这种模型：用户给 Goal，Runtime 根据环境和反馈决定下一步。

## 十七、控制与反馈：系统不是一次执行，而是一个闭环

控制理论、PID、Reconciliation、Retry Loop、Agent Loop 看起来跨越很大，但共享一个结构：

```text
目标 → 行动 → 观察 → 偏差 → 修正 → 再行动
```

可以把它写成：

```text
Gap = Expected Outcome - Actual Outcome
```

系统真正重要的能力不是“执行一次”，而是**知道结果和目标之间差多少，并知道如何缩小这个 Gap。**

## 十八、可观测性：把系统内部状态变成可以被观察的信息

Logs、Metrics、Tracing、Profiling、Audit Log、Event Stream，本质都是增加系统的“可见性”。

没有观察，就没有可靠反馈；没有反馈，就无法有效控制。

所以 Observability 不只是运维能力，也可以看作**复杂系统的感知层**。

## 十九、契约与类型：把隐含假设变成显式约束

Type System、Schema、API Contract、Protocol、Contract Test 都是在做一件事：**把“双方默认知道”的规则显式化。**

在 Agent 世界，这个思想直接对应：

传统软件Agent
API ContractStructured Output SchemaRPC InterfaceFunction Calling SchemaType ConstraintTool Input / Output SchemaContract TestTool / Workflow Verification

这也是 Agent 从“自然语言协作”走向“工程化协作”的关键一步。

## 二十、最小权限与能力边界：默认不要给系统更多能力

Least Privilege、Capability Security、Sandbox、Permission Boundary 都遵循同一个原则：**一个组件只应该拥有完成任务所必需的能力。**

对于 Agent 尤其重要，因为 Agent 不只是读数据，还可能执行 Tool、访问文件、修改代码、调用外部系统。

## 二十一、组合与插件化：让能力成为可以重新排列的积木

Strategy、Plugin、Middleware、Pipeline、Composition、Dependency Injection 都在追求可组合性。

好的系统不是把所有可能性提前写死，而是提供足够稳定的组合接口，让新的能力能够进入系统。

## 二十二、状态机与生命周期：复杂系统必须知道“现在处于什么阶段”

State Machine、Workflow、Saga、Task Lifecycle、Actor Lifecycle 都在显式描述状态和迁移。

```text
Created → Running → Waiting → Verifying → Succeeded
                    ↓
                  Failed
                    ↓
                 Retrying
```

很多“奇怪 Bug”本质上不是某一行代码错了，而是系统没有明确表达某个状态是否允许某个动作。

## 二十三、批处理与摊销：Batching / Amortization

把这一类单独列出来，是因为它与“缓存”有一个非常重要的区别：

**缓存复用过去的结果；摊销复用一次操作的固定成本。**

除了数据库 Batch、Group Commit、LLM Batch Inference，还有 SIMD、Vectorized Query、批量 RPC、批量消息确认等。它们都在寻找同一个机会：**让 N 个工作单元共享一次固定成本。**

工程上的代价是等待攒批。因此 Batch 通常是在**吞吐与延迟**之间做交换。

## 二十四、随机性与采样：不要把所有不确定性都当成 Bug

负载均衡、随机退避、Sampling、探索-利用、随机化算法，都利用了随机性。

有些系统不是要消灭不确定性，而是要让不确定性**可控、可测量、可约束**。

## 二十五、局部最优与全局约束：复杂系统中的权衡

缓存命中率、局部吞吐、单 Agent 成功率都可能很高，但系统整体未必最好。分布式系统、调度、资源分配和 Multi-Agent 都会遇到这个问题。

因此架构设计经常需要两个层次：**局部策略 + 全局约束**。这也是 Control Plane、Scheduler、Policy Engine 出现的原因之一。

## 二十六、把这些思想映射到 Agent Runtime

当 Agent 进入软件工程，过去几十年的思想并没有消失，而是在换名字。

软件工程思想Agent Runtime 对应物
抽象层Tool / Skill / Provider / Model Adapter
广进严出Intent → Retrieval → Planning → Execution → Verification
缓存Context Cache / KV Cache / Memory / Trajectory
异步Event Bus / Task Queue / Agent Message
背压Token Budget / Rate Limit / Tool Quota / Context Budget
契约Structured Output / Function Calling Schema
隔离Sandbox / Tenant / Permission Boundary
版本化Checkpoint / Resume / Replay / Conversation State
反馈闭环Observe → Evaluate → Optimize
控制面Scheduler / Policy / Model Routing / Risk Control
声明式Goal / Desired State / Agent Specification
多主体Multi-Agent / Actor / Agent Society

这让我越来越倾向于把 Agent Runtime 理解成一种**“面向智能执行实体的操作环境”**：它继承了操作系统、分布式系统、Kubernetes 和工作流系统的大量思想，但执行主体第一次具有了自己的决策能力。

## 二十七、所有“万能思想”都有反模式

万能药它带来的新问题
加一层链路更长、延迟更高、排查更难加缓存一致性、失效、内存成本加 Batch等待时间、尾延迟、批次管理加队列堆积、顺序、重复消费加重试雪崩、重复副作用加副本一致性和运维成本加微服务网络、部署、观测、事务复杂度加抽象认知负担、泄漏抽象加 Agent不确定性、成本、验证难度加反馈控制回路振荡、错误反馈放大

所以真正的问题从来不是“有没有这个模式”，而是：

**这个模式把复杂度从哪里搬到了哪里？它降低了什么成本，又增加了什么成本？**

## 二十八、我现在更喜欢用这些问题检查一个架构

- **边界在哪里？** 谁和谁不应该直接耦合？

- **复杂度在哪里？** 是结构、时间、并发、故障还是决策复杂度？

- **昂贵决策能否后置？** 能不能先粗筛，再精算？

- **固定成本能否摊销？** 能不能 Batch、合并提交或复用连接？

- **结果能否复用？** 能不能缓存、索引、预计算？

- **失败能否局部化？** 一个组件坏了，传播半径多大？

- **状态能否恢复？** 有没有版本、日志、Checkpoint、Replay？

- **系统能否反馈？** 它怎么知道自己做得对不对？

- **约束是否显式？** 输入、输出、权限、资源预算是否被契约化？

- **局部优化是否服从全局目标？** 单点变快是否让整体变慢？

## 二十九、最后：设计模式可能只是表面，复杂度管理才是底层

Design Pattern 给了我们很多名字：Adapter、Facade、Proxy、Strategy、Observer、Chain of Responsibility、Circuit Breaker、Saga……

但如果只记名字，很容易变成“看到问题就套模式”。如果往下抽象一层，会看到更少、更稳定的东西：

```text
软件设计
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
         边界          时间          信息
          │            │            │
      隔离 / 抽象    延迟 / 异步    过滤 / 聚合
      拆分 / 代理    缓存 / Batch   索引 / 压缩
          │            │            │
          └────────────┼────────────┘
                       ↓
                    复杂度管理
                       ↓
                    反馈与控制
                       ↺
```

也许这才是软件工程更底层的“隐形语法”：**我们不是在不断增加技术，而是在不断寻找更合适的边界、时间尺度、信息过滤方式、资源分配方式和反馈机制。**

“加一层”与“广进严出”只是其中两个非常漂亮的缩写。

而当 Agent 开始进入软件系统之后，这张地图还会继续扩张：过去我们主要设计“程序如何执行”，现在开始设计“一个会决策的系统如何在不确定环境里持续执行、验证、修正和演化”。

**好的架构，不是堆积更多组件，而是不断把问题变成更容易控制的问题。**
