# RedPacket：抢红包的并发解剖

GitHub: https://github.com/chengguruchun/RedPacket

## Problem

抢红包是经典热点：瞬时高并发写同一资金池，还要尽量公平、防超发、可审计。表面是「随机金额」，内核是**高竞争下的一致性与体验折中**。

## Architecture

- **Edge：** 接入与限流，保护核心账户
- **Ledger：** 红包池与扣减真相源
- **Cache：** Redis 加速与原子操作
- **Async：** 账单落库与对账

## Design

关键设计点：扣减必须原子；超发不可接受；随机策略要在「剩余次数/剩余金额」约束下可证明不穿透。对账链路允许最终一致，但预扣/预减必须有明确生命周期。

## Implementation

仓库聚焦抢红包路径的拆解与实现实验，强调并发下的正确性论证，而不是 UI。可与秒杀项目对照：二者都是热点写，但公平性与金额分布约束不同。

## Demo

通过压测观察：单 key 热点、锁粒度、Lua/事务方案的差异。记录超发是否为零、尾延迟如何随并发上升。

## GitHub

https://github.com/chengguruchun/RedPacket

## Lessons Learned

- 热点写的第一敌人是「先查后改」的侥幸。
- 公平性是算法问题，也是事务边界问题。
- 对 Agent：任何「先推理再写外部状态」都要有同样的原子闸门。
