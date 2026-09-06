# AI Knowledge Lab

**EN:** This is not a personal blog. It is an open, evolving knowledge system for AI agents — Independent Thinker · AI Agents · Complex Systems · Diverse Thinking.

**ZH:** 这不是个人博客。它是一个面向 AI Agent、持续演进的开放知识系统——Independent Thinker · AI Agents · Complex Systems · Diverse Thinking。

个人站点：https://chengguruchun.github.io  
作者：chengguruchun（杭州）· chengguruchun@163.com

## 本地预览

零构建静态站点。在仓库根目录执行：

```bash
python3 -m http.server 8765
```

然后打开 http://127.0.0.1:8765/

## 结构

- `index.html` 及各栏目目录：静态页面
- `assets/css` · `assets/js`：样式与检索/导航
- `content/`：Markdown 源与 `index.json`（搜索索引）
- `PRODUCT.md`：产品愿景与 P1–P3 路线图

## 技术选择

纯静态 HTML/CSS/JS（Option A），不依赖 Node 构建，便于 GitHub Pages 直接托管。

## For Agents

1. Start with [`SKILL.md`](./SKILL.md)
2. Tool contract: [`mcp/tools.json`](./mcp/tools.json)
3. Catalog: [`api/catalog.json`](./api/catalog.json)
4. Canonical knowledge: `content/**/*.md`

Capabilities are exposed as read-only tools (`lab_get_skill`, `lab_list_entries`, `lab_get_entry`, …). Today they map to static HTTP on GitHub Pages; the same names are reserved for a future MCP server.

