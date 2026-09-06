# Pi / Oh My Pi + DeepSeek · Hot Words Loop

把 Knowledge Lab 的 Hot Words 周更接到 **Pi / Oh My Pi**，模型走 **DeepSeek**。

## 1. 安装

- Oh My Pi: https://github.com/can1357/oh-my-pi  
- 或 Pi coding agent: https://pi.dev / `@earendil-works/pi-coding-agent`

## 2. 模型：多模型 + LiteLLM（推荐）

Hot Words 不绑死单一模型。推荐链路：

```text
Pi / Oh My Pi  →  LiteLLM Proxy (OpenAI-compatible)  →  DeepSeek / Claude / GPT / ...
```

- Pi/OMP 只配置一个 `baseUrl`（LiteLLM）
- 模型切换用 `provider/model` 或 `/model`
- 密钥放在 LiteLLM 或环境变量，不进 git

示例配置见：

- `litellm.config.example.yaml` — LiteLLM 路由
- `models.omp.litellm.example.yml` — OMP 指向本地 LiteLLM
- `models.pi.litellm.example.json` — Pi 指向本地 LiteLLM

仍可不用 LiteLLM，直连 DeepSeek（见下方 example）。

## 2b. DeepSeek API Key（直连时）

```bash
export DEEPSEEK_API_KEY=sk-...
```

不要把 key 写进仓库。示例配置见同目录（无密钥）。

## 3. 拷贝模型配置

**Oh My Pi**

```bash
mkdir -p ~/.omp/agent
cp docs/pi-deepseek/models.omp.example.yml ~/.omp/agent/models.yml
```

**Pi**

```bash
mkdir -p ~/.pi/agent
cp docs/pi-deepseek/models.pi.example.json ~/.pi/agent/models.json
```

## 4. 在本仓库启用包

仓库已含：

- `.pi/settings.json` → packages: `./.pi/packages/lab-hot-words`
- 扩展：`/hot-words` + tools `lab_hot_words_*`
- Skill：`hot-words-weekly`

## 5. 跑一周

```bash
cd /path/to/githubpage
omp --model deepseek/deepseek-v4-flash
# 或 pi，并选 DeepSeek 模型
```

会话里：

```
/hot-words
```

或让 agent 按 skill：`status → propose → research → apply(dryRun) → apply`。

无 Pi 时可用 Python 回退：

```bash
python3 scripts/hot_words_apply.py --period 2026-09-W2 --word "Example" --why "..." --dry-run
```

## 6. CI

`.github/workflows/hot-words-weekly.yml`：每周一 09:00（上海）提醒；若配置了 `DEEPSEEK_API_KEY` secret，可自动开提案 Issue/PR（仍需人工合并）。
