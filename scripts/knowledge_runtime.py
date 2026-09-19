#!/usr/bin/env python3
"""Research Runtime Observe layer: url_fetch + arxiv_lookup on cited URLs.

Does not edit articles. Does not search the open web.
"""
from __future__ import annotations

import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from html import unescape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from knowledge_lib import parse_date, utc_now  # noqa: E402

ATOM = "{http://www.w3.org/2005/Atom}"
UA = (
    "AIKnowledgeLab-knowledge-runtime/1.0 "
    "(+https://github.com/chengguruchun/chengguruchun.github.io; "
    "mailto:chengguruchun@163.com)"
)
ARXIV_API = "https://export.arxiv.org/api/query"
MD_LINK = re.compile(r"\[([^\]]*)\]\((https?://[^)\s]+)\)")
AUTO_LINK = re.compile(r"<(https://[^>\s]+)>")
BARE_URL = re.compile(r"(?<!\()(?<!<)(https://[^\s<>\]\"']+)")
ARXIV_ID = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf|html)/|arxiv:)(\d{4}\.\d{4,5})(?:v(\d+))?",
    re.I,
)
ARXIV_VERSION = re.compile(r"(\d{4}\.\d{4,5})(?:v(\d+))?$", re.I)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
FRONT = re.compile(r"^---\n.*?\n---\n?", re.S)
TRAIL = re.compile(r"[)\].,;:]+$")

SKIP_HOSTS = {
    "chengguruchun.github.io",
    "www.chengguruchun.github.io",
}
SKIP_PREFIXES = (
    "https://github.com/chengguruchun/chengguruchun.github.io",
)
DEFAULT_BUDGET = {"url_fetch": 6, "arxiv_lookup": 3}


def runtime_policy(criteria: dict[str, Any] | None) -> dict[str, Any]:
    raw = (criteria or {}).get("runtime") if isinstance((criteria or {}).get("runtime"), dict) else {}
    budget = raw.get("budget") if isinstance(raw.get("budget"), dict) else {}
    return {
        "tools": list(raw.get("tools") or ["url_fetch", "arxiv_lookup"]),
        "budget": {
            "url_fetch": int(budget.get("url_fetch") or DEFAULT_BUDGET["url_fetch"]),
            "arxiv_lookup": int(budget.get("arxiv_lookup") or DEFAULT_BUDGET["arxiv_lookup"]),
        },
    }


def markdown_body(entry: dict[str, Any]) -> str:
    rel = entry.get("content")
    if not rel:
        return str(entry.get("excerpt") or "")
    path = ROOT / str(rel).lstrip("/")
    if not path.exists():
        return str(entry.get("excerpt") or "")
    text = path.read_text(encoding="utf-8")
    return FRONT.sub("", text, count=1)


def _clean_url(raw: str) -> str:
    url = TRAIL.sub("", (raw or "").strip())
    url = url.rstrip("。，、")
    if url.startswith("http://arxiv.org/"):
        url = "https://" + url[len("http://") :]
    return url


def _host(url: str) -> str:
    try:
        return (urllib.parse.urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def skip_url(url: str) -> bool:
    if not url.startswith("https://"):
        return True
    host = _host(url)
    if host in SKIP_HOSTS:
        return True
    if any(url.startswith(p) for p in SKIP_PREFIXES):
        return True
    return False


def parse_arxiv(url_or_id: str) -> tuple[str, int | None] | None:
    m = ARXIV_ID.search(url_or_id)
    if not m:
        return None
    vid = m.group(2)
    return m.group(1), int(vid) if vid else None


def abs_url(arxiv_id: str, version: int | None = None) -> str:
    suffix = f"v{version}" if version else ""
    return f"https://arxiv.org/abs/{arxiv_id}{suffix}"


def extract_citations(text: str) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}

    def add(url: str, source: str) -> None:
        url = _clean_url(url)
        if skip_url(url) or url in found:
            return
        rec: dict[str, Any] = {"url": url, "source": source}
        parsed = parse_arxiv(url)
        if parsed:
            rec["arxiv_id"] = parsed[0]
            rec["arxiv_version"] = parsed[1]
        found[url] = rec

    for m in MD_LINK.finditer(text):
        add(m.group(2), "markdown")
    for m in AUTO_LINK.finditer(text):
        add(m.group(1), "autolink")
    for m in BARE_URL.finditer(text):
        add(m.group(1), "bare")
    for m in ARXIV_ID.finditer(text):
        aid, ver = m.group(1), int(m.group(2)) if m.group(2) else None
        url = abs_url(aid, ver)
        if url not in found:
            add(url, "arxiv_id")
        elif "arxiv_id" not in found[url]:
            found[url]["arxiv_id"] = aid
            found[url]["arxiv_version"] = ver
    return list(found.values())


