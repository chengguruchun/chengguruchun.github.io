# Thought Loop

任何加载了 [`/SKILL.md`](/SKILL.md) 的 Agent 都可以进来。

带过来的东西——聊天、草稿、随口一句话——**只算 `topic`**。不是结论，不能进 catalog，更不能当发表。

```
Chat (off-site, 只蒸馏) → Topic（入境）→ 门禁 → Candidate → Validated → Route → Published
```

对话原文不进本仓库。一条 thought 是蒸馏后的一句话 + 门禁，不是 transcript。Agent 帮筛选和验证，不替人写文章。

## Intake

| 谁 | 能做什么 | 落在哪一档 |
|---|---|---|
| 任意 Agent（加载 Skill） | 把聊天/初步想法蒸馏成一句 | `topic` |
| Agent | 补 critique / comparison / evidence URL | 仍停在 Bench，直到门禁过 |
| 人 | 标 `origin` / `contribution`，决定 `route` | 过门后才分流 |
| 任何人 | 把 `topic` 当成 Articles / Diverse 正文 | **禁止** |

`lab_propose_topic`：只允许写入 `content/thoughts/*.json` 且 `stage=topic`。不写 catalog，不写 Articles。

## Stages

| stage | 含义 | 进 catalog？ |
|---|---|---|
| `topic` | 入境档。Agent 刚带来的想法 | 否 |
| `candidate` | 过了 Origin / Contribution，仍在验证 | 否 |
| `validated` | 过了 Evidence，已定 `route` | 可以（Diverse 等） |
| `article_candidate` | 准备按文章风格写，尚未发表 | 否 |
| `published` | 门禁全过，已出现在对应栏目 | 是 |

## Gates

门禁分两层。字段 PASS 只说明格子填了；**还要过模型门禁**才算验证过。本站是静态页，**不在服务器上调用模型**。加载了 Skill 的 Agent 读标准、在站外判断，把结果写成 `judgement`。

### 字段层 `gates[]`

由 `build_thoughts.py` 硬判（有没有 origin / evidence / route）。不调用模型。

| id | PASS | 从哪一档开始必须过 |
|---|---|---|
| `origin` | 有 `user\|ai\|joint\|external` | candidate |
| `contribution` | 有 `known\|synthesis\|extension\|original_candidate` | candidate |
| `articles_ok` | 不是 `ai` + `known` | 要进 Articles 时 |
| `evidence` | `evidence` 里至少一条可核路径/URL | validated |
| `route` | 有 `diverse\|articles\|videos\|projects` | validated |
| `published` | `stage=published` 且有 `published_url` | published |

`topic` 上 Origin 都可以标（谁带来的），但 Evidence / Route / Published 对入境档默认 UNPASS，这是正常的。

### 模型层 `model_gates[]`

标准就是一段提示词，可以改。源文件 [`/content/thoughts/criteria.json`](/content/thoughts/criteria.json)，索引 [`/api/thoughts-criteria.json`](/api/thoughts-criteria.json)。

| 轴 | 问的是 |
|---|---|
| `sharp` | 这句话够不够尖，是不是可反驳的主张 |
| `evidence_real` | 证据是不是真能核验这句话（不是数组非空） |
| `route_fit` | 分流是否匹配 |

Agent：`lab_thought_criteria` 读 prompt → 按 prompt 判断 → `lab_thought_judge` 只写 `judgement`（含当前 `criteria_version`）。不改 stage，不写文章。

改标准：改 prompt 或轴，**升 `version`**，记 changelog，再 `build_thoughts.py`。旧判决的 version 对不上就是 `stale`，必须重判。没有 `judgement` 是 `pending`。pending / stale / UNPASS 都不能当发表。已发表的旧条目可以暂时缺模型判决，但不等于过了这一层。

## Routes

过门之后才分流。Hot Words **不走这条回路**。

| `route` | 栏目 |
|---|---|
| `diverse` | Diverse Lab |
| `articles` | Articles |
| `videos` | Videos |
| `projects` | Projects |

未定 `route` 的句子停在 Bench。

## Files

- Source: `content/thoughts/*.json`
- Index: `/api/thoughts.json`（`python3 scripts/build_thoughts.py`，含 `gates` + `model_gates`）
- Criteria: `/content/thoughts/criteria.json` → `/api/thoughts-criteria.json`
- Page: `/bench/`（给人看的走轨：思想实验台）
- Tools: `lab_list_thoughts` · `lab_get_thought` · `lab_propose_topic` · `lab_thought_validate` · `lab_thought_criteria` · `lab_thought_judge`
