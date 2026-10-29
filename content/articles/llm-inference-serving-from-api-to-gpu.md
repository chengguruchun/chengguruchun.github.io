---
id: llm-inference-serving-from-api-to-gpu
type: Articles
title: 从 API 请求到 GPU 执行：拆解大模型推理服务架构
date: 2026-10-30
thought_date: 2026-10-30
published_date: 2026-10-30
tags: [LLM, Inference, vLLM, SGLang, GPU, KV Cache, CUDA, Tensor Parallelism, Serving Architecture]
excerpt: 从云端接入、API Gateway、模型路由，到 vLLM/SGLang 的请求队列、连续批处理、KV Cache 管理，再到 Tensor Parallel、CUDA、NCCL 与 GPU 执行，串起一次流式推理请求的完整链路。
history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main/content/articles/llm-inference-serving-from-api-to-gpu.md
last_verified: 2026-10-30
cadence_days: 90
---

# 从 API 请求到 GPU 执行：拆解大模型推理服务架构

理解大模型推理，不能只盯着模型本身。一次 Chat Completions 请求从客户端发出，到最终逐个 Token 返回，中间经过一套分层的在线服务系统：网络接入、API 服务、模型路由、推理运行时、GPU 并行计算，以及反向的流式响应。

本文以一次请求一个模型的流式生成请求为主线，拆开这些层次，并重点解释 vLLM / SGLang、KV Cache、Continuous Batching、Tensor Parallelism 与 CUDA 各自负责什么。

## 一、完整请求链路
```text
Client → DNS / GSLB → Regional LB / WAF → API Gateway
  → Model Router → vLLM / SGLang Runtime
  → Scheduler / Continuous Batching / KV Cache
  → GPU Workers（TP / PP / NCCL / CUDA）
  → SSE Token Stream → Client
```

这是逻辑架构图，不意味着每家云厂商都部署了完全相同的组件。小规模部署可能没有独立的 Model Router；大型平台则可能把接入、模型控制面和 GPU 数据面拆成多个服务。CDN 在动态大模型 API 场景中通常更多承担边缘接入、TLS、WAF、DDoS 防护和网络加速，不应简单理解为像静态网页一样缓存模型生成结果。

## 二、入口层：DNS、负载均衡与 API Gateway

客户端首先通过 DNS 解析服务域名。全球流量调度（GSLB / Global Traffic Management）可以结合地域、网络质量、可用区健康状态和容量，把请求导向某个区域。请求进入区域后，通常还会经过负载均衡器和 API Gateway。

- **Load Balancer**：把连接分发到可用的 API 服务实例，关注健康检查、连接数和负载。
- **API Gateway**：处理身份认证、API Key、租户配额、限流、请求格式校验、审计和用量元数据。
- **流式代理**：对于 SSE 请求，需要正确处理长连接、超时、断连、背压和逐段转发，不能按普通短请求的生命周期处理。

这一层主要管理用户请求和平台访问策略，并不直接负责 GPU 上的 Token 计算。

## 三、Model Router：决定请求去哪个模型服务

API Gateway 验证请求后，平台需要根据请求中的 model 字段找到目标部署。比如 deepseek-v3 映射到某个模型部署；该部署又可能有多个 serving replicas；每个 replica 可能由一组 GPU worker 组成。

这里要区分模型选择和实例选择：前者决定使用哪个模型或版本，后者决定该模型有多个副本时，把请求交给哪个副本或 GPU worker group。

平台可能综合考虑实例健康状态、排队长度、当前运行请求数、GPU 显存压力、吞吐和延迟目标。对于多轮对话，还可能考虑会话亲和性和 Prefix Cache / KV Cache 的局部性：如果某个实例保留着可复用的前缀缓存，把后续请求路由到该实例可能减少重复计算。

但缓存亲和性不是绝对规则。缓存可能已经被驱逐，实例也可能过载或故障；路由器需要在缓存收益与负载均衡之间权衡。同一个用户请求也不天然保证命中同一块 GPU 的缓存，必须由系统显式维护相应的路由和缓存机制。

