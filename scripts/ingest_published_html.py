#!/usr/bin/env python3
"""Turn published article/diverse HTML into canonical Markdown + catalog rows.

Agent-native rule: a public HTML page is not knowledge until it has
/content/**/*.md and a catalog entry. This script only writes missing sources.
It does not rewrite existing Markdown.
"""
from __future__ import annotations

import html as html_lib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import (  # noqa: E402
    ARTICLES,
    CATALOG,
    DIVERSE,
    INDEX,
    load_json,
    write_json,
)

CITE_JUNK = re.compile(r"\uE200cite\uE202[^\uE201]*\uE201")

PAGES = [
    {
        "id": "iot-agent-from-automation-to-physical-infrastructure",
        "type": "Articles",
        "title": "IoT Agent 化：从自动化平台到 Physical Infrastructure",
        "excerpt": "Agent 不会消灭 IoT 的基础设施，而会解构过去为了服务人类而预先打包好的应用层确定性。契约留下，打包物被解包到运行时。",
        "url": "/articles/iot-agent-from-automation-to-physical-infrastructure.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Agent", "IoT", "Smart Home", "Benchmark", "MHS", "Architecture", "Physical AI"],
        "html": ROOT / "articles" / "iot-agent-from-automation-to-physical-infrastructure.html",
        "content": "/content/articles/iot-agent-from-automation-to-physical-infrastructure.md",
    },
    {
        "id": "iot-agent-from-automation-to-physical-infrastructure-part-ii",
        "type": "Articles",
        "title": "IoT Agent 化：从自动化平台到 Physical Infrastructure（二）",
        "excerpt": "第一篇讨论“契约留下，打包物被解包到运行时”。这一篇继续往下追：当 Agent 真正进入物理世界，IoT 平台究竟应该提供什么？",
        "url": "/articles/iot-agent-from-automation-to-physical-infrastructure-part-ii.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Agent", "IoT", "Physical AI", "Architecture", "Benchmark"],
        "html": ROOT / "articles" / "iot-agent-from-automation-to-physical-infrastructure-part-ii.html",
        "content": "/content/articles/iot-agent-from-automation-to-physical-infrastructure-part-ii.md",
    },
    {
        "id": "ai-era-production-consumption-balance",
        "type": "Articles",
        "title": "AI 时代，企业真正需要解决的不是流程，而是生产与消费的平衡",
        "excerpt": "当 AI 让生产、执行和运营越来越便宜，企业真正需要关注的可能不再只是流程效率，而是如何缩短需求、生产、消费与反馈之间的距离。",
        "url": "/articles/ai-era-production-consumption-balance.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Agent", "Feedback Loop", "Production", "Consumption"],
        "html": ROOT / "articles" / "ai-era-production-consumption-balance.html",
        "content": "/content/articles/ai-era-production-consumption-balance.md",
    },
    {
        "id": "h-neurons-paper-reading",
        "type": "Diverse Lab",
        "title": "H-Neurons：幻觉可能藏在模型内部的稀疏神经元中",
        "excerpt": "从神经元层面理解 hallucination、over-compliance 与预训练起源，并思考内部风险信号如何进入 Agent Runtime。",
        "url": "/diverse/h-neurons-paper-reading.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Diverse", "Interpretability", "Hallucination", "Agent Runtime", "LLM"],
        "html": ROOT / "diverse" / "h-neurons-paper-reading.html",
        "content": "/content/diverse/h-neurons-paper-reading.md",
    },
    {
        "id": "simuhome-paper-reading",
        "type": "Diverse Lab",
        "title": "SimuHome：从“调用设备”到“与环境闭环”",
        "excerpt": "智能家居 Agent benchmark 的一个重要转变：从判断 API 是否调用正确，到观察环境、行动、等待状态变化并验证目标状态。",
        "url": "/diverse/simuhome-paper-reading.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Diverse", "IoT", "Agent", "Physical Runtime", "Benchmark"],
        "html": ROOT / "diverse" / "simuhome-paper-reading.html",
        "content": "/content/diverse/simuhome-paper-reading.md",
    },
    {
        "id": "agent-runtime-cognitive-actor",
        "type": "Articles",
        "title": "从 Actor Model 到 Cognitive Actor：Claude Agent Teams 给 Agent Runtime 的启发",
        "excerpt": "从 Akka Actor、Mailbox、Supervisor、Sharding 出发，分析 Claude Agent Teams、多 Agent 通信与 Agent Runtime 的演化。",
        "url": "/articles/agent-runtime-cognitive-actor.html",
        "date": "2026-09-20",
        "thought_date": "2026-09-20",
        "published_date": "2026-09-20",
        "tags": ["Agent", "Runtime", "Akka", "Actor Model"],
        "html": ROOT / "articles" / "agent-runtime-cognitive-actor.html",
        "content": "/content/articles/agent-runtime-cognitive-actor.md",
    },
    {
        "id": "fde-agent-opportunity-discovery",
        "type": "Articles",
        "title": "FDE 的新价值：识别业务复杂度，而不是简单交付 Agent",
        "excerpt": "从 Business Reality 到 Decision Unit，再到 Agent Suitability：重新理解 FDE 在 Agent 项目中的价值。",
        "url": "/articles/fde-agent-opportunity-discovery.html",
        "date": "2026-09-17",
        "thought_date": "2026-09-17",
        "published_date": "2026-09-17",
        "tags": ["Agent", "FDE", "Forward-Deployed-Engineer", "Business-Complexity", "Decision-Unit", "Agent-Suitability", "Agent-Architecture"],
        "html": ROOT / "articles" / "fde-agent-opportunity-discovery.html",
        "content": "/content/articles/fde-agent-opportunity-discovery.md",
    },
    {
        "id": "from-llm-to-agent-runtime",
        "type": "Articles",
        "title": "从 LLM 到 Agent Runtime：当“预测下一个 Token”开始进入真实世界",
        "excerpt": "从模型推理、KV Cache、Inference Runtime、Tool、Environment 和 Feedback 出发，思考为什么 Agent Runtime 是模型能力进入真实世界之后的新一层。",
        "url": "/articles/from-llm-to-agent-runtime.html",
        "date": "2026-09-21",
        "thought_date": "2026-09-21",
        "published_date": "2026-09-21",
        "tags": ["LLM", "Runtime", "Agent", "Inference"],
        "html": ROOT / "articles" / "from-llm-to-agent-runtime.html",
        "content": "/content/articles/from-llm-to-agent-runtime.md",
    },
    {
        "id": "from-mes-to-manufacturing-agent-runtime",
        "type": "Articles",
        "title": "从 MES 到 Manufacturing Agent Runtime：当生产系统开始自己做决策",
        "excerpt": "SHEIN 式制造的关键不是把 MES 加上一个 Copilot，而是把高频、动态、组合复杂的生产决策变成 Agent Runtime 的持续闭环。核心观点：不要替代岗位，要替代决策单元。",
        "url": "/articles/from-mes-to-manufacturing-agent-runtime.html",
        "date": "2026-09-16",
        "thought_date": "2026-09-16",
        "published_date": "2026-09-16",
        "tags": ["Agent", "Manufacturing", "MES", "Agent Runtime", "Control Plane", "Supply Chain", "Decision Engineering"],
        "html": ROOT / "articles" / "from-mes-to-manufacturing-agent-runtime.html",
        "content": "/content/articles/from-mes-to-manufacturing-agent-runtime.md",
    },
    {
        "id": "spring-dubbo-deepseek-harness-runtime",
        "type": "Articles",
        "title": "从 Spring、Dubbo 到 DeepSeek Harness：运行时架构为什么正在趋同",
        "excerpt": "从 Spring、Dubbo Service 到 DeepSeek Harness，观察依赖注入、Context、Event Bus、生命周期与运行时治理这些工程思想如何在 Agent 时代重新组合。",
        "url": "/articles/spring-dubbo-deepseek-harness-runtime.html",
        "date": "2026-09-21",
        "thought_date": "2026-09-21",
        "published_date": "2026-09-21",
        "tags": ["Agent", "Runtime", "Spring", "Dubbo", "Harness"],
        "html": ROOT / "articles" / "spring-dubbo-deepseek-harness-runtime.html",
        "content": "/content/articles/spring-dubbo-deepseek-harness-runtime.md",
    },
    {
        "id": "transformer-from-attention-to-decoder-only",
        "type": "Articles",
        "title": "从 Transformer 到 Decoder-only：我重新理解大语言模型是怎么“学会”的",
        "excerpt": "从一次关于 Transformer 的追问出发，重新理解 Self-Attention、Encoder-Decoder、Decoder-only，以及训练与推理到底有什么不同。",
        "url": "/articles/transformer-from-attention-to-decoder-only.html",
        "date": "2026-09-21",
        "thought_date": "2026-09-21",
        "published_date": "2026-09-21",
        "tags": ["Agent", "Transformer", "LLM", "Attention"],
        "html": ROOT / "articles" / "transformer-from-attention-to-decoder-only.html",
        "content": "/content/articles/transformer-from-attention-to-decoder-only.md",
    },
]


