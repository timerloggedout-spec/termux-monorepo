#!/usr/bin/env python3
"""Discover public Devpost hackathon directory leads into a review-only repo feed.

This is discovery, not admission: it never edits coordinator.json, registers,
submits, or creates wagering-book subjects. Every lead remains unverified
until its event page and rules are independently checked.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import URLError
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

SOURCES = (
    "https://devpost.com/hackathons",
    "https://devpost.com/c/artificial-intelligence",
)
SCHEMA = "devpost-directory-discovery/v1"
AI_TERMS = ("ai", "artificial intelligence", "machine learning", "llm", "agent", "generative", "robot", "data science")
OTHER_TERMS = ("hackathon", "challenge", "build", "developer", "open source")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_event_url(raw: str, base: str) -> str | None:
    absolute = urljoin(base, raw.strip())
    p = urlparse(absolute)
    host = (p.hostname or "").lower()
    if p.scheme not in ("http", "https") or not host.endswith(".devpost.com"):
        return None
    if host in ("www.devpost.com", "devpost.com") or host.count(".") < 2:
        return None
    return urlunparse(("https", host, "/", "", "", ""))


class DirectoryParser(HTMLParser):
    def __init__(self, base: str):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.links: list[dict] = []
        self.current: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        a = dict(attrs)
        href = a.get("href") or ""
        url = canonical_event_url(href, self.base)
        if url:
            self.current = {"url": url, "title_parts": [], "aria": a.get("aria-label") or a.get("title") or ""}

    def handle_data(self, data: str) -> None:
        if self.current is not None and data.strip():
            self.current["title_parts"].append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current is not None:
            title = " ".join(self.current["title_parts"]).strip() or self.current["aria"]
            title = re.sub(r"\\s+", " ", title).strip()
            self.links.append({"url": self.current["url"], "title": title})
            self.current = None


def parse_directory(html_text: str, source_url: str) -> list[dict]:
    parser = DirectoryParser(source_url)
    parser.feed(html_text)
    found: dict[str, dict] = {}
    for item in parser.links:
        url = item["url"]
        title = item["title"] or urlparse(url).hostname.split(".")[0].replace("-", " ").title()
        if url not in found or (len(title) > len(found[url]["title"])):
            found[url] = {"url": url, "title": title}
    return list(found.values())


def triage_score(title: str) -> tuple[int, list[str]]:
    text = title.lower()
    matched = [term for term in AI_TERMS if term in text]
    score = min(100, len(matched) * 22 + (12 if any(t in text for t in OTHER_TERMS) else 0))
    return score, matched


def fetch_page(url: str) -> str:
    req = Request(url, headers={"User-Agent": "termux-monorepo-devpost-discovery/1.0 (+https://github.com/timerloggedout-spec/termux-monorepo)"})
    with urlopen(req, timeout=35) as response:
        return response.read().decode("utf-8", "replace")


def known_urls(root: Path) -> dict[str, str]:
    path = root / "ops/challenge/coordinator.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    known: dict[str, str] = {}
    for group in ("events", "candidate_events"):
        for record in data.get(group, []):
            url = record.get("official_url")
            if url:
                canonical = canonical_event_url(url, url)
                if canonical:
                    known[canonical] = record.get("id", "known")
    return known


def collect(root: Path, pages: dict[str, str], fetched_at: str) -> dict:
    out_path = root / "ops/challenge/discovery/devpost-directory.json"
    old = json.loads(out_path.read_text()) if out_path.exists() else {"schema": SCHEMA, "leads": [], "runs": []}
    by_url = {x["url"]: x for x in old.get("leads", []) if x.get("url")}
    known = known_urls(root)
    run_sources = []
    fresh: dict[str, dict] = {}
    for source_url, html_text in pages.items():
        run_sources.append({"url": source_url, "fetched_at": fetched_at, "status": "ok", "sha256": __import__("hashlib").sha256(html_text.encode()).hexdigest()})
        for item in parse_directory(html_text, source_url):
            url = item["url"]
            score, terms = triage_score(item["title"])
            row = fresh.setdefault(url, {
                "url": url, "title": item["title"], "first_seen": fetched_at,
                "last_seen": fetched_at, "discovery_sources": [],
                "verification_state": "UNVERIFIED_LEAD",
                "eligibility_state": "NOT_ESTABLISHED",
                "triage_score": score, "triage_basis": "title-keyword heuristic only; not an opportunity probability",
                "matched_terms": terms, "known_record_id": known.get(url),
            })
            row["last_seen"] = fetched_at
            if source_url not in row["discovery_sources"]:
                row["discovery_sources"].append(source_url)
    for url, row in fresh.items():
        prior = by_url.get(url)
        if prior:
            row["first_seen"] = prior.get("first_seen", fetched_at)
            row["discovery_sources"] = sorted(set(prior.get("discovery_sources", []) + row["discovery_sources"]))
            # Preserve human review state; discovery never promotes a lead.
            for field in ("verification_state", "eligibility_state", "review_note", "known_record_id"):
                if prior.get(field) is not None:
                    row[field] = prior[field]
        by_url[url] = row
    leads = sorted(by_url.values(), key=lambda x: (-int(x.get("triage_score", 0)), x.get("title", "").lower(), x["url"]))
    run = {"fetched_at": fetched_at, "sources": run_sources, "discovered_this_run": len(fresh), "total_leads": len(leads)}
    old["schema"] = SCHEMA
    old["generated_at"] = fetched_at
    old["source_policy"] = "Public directory listings are leads only; event rules, dates, eligibility and prizes require official-page verification."
    old["alternatives"] = [
        {"name": "lablab.ai", "state": "source-listed-not-crawled-by-this-collector"},
        {"name": "MLH", "state": "source-listed-not-crawled-by-this-collector"},
        {"name": "HackerEarth", "state": "source-listed-not-crawled-by-this-collector"},
        {"name": "Devfolio", "state": "source-listed-not-crawled-by-this-collector"},
        {"name": "Sponsor and organizer program pages", "state": "source-listed-not-crawled-by-this-collector"},
    ]
    old["leads"] = leads
    old.setdefault("runs", []).append(run)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n")
    return run


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--no-fetch", action="store_true", help="write an empty-safe run using supplied existing feed only")
    ap.add_argument("--fixture", action="append", default=[], metavar="URL=PATH", help="offline HTML fixture for a source URL")
    ns = ap.parse_args()
    root = Path(ns.root)
    pages: dict[str, str] = {}
    fixtures = dict(item.split("=", 1) for item in ns.fixture)
    errors = []
    if not ns.no_fetch:
        for source in SOURCES:
            try:
                pages[source] = Path(fixtures[source]).read_text() if source in fixtures else fetch_page(source)
            except Exception as exc:
                errors.append(f"{source}: {type(exc).__name__}")
                print(f"::warning title=devpost-discovery::{source} fetch failed: {type(exc).__name__}")
    if not pages and not ns.no_fetch:
        print("devpost discovery: no source fetched; existing feed left unchanged", file=sys.stderr)
        return 2
    run = collect(root, pages, utc_now())
    print(f"devpost discovery: {run['discovered_this_run']} leads seen; {run['total_leads']} retained; {len(errors)} source failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
