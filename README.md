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

条目清单以 [`api/catalog.json`](./api/catalog.json) 为唯一权威（这里只记规模，避免手写清单再次漂移）：

| 类型 | 数量 | 入口 |
|------|------|------|
| Articles | 9 | [`/articles/`](https://chengguruchun.github.io/articles/) |
| Diverse Lab | 5 | [`/diverse/`](https://chengguruchun.github.io/diverse/) |
| Hot Words | 1 | [`/times/`](https://chengguruchun.github.io/times/) |

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
sitemap.xml robots.txt     搜索引擎入口（生成物）
scripts/build_feeds.py     从 catalog 生成 RSS
scripts/build_seo.py       注入页面元数据 + 生成 sitemap / robots
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

推送到 GitHub 后，`.github/workflows/build-feed.yml` 会在内容或页面变更时自动重建 `feed.xml`、页面元数据、`sitemap.xml` 与 `robots.txt`。

## 搜索引擎可发现性

Agent 侧靠 `SKILL.md` / `discover.json`；人类侧靠搜索引擎。后者由一个脚本统一维护：

```bash
python3 scripts/build_seo.py           # 重建元数据 + sitemap + robots
python3 scripts/build_seo.py --check   # CI：校验产物是否最新，不写盘
```

它只拥有每个页面 `<head>` 里 `<!-- seo:begin -->` 与 `<!-- seo:end -->` 之间的内容，可反复重跑：

- `canonical`、`og:*`、`twitter:*`、全站 RSS `<link rel="alternate">`
- JSON-LD：文章 `BlogPosting`（含 `datePublished` / `keywords`）+ `BreadcrumbList`；栏目页 `CollectionPage`；首页 `WebSite`；About `ProfilePage`
- `sitemap.xml`（`lastmod` 取自 catalog 日期，缺失时回退到 git 提交日期）
- `robots.txt`（显式放行 GPTBot / ClaudeBot / PerplexityBot 等模型抓取器，并声明 sitemap）

分享卡片：`assets/img/og-cover.svg` 是源，PNG 是产物。改完 SVG 重新光栅化：

```bash
rsvg-convert -w 1200 -h 630 assets/img/og-cover.svg -o assets/img/og-cover.png
```

上线后需在 [Google Search Console](https://search.google.com/search-console) 完成一次资源验证并提交 `sitemap.xml`，收录才会开始。

## 分发与度量

搜索引擎解决人类侧的发现；Agent 侧靠投放和一个信标。

**可安装的 Skill 包**：[`dist/skills/ai-knowledge-lab/`](./dist/skills/ai-knowledge-lab/SKILL.md)。它是薄加载器，只讲协议、指向线上接口，内容和工具变化时不会过期。Cursor 与 Claude 共用同一形态（目录 + 带 `name` / `description` 前置元数据的 `SKILL.md`），安装方式见 [`dist/skills/README.md`](./dist/skills/README.md)。

`description` 决定 Agent 会不会加载这个 Skill——必须写清**覆盖什么主题**和**什么时候用**，含糊的描述永远不会被触发。`validate_lab.py` 会强制它与根目录 `/SKILL.md` 保持一致，防止两份描述漂移。

**信标 `lab_hello`**：静态站没有服务端日志，无法被动统计谁抓了 `discover.json`。协议因此要求 Agent 接入时做一次匿名 GET：

```
GET https://abacus.jasoncameron.dev/hit/chengguruchun-lab/agent-connect
```

不带身份、不带载荷、本站不记日志。首页展示这个计数（用 `/get/` 读取，人类浏览不会把自己算进去），所以它是一条公开的反馈回路，而不是私下埋点。它只统计守协议的 Agent——但这恰恰就是要验证的假设：**有没有 Agent 真的按 Agent-Native 协议在用这个站**。

## 技术选择

纯静态 HTML/CSS/JS，无 Node 构建，GitHub Pages 直接托管（`.nojekyll`）。

## Validation

```bash
python3 scripts/build_seo.py --check     # SEO 产物是否最新
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
