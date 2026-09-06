# Agent Runtime 与 Kubernetes：相似的外壳，不同的内核

- tags: Agent, Kubernetes, Runtime, 系统抽象
- date: 2026-08-28

## 问题

团队容易直接套用 K8s 心智：把 Agent 当 Pod，把工具当 Sidecar。外壳相似，内核不同。

## 观点

| 维度 | Kubernetes | Agent Runtime |
|---|---|---|
| 调度对象 | 容器副本 | 目标驱动的执行会话 |
| 成功标准 | Ready / 健康检查 | 任务完成度 / 约束满足 |
| 状态 | 大多无状态或外置 | 记忆、轨迹、工具副作用 |
| 失败 | 重启、重调度 | 重试、改写计划、人工接管 |

有用的迁移：声明式期望、控制器循环、可观测标准。危险的迁移：假设执行可幂等、假设输出可字节级复现。

## 开放问题

「Desired State」对开放世界任务是否仍然成立？还是该换成「Desired Policy」？
