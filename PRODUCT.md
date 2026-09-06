# AI Knowledge Lab — Product Vision

**定位一句话：** AI Knowledge Lab 是面向人类与 AI Agent 共同阅读的开放知识系统——用独立思考面对复杂系统，把工程直觉接到 Agent 基础设施上。

**Brand：** Independent Thinker · Complex Systems · AI Agents  
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
| **Articles** | 可引用长文（问题、架构、开放问题） |
| **Thinking Lab** | Question / My Thinking / Open Questions |
| **Projects** | Problem → Architecture → … → Lessons + 真实仓库 |
| **Videos** | 讲解与白板（可占位） |
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

## 设计原则

1. **问题优于观点包装** — 开放问题必须可见  
2. **架构可论证** — Projects 写清取舍，不只贴仓库链接  
3. **双读者** — 人类可读，Agent 可抓取 Markdown/JSON  
4. **静态优先** — 部署简单，审查面小  
5. **克制** — 不做功能堆砌；P0 以外写在路线图，不假装已上线  
