---
name: hot-words-weekly
description: >
  Use this when running the Knowledge Lab Hot Words weekly loop — propose one
  hot word, write why, and apply files under content/times and times/. Prefer
  DeepSeek via Pi/Oh My Pi as the reasoning model.
---

# Hot Words Weekly Loop

## Goal

Each week: pick **one** hot word + a tight why, write canonical Markdown, update the Hot Words page. Human reviews before git push / Pages publish.

## Protocol

1. Call `lab_hot_words_status` (or read `content/times/` + `api/times.json`).
2. Call `lab_hot_words_propose` for the next `period` (e.g. `2026-09-W2`).
3. Research public AI/engineering signals (papers, launches, incident writeups, infra blogs).
4. Produce **3 candidates** with evidence. Compare novelty / continuity / engineering relevance.
5. Choose one. Write `why` in direct Chinese editorial voice. No hedging filler. No roadmap/placeholder language on the public page.
6. `lab_hot_words_apply` with `dryRun: true`, inspect paths, then apply with `dryRun: false`.
7. Summarize for the human: word, why, files changed. Do **not** claim GitHub Pages is updated unless pushed.

## Quality bar

- One word (or short compound), not a paragraph title.
- Why answers: why **this week**, why it matters for Agents / production systems.
- Separate buzz (proxy) from real practice shift (outcome).
- Prefer advancing the period; do not silently overwrite history without need — keep prior `content/times/*.md` files.

## Model

Prefer DeepSeek (`deepseek-v4-flash` for speed, `deepseek-v4-pro` for harder weeks). Configure via `docs/pi-deepseek/`.
