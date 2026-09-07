# Hot Words Loop

Weekly loop for `/times/` (nav: **Hot Words**).

## Period

`YYYY-MM-WN` means the **Nth 7-day block of that calendar month** in `Asia/Shanghai`:

- days 1–7 → `W1`
- days 8–14 → `W2`
- …

This is **not** an ISO 8601 week number. `2026-09-W1` is not “ISO week 36”.

## Lifecycle

```
State → Propose → Validate → Apply → Publish → Observe
```

| Phase | Tool | Side effects |
|---|---|---|
| State | `lab_hot_words_state` | none |
| Propose | `lab_hot_words_propose` | none (Actions / DeepSeek today) |
| Validate | `lab_hot_words_validate` | none |
| Apply | `lab_hot_words_apply` | **local files only** + consistency check |
| Publish | `lab_hot_words_publish` | **remote commit/push** when mode=autonomous |
| Observe | `lab_hot_words_run_status` / `lab_hot_words_feedback` | none |

**Apply ≠ Publish.** Evidence must include at least one `https` URL or publish fails (`force` can override duplicate only, not a missing URL unless you skip the gate locally).

## Modes

| Mode | Behavior |
|---|---|
| **autonomous** (schedule default) | gates pass → apply → consistency → commit/push |
| **review** (`workflow_dispatch`) | gates pass → `phase=awaiting_review` → no content publish |

## Gates

- `schema` — word present
- `duplicate` — not the same current word / `proposalHash`
- `editorial` — `why` ≥ 40 chars
- `evidence` — ≥1 https URL required to publish
- `relevance` — overlap with catalog titles/tags (`pass` / `weak`)
- `consistency` — markdown, HTML, `times.json`, catalog, index agree after apply

## Run manifest

- `/api/hot-words/runs/<runId>.json`
- `/api/hot-words/runs/latest.json`
- `/api/hot-words/runs/index.json`

Phases: `started | proposed | validated | awaiting_review | applied | published | skipped | failed`.

## Monday 09:00 Asia/Shanghai

GitHub Action **Hot Words Weekly**:

1. Compute period + `runId`
2. Propose (DeepSeek, structured evidence)
3. Validate (hard evidence URL)
4. Review mode stops here
5. Apply + consistency
6. Publish + finalize manifest with commit SHA
7. Failure Issue / FYI Issue

Secret: `DEEPSEEK_API_KEY`. Inputs: `force`, `mode`.

## Local

```bash
python3 scripts/hot_words_validate.py --period 2026-09-W2 --word "…" --why "…" --require-evidence-url --candidates-json proposal.json
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "…" --why "…"
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "…" --why "…" --verify
```