## 四、推理引擎：vLLM / SGLang 内部做什么

请求进入 vLLM 或 SGLang 后，才进入推理运行时的核心管理范围。可以把它理解成一个面向 GPU 执行的在线任务运行时。典型职责包括：接收和维护待执行请求、管理请求状态和生成进度、决定哪些请求进入当前执行批次、分配和回收 KV Cache，以及调用模型执行代码和 GPU Kernel。

### 4.1 等待队列在哪里？

等待队列通常由推理运行时在 CPU 侧维护，不是 GPU 自己维护用户请求队列。请求进入后，运行时保存请求文本或 Token、采样参数、生成状态、截止长度等元数据。调度器根据当前运行情况选择请求。队列和调度策略属于 vLLM / SGLang 的运行时实现细节；平台外层也可能另有队列，但两者不是同一个队列。

### 4.2 Continuous Batching：动态组成批次

Batch 就是批量处理。传统静态批处理可能要等一批请求凑齐，再一起执行；Continuous Batching（连续批处理）会在请求持续到达、持续完成的过程中动态调整执行批次。

举例：当前 GPU 正在为 A、B、C 三个请求生成 Token。B 已经生成结束，运行时不必等 A 和 C 也结束后才开始下一批；它可以在调度边界移除 B，并让等待中的 D 进入后续执行批次。这样可以减少 GPU 空转，让不同请求更充分地共享 GPU 计算资源，提高整体吞吐量。

吞吐量通常指单位时间完成的请求数或生成 Token 数；它不等于单个请求的响应速度，调度器仍需要在吞吐和延迟之间权衡。

### 4.3 Prefill 与 Decode：为什么调度不简单

- **Prefill**：处理输入 Prompt，把输入 Token 并行送入模型计算，并构建对应的 KV Cache。输入越长，Prefill 计算量通常越大。
- **Decode**：基于已有上下文逐步生成下一个 Token。每一步通常只新增一个或少量 Token，但需要读取已有 KV Cache。

Prefill 往往更偏计算密集；Decode 常常更容易受到显存带宽和 KV Cache 访问的影响。两类工作混在一起时，调度器不仅要考虑请求数量，还要考虑每个请求的输入长度、生成进度、缓存占用和可用 GPU 资源。

## 五、KV Cache：推理过程中的关键显存资源

Transformer 在生成过程中会反复使用历史 Token 的 Key / Value。如果每生成一个 Token 都重新计算完整历史上下文，成本会很高。因此推理引擎会缓存历史 Token 对应的 K/V 张量，这就是 KV Cache。

KV Cache 能避免重复计算，但它本身需要占用 GPU 显存，而且会随着上下文长度和并发请求数量增长。一个粗略的理解方式是：

```text
KV Cache 占用 ≈ 2 × 层数 × Token 数 × KV Heads
              × Head Dimension × 每元素字节数
```

实际计算还要考虑张量并行切分、模型结构、缓存精度、对齐和块管理方式。vLLM 的 PagedAttention 采用类似虚拟内存分页的思路管理 KV Cache：把缓存切成固定大小的 Block，再通过逻辑映射管理物理块，降低连续大块分配带来的碎片和浪费。SGLang 也有 RadixAttention / Radix Cache 等前缀缓存机制，用于复用共享前缀的 KV 状态。

因此，KV Cache 管理不仅是多省一点显存，它直接影响同一张 GPU 能容纳多少并发请求，以及请求能否复用已经计算过的前缀。

## 六、SGLang 与 CUDA：运行时和计算平台不是一回事

- **SGLang / vLLM**：推理运行时，管理请求、调度、批处理、缓存和模型执行流程。
- **CUDA**：NVIDIA GPU 的编程与执行平台，提供运行时、驱动接口和 Kernel 执行能力。
- **GPU**：实际执行矩阵运算、注意力计算等工作的硬件。

