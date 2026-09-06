from pathlib import Path
import json
import re

root = Path(__file__).resolve().parent if False else Path.cwd()
# when run from githubpage cwd
root = Path.cwd()

for rel in ["api/discover.json", "mcp/tools.json"]:
    p = root / rel
    data = json.loads(p.read_text(encoding="utf-8"))
    tools = data.get("tools") or []

    def upsert(entry):
        for i, e in enumerate(tools):
            if e.get("name") == entry["name"]:
                tools[i] = entry
                return
        tools.append(entry)

    if rel.endswith("discover.json"):
        upsert({
            "name": "lab_hot_words_status",
            "kind": "read",
            "description": "Read current Hot Words (Times) state from api/times.json.",
            "invoke": {"method": "GET", "path": "/api/times.json"},
        })
        upsert({
            "name": "lab_hot_words_list",
            "kind": "read",
            "description": "List Hot Words markdown under /content/times/.",
            "invoke": {"method": "GET", "path": "/content/times/"},
        })
        upsert({
            "name": "lab_hot_words_apply",
            "kind": "contribute",
            "description": "Apply Hot Words via Pi tool or scripts/hot_words_apply.py (no auto push).",
            "invoke": {
                "method": "ACTION",
                "action": "local",
                "hint": "python3 scripts/hot_words_apply.py --period PERIOD --word WORD --why WHY",
            },
        })
    else:
        upsert({
            "name": "lab_hot_words_status",
            "kind": "read",
            "description": "Read current Hot Words state.",
            "inputSchema": {"type": "object", "properties": {}},
            "static": {"method": "GET", "path": "/api/times.json"},
        })
        upsert({
            "name": "lab_hot_words_list",
            "kind": "read",
            "description": "List Hot Words content files.",
            "inputSchema": {"type": "object", "properties": {}},
            "static": {"method": "GET", "path": "/content/times/"},
        })
        upsert({
            "name": "lab_hot_words_apply",
            "kind": "contribute",
            "description": "Apply Hot Words via local script/Pi (review before push).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "period": {"type": "string"},
                    "word": {"type": "string"},
                    "why": {"type": "string"},
                    "dryRun": {"type": "boolean"},
                },
                "required": ["period", "word", "why"],
            },
            "static": {
                "method": "ACTION",
                "action": "local",
                "command_template": "python3 scripts/hot_words_apply.py --period {period} --word {word} --why {why}",
            },
        })
    data["tools"] = tools
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("updated", rel, len(tools))

times = root / "api" / "times.json"
if not times.exists():
    md = (root / "content" / "times" / "2026-09-w1.md").read_text(encoding="utf-8")
    parts = md.split("---")
    body = parts[2].strip() if len(parts) >= 3 else ""
    why = "\n".join([ln for ln in body.splitlines() if ln.strip() and not ln.startswith("#")]).strip()
    entry = {
        "id": "times-2026-09-w1",
        "type": "Times",
        "title": "2026-09-W1 · Agent Reliability",
        "period": "2026-09-W1",
        "cadence": "weekly",
        "date": "2026-09-06",
        "word": "Agent Reliability",
        "why": why,
        "url": "/times/",
        "content": "/content/times/2026-09-w1.md",
    }
    times.write_text(
        json.dumps({"updated": "2026-09-06", "current": entry, "items": [entry]}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print("created api/times.json")
else:
    print("times.json ok")

readme = root / "README.md"
rt = readme.read_text(encoding="utf-8") if readme.exists() else ""
if "HOT_WORDS_LOOP" not in rt and "Hot Words Loop" not in rt:
    rt = rt.rstrip() + """

## Hot Words Loop (Pi + LiteLLM + DeepSeek)

Weekly Hot Words under `/times/`. See [HOT_WORDS_LOOP.md](HOT_WORDS_LOOP.md) and [docs/pi-deepseek/README.md](docs/pi-deepseek/README.md).

- Pi package: `.pi/packages/lab-hot-words`
- Apply script: `scripts/hot_words_apply.py`
- Models: DeepSeek direct, or multi-model via LiteLLM (`docs/pi-deepseek/`)
- CI: `.github/workflows/hot-words-weekly.yml`
"""
    readme.write_text(rt, encoding="utf-8")
    print("README patched")
else:
    print("README ok")

# llms.txt mention
llms = root / "llms.txt"
lt = llms.read_text(encoding="utf-8")
if "hot-words" not in lt.lower() and "Hot Words" not in lt:
    lt = lt.rstrip() + "\n- lab_hot_words_status / lab_hot_words_apply\n- [Hot Words](/times/)\n"
    llms.write_text(lt, encoding="utf-8")
    print("llms.txt patched")
else:
    print("llms ok")

print("done")
