# AI Knowledge Lab

**EN:** An Agent-Native knowledge blog — discoverable, callable, editable, publishable. Independent Thinker · AI Agents · Complex Systems · Diverse Thinking.

**ZH:** Blog for Agents — 面向 Agent-Native 的知识博客：可发现、可调用、可编辑、可发布的笔记。Independent Thinker · AI Agents · Complex Systems · Diverse Thinking。

- 站点：https://chengguruchun.github.io
- 仓库：https://github.com/chengguruchun/chengguruchun.github.io
- 作者：chengguruchun（杭州）· chengguruchun@163.com

**Blog for Agents** — 面向 Agent-Native 的知识博客，首页：**Discover → execute**。

## 人类阅读

| 栏目 | 路径 | 作用 |
|------|------|------|
| Home | [`/`](https://chengguruchun.github.io/) | Agent 接入协议 |
| Bench | [`/bench/`](https://chengguruchun.github.io/bench/) | 实验台：筛选后分流 |
| Diverse Lab | [`/diverse/`](https://chengguruchun.github.io/diverse/) | 跨学科、多元写法 |
| Articles | [`/articles/`](https://chengguruchun.github.io/articles/) | 按文章风格写下的结论 |
| Projects | [`/projects/`](https://chengguruchun.github.io/projects/) | 真实仓库的问题 → 架构 → 教训 |
| Videos | [`/videos/`](https://chengguruchun.github.io/videos/) | 讲解与白板 |
| Hot Words | [`/times/`](https://chengguruchun.github.io/times/) | 热词 |
| About Me | [`/about/`](https://chengguruchun.github.io/about/) | 作者与 The Road Here |
| Tags / Search | [`/tags/`](https://chengguruchun.github.io/tags/) | 标签与检索 |

## 当前知识条目

以 `content/index.json` / `api/catalog.json` 为准（2026-09-06）：

**Articles**

- [Kubernetes × Agent：从容器编排到目标收敛](articles/k8s-to-agent-control-plane.html)

**Diverse Lab**

- [大模型：用科学实验的方式使用](diverse/llm-scientific-experiment.html)
- [物理学 × 生态学：对复杂系统的一个思考](diverse/physics-ecology-llm.html)

**Projects** (page + API only; not in catalog search)

- `/projects/` · research + personal snapshots: `api/projects-research.json`, `api/projects-personal.json`（个人目前只列 [llm-trace-reuse](https://github.com/chengguruchun/llm-trace-reuse)）

**Videos** (page only; not in catalog search)

- `/videos/` · 3 cards · `api/videos.json`

**Hot Words / Times** (in catalog)

- [`/times/`](times/)：热词周记（源：`content/times/` · `api/times.json`）

正文以 `content/**/*.md` 为权威源，HTML 是渲染层。

**Thought Loop**（人看 [`/bench/`](./bench/)）：任意 Agent 加载 Skill 后，聊天/初步想法只落 `topic`，过字段 `gates[]` 和模型 `model_gates[]` 再分流。模型标准是可改提示词。已有文章正文不重写。Hot Words 仍走周环。索引：[`/api/thoughts.json`](./api/thoughts.json) · [`/api/thoughts-criteria.json`](./api/thoughts-criteria.json) · [`THOUGHT_LOOP.md`](./THOUGHT_LOOP.md)

## For Agents

1. 读 [`SKILL.md`](./SKILL.md)（只定义 discover → execute）
2. `GET` [`/api/discover.json`](./api/discover.json)
3. schema 在 [`/mcp/tools.json`](./mcp/tools.json)，再 `lab_execute`
4. 知识索引 [`/api/catalog.json`](./api/catalog.json) → `/content/**/*.md`
5. 站点地图 [`llms.txt`](./llms.txt)
6. 入境是 [`topic`](./THOUGHT_LOOP.md)：聊天和初步想法先蒸馏，再看 [`/api/thoughts.json`](./api/thoughts.json) 的字段 `gates[]` 和模型 `model_gates[]`。标准在 [`/api/thoughts-criteria.json`](./api/thoughts-criteria.json)。未 `published` 的当实验，不当结论。

元工具：`lab_discover`、`lab_execute`。

## 目录

```
index.html                 首页（Agent 接入）
bench/ diverse/ articles/ projects/ videos/ times/ about/ tags/
content/                   Markdown 源 + index.json
api/                       catalog / discover / 分栏 JSON / feeds.json
mcp/tools.json             工具 schema
SKILL.md                   Agent 协议
llms.txt                   机器可读地图
feed.xml                   内容 RSS
scripts/build_feeds.py     从 catalog 生成 RSS
PRODUCT.md                 产品愿景与路线图
assets/                    CSS / JS
```

## 本地预览

零构建。仓库根目录：

```bash
python3 -m http.server 8765
```

打开 http://127.0.0.1:8765/

## 订阅

更新 `content/` 或 `api/catalog.json` 后重建 RSS：

```bash
python3 scripts/build_feeds.py
```

- 内容 RSS：https://chengguruchun.github.io/feed.xml
- 订阅索引：[`/api/feeds.json`](./api/feeds.json)
- Watch 仓库：https://github.com/chengguruchun/chengguruchun.github.io/subscription
- commits Atom：https://github.com/chengguruchun/chengguruchun.github.io/commits/main.atom

推送到 GitHub 后，`.github/workflows/build-feed.yml` 会在内容变更时自动重建 `feed.xml`。

## 技术选择

纯静态 HTML/CSS/JS，无 Node 构建，GitHub Pages 直接托管（`.nojekyll`）。

## Validation

```bash
python3 scripts/validate_lab.py          # local / CI
python3 scripts/validate_lab.py --live   # optional soft live checks
```

CI runs on PR/push via `.github/workflows/validate-lab.yml` (no `--live`).

## Agent-native Loop

Weekly scheduled check: does the Lab still look like a site agents can discover and call?

```bash
python3 scripts/agent_native_check.py --write
python3 scripts/agent_native_check.py --write --live
```

- Criteria: [`/api/agent-native/criteria.json`](./api/agent-native/criteria.json)
- Latest run: [`/api/agent-native/runs/latest.json`](./api/agent-native/runs/latest.json)
- CI: `.github/workflows/agent-native-weekly.yml` (Sunday 10:00 Asia/Shanghai; drift opens an issue)
- Tool: `lab_agent_native_status`

## Hot Words Loop (Pi + LiteLLM + DeepSeek)

Weekly Hot Words under `/times/`. See [HOT_WORDS_LOOP.md](HOT_WORDS_LOOP.md) and [docs/pi-deepseek/README.md](docs/pi-deepseek/README.md).

- Pi package: `.pi/packages/lab-hot-words`
- Apply script: `scripts/hot_words_apply.py`
- Models: DeepSeek direct, or multi-model via LiteLLM (`docs/pi-deepseek/`)
- CI: `.github/workflows/hot-words-weekly.yml` (evidence gate + apply + consistency; autonomous Monday or review mode)
- Period `YYYY-MM-WN` = Nth 7-day block of the month (not ISO week)
- Agent Card: `/.well-known/agent-card.json` (static documentation card)
