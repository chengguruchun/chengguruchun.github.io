# Hot Words Loop

Weekly loop for `/times/` (nav: **Hot Words**).

## Lifecycle (tools protocol)

```
State → Propose → Validate → Apply → Publish → Observe
```

| Phase | Tool | Side effects |
|---|---|---|
| State | `lab_hot_words_state` | none |
| Propose | `lab_hot_words_propose` | none (Actions / DeepSeek today) |
| Validate | `lab_hot_words_validate` | none |
| Apply | `lab_hot_words_apply` | **local files only** |
| Publish | `lab_hot_words_publish` | **remote commit/push** (requiresApproval) |
| Observe | `lab_hot_words_run_status` / `lab_hot_words_feedback` | none |

**Apply ≠ Publish.** `lab_hot_words_apply` never pushes. Publish is Actions (autonomous Mondays) or an explicit high-risk publish contract.

## Run manifest (Observe)

Every weekly run writes:

- `/api/hot-words/runs/<runId>.json`
- `/api/hot-words/runs/latest.json`
- `/api/hot-words/runs/index.json`

Agents should call **`lab_hot_words_run_status`** (GET latest) instead of parsing Actions logs.

Manifest fields: `runId`, `period`, `phase` (`started|proposed|validated|applied|published|skipped|failed`), `input`, `proposal`, `gates`, `apply`, `publish`, `error`.

## What runs Mondays 09:00 Asia/Shanghai

GitHub Action **Hot Words Weekly** (`hot-words-weekly.yml`):

1. Compute period + `runId`
2. DeepSeek Propose (prefer structured evidence objects; string evidence still allowed)
3. Validate gates: word non-empty; why ≥ 40 chars; word ≠ current (unless `force`)
4. If period already published and not `force` → `phase=skipped`, still commit run manifest
5. Apply via `scripts/hot_words_apply.py`
6. Publish: commit/push content + manifests; finalize `phase=published` with commit SHA
7. FYI / failure Issues as before

Secret: `DEEPSEEK_API_KEY`. Manual dispatch input **`force`**.

Default mode: **autonomous**. Future option: **review** (proposal/PR before publish) — not required yet.

## Eval / Learn (next)

Execute loop is in place. Later: feed visits / votes / comments / citations into `lab_hot_words_feedback` and next week's Propose context.

## Local / agent fallback

```bash
python3 scripts/hot_words_validate.py --period 2026-09-W2 --word "…" --why "…"
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "…" --why "…"
# apply writes files only — no push
python3 scripts/hot_words_manifest.py --run-id hot-words-local-1 --period 2026-09-W2 --phase applied
```


## Evidence (Propose)

Candidates should carry structured evidence:

```json
{
  "title": "…",
  "url": "https://…",
  "sourceType": "article",
  "publishedAt": "2026-09-05",
  "claim": "…"
}
```

Gate: `evidence=pass` when ≥1 https URL; `weak` for string-only; `skip` if empty.

## Observe on /times/

The Hot Words page renders **运行观测** from:

- `/api/hot-words/runs/latest.json`
- `/api/hot-words/runs/index.json`
- `/api/hot-words/feedback.json`

`scripts/hot_words_feedback.py --write` rebuilds feedback (learnHints + lastRun) for the next Propose context.
