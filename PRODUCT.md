# AI Knowledge Lab — Product Vision

**定位一句话：** AI Knowledge Lab = Blog for Agents — 给 Agent 读的个人知识博客：可发现、可调用；用独立思考面对复杂系统，把工程实践接到 Agent 基础设施上。

**Brand：** Independent Thinker · AI Agents · Complex Systems · Diverse Thinking  
**Owner：** chengguruchun（杭州）· chengguruchun@163.com  
**路径：** Backend / Distributed → AI Agents / Infrastructure

---

## 它不是什么

- 不是传统博客或个人名片站  
- 不是课程平台或资讯聚合  
- P0 **不包含**：Questions 广场、Hot Topics、Research Notes、Evolution UI、Guestbook、Subscribe、API/RSS/MCP、AI Editor、数据库

## 它是什么（P0）

可静态托管的知识实验室，信息架构：

| 区域 | 作用 |
|------|------|
| **Home** | 坐标、导航、阅读路径（人类 / Agent） |
| **Bench** | 实验台：筛选、验证，过门后再分流 |
| **Articles** | 按文章风格写下的过门结论 |
| **Diverse Lab** | 跨学科、多元写法 |
| **Projects** | 能直接做的工程 + 真实仓库 |
| **Videos** | 口述 / 白板；需要画面的可模型生成后再发 |
| **Hot Words** | 热词周环（不走 Thought Loop） |
| **About** | 作者与实验室说明 |
| **Tags / Search** | 标签穿越 + content/index.json 客户端检索 |

知识源优先：PRODUCT.md、content/index.json、content/**/*.md；HTML 为渲染层。

---

## P0（已交付方向）

- 纯静态多页（HTML/CSS/JS），GitHub Pages 可直接服务  
- .nojekyll；无 Node/Astro 构建依赖  
- 中文优先的编辑式深色 UI、响应式  
- 种子内容：Control Plane / Runtime vs K8s / Registry；三条 Thinking；三项目档案；视频占位  

## P1（下一步）

- 更细的标签图谱与相关推荐  
- 文章内图表组件化（仍保持静态）  
- 视频替换为真实嵌入与字幕文稿  
- 轻量「修订历史」展示（基于 git 日志说明，非应用 DB）  

## P2

- 面向 Agent 的结构化导出（稳定 schema 的 JSON/MD bundle）  
- 主题合集（读单）与学习路径  
- 双语摘要层（中文正文 + 英文 abstract）  

## P3

- 可选 RSS / 只读 API  
- MCP 只读工具（若有明确需求）  
- 演化视图、热门主题等社区层——仅在不破坏「实验室」气质时引入  

---



## Thought Loop

本站的工作方式，不是「聊天 → 直接发文」，而是：

`对话（站外）→ Topic → Candidate → Validated → Article Candidate → Published → Evolution`

Skill 可被任意 Agent 加载。带过来的聊天和初步想法只落 `topic`，过完字段 `gates[]` **和** 模型 `model_gates[]` 才能当验证过。模型标准是可改的提示词（`/content/thoughts/criteria.json`）；本站不调用模型，Agent 读 prompt、写 `judgement`。`ai` + `known` 不能当 Articles 主文。过门后按 `route` 分流。已有正文不重写。Hot Words 仍走自己的周环。详见 `THOUGHT_LOOP.md`、`lab_thought_criteria`、`lab_thought_judge`。

## Agent-native Loop

周日上海 10:00 定时检查本站是否仍面向 Agent 原生（可发现、可调用、正文在 Markdown/JSON）。只写 run 报告，不改知识内容；硬门禁失败开 issue。详见 `api/agent-native/criteria.json` 与 `lab_agent_native_status`。

## Hot Words Loop（Pi + DeepSeek / LiteLLM）

周更 Hot Words（`/times/`）：Actions 默认 **autonomous**（周一上海 09:00：Propose → 证据门禁 → Apply → 一致性 → push）。`workflow_dispatch` 可选 `mode=review`，只写 `awaiting_review` 不发布。周期 `YYYY-MM-WN` 是当月第 N 个 7 天，不是 ISO week。详见 `HOT_WORDS_LOOP.md`。

## 设计原则

1. **问题优于观点包装** — 开放问题必须可见  
2. **架构可论证** — Projects 写清取舍，不只贴仓库链接  
3. **双读者** — 人类可读，Agent 可抓取 Markdown/JSON  
4. **静态优先** — 部署简单，审查面小  
5. **克制** — 不做功能堆砌；P0 以外写在路线图，不假装已上线  
