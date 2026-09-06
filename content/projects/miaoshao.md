# miaoshao_test：秒杀链路压测与优化

GitHub: https://github.com/chengguruchun/miaoshao_test

## Problem

秒杀把流量尖峰、库存约束与用户体验压进同一条链路。目标不是「绝对公平的完美系统」，而是在可接受的一致性模型下活下来，并让失败可解释。

## Architecture

- **API：** Spring Boot 接入与校验
- **Redis：** 预减库存 / 缓存热点
- **MQ：** RabbitMQ 异步下单
- **DB：** 订单与库存最终落盘

## Design

取舍清晰化：同步链路越短越好；能在 Redis 拒绝的绝不打到 DB；MQ 负责削峰，但也引入重复消费与乱序，必须幂等。售罄语义要在缓存层先闭合。

## Implementation

实现组合常见互联网栈：Spring Boot、Redis、RabbitMQ。重点在压测驱动优化——每次改动对应可观测指标：成功率、超卖次数、P99、队列堆积。

## Demo

按仓库说明启动依赖后压测下单路径。建议场景：库存 100 / 并发 1k+；观察预减与消息消费是否对齐，DLQ 是否可解释。

## GitHub

https://github.com/chengguruchun/miaoshao_test

## Lessons Learned

- 削峰不是消除矛盾，是转移矛盾——要有人负责消化。
- 幂等键是秒杀与 Agent 工具调用的共同基础设施。
- 优化顺序：正确性 → 可拒绝 → 可异步 → 再谈极致吞吐。