推理运行时会通过 PyTorch、Triton、自定义 CUDA Kernel 等软件栈组织计算，最终让 GPU 执行具体操作。因此并不是 SGLang 自己实现了所有底层算子，也不是 CUDA 替 SGLang 决定哪个用户请求先执行。

可以用数据库做一个有限的类比：API Gateway 类似连接入口和访问控制；Model Router 类似服务路由；vLLM / SGLang 类似 Server / 执行调度层；CUDA / Kernel 提供底层计算执行能力；GPU 是计算硬件。

这个类比有边界：SQL 通常有相对明确的执行计划，而 LLM Decode 是逐 Token 持续推进的过程；KV Cache 会动态增长，运行时需要不断重新安排批次和显存资源。

## 七、一个模型如何使用多张 GPU

### 7.1 Tensor Parallelism（TP）

张量并行把模型中的部分权重矩阵或计算维度切分到多张 GPU。以 TP=8 为例，一个模型层的部分计算由 8 张 GPU 分担；它们各自计算局部结果，并在需要时交换或归约结果。

### 7.2 Pipeline Parallelism（PP）

流水线并行把模型的不同层放到不同 GPU 或 GPU 组上。输入依次经过不同阶段，像流水线一样推进。TP 更像同一层的计算切分给多张 GPU；PP 更像不同层分布在不同 GPU 上。

### 7.3 NCCL、NVLink 与 InfiniBand

- **NCCL**：NVIDIA 的多 GPU 集合通信库，提供 All-Reduce、All-Gather、Reduce-Scatter 等通信原语。
- **NVLink / NVSwitch**：主要用于服务器内部 GPU 间高速互联。
- **InfiniBand / RoCE**：用于服务器之间的高速网络通信，配合 RDMA 降低数据搬运开销。

TP=8 并不意味着把模型简单切成八份就结束。模型切分、通信拓扑、算子实现和调度都要协同设计。通信开销过高时，增加 GPU 数量未必能线性提升性能。

## 八、把职责边界记清楚

| 层次 | 核心问题 | 典型组件 |
|---|---|---|
| 全球与区域接入 | 请求进入哪个区域？ | DNS、GSLB、WAF、LB |
| API 服务 | 谁能调用、调用额度多少？ | API Gateway、Auth、Rate Limit |
| 模型服务路由 | 使用哪个模型部署和副本？ | Model Router、Serving Controller |
| 推理运行时 | 哪些请求现在执行、如何复用缓存？ | vLLM、SGLang、Scheduler |
| GPU 分布式执行 | 模型计算如何跨卡协作？ | TP、PP、NCCL |
| 底层计算 | 算子在哪里执行？ | CUDA、GPU Kernel、GPU |

最值得记住的是四个边界：

1. **Model Router 与 Runtime Scheduler 是两层不同的调度**：前者选择模型服务实例，后者决定实例内部哪些请求进入当前执行批次。
2. **Continuous Batching 与 Tensor Parallelism 解决不同问题**：前者让多个请求共享一套 GPU 算力，后者让一个模型的计算跨多张 GPU 协作。
3. **KV Cache 是运行时管理的关键资源**：它影响并发容量、缓存复用和请求调度。
4. **SGLang / vLLM 不等于 CUDA**：推理运行时组织请求和计算，CUDA 软件栈提供底层 GPU 执行能力。

一次请求通常只选择一个模型，然后沿着对应模型部署的执行链路完成生成；平台需要管理的才是多个模型、多个部署副本和多组 GPU 资源。

## 结语

大模型推理服务并不是把模型放到 GPU 上，再暴露一个 HTTP 接口这么简单。它同时是一个在线请求服务系统、一个 GPU 资源调度系统，也是一套围绕 KV Cache 和持续 Token 生成设计的执行运行时。

从系统设计角度看，理解它最有效的方式不是把所有优化都归结为显存优化或多线程，而是先明确每层管理的对象：网络层管理流量，API 层管理调用者，路由层管理模型部署，推理运行时管理请求与缓存，分布式执行层管理 GPU 协作，CUDA 和 GPU 完成底层计算。