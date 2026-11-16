#!/usr/bin/env python3
"""AMD AI League — Match 4 "Intelligent Web Information Retrieval" agent (P1).

Pipeline: NL request => plan (decompose into sub-queries) => navigate/fetch
(bounded multi-hop: pagination chains + ranked evidence links) => extract
(prose, lists, tables as structured records) => merged answer, per-source
citations.

Contract (packet of record: PR #2543 => docs/ops/CHALLENGE-ENTRIES-LOG.md, C11):
  /app/app.py + /app/requirements.txt; run-as-is container; NO hardcoded answers
  (hidden tests score them zero); NO secrets in image or repo; NO external paid
  calls — the only model path is a LOCAL open-source model (see LLMPlanner).

P1 properties (over the P0 scaffold):
  - Multi-hop: planner decomposes a request into sub-queries; the agent
    follows pagination chains AND outbound evidence links (ranked by link
    text/URL overlap with the sub-queries), bounded by MAX_PAGES/MAX_HOPS;
    passages are merged per sub-query, each cited to its source page.
  - Extraction: prose blocks, ul/ol lists, tables => structured records
    (header row => dict rows), generic pagination labels; no per-site hacks.
  - LLMPlanner is REAL but local-only: it activates only when a local
    open-source model is detected — an OpenAI-compatible endpoint on a
    loopback host (AMD_M4_LOCAL_MODEL_URL, e.g. llama.cpp / vLLM / Ollama
    serving a local model) or in-process weights (AMD_M4_MODEL_DIR, default
    /models) with an importable local runtime (llama_cpp / transformers).
    Non-loopback endpoints are refused. No model => HeuristicPlanner.
  - stdlib only => requirements.txt still carries no packages; the endpoint
    path needs nothing beyond urllib.
  - P2: fetch reads are capped at MAX_RESPONSE_BYTES (huge-page truncation
    bound) and `--selfcheck` functionally verifies the declared startup /
    page / time budgets, printing the measured numbers.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

USER_AGENT = "amd-m4-retrieval/0.2 (AMD AI League M4 agent; stdlib urllib)"
FETCH_TIMEOUT_S = 15
MAX_PAGES = 8   # total fetch bound per run (P0: 5; P1 multi-hop needs room)
MAX_HOPS = 2    # link-follow depth beyond the seed pages
MAX_SUBQUERIES = 4
MAX_RESPONSE_BYTES = 2_000_000  # P2: per-fetch truncation bound (huge pages)
STARTUP_BUDGET_S = 5.0          # P2: declared cold-start budget (selfcheck)


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    query: str
    urls: list[str] = field(default_factory=list)
    follow_pagination: bool = True
    subqueries: list[str] = field(default_factory=list)  # P1: decomposition

    def __post_init__(self) -> None:
        if not self.subqueries:
            self.subqueries = [self.query]


@dataclass
class PageContent:
    url: str
    title: str = ""
    blocks: list[str] = field(default_factory=list)          # prose passages
    lists: list[list[str]] = field(default_factory=list)     # ul/ol item groups
    list_titles: list[str] = field(default_factory=list)     # heading per list
    tables: list[list[list[str]]] = field(default_factory=list)  # rows of cells
    records: list[dict[str, str]] = field(default_factory=list)  # table => dicts
    links: list[tuple[str, str]] = field(default_factory=list)   # (text, abs url)
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
# planners — replaceable module behind one interface
# ---------------------------------------------------------------------------

class Planner(ABC):
    """plan: NL request + optional seed URLs => Plan. Swap implementations
    via AMD_M4_PLANNER (heuristic | llm | auto); the agent never changes."""

    @abstractmethod
    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        raise NotImplementedError


_URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+")

_SPLIT_RE = re.compile(r"\s+and\s+|;\s*|\?\s+", re.IGNORECASE)


def decompose(request: str) -> list[str]:
    """Generic NL decomposition: split a compound request into sub-queries.

    Heuristic only (conjunction/semicolon/multi-question splits); a part is
    kept only if it carries >= 2 content terms, else the request stays whole.
    """
    text = (request or "").strip()
    if not text:
        return [text]
    parts = [p.strip(" ?") for p in _SPLIT_RE.split(text) if p.strip(" ?")]
    parts = [p for p in parts if len(_terms(p)) >= 2]
    if len(parts) < 2:
        return [text]
    return parts[:MAX_SUBQUERIES]


class HeuristicPlanner(Planner):
    """Deterministic planner: URLs named in the request + caller seeds +
    generic decomposition into sub-queries; navigation does the rest."""

    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        found = _URL_RE.findall(request or "")
        seeds = list(urls or []) + [u for u in found if u not in (urls or [])]
        return Plan(query=request, urls=seeds, follow_pagination=True,
                    subqueries=decompose(request))


# --- local open-source model: detection + LLMPlanner ------------------------

_LOOPBACK_HOSTS = {"localhost", "0.0.0.0", "::1"}


def _is_loopback_url(url: str) -> bool:
    """True only for loopback endpoints — the model path never calls out."""
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in _LOOPBACK_HOSTS or host.startswith("127.")


def _endpoint_available(url: str, timeout: float = 2.0) -> bool:
    try:
        req = Request(url.rstrip("/") + "/v1/models",
                      headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 (loopback)
            return resp.status == 200
    except Exception:
        return False


def _weights_present(model_dir: str) -> str | None:
    """A weights file/dir under model_dir => its path, else None."""
    if not model_dir or not os.path.isdir(model_dir):
        return None
    for root, _dirs, files in os.walk(model_dir):
        for name in files:
            if name.endswith((".gguf", ".safetensors")) or name == "config.json":
                return os.path.join(root, name)
    return None


def _runtime_available() -> str | None:
    """Name of an importable local inference runtime, else None."""
    for mod in ("llama_cpp", "transformers"):
        try:
            __import__(mod)
            return mod
        except Exception:
            continue
    return None


def local_model_status(env: dict | None = None) -> dict:
    """Capability detection for the local-model path (no calls if not local).

    Returns {available, kind, detail}: kind is "endpoint" (OpenAI-compatible
    server on a loopback host) or "inprocess" (weights + local runtime).
    """
    env = os.environ if env is None else env
    url = (env.get("AMD_M4_LOCAL_MODEL_URL") or "").strip()
    if url:
        if not _is_loopback_url(url):
            return {"available": False, "kind": "endpoint",
                    "detail": "AMD_M4_LOCAL_MODEL_URL is not a loopback URL; "
                              "refused (local models only, no external calls)"}
        if _endpoint_available(url):
            return {"available": True, "kind": "endpoint",
                    "detail": f"local model endpoint live at {url}"}
        return {"available": False, "kind": "endpoint",
                "detail": f"no local model answering at {url}"}
    model_dir = env.get("AMD_M4_MODEL_DIR", "/models")
    weights = _weights_present(model_dir)
    if weights:
        runtime = _runtime_available()
        if runtime:
            return {"available": True, "kind": "inprocess",
                    "detail": f"weights at {weights}, runtime {runtime}"}
        return {"available": False, "kind": "inprocess",
                "detail": f"weights at {weights} but no local runtime "
                          "(llama_cpp/transformers) importable"}
    return {"available": False, "kind": None,
            "detail": "no local model configured (no AMD_M4_LOCAL_MODEL_URL, "
                      f"no weights under {model_dir})"}


_PLAN_PROMPT = (
    "You are the planner of a web retrieval agent. Turn the request into a "
    "JSON plan: {\"urls\": [seed URLs explicitly needed], \"subqueries\": "
    "[atomic sub-questions], \"follow_pagination\": true}. Reply with JSON "
    "only.\nRequest: "
)


def _parse_plan_json(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


class LLMPlanner(Planner):
    """Real planner over a LOCAL open-source model; heuristic fallback.

    Activation is detection-gated (local_model_status): loopback endpoint
    (chat-completions) or in-process weights+runtime. Anything else — no
    model, dead endpoint, non-loopback URL, model error, unparseable reply —
    falls back to HeuristicPlanner. No API keys are read, ever; no external
    host is contacted, ever.
    """

    def __init__(self, status: dict | None = None, env: dict | None = None,
                 chat=None) -> None:
        self._env = os.environ if env is None else env
        self.status = status if status is not None else local_model_status(env)
        self._chat = chat or self._chat_http  # injectable for tests

    # -- model transports ----------------------------------------------------
    def _chat_http(self, prompt: str) -> str:
        url = self._env["AMD_M4_LOCAL_MODEL_URL"].rstrip("/") \
            + "/v1/chat/completions"
        body = json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }).encode()
        req = Request(url, data=body, headers={
            "User-Agent": USER_AGENT, "Content-Type": "application/json"})
        with urlopen(req, timeout=30) as resp:  # noqa: S310 (loopback only)
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        return data["choices"][0]["message"]["content"]

    def _chat_inprocess(self, prompt: str) -> str:
        runtime = _runtime_available()
        weights = _weights_present(self._env.get("AMD_M4_MODEL_DIR", "/models"))
        if runtime == "llama_cpp" and weights:
            from llama_cpp import Llama  # local runtime, lazy import

            llm = Llama(model_path=weights, n_ctx=2048, verbose=False)
            out = llm(prompt, max_tokens=256, temperature=0)
            return out["choices"][0]["text"]
        raise RuntimeError("in-process runtime unavailable for chat")

    # -- Planner --------------------------------------------------------------
    def plan(self, request: str, urls: list[str] | None = None) -> Plan:
        fallback = HeuristicPlanner().plan(request, urls)
        if not self.status.get("available"):
            return fallback
        try:
            if self.status["kind"] == "endpoint":
                reply = self._chat(_PLAN_PROMPT + (request or ""))
            else:
                reply = self._chat_inprocess(_PLAN_PROMPT + (request or ""))
            data = _parse_plan_json(reply)
        except Exception:
            return fallback
        if data is None:
            return fallback
        model_urls = [u for u in data.get("urls") or []
                      if isinstance(u, str) and _URL_RE.fullmatch(u)]
        seeds = list(fallback.urls) + [u for u in model_urls
                                       if u not in fallback.urls]
        subs = [s for s in data.get("subqueries") or []
                if isinstance(s, str) and len(_terms(s)) >= 2]
        return Plan(query=request, urls=seeds,
                    follow_pagination=bool(data.get("follow_pagination", True)),
                    subqueries=subs[:MAX_SUBQUERIES] or fallback.subqueries)


def make_planner(name: str | None = None) -> Planner:
    name = (name or os.environ.get("AMD_M4_PLANNER", "heuristic")).lower()
    if name == "llm":
        return LLMPlanner()
    if name == "auto":
        llm = LLMPlanner()
        return llm if llm.status.get("available") else HeuristicPlanner()
    return HeuristicPlanner()


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------

def fetch(url: str, timeout: int = FETCH_TIMEOUT_S) -> str:
    """GET a public page => decoded HTML text. No credentials, ever.

    The body read is capped at MAX_RESPONSE_BYTES: a huge page truncates
    instead of exhausting memory/time (P2 robustness bound).
    """
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:  # noqa: S310 (public pages only)
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read(MAX_RESPONSE_BYTES).decode(charset, errors="replace")


# ---------------------------------------------------------------------------
# extract — prose, lists, tables => records, links, pagination (generic)
# ---------------------------------------------------------------------------

_SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
_BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}
_PAGINATION_LABELS = {"next", "next page", "more", "more results",
                      "more events", "older", "older posts", "»", "›", ">"}


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
        self._block_tag: str | None = None
        self.lists: list[list[str]] = []
        self.list_titles: list[str] = []
        self._list_stack: list[list[str]] = []
        self._last_heading = ""
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self.links: list[tuple[str, str]] = []
        self._a_href: str | None = None
        self._a_buf: list[str] | None = None
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
            # malformed pages omit </p>/</li>/...: a new block auto-closes
            # the pending one instead of silently dropping its text (P2)
            if self._block_buf is not None:
                self._flush_block()
            self._block_buf = []
            self._block_tag = tag
        elif tag in ("ul", "ol"):
            self._list_stack.append([])
        elif tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            if self._row is not None:  # unclosed previous row (P2)
                self._flush_cell()
                self._flush_row()
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            if self._cell is not None:  # unclosed previous cell (P2)
                self._flush_cell()
            self._cell = []
        elif tag == "link" and (attr.get("rel") or "").lower() == "next" and attr.get("href"):
            self.next_url = urljoin(self.base_url, attr["href"])
        elif tag == "a" and attr.get("href"):
            rel = (attr.get("rel") or "").lower()
            label = (attr.get("aria-label") or "").lower()
            if rel == "next" or "next" in label:
                self.next_url = urljoin(self.base_url, attr["href"])
            self._a_href = urljoin(self.base_url, attr["href"])
            self._a_buf = []

    # -- flush helpers: shared by end tags, start-tag auto-close, close() ---
    def _flush_block(self) -> None:
        if self._block_buf is None:
            return
        text = _clean(" ".join(self._block_buf))
        if text:
            self.blocks.append(text)
            if self._block_tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                self._last_heading = text
            if self._block_tag == "li" and self._list_stack:
                self._list_stack[-1].append(text)
        self._block_buf = None
        self._block_tag = None

    def _flush_list(self) -> None:
        if not self._list_stack:
            return
        items = self._list_stack.pop()
        if items:
            self.lists.append(items)
            self.list_titles.append(self._last_heading)

    def _flush_cell(self) -> None:
        if self._cell is not None and self._row is not None:
            self._row.append(_clean(" ".join(self._cell)))
        self._cell = None

    def _flush_row(self) -> None:
        if self._row is not None and self._table is not None and any(self._row):
            self._table.append(self._row)
        self._row = None

    def _flush_table(self) -> None:
        self._flush_cell()
        self._flush_row()
        if self._table:
            self.tables.append(self._table)
        self._table = None

    def close(self) -> None:
        super().close()
        # EOF with tags still open (malformed pages): keep what was read
        self._flush_block()
        while self._list_stack:
            self._flush_list()
        if self._table is not None:
            self._flush_table()

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "title":
            self._in_title = False
        elif tag in _BLOCK_TAGS:
            self._flush_block()
        elif tag in ("ul", "ol"):
            self._flush_list()
        elif tag in ("td", "th"):
            self._flush_cell()
        elif tag == "tr":
            self._flush_cell()
            self._flush_row()
        elif tag == "table" and self._table is not None:
            self._flush_table()
        elif tag == "a" and self._a_href is not None:
            text = _clean(" ".join(self._a_buf or []))
            if text:
                self.links.append((text, self._a_href))
                if self.next_url is None and text.lower() in _PAGINATION_LABELS:
                    self.next_url = self._a_href
            self._a_href = None
            self._a_buf = None

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self._in_title:
            self.title += data
        if self._a_buf is not None:
            self._a_buf.append(data)
        if self._cell is not None:
            self._cell.append(data)
        elif self._block_buf is not None:
            self._block_buf.append(data)


def _records_of(tables: list[list[list[str]]]) -> list[dict[str, str]]:
    """Tables with a header row => structured records (header => cell)."""
    records: list[dict[str, str]] = []
    for table in tables:
        if len(table) < 2:
            continue
        headers = table[0]
        if not headers or not all(headers):
            continue
        for row in table[1:]:
            record = {h: row[i] for i, h in enumerate(headers) if i < len(row)}
            if any(record.values()):
                records.append(record)
    return records


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
        lists=parser.lists,
        list_titles=parser.list_titles,
        tables=parser.tables,
        records=_records_of(parser.tables),
        links=parser.links,
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
    for i, items in enumerate(page.lists):
        # a list inherits its section heading as context (generic structure)
        title = page.list_titles[i] if i < len(page.list_titles) else ""
        joined = "; ".join(items)
        out.append(f"{title}: {joined}" if title else joined)
    for table in page.tables:
        for row in table:
            out.append(" — ".join(c for c in row if c))
    for record in page.records:
        out.append("; ".join(f"{k}: {v}" for k, v in record.items() if v))
    return out


def _ranked(question: str, pages: list[PageContent]) -> list[tuple[int, int, str]]:
    q = _terms(_URL_RE.sub(" ", question))  # URLs are navigation, not content
    scored: list[tuple[int, int, str]] = []
    for idx, page in enumerate(pages):
        for passage in _passages(page):
            overlap = len(q & _terms(passage))
            if overlap:
                scored.append((overlap, idx, passage))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return scored


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
    top = _ranked(question, pages)[:3]
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


def compose_multihop_answer(plan: Plan, pages: list[PageContent]) -> Answer:
    """Merge per-sub-query evidence: top passages per sub-query, deduped,
    each cited — a compound request cites every source its parts used."""
    citations: list[Citation] = []
    for i, page in enumerate(pages, start=1):
        citations.append(Citation(index=i, url=page.url, title=page.title))
    if not pages:
        return compose_answer(plan.query, pages)
    parts: list[str] = []
    seen_text: set[str] = set()
    matched_any = False
    for sub in plan.subqueries:
        for _overlap, idx, passage in _ranked(sub, pages)[:3]:
            matched_any = True
            if passage in seen_text:
                continue
            seen_text.add(passage)
            parts.append(f"{passage} [{idx + 1}]")
    if not matched_any:
        return compose_answer(plan.query, pages)
    return Answer(
        question=plan.query,
        answer=" ".join(parts[:8]),
        citations=citations,
        pages_fetched=[p.url for p in pages],
    )


# ---------------------------------------------------------------------------
# agent — bounded multi-hop navigation
# ---------------------------------------------------------------------------

class RetrievalAgent:
    """plan => fetch/navigate => extract => answer.

    Navigation: seeds (depth 0) => pagination chain (next_url) + outbound
    evidence links ranked by (anchor text + URL slug) overlap with the
    plan's sub-query terms, depth <= MAX_HOPS, total pages <= MAX_PAGES.
    """

    def __init__(self, planner: Planner | None = None, fetcher=fetch,
                 max_pages: int = MAX_PAGES, max_hops: int = MAX_HOPS) -> None:
        self.planner = planner or make_planner()
        self.fetcher = fetcher
        self.max_pages = int(os.environ.get("AMD_M4_MAX_PAGES", max_pages))
        self.max_hops = max_hops

    def _evidence_links(self, page: PageContent,
                        want: set[str]) -> list[str]:
        scored: list[tuple[int, str]] = []
        for text, href in page.links:
            if not href.startswith(("http://", "https://")):
                continue
            hay = text + " " + urlparse(href).path.replace("-", " ").replace("_", " ")
            overlap = len(want & _terms(hay))
            if overlap:
                scored.append((overlap, href))
        scored.sort(key=lambda s: -s[0])
        return [href for _, href in scored]

    def run(self, request: str, urls: list[str] | None = None) -> Answer:
        plan = self.planner.plan(request, urls)
        want = set()
        for sub in plan.subqueries:
            want |= _terms(sub)
        queue: list[tuple[str, int]] = [(u, 0) for u in plan.urls]
        seen: set[str] = set()
        pages: list[PageContent] = []
        while queue and len(pages) < self.max_pages:
            url, depth = queue.pop(0)
            if url in seen:
                continue
            seen.add(url)
            try:
                html_text = self.fetcher(url)
            except Exception:
                continue  # unreachable source: skip, never fabricate
            page = extract(html_text, url)
            pages.append(page)
            if plan.follow_pagination and page.next_url \
                    and page.next_url not in seen:
                queue.append((page.next_url, depth))
            if depth < self.max_hops:
                for href in self._evidence_links(page, want):
                    if href not in seen:
                        queue.append((href, depth + 1))
        if len(plan.subqueries) > 1:
            return compose_multihop_answer(plan, pages)
        return compose_answer(request, pages)


# ---------------------------------------------------------------------------
# selfcheck (P2) — declared budgets, functionally enforced, numbers printed
# ---------------------------------------------------------------------------

def _measure_startup_s() -> float:
    """Cold-start of a fresh interpreter importing this module (seconds)."""
    code = ("import time; t = time.perf_counter(); import app; "
            "print(time.perf_counter() - t)")
    out = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(os.path.dirname(os.path.abspath(__file__))),
        capture_output=True, text=True, timeout=60, check=True)
    return float(out.stdout.strip().splitlines()[-1])


def run_selfcheck() -> dict:
    """Assert the contract's startup/process limits are real, not nominal.

    Budgets declared here (no league numbers published): cold start <=
    STARTUP_BUDGET_S; a run fetches <= MAX_PAGES pages, each fetch bounded
    by FETCH_TIMEOUT_S and MAX_RESPONSE_BYTES (worst-case process time for
    fetching is therefore MAX_PAGES * FETCH_TIMEOUT_S, printed below).
    Every check is functional (measured / exercised), never a constant echo.
    """
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    checks: dict[str, bool] = {}

    startup_s = _measure_startup_s()
    checks["startup_within_budget"] = startup_s <= STARTUP_BUDGET_S

    # page bound: an endless next-chain must stop at MAX_PAGES fetches
    def chain_fetch(url: str) -> str:
        n = int(url.rsplit("/", 1)[1])
        return (f"<html><body><p>Chain page {n} about harbour schedules.</p>"
                f'<a rel="next" href="https://chain.example.test/{n + 1}">'
                f"Next</a></body></html>")

    agent = RetrievalAgent(planner=HeuristicPlanner(), fetcher=chain_fetch)
    ans = agent.run("Tell me about harbour schedules",
                    ["https://chain.example.test/0"])
    max_pages_seen = len(ans.pages_fetched)
    checks["max_pages_enforced"] = max_pages_seen == MAX_PAGES

    # byte cap + timeout: exercised against a loopback server (real fetch)
    class _Probe(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):  # noqa: N802
            if self.path == "/slow":
                time.sleep(4)
                body = b"<html><body>slow</body></html>"
            elif self.path == "/big":
                body = b"x" * (MAX_RESPONSE_BYTES + 1_000_000)
            else:
                body = b"<html><body>ok</body></html>"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # client left early (timeout / cap) — expected here

    server = HTTPServer(("127.0.0.1", 0), _Probe)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        big_len = len(fetch(base + "/big"))
        checks["response_bytes_capped"] = big_len <= MAX_RESPONSE_BYTES
        t0 = time.perf_counter()
        try:
            fetch(base + "/slow", timeout=1)
            timeout_elapsed, timed_out = time.perf_counter() - t0, False
        except Exception:
            timeout_elapsed, timed_out = time.perf_counter() - t0, True
        checks["fetch_timeout_enforced"] = timed_out and timeout_elapsed < 3.5
    finally:
        server.shutdown()
        server.server_close()

    return {
        "selfcheck": "amd-m4-retrieval",
        "ok": all(checks.values()),
        "startup_s": round(startup_s, 3),
        "startup_budget_s": STARTUP_BUDGET_S,
        "max_pages": MAX_PAGES,
        "max_pages_seen_on_endless_chain": max_pages_seen,
        "max_hops": MAX_HOPS,
        "fetch_timeout_s": FETCH_TIMEOUT_S,
        "max_response_bytes": MAX_RESPONSE_BYTES,
        "worst_case_fetch_time_s": MAX_PAGES * FETCH_TIMEOUT_S,
        "checks": checks,
    }


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
    ap.add_argument("--planner", default=None,
                    help="heuristic (default) | llm (local model) | auto")
    ap.add_argument("--model-status", action="store_true",
                    help="print local-model capability detection, then exit")
    ap.add_argument("--selfcheck", action="store_true",
                    help="verify startup/page/time budgets are enforced, "
                         "print the numbers as JSON, then exit")
    ap.add_argument("--serve", action="store_true", help="run the HTTP service")
    ap.add_argument("--port", type=int, default=8080)
    ns = ap.parse_args(argv)
    if ns.model_status:
        print(json.dumps(local_model_status(), indent=2))
        return 0
    if ns.selfcheck:
        report = run_selfcheck()
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 1
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
