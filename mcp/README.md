# MCP / tool registry

Agents load `/SKILL.md`, then:

1. `GET /api/discover.json`
2. `GET /mcp/tools.json` and execute via `lab_execute`

Add or change domain tools **here** (and mirror short entries in `/api/discover.json`). Do not bloat `SKILL.md`.

P0 transport: static HTTP + ACTION urls (GitHub / mailto). Later: real MCP.
