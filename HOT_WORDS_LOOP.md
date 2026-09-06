# Hot Words Loop (fully automatic)

Weekly loop for `/times/` (nav: **Hot Words**).

## What runs Mondays 09:00 Asia/Shanghai

GitHub Action **Hot Words Weekly** (`hot-words-weekly.yml`):

1. DeepSeek drafts candidates + chooses one word
2. **Quality gates**: `chosen.word` non-empty; `why` length ≥ 40; word ≠ current word (unless `force=true`)
3. If the period is already published and `force` is false → skip apply/push (job succeeds)
4. `scripts/hot_words_apply.py` writes `times/`, `content/times/`, `api/times.json`, and upserts Times into `content/index.json` + `api/catalog.json`
5. Commits and pushes to `main` — **no human confirmation**
6. Opens a FYI issue `[hot-words] published …` (not a gate)
7. On DeepSeek/parse/quality failure → opens `[hot-words] failed PERIOD` (does not silent-exit 0)

Secret required: `DEEPSEEK_API_KEY`.

Manual dispatch supports input **`force`** (boolean, default false) to republish the same period/word.

## Local / agent fallback

```bash
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "…" --why "…"
# writes files only — no push
git add times/index.html content/times api/times.json content/index.json api/catalog.json
git commit && git push
```

Pi package (optional): `.pi/packages/lab-hot-words` — see [docs/pi-deepseek/README.md](docs/pi-deepseek/README.md).
