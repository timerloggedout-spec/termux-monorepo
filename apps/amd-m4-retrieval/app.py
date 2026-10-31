#!/usr/bin/env python3
"""AMD AI League — Match 4 "Intelligent Web Information Retrieval" agent (P0 scaffold).

Pipeline: NL request => plan => navigate/fetch => extract => answer + source citations.

Contract (packet of record: PR #2543 => docs/ops/CHALLENGE-ENTRIES-LOG.md, C11):
  /app/app.py + /app/requirements.txt; run-as-is container; NO hardcoded answers
  (hidden tests score them zero); NO secrets in image or repo.

P0 properties:
  - stdlib only (urllib + html.parser) => requirements.txt carries no packages.
  - Planner is a replaceable module behind the Planner interface; the LLM hook
    (LLMPlanner) is stubbed and reads NO keys at P0.
  - Answers are composed ONLY from fetched page content, each passage cited.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urljoin
from urllib.request import Request, urlopen

USER_AGENT = "amd-m4-retrieval/0.1 (AMD AI League M4 agent; stdlib urllib)"
FETCH_TIMEOUT_S = 15
MAX_PAGES = 5  # navigation bound: keeps process time inside league limits


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    query: str
    urls: list[str] = field(default_factory=list)
    follow_pagination: bool = True


@dataclass
class PageContent:
    url: str
    title: str = ""
    blocks: list[str] = field(default_factory=list)          # prose passages
    tables: list[list[list[str]]] = field(default_factory=list)  # rows of cells
    next_url: str | None = None


@dataclass
class Citation:
    index: int
    url: str
    title: str = ""


@dataclass
class Answer:
    question: str
    answer: str
    citations: list[Citation] = field(default_factory=list)
    pages_fetched: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# planner — replaceable module; LLM hook stubbed behind the same interface
# ---------------------------------------------------------------------------

class Planner(ABC):
    """plan: NL request + optional seed URLs => Plan. Swap implementations
    via AMD_M4_PLANNER (heuristic | llm); the agent never changes."""

    @abstractmethod
    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        raise NotImplementedError


_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")


class HeuristicPlanner(Planner):
    """Deterministic P0 planner: URLs named in the request + caller seeds;
    everything else is left to navigation (pagination links)."""

    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        found = _URL_RE.findall(request or "")
        seeds = list(urls or []) + [u for u in found if u not in (urls or [])]
        return Plan(query=request, urls=seeds, follow_pagination=True)


class LLMPlanner(Planner):
    """P1 hook — NOT implemented at P0.

    Intended shape: an open-source model (served locally, weights in /models)
    turns the NL request into seed URLs + a search strategy. P0 ships no model
    and reads no API keys; any future credential would be injected at runtime
    via environment, never baked into the image or repo (contract, PR #2543).
    """

    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        raise NotImplementedError("LLMPlanner lands in P1; use HeuristicPlanner at P0")


def make_planner(name: str | None = None) -> Planner:
    name = (name or os.environ.get("AMD_M4_PLANNER", "heuristic")).lower()
    if name == "llm":
        return LLMPlanner()
    return HeuristicPlanner()


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------

def fetch(url: str, timeout: int = FETCH_TIMEOUT_S) -> str:
    """GET a public page => decoded HTML text. No credentials, ever."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310 (public pages only)
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

_SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
_BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class _Extractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.skip_depth = 0
        self.title = ""
        self._in_title = False
        self.blocks: list[str] = []
        self._block_buf: list[str] | None = None
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.next_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if tag in _SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self._in_title = True
        elif tag in _BLOCK_TAGS:
            self._block_buf = []
        elif tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []
        elif tag == "link" and (attr.get("rel") or "").lower() == "next" and attr.get("href"):
            self.next_url = urljoin(self.base_url, attr["href"])
        elif tag == "a" and attr.get("href"):
            rel = (attr.get("rel") or "").lower()
            if rel == "next":
                self.next_url = urljoin(self.base_url, attr["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "title":
            self._in_title = False
        elif tag in _BLOCK_TAGS and self._block_buf is not None:
            text = _clean(" ".join(self._block_buf))
            if text:
                self.blocks.append(text)
            self._block_buf = None
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(_clean(" ".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            if self._table:
                self.tables.append(self._table)
            self._table = None
        elif tag == "a":
            pass

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self._in_title:
            self.title += data
        if self._cell is not None:
            self._cell.append(data)
        elif self._block_buf is not None:
            self._block_buf.append(data)

    # anchor text "Next" as pagination fallback, checked post-parse in extract()


def extract(html_text: str, url: str) -> PageContent:
    parser = _Extractor(url)
    parser.feed(html_text)
    next_url = parser.next_url
    if next_url is None:
        # fallback: an <a> whose visible text is exactly "next" (any case)
        m = re.search(
            r'<a[^>]+href="([^"]+)"[^>]*>\s*next\s*</a>', html_text, re.IGNORECASE
        )
        if m:
            next_url = urljoin(url, m.group(1))
    return PageContent(
        url=url,
        title=_clean(parser.title),
        blocks=parser.blocks,
        tables=parser.tables,
        next_url=next_url,
    )


# ---------------------------------------------------------------------------
# answer — passages ranked by term overlap; every passage cited; no invention
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "when", "where",
    "which", "who", "how", "much", "many", "does", "do", "did", "can", "could",
    "i", "me", "my", "you", "your", "it", "its", "of", "on", "in", "at", "to",
    "for", "and", "or", "with", "from", "by", "be", "been", "please", "tell",
}


def _terms(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS}


def _passages(page: PageContent) -> list[str]:
    out = list(page.blocks)
    for table in page.tables:
        for row in table:
            out.append(" — ".join(c for c in row if c))
    return out


def compose_answer(question: str, pages: list[PageContent]) -> Answer:
    citations: list[Citation] = []
    for i, page in enumerate(pages, start=1):
        citations.append(Citation(index=i, url=page.url, title=page.title))
    if not pages:
        return Answer(
            question=question,
            answer="No sources could be retrieved for this request, so no "
                   "answer can be given with citations.",
            citations=[],
            pages_fetched=[],
        )
    q = _terms(_URL_RE.sub(" ", question))  # URLs are navigation, not content terms
    scored: list[tuple[int, int, str]] = []  # (overlap, page_idx, passage)
    for idx, page in enumerate(pages):
        for passage in _passages(page):
            overlap = len(q & _terms(passage))
            if overlap:
                scored.append((overlap, idx, passage))
    scored.sort(key=lambda s: (-s[0], s[1]))
    top = scored[:3]
    if not top:
        lines = [
            "The retrieved sources did not contain a passage matching this "
            "request. Sources consulted:"
        ]
        lines += [f"[{c.index}] {c.title or c.url} — {c.url}" for c in citations]
        return Answer(question, "\n".join(lines), citations, [p.url for p in pages])
    parts = [f"{passage} [{idx + 1}]" for _, idx, passage in top]
    return Answer(
        question=question,
        answer=" ".join(parts),
        citations=citations,
        pages_fetched=[p.url for p in pages],
    )


# ---------------------------------------------------------------------------
# agent
# ---------------------------------------------------------------------------

class RetrievalAgent:
    """plan => fetch/navigate (bounded, pagination-aware) => extract => answer."""

    def __init__(self, planner: Planner | None = None, fetcher=fetch) -> None:
        self.planner = planner or make_planner()
        self.fetcher = fetcher

    def run(self, request: str, urls: list[str] | None = None) -> Answer:
        plan = self.planner.plan(request, urls)
        queue = list(plan.urls)
        seen: set[str] = set()
        pages: list[PageContent] = []
        while queue and len(pages) < MAX_PAGES:
            url = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                html_text = self.fetcher(url)
            except Exception:
                continue  # unreachable source: skip, never fabricate
            page = extract(html_text, url)
            pages.append(page)
            if plan.follow_pagination and page.next_url and page.next_url not in seen:
                queue.append(page.next_url)
        return compose_answer(request, pages)


# ---------------------------------------------------------------------------
# service + CLI
# ---------------------------------------------------------------------------

def _make_handler(agent: RetrievalAgent):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep stdout clean
            pass

        def _json(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802 (stdlib naming)
            if self.path == "/health":
                self._json(200, {"ok": True, "service": "amd-m4-retrieval"})
            else:
                self._json(200, {"service": "amd-m4-retrieval",
                                 "usage": "POST /ask {request, urls[]}"})

        def do_POST(self):  # noqa: N802
            if self.path != "/ask":
                self._json(404, {"error": "unknown path"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(length) or b"{}")
                answer = agent.run(payload.get("request", ""),
                                   payload.get("urls") or [])
                self._json(200, answer.to_dict())
            except Exception as exc:  # surface, never crash the service
                self._json(400, {"error": str(exc)})

    return Handler


def serve(port: int) -> None:
    HTTPServer(("0.0.0.0", port), _make_handler(RetrievalAgent())).serve_forever()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AMD M4 web information retrieval agent")
    ap.add_argument("request", nargs="?", help="natural-language request")
    ap.add_argument("--url", action="append", default=[], help="seed URL (repeatable)")
    ap.add_argument("--planner", default=None, help="heuristic (default) | llm (P1 stub)")
    ap.add_argument("--serve", action="store_true", help="run the HTTP service")
    ap.add_argument("--port", type=int, default=8080)
    ns = ap.parse_args(argv)
    if ns.serve:
        serve(ns.port)
        return 0
    if not ns.request:
        ap.error("a request is required unless --serve is given")
    agent = RetrievalAgent(planner=make_planner(ns.planner))
    print(json.dumps(agent.run(ns.request, ns.url).to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
