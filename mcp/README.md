# MCP / Skill surface

AI Knowledge Lab exposes **read-only** knowledge capabilities as tools.

## Today (P0+)

- Agents follow [`/SKILL.md`](../SKILL.md).
- Tool contract: [`tools.json`](./tools.json).
- Each tool maps to a **static URL** under GitHub Pages (`/api/*`, `/content/**/*.md`).
- No always-on MCP process required for basic agent access.

## Next

Wrap the same tool names/schemas in an MCP server (`stdio` or HTTP) that:
1. Serves `lab_*` tools from this manifest
2. Fetches Markdown from the repo or Pages URL
3. Optionally adds `lab_subscribe` (P2) for topic watchers

Do not invent write tools (publish, merge, AI editor) until those product stages exist.