def _request(url: str, method: str, limit: int = 80_000) -> tuple[int, str, bytes]:
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml,application/pdf;q=0.9,*/*;q=0.8"},
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        status = int(getattr(resp, "status", 200) or 200)
        final = resp.geturl()
        body = b"" if method == "HEAD" else resp.read(limit)
        return status, final, body


def _title(body: bytes) -> str | None:
    if not body:
        return None
    if body[:4] == b"%PDF":
        return None
    try:
        text = body.decode("utf-8", errors="ignore")
    except Exception:
        return None
    m = TITLE_RE.search(text)
    if not m:
        return None
    title = unescape(re.sub(r"\s+", " ", m.group(1))).strip()
    return title[:200] or None


def url_fetch(url: str) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "tool": "url_fetch",
        "url": url,
        "observed_at": utc_now(),
        "ok": False,
        "status": None,
        "final_url": None,
        "title": None,
        "signal": "error",
        "error": None,
    }
    try:
        try:
            status, final, body = _request(url, "HEAD")
            if status == 405 or not (200 <= status < 400):
                status, final, body = _request(url, "GET")
            elif 200 <= status < 400:
                body = b""
        except Exception:
            status, final, body = _request(url, "GET")
        rec["status"] = status
        rec["final_url"] = final
        rec["title"] = _title(body)
        if 200 <= status < 400:
            rec["ok"] = True
            rec["signal"] = "live"
        elif status in {404, 410, 451}:
            rec["signal"] = "gone"
            rec["error"] = f"http {status}"
        elif status in {401, 403}:
            rec["signal"] = "blocked"
            rec["error"] = f"http {status}"
        else:
            rec["signal"] = "error"
            rec["error"] = f"http {status}"
    except urllib.error.HTTPError as exc:
        rec["status"] = int(exc.code)
        rec["error"] = f"http {exc.code}"
        rec["signal"] = "gone" if exc.code in {404, 410, 451} else ("blocked" if exc.code in {401, 403} else "error")
    except Exception as exc:
        rec["error"] = str(exc)[:160]
        rec["signal"] = "error"
    return rec


def _arxiv_version(entry_id: str) -> tuple[str | None, int | None]:
    m = ARXIV_VERSION.search((entry_id or "").rstrip("/"))
    if not m:
        return None, None
    return m.group(1), int(m.group(2)) if m.group(2) else None


def arxiv_lookup(arxiv_id: str, cited_version: int | None, last_verified: date | None) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "tool": "arxiv_lookup",
        "arxiv_id": arxiv_id,
        "cited_version": cited_version,
        "url": abs_url(arxiv_id, cited_version),
        "abs_url": abs_url(arxiv_id),
        "observed_at": utc_now(),
        "ok": False,
        "title": None,
        "published": None,
        "updated": None,
        "latest_version": None,
        "newer_than_cite": False,
        "updated_after_verified": False,
        "error": None,
    }
    query = urllib.parse.urlencode({"id_list": arxiv_id, "max_results": 1})
    req = urllib.request.Request(
        f"{ARXIV_API}?{query}",
        headers={"User-Agent": UA, "Accept": "application/atom+xml"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml = resp.read()
        root = ET.fromstring(xml)
        entry = root.find(f"{ATOM}entry")
        if entry is None:
            rec["error"] = "arxiv entry missing"
            return rec
        aid_text = (entry.findtext(f"{ATOM}id") or "").strip()
        title = unescape(re.sub(r"\s+", " ", entry.findtext(f"{ATOM}title") or "")).strip()
        published = (entry.findtext(f"{ATOM}published") or "")[:10] or None
        updated = (entry.findtext(f"{ATOM}updated") or "")[:10] or None
        latest_id, latest_ver = _arxiv_version(aid_text)
        rec.update(
            {
                "ok": True,
                "title": title[:200] or None,
                "published": published,
                "updated": updated,
                "latest_version": latest_ver,
                "abs_url": abs_url(latest_id or arxiv_id, None),
            }
        )
        if cited_version and latest_ver and latest_ver > cited_version:
            rec["newer_than_cite"] = True
        upd = parse_date(updated)
        if last_verified and upd and upd > last_verified:
            rec["updated_after_verified"] = True
    except Exception as exc:
        rec["error"] = str(exc)[:160]
    return rec


def prioritize(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    arxiv = [c for c in citations if c.get("arxiv_id")]
    other = [c for c in citations if not c.get("arxiv_id")]
    return arxiv + other


def observe_entry(entry: dict[str, Any], criteria: dict[str, Any] | None = None) -> dict[str, Any]:
    policy = runtime_policy(criteria)
    fetch_budget = policy["budget"]["url_fetch"]
    arxiv_budget = policy["budget"]["arxiv_lookup"]
    body = markdown_body(entry)
    citations = extract_citations(body)
    ranked = prioritize(citations)
    fetches: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for i, cite in enumerate(ranked):
        if i >= fetch_budget:
            skipped.append({"url": cite["url"], "reason": "fetch_budget"})
            continue
        if i:
            time.sleep(0.35)
        fetches.append(url_fetch(cite["url"]))

    seen_ids: list[tuple[str, int | None]] = []
    for cite in ranked:
        aid = cite.get("arxiv_id")
        if not aid:
            continue
        key = (str(aid), cite.get("arxiv_version"))
        if key[0] not in {x[0] for x in seen_ids}:
            seen_ids.append((str(aid), cite.get("arxiv_version")))

    kn = entry.get("knowledge") or {}
    verified = parse_date(kn.get("last_verified") or entry.get("published_date"))
    arxiv: list[dict[str, Any]] = []
    for i, (aid, ver) in enumerate(seen_ids[:arxiv_budget]):
        if i:
            time.sleep(3.1)
        arxiv.append(arxiv_lookup(aid, ver, verified))
    for aid, ver in seen_ids[arxiv_budget:]:
        skipped.append({"url": abs_url(aid, ver), "reason": "arxiv_budget"})

    signals: list[dict[str, Any]] = []
    for f in fetches:
        if f.get("signal") == "gone":
            signals.append(
                {
                    "kind": "gone",
                    "tool": "url_fetch",
                    "url": f.get("url"),
                    "note": f"cited URL {f.get('status') or 'gone'}",
                    "observed_at": f.get("observed_at"),
                }
            )
    for a in arxiv:
        if not a.get("ok"):
            continue
        if a.get("newer_than_cite"):
            signals.append(
                {
                    "kind": "arxiv_newer",
                    "tool": "arxiv_lookup",
                    "url": a.get("abs_url") or a.get("url"),
                    "note": f"{a.get('arxiv_id')} cited v{a.get('cited_version')} now v{a.get('latest_version')}",
                    "observed_at": a.get("observed_at"),
                }
            )
        elif a.get("updated_after_verified"):
            signals.append(
                {
                    "kind": "arxiv_updated",
                    "tool": "arxiv_lookup",
                    "url": a.get("abs_url") or a.get("url"),
                    "note": f"{a.get('arxiv_id')} updated {a.get('updated')} after last_verified",
                    "observed_at": a.get("observed_at"),
                }
            )

    return {
        "observed_at": utc_now(),
        "tools": ["url_fetch", "arxiv_lookup"],
        "budget": policy["budget"],
        "used": {"url_fetch": len(fetches), "arxiv_lookup": len(arxiv)},
        "citations": citations,
        "fetches": fetches,
        "arxiv": arxiv,
        "skipped": skipped,
        "signals": signals,
    }


def observed_urls(observe: dict[str, Any]) -> set[str]:
    urls: set[str] = set()
    for key in ("citations", "fetches", "arxiv"):
        for row in observe.get(key) or []:
            if not isinstance(row, dict):
                continue
            for field in ("url", "final_url", "abs_url"):
                val = row.get(field)
                if isinstance(val, str) and val.startswith("https://"):
                    urls.add(val)
    for sig in observe.get("signals") or []:
        val = sig.get("url") if isinstance(sig, dict) else None
        if isinstance(val, str) and val.startswith("https://"):
            urls.add(val)
    return urls


def evidence_from_signals(observe: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for sig in observe.get("signals") or []:
        if not isinstance(sig, dict) or not str(sig.get("url") or "").startswith("https://"):
            continue
        out.append(
            {
                "url": sig["url"],
                "note": sig.get("note") or sig.get("kind") or "",
                "tool": sig.get("tool") or "url_fetch",
                "observed_at": sig.get("observed_at") or observe.get("observed_at"),
            }
        )
    return out


def judge_from_observe(observe: dict[str, Any], entry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Deterministic Judge. changed only when Observe has a signal."""
    citations = observe.get("citations") or []
    fetches = observe.get("fetches") or []
    arxiv = observe.get("arxiv") or []
    signals = observe.get("signals") or []
    tags = [str(t) for t in (entry or {}).get("tags") or []]
    philosophy = "Philosophy" in tags

    if not citations:
        return {
            "verdict": "insufficient",
            "note": "文内没有可复查的 https 引用，Observe 为空",
            "evidence": [],
            "proposed_change": "",
            "model": "observe",
        }

    if signals:
        kinds = {s.get("kind") for s in signals if isinstance(s, dict)}
        if "gone" in kinds:
            note = "已引用 URL 失效"
        elif "arxiv_newer" in kinds:
            note = "引用的 arXiv 论文已有更新版本"
        else:
            note = "引用的 arXiv 记录在 last_verified 之后有更新"
        return {
            "verdict": "changed",
            "note": note,
            "evidence": evidence_from_signals(observe),
            "proposed_change": "核对这些引用，决定改写、加注或归档；不要让报告直接改正文",
            "model": "observe",
        }

    fetch_errors = [f for f in fetches if f.get("signal") == "error"]
    arxiv_errors = [a for a in arxiv if not a.get("ok")]
    if fetches and len(fetch_errors) == len(fetches) and not any(f.get("ok") for f in fetches):
        return {
            "verdict": "insufficient",
            "note": "url_fetch 全部失败，无法观察",
            "evidence": [],
            "proposed_change": "",
            "model": "observe",
        }

    extra = ""
    if fetch_errors or arxiv_errors:
        extra = "；部分观察失败"
    if philosophy:
        return {
            "verdict": "insufficient",
            "note": "哲学/论题条目：引用仍在不等于主张过期" + extra,
            "evidence": [],
            "proposed_change": "",
            "model": "observe",
        }
    if any(a.get("ok") for a in arxiv):
        return {
            "verdict": "unchanged",
            "note": "已引用 URL 仍可访问，arXiv 记录无更新" + extra,
            "evidence": [],
            "proposed_change": "",
            "model": "observe",
        }
    return {
        "verdict": "insufficient",
        "note": "已引用 URL 仍可访问，但链接存活不能证明主张仍成立" + extra,
        "evidence": [],
        "proposed_change": "",
        "model": "observe",
    }


def constrain_to_observe(raw: dict[str, Any], observe: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    """Model may not invent URLs or emit changed/obsolete without an Observe signal."""
    allowed = observed_urls(observe)
    signals = observe.get("signals") or []
    evidence = []
    for e in raw.get("evidence") or []:
        if not isinstance(e, dict):
            continue
        url = str(e.get("url") or "").strip()
        if url in allowed:
            evidence.append(
                {
                    "url": url,
                    "note": e.get("note") or "",
                    "tool": e.get("tool") or "url_fetch",
                    "observed_at": e.get("observed_at") or observe.get("observed_at"),
                }
            )
    raw["evidence"] = evidence
    verdict = raw.get("verdict")
    if not (observe.get("citations") or []):
        raw["verdict"] = "insufficient"
        raw["note"] = "Observe 为空，不能判断"
        raw["evidence"] = []
        return raw
    if verdict in {"changed", "obsolete"} and not signals:
        raw["verdict"] = "insufficient"
        raw["note"] = (raw.get("note") or "") + "；无 Observe 信号，不能升为 changed/obsolete"
        raw["evidence"] = []
        return raw
    if verdict in {"changed", "obsolete"} and not evidence:
        raw["evidence"] = evidence_from_signals(observe) or fallback.get("evidence") or []
        if not raw["evidence"]:
            raw["verdict"] = "insufficient"
            raw["note"] = (raw.get("note") or "") + "；证据不在本轮 Observe 里"
    if raw.get("verdict") not in {"unchanged", "changed", "insufficient", "obsolete"}:
        raw.update(fallback)
    return raw
