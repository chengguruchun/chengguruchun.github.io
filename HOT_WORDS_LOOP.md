# Hot Words Loop (fully automatic)

Weekly loop for `/times/` (nav: **Hot Words**).

## What runs Mondays 09:00 Asia/Shanghai

GitHub Action **Hot Words Weekly** (`hot-words-weekly.yml`):

1. DeepSeek drafts candidates + chooses one word
2. `scripts/hot_words_apply.py` writes `times/`, `content/times/`, `api/times.json`
3. Commits and pushes to `main` — **no human confirmation**
4. Opens a FYI issue `[hot-words] published …` (not a gate)

Secret required: `DEEPSEEK_API_KEY`.

## Local / agent fallback

```bash
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "…" --why "…"
git add times/index.html content/times api/times.json && git commit && git push
```

Pi package (optional): `.pi/packages/lab-hot-words` — see [docs/pi-deepseek/README.md](docs/pi-deepseek/README.md).
