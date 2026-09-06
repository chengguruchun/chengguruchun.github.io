# AI Knowledge Lab

**EN:** An open knowledge system for AI Agents — discoverable, callable. Independent Thinker · AI Agents · Complex Systems · Diverse Thinking.

**ZH:** 面向 AI Agent 的开放知识系统：可发现、可调用。Independent Thinker · AI Agents · Complex Systems · Diverse Thinking。

- 站点：https://chengguruchun.github.io
- 仓库：https://github.com/chengguruchun/chengguruchun.github.io
- 作者：chengguruchun（杭州）· chengguruchun@163.com

这不是个人博客。首页只做一件事：告诉 Agent 如何 **Discover → execute**。Skill 保持极薄，能力在 catalog 里生长。

## 人类阅读

| 栏目 | 路径 | 作用 |
|------|------|------|
| Home | [`/`](https://chengguruchun.github.io/) | Agent 接入协议 |
| Diverse Lab | [`/diverse/`](https://chengguruchun.github.io/diverse/) | 开放问题与未闭合思考 |
| Articles | [`/articles/`](https://chengguruchun.github.io/articles/) | 可引用长文 |
| Projects | [`/projects/`](https://chengguruchun.github.io/projects/) | 真实仓库的问题 → 架构 → 教训 |
| Videos | [`/videos/`](https://chengguruchun.github.io/videos/) | 讲解与白板（部分占位） |
| About Me | [`/about/`](https://chengguruchun.github.io/about/) | 作者与 The Road Here |
| Tags / Search | [`/tags/`](https://chengguruchun.github.io/tags/) | 标签穿越 + 客户端检索 |

## 当前知识条目

以 `content/index.json` / `api/catalog.json` 为准（2026-09-06）：

**Articles**

- [Agent Control Plane：把智能体当成可治理的运行时](articles/agent-control-plane.html)
- [Agent Runtime 与 Kubernetes：相似的外壳，不同的内核](articles/agent-runtime-vs-k8s.html)
- [Agent Registry：能力发现、版本契约与信任边界](articles/agent-registry.html)

**Diverse Lab**

- [不确定执行能否被「像服务一样」SLA 化？](diverse/determinism-sla.html)
- [Agent 记忆：状态、知识，还是日志？](diverse/agent-memory.html)
- [多 Agent 协作的失败模式更像分布式事务](diverse/multi-agent-failure.html)

**Projects**

- [concurrency：高并发实验台](projects/concurrency.html)
- [RedPacket：抢红包的并发解剖](projects/redpacket.html)
- [miaoshao_test：秒杀链路压测与优化](projects/miaoshao.html)

**Videos**（即将上线）

- 讲解：为什么 Agent 需要 Control Plane
- 对照阅读：K8s 抽象 vs Agent Runtime

正文以 `content/**/*.md` 为权威源，HTML 是渲染层。

## For Agents

1. 读 [`SKILL.md`](./SKILL.md)（只定义 discover → execute）
2. `GET` [`/api/discover.json`](./api/discover.json)（能力会增长，勿写死）
3. schema 在 [`/mcp/tools.json`](./mcp/tools.json)，再 `lab_execute`
4. 知识索引 [`/api/catalog.json`](./api/catalog.json) → `/content/**/*.md`
5. 站点地图 [`llms.txt`](./llms.txt)

稳定元工具：`lab_discover`、`lab_execute`。新能力只加 discover / tools，不改 SKILL。

## 目录

```
index.html                 首页（Agent 接入）
diverse/ articles/ projects/ videos/ about/ tags/
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
