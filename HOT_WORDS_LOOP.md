# Hot Words Loop (Pi + DeepSeek)

Weekly loop for `/times/` (nav: **Hot Words**).

## Stack

| Layer | Role |
|-------|------|
| Pi / Oh My Pi | Agent harness (`/hot-words`, tools) |
| DeepSeek (default) | Reasoning model |
| LiteLLM (optional) | Multi-model OpenAI-compatible gateway |
| `scripts/hot_words_apply.py` | Deterministic file writer (also CI/fallback) |
| GitHub Action | Monday 09:00 CST nudge + optional DeepSeek draft |

Setup: [docs/pi-deepseek/README.md](docs/pi-deepseek/README.md)
