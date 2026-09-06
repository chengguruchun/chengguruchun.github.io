# concurrency：高并发实验台

GitHub: https://github.com/chengguruchun/concurrency

## Problem

并发 bug 很难靠「感觉」学会。需要一个能反复跑、能对照不同策略、能量化等待与吞吐的实验台：在可控压力下观察数据竞争、活锁、伪共享与队列堆积。

## Architecture

- **Workload：** 可配置生产者/消费者与共享状态
- **Sync Layer：** 内置锁 / 显式锁 / 无锁路径对照
- **Metrics：** 吞吐、延迟分布、错误与重试
- **Harness：** 可重复种子与场景脚本

## Design

设计原则：**对照优于堆砌**。同一业务语义用多种同步策略实现；默认暴露失败，而不是只展示 happy path。背压必须可见——否则高吞吐只是把崩溃推迟到下游。

## Implementation

以 Java 并发工具为主（线程池、队列、锁与原子类），配合场景化测试。重点不在框架炫技，而在把「正确性条件」写清楚：不变量是什么、哪些操作需要原子、哪些可以最终一致。

## Demo

本地运行仓库中的示例与压测入口，对比不同实现在相同负载下的吞吐与错误率。建议记录：线程数拐点、队列长度与尾延迟的关系。

## GitHub

https://github.com/chengguruchun/concurrency

## Lessons Learned

- 没有不变量的并发优化是表演。
- 背压是特性，不是耻辱；它保护的是系统整体。
- 这些直觉可迁移到 Agent Tool Gateway：限流、排队、拒绝策略同一套。