class BodyParser(HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer"}
    BLOCK = {"p", "h1", "h2", "h3", "h4", "pre", "blockquote", "li", "div"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0
        self.in_body = False
        self.stack: list[str] = []
        self.href = ""
        self.buf = ""
        self.list_open = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        cls = attrs_d.get("class") or ""
        if tag in self.SKIP or tag == "section" and "site-header" in cls:
            self.skip += 1
            return
        if self.skip:
            if tag in self.SKIP:
                self.skip += 1
            return
        if tag in {"article", "main"} or "prose-wrap" in cls or "article-content" in cls or "article-body" in cls:
            self.in_body = True
        if not self.in_body:
            return
        if tag == "a":
            self.href = attrs_d.get("href") or ""
        if tag == "ul":
            self.list_open = True
        if tag == "br":
            self.buf += "\n"
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if self.skip:
            if tag in self.SKIP:
                self.skip = max(0, self.skip - 1)
            return
        if not self.in_body:
            return
        if tag in {"article", "main"} and tag in self.stack:
            self.flush()
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag in self.BLOCK:
            self.flush(tag)
        if tag == "a":
            self.href = ""
        if tag == "ul":
            self.list_open = False

    def handle_data(self, data: str) -> None:
        if self.skip or not self.in_body:
            return
        text = CITE_JUNK.sub("", data)
        if not text:
            return
        if self.stack and self.stack[-1] == "a" and self.href:
            label = text.strip()
            if label:
                self.buf += f"[{label}]({self.href})"
            return
        if self.stack and self.stack[-1] in {"strong", "b"}:
            self.buf += f"**{text}**" if text.strip() else text
            return
        if self.stack and self.stack[-1] in {"em", "i"}:
            self.buf += f"*{text}*" if text.strip() else text
            return
        if self.stack and self.stack[-1] == "code":
            self.buf += f"`{text}`"
            return
        self.buf += text

    def flush(self, tag: str = "p") -> None:
        text = self.buf.strip()
        self.buf = ""
        if not text:
            return
        if tag == "h1":
            self.parts.append(f"# {text}")
        elif tag == "h2":
            self.parts.append(f"## {text}")
        elif tag == "h3":
            self.parts.append(f"### {text}")
        elif tag == "h4":
            self.parts.append(f"#### {text}")
        elif tag == "pre":
            self.parts.append("```text\n" + text + "\n```")
        elif tag == "blockquote":
            quoted = "\n".join("> " + line if line else ">" for line in text.splitlines())
            self.parts.append(quoted)
        elif tag == "li":
            self.parts.append(f"- {text}")
        elif tag == "div" and ("architecture" in text or "┌" in text or "↓" in text):
            self.parts.append("```text\n" + text + "\n```")
        else:
            if tag == "div" and len(text) < 40 and text in {"Articles", "Diverse Lab"}:
                return
            self.parts.append(text)


def html_to_markdown(path: Path, title: str) -> str:
    parser = BodyParser()
    raw = path.read_text(encoding="utf-8")
    parser.feed(raw)
    chunks = [p for p in parser.parts if p and p not in {title, f"# {title}"}]
    body = "\n\n".join(chunks).strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    return f"# {title}\n\n{body}\n"


def catalog_row(meta: dict) -> dict:
    rel = meta["content"]
    return {
        "id": meta["id"],
        "type": meta["type"],
        "title": meta["title"],
        "excerpt": meta["excerpt"],
        "url": meta["url"],
        "date": meta["date"],
        "tags": meta["tags"],
        "thought_date": meta["thought_date"],
        "published_date": meta["published_date"],
        "history_url": f"https://github.com/chengguruchun/chengguruchun.github.io/commits/main{rel}",
        "content": rel,
    }


def upsert(path: Path, row: dict, wrap_catalog: bool = False) -> None:
    data = load_json(path) if path.exists() else {}
    items = [x for x in (data.get("items") or []) if isinstance(x, dict) and x.get("id") != row["id"]]
    non_times = [x for x in items if x.get("type") != "Times"]
    times = [x for x in items if x.get("type") == "Times"]
    data["items"] = [row] + non_times + times
    if wrap_catalog:
        data.setdefault("name", "AI Knowledge Lab")
        data.setdefault("skill", "/SKILL.md")
        data.setdefault("product", "/PRODUCT.md")
        data.setdefault("llms", "/llms.txt")
        data.setdefault("base_url", "https://chengguruchun.github.io")
    write_json(path, data)


def write_markdown(meta: dict) -> bool:
    dest = ROOT / str(meta["content"]).lstrip("/")
    if dest.exists():
        return False
    if not meta["html"].exists():
        raise SystemExit(f"missing html {meta['html']}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = html_to_markdown(meta["html"], meta["title"])
    tags = ", ".join(meta["tags"])
    front = (
        "---\n"
        f"id: {meta['id']}\n"
        f"type: {meta['type']}\n"
        f"title: {meta['title']}\n"
        f"date: {meta['date']}\n"
        f"thought_date: {meta['thought_date']}\n"
        f"published_date: {meta['published_date']}\n"
        f"tags: [{tags}]\n"
        f"excerpt: {meta['excerpt']}\n"
        f"history_url: https://github.com/chengguruchun/chengguruchun.github.io/commits/main{meta['content']}\n"
        f"last_verified: {meta['published_date']}\n"
        f"cadence_days: {90 if meta['type'] == 'Articles' else 180}\n"
        "---\n\n"
    )
    dest.write_text(front + text, encoding="utf-8")
    return True


def main() -> int:
    created = 0
    for meta in PAGES:
        if not meta["html"].exists():
            print(f"skip missing html {meta['id']}")
            continue
        if write_markdown(meta):
            print(f"wrote {meta['content']}")
            created += 1
        else:
            print(f"keep {meta['content']}")
        row = catalog_row(meta)
        upsert(CATALOG, row, wrap_catalog=True)
        upsert(INDEX, row)
        if meta["type"] == "Articles":
            upsert(ARTICLES, row)
        else:
            upsert(DIVERSE, row)
    print(f"ingested {len(PAGES)} catalog rows; created {created} markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
