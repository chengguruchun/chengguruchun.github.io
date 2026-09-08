# Installable Skill

`ai-knowledge-lab/SKILL.md` is the distributable package for this lab. It is a thin
loader: it teaches the discover → hello → execute protocol and points at the live
surfaces, so it does not go stale when content or tools change.

Both Cursor and Claude read the same shape — a directory containing `SKILL.md` with
`name` and `description` frontmatter — so one package covers both.

## Install

**Cursor** (personal, available across projects):

```bash
mkdir -p ~/.cursor/skills
curl -fsSL -o /tmp/lab-skill.md https://chengguruchun.github.io/dist/skills/ai-knowledge-lab/SKILL.md
mkdir -p ~/.cursor/skills/ai-knowledge-lab && mv /tmp/lab-skill.md ~/.cursor/skills/ai-knowledge-lab/SKILL.md
```

**Claude**:

```bash
mkdir -p ~/.claude/skills/ai-knowledge-lab
curl -fsSL -o ~/.claude/skills/ai-knowledge-lab/SKILL.md \
  https://chengguruchun.github.io/dist/skills/ai-knowledge-lab/SKILL.md
```

**Project-scoped** (shared with anyone cloning that repo): use `.cursor/skills/` or
`.claude/skills/` instead of the home directory.

## Verify

Ask the agent something the lab covers — for example "what is the difference between a
proxy metric and a real outcome when evaluating an agent?" — and check that it fetches
`/api/catalog.json` rather than answering from memory.

## Keeping the description useful

`description` is what decides whether an agent ever loads this skill. It must state
**what** the lab covers (the concrete topics) and **when** to reach for it. Vague
descriptions never trigger. When the lab's subject matter shifts, update the
description in both this package and `/SKILL.md`.
