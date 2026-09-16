# Knowledge Loop

发表之后的有效性回路。入库仍走 [`THOUGHT_LOOP.md`](/THOUGHT_LOOP.md)。Times / Hot Words **不进**这条线——它们已经是带日期的快照。

```
Published knowledge
        ↓
  time gate (script)
        ↓
   FRESH / STALE
        ↓
Research / Verifier  (optional, report only)
        ↓
   unchanged | changed | insufficient | obsolete
        ↓
Human review  →  keep / changed / contested / archived
        ↓
Git commit
```

过期不等于错误。`STALE` 只表示超过验证周期。`CHANGED` 才表示出现了需要人看的新证据。

## 两条正交轴

| 轴 | 问的问题 | 状态 |
|---|---|---|
| Thought Loop | 有没有资格入库？ | `topic` → `published` |
| Knowledge Loop | 入库之后还成立吗？ | `fresh` / `stale` / `changed` / `contested` / `archived` |

一篇文章可以同时是 `stage=published` 且 `knowledge.status=stale`。复查通过是刷新 `last_verified`，不是重新入库。

## 状态

| status | 谁写下 | 含义 |
|---|---|---|
| `fresh` | 脚本 | 最近验证过，仍可当作现行知识 |
| `stale` | 脚本 | `now > next_review`，还没复查 |
| `changed` | 人 | 外部事实变了，正文待改 |
| `contested` | 人 | 出现了不同观点，尚未裁决 |
| `archived` | 人 | 历史上成立，不再当现行知识 |

人钉住的三种状态写在 `content/knowledge/overrides/{id}.json`，脚本不会覆盖。

## 周期

默认写在 [`/content/knowledge/criteria.json`](/content/knowledge/criteria.json)：

- Articles：90 天
- Diverse Lab：180 天
- 带 `Philosophy` 标签：365 天
- 文章 frontmatter 的 `last_verified` / `cadence_days` 可覆盖
- 人复查时的 override 优先于 frontmatter

## 文件

- Source policy: `content/knowledge/criteria.json`
- Human pins: `content/knowledge/overrides/*.json`
- Agent reports: `content/knowledge/reports/*.json`（只提案，不改正文）
- Index: `/api/knowledge.json`（`python3 scripts/build_knowledge.py`）
- Criteria: `/api/knowledge-criteria.json`
- Runs: `/api/knowledge/runs/latest.json`
- Page: 文章页徽章 + [`/bench/`](/bench/) 的 registry

## Agent 纪律

1. `lab_knowledge_status` / `lab_knowledge_due` 只读。
2. `lab_knowledge_criteria` 读现行 prompt。
3. `lab_knowledge_report` 只写 `content/knowledge/reports/`。不改 Articles / catalog / stage。
4. `changed` / `obsolete` 必须带可核的 https URL；核不过就降为 `insufficient`。
5. 人用 `lab_knowledge_review` / `scripts/knowledge_review.py` 才允许改 `last_verified` 或钉状态。
6. Git commit 是审批记录。Agent 不得 autonomous 改观点。

## 周环

周日上海 10:00（与 agent-native 同一窗口）：

1. `build_knowledge.py` 重算 STALE
2. `knowledge_check.py --write` 写 run
3. 若有 `DEEPSEEK_API_KEY` 且存在 STALE：`knowledge_verify.py --due` 最多 3 篇，只写报告
4. 有待复查条目则开 issue
5. 人 `keep` / `changed` / `contested` / `archived` 后再 commit 正文

## 本地

```bash
python3 scripts/build_knowledge.py
python3 scripts/build_knowledge.py --seed-frontmatter
python3 scripts/build_knowledge.py --check
python3 scripts/knowledge_check.py --write
python3 scripts/knowledge_verify.py --due
python3 scripts/knowledge_verify.py --file report.json
python3 scripts/knowledge_review.py --id k8s-to-agent-control-plane --decision keep
```
