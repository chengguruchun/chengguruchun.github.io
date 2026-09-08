# llm-trace-reuse：编程助手的过程性记忆

GitHub: https://github.com/chengguruchun/llm-trace-reuse

## Problem

编程 Agent 每轮任务都从零规划：同类请求不会复用上次走通的路径，反复踩过的坑也不会沉淀成更短的手册。缺的不是更大的上下文窗口，而是可检索、可复用的过程性记忆。

## Architecture

- **Preferences：** 始终注入的工具偏好（短）
- **Playbooks：** 别名命中则跳过规划，直接跑 SOP
- **Episodes：** 按相似度 × 信任度检索长尾轨迹
- **Distill：** 同一 critique 槽位反复出现则收成更短的手册或脚本

## Design

不是改模型权重的强化学习。是检索 + 蒸馏：把 `preferred_path` 当作可执行资产。路由分数是 `similarity × (0.5 + trust)`；相似度用 IDF 加权的 query coverage，信任度由后续 `retrieved[].used` 与 `outcome.ok` 平滑得到。

## Implementation

仓库根目录即 Cursor skill（`SKILL.md` + `scripts/`）。`route.py` 在任务开始分流；`append-episode.py` 在结束时写入轨迹（必须带 retrieved + preferred_path）。真实轨迹不进仓库，发布前走 `redact-check.py --publish`。

## Demo

```
python3 scripts/route.py "把代码推到远端"
python3 scripts/eval-loo.py
python3 scripts/distill.py
```

## GitHub

https://github.com/chengguruchun/llm-trace-reuse

## Related

- [Agent Optimizer：不训练模型，而是优化经验与策略](/articles/agent-optimizer-experience-policy.html)
- [Agent 的评价：Proxy Metric ≠ Real Outcome](/articles/agent-evaluation-proxy-vs-real-outcome.html)
- 站内卡片：[/projects/](/projects/)

## Lessons Learned

- 有用的记忆是短可执行路径，不是整段 jsonl 回放。
- `retrieved[].used` 必须诚实填写，否则信任度不会动。
- 手册命中就不要再让模型重新规划。
- `outcome.ok` 仍可能只是 Proxy，不能直接当成功案例学习。
