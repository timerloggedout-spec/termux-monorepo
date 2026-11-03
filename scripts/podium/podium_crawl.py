#!/usr/bin/env python3
"""Podium dataset crawler — lablab.ai public surfaces.

[MUSEai]@{role:{scraping-tools}}

Crawls server-rendered public pages only (no login, no session):
  - edition index      https://lablab.ai/ai-hackathons
  - edition pages      https://lablab.ai/ai-hackathons/<slug>
        -> core fields, prize tiers, judges (Speakers/Mentors/Judges cards)
  - recent winners     https://lablab.ai/apps/recent-winners
        -> winning project cards (medal icon = placement, card URL =
           /ai-hackathons/<edition>/<team>/<project>)

Every emitted row carries a receipt {source_url, captured_at, collector}.
Output = one snapshot JSON (envelope podium-snapshot/v1). Ingest,
dedupe, conflict detection and diffing live in podium_ingest.py.
Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

COLLECTOR = "scraping-tools/podium_crawl.py"
BASE = "https://lablab.ai"
UA = "termux-monorepo podium-crawl/1.0 (+public pages only)"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url: str) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.status, resp.read()


def text_lines(raw_html: str) -> list[str]:
    t = re.sub(r"<script.*?</script>", " ", raw_html, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    return [ln.strip() for ln in t.split("\n") if ln.strip()]


def receipt(url: str, captured_at: str) -> dict:
    return {"source_url": url, "captured_at": captured_at, "collector": COLLECTOR}


# ---------------- edition index ----------------

def parse_edition_index(raw_html: str) -> list[str]:
    slugs = set()
    for m in re.finditer(r'href="/ai-hackathons/([a-z0-9\-]+)"', raw_html):
        slug = m.group(1)
        if slug not in ("live",):
            slugs.add(slug)
    return sorted(slugs)


# ---------------- edition page ----------------

TIER_RE = re.compile(r"^(?:🥇|🥈|🥉)?\s*(1st|2nd|3rd)\s+place$", re.I)
MONEY_RE = re.compile(r"\$\s?[\d,]+")
DATE_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b"
)


def parse_prize_tiers(lines: list[str]) -> list[dict]:
    tiers: list[dict] = []
    for i, ln in enumerate(lines):
        m = TIER_RE.match(ln)
        if not m:
            continue
        window = lines[i : i + 5]
        amounts = []
        for w in window[1:]:
            amounts += MONEY_RE.findall(w)
            if len(amounts) >= 2:
                break
        tiers.append({"place": m.group(1), "amounts": amounts, "raw": window})
    # dedupe identical place rows (responsive duplicates)
    seen, out = set(), []
    for t in tiers:
        k = (t["place"], tuple(t["amounts"]))
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def parse_judges(lines: list[str]) -> list[dict]:
    """Speakers/Mentors/Judges section = (name, title) line pairs, heavily
    duplicated by responsive variants; dedupe by name."""
    start = None
    for i, ln in enumerate(lines):
        if re.search(r"Speakers,?\s+Mentors\s+&\s+Judges|Meet the Judges|^Judges$", ln):
            start = i + 1
            break
    if start is None:
        return []
    stop_words = {"Disclosures", "Guidelines", "Event Schedule", "Partners", "Community & social channels"}
    judges: list[dict] = []
    seen = set()
    i = start
    while i < len(lines) - 1 and lines[i] not in stop_words and len(judges) < 60:
        name, title = lines[i], lines[i + 1]
        if (
            2 <= len(name.split()) <= 5
            and name[0].isupper()
            and not re.search(r"\$|http|©|\d{4}", name)
            and len(title) < 70
            and not re.search(r"\$|http|©", title)
        ):
            if name not in seen:
                seen.add(name)
                judges.append({"name": name, "title": title})
            i += 2
        else:
            i += 1
    return judges


def parse_edition(slug: str, raw_html: str, captured_at: str) -> dict:
    lines = text_lines(raw_html)
    title = None
    m = re.search(r"<h1[^>]*>(.*?)</h1>", raw_html, re.S)
    if m:
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    dates = []
    for ln in lines:
        dates += DATE_RE.findall(ln)
    url = f"{BASE}/ai-hackathons/{slug}"
    r = receipt(url, captured_at)
    return {
        "edition": {
            "slug": slug, "title": title, "url": url,
            "dates_seen": sorted(set(dates)), "receipt": r,
        },
        "prize_tiers": [
            {"slug": slug, **t, "receipt": r} for t in parse_prize_tiers(lines)
        ],
        "judges": [
            {"slug": slug, **j, "receipt": r} for j in parse_judges(lines)
        ],
    }


# ---------------- winners feed ----------------

CARD_RE = re.compile(
    r'href="(/ai-hackathons/([a-z0-9\-]+)/([a-z0-9\-]+)/([a-z0-9\-]+))"'
)
MEDAL_RE = re.compile(r"(1st|2nd|3rd)_place_icon")
TAG_RE = re.compile(
    r'<span class="inline-flex rounded-full bg-\[#e1effe\][^"]*"[^>]*>([^<]{2,60})</span>'
)


def parse_winners_feed(raw_html: str, captured_at: str) -> list[dict]:
    url = f"{BASE}/apps/recent-winners"
    r = receipt(url, captured_at)
    out: list[dict] = []
    seen = set()
    # split the document into card blocks at each card anchor
    anchors = list(CARD_RE.finditer(raw_html))
    for idx, a in enumerate(anchors):
        path, edition, team, project = a.group(1), a.group(2), a.group(3), a.group(4)
        if path in seen:
            continue
        seen.add(path)
        end = anchors[idx + 1].start() if idx + 1 < len(anchors) else a.start() + 20000
        block = raw_html[a.start() : end]
        medal = None
        mm = MEDAL_RE.search(block)
        if mm:
            medal = mm.group(1)
        tm = re.search(r'alt="([^"]{3,120})"', block[block.find('href="' + path) :] or block)
        title = html.unescape(tm.group(1)) if tm else None
        tags = [html.unescape(t) for t in TAG_RE.findall(block)][:12]
        out.append(
            {
                "edition_slug": edition, "team_slug": team, "project_slug": project,
                "title": title, "placement": medal,
                "url": BASE + path, "tech_tags": tags, "receipt": r,
            }
        )
    return out


# ---------------- main ----------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Podium crawler (lablab public surfaces)")
    ap.add_argument("--editions", default="vultr-hackathon,alpaca-ai-trading-agents-hackathon,assemblyai-voice-agent-hackathon,ibm-bob-2-hackathon",
                    help="comma-separated edition slugs to crawl (plus index + winners feed)")
    ap.add_argument("--out", default="-", help="snapshot JSON path or - for stdout")
    args = ap.parse_args(argv)

    captured = now_iso()
    snapshot: dict = {
        "envelope": "podium-snapshot/v1",
        "captured_at": captured,
        "collector": COLLECTOR,
        "sources": [],
        "editions": [], "prize_tiers": [], "judges": [], "projects": [],
        "errors": [],
    }

    def get(url: str) -> str | None:
        try:
            status, body = fetch(url)
        except Exception as e:  # network/HTTP failure = recorded, not fatal
            snapshot["errors"].append({"url": url, "error": str(e)[:200]})
            return None
        snapshot["sources"].append(
            {"url": url, "http": status, "bytes": len(body),
             "sha256": hashlib.sha256(body).hexdigest()}
        )
        return body.decode("utf-8", errors="replace")

    index_html = get(f"{BASE}/ai-hackathons")
    index_slugs = parse_edition_index(index_html) if index_html else []
    snapshot["index_slugs"] = index_slugs

    for slug in [s.strip() for s in args.editions.split(",") if s.strip()]:
        page = get(f"{BASE}/ai-hackathons/{slug}")
        if page is None:
            continue
        parsed = parse_edition(slug, page, captured)
        snapshot["editions"].append(parsed["edition"])
        snapshot["prize_tiers"] += parsed["prize_tiers"]
        snapshot["judges"] += parsed["judges"]

    winners = get(f"{BASE}/apps/recent-winners")
    if winners:
        snapshot["projects"] = parse_winners_feed(winners, captured)

    out = json.dumps(snapshot, indent=1, ensure_ascii=False)
    if args.out == "-":
        print(out)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"snapshot: editions={len(snapshot['editions'])} tiers={len(snapshot['prize_tiers'])} "
              f"judges={len(snapshot['judges'])} projects={len(snapshot['projects'])} "
              f"errors={len(snapshot['errors'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
