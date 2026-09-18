#!/usr/bin/env python3
"""Help-wanted scout: GitHub search + Complexity Perception Prediction Heuristics.

Emits ranked JSON catalog. Stdlib-first. Safe for Termux / Codespace / Actions.

Usage:
  python3 scripts/ci/help_wanted_scout.py
  python3 scripts/ci/help_wanted_scout.py --max 30 --lang python --out /tmp/catalog.json

Env:
  GITHUB_TOKEN or GH_TOKEN optional (higher rate limits).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

PREFERRED_LANGS = {
    "python", "typescript", "javascript", "go", "rust", "shell", "markdown", "yaml", "bash"
}

LABEL_SCORES = {
    "good first issue": 25,
    "good-first-issue": 25,
    "help wanted": 18,
    "help-wanted": 18,
    "beginner": 15,
    "easy": 15,
    "difficulty/easy": 15,
    "up-for-grabs": 12,
    "hacktoberfest": 8,
    "contributions welcome": 8,
}


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-monorepo-help-wanted-scout",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _get(url: str) -> Any:
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def search_issues(query: str, per_page: int = 30) -> list[dict]:
    q = urllib.parse.quote(query)
    url = f"https://api.github.com/search/issues?q={q}&sort=updated&order=desc&per_page={per_page}"
    try:
        data = _get(url)
    except urllib.error.HTTPError as e:
        print(f"search HTTP {e.code}: {e.reason}", file=sys.stderr)
        return []
    return data.get("items") or []


def label_score(labels: list[dict]) -> int:
    names = {str(l.get("name", "")).lower() for l in labels}
    best = 0
    for n, s in LABEL_SCORES.items():
        if n in names:
            best = max(best, s)
    return best


def body_clarity(body: str | None) -> int:
    if not body:
        return 0
    b = body.lower()
    score = 0
    if any(k in b for k in ("acceptance", "expected", "steps to", "checklist", "- [ ]", "repro")):
        score += 10
    n = len(body)
    if 80 <= n <= 2000:
        score += 5
    elif n > 4000:
        score -= 3
    return max(0, min(15, score))


def freshness_score(updated_at: str | None) -> int:
    if not updated_at:
        return 0
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).days
    except Exception:
        return 0
    if age < 30:
        return 10
    if age < 90:
        return 6
    if age > 365:
        return -5
    return 2


def comment_score(n: int | None) -> int:
    n = n or 0
    if n <= 3:
        return 10
    if n <= 12:
        return 5
    if n > 30:
        return -5
    return 0


def language_score(repo_url: str, preferred: set[str]) -> int:
    # Search results do not always embed language; light heuristic from URL/path
    # Full language requires secondary API; keep zero-cost for scout.
    return 5  # neutral baseline; workflow can enrich later


def rank_issue(item: dict) -> dict:
    labels = item.get("labels") or []
    body = item.get("body") or ""
    assignees = item.get("assignees") or []
    comments = item.get("comments") or 0
    updated = item.get("updated_at")
    html = item.get("html_url") or ""
    title = item.get("title") or ""
    repo = (item.get("repository_url") or "").replace("api.github.com/repos/", "github.com/")

    score = 0
    score += label_score(labels)
    score += 15 if not assignees else (5 if len(assignees) == 1 else 0)
    score += body_clarity(body)
    score += freshness_score(updated)
    score += comment_score(comments)
    score += 8  # repo health baseline (search already filters active-ish)
    score += language_score(repo, PREFERRED_LANGS)
    score += 5  # assume no competing PR unless later enriched
    score = max(0, min(100, score))

    return {
        "score": score,
        "title": title,
        "url": html,
        "repo": repo,
        "labels": [l.get("name") for l in labels],
        "assignees": [a.get("login") for a in assignees],
        "comments": comments,
        "updated_at": updated,
        "number": item.get("number"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Help-wanted scout + CPPH ranking")
    ap.add_argument("--max", type=int, default=25, help="max issues to rank")
    ap.add_argument("--lang", default="", help="optional language qualifier")
    ap.add_argument("--label", default="help wanted", help="primary label phrase")
    ap.add_argument("--out", default="", help="write JSON catalog path")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # GitHub search: open issues with help-wanted style labels
    parts = ["is:issue", "is:open", f'label:"{args.label}"']
    if args.lang:
        parts.append(f"language:{args.lang}")
    query = " ".join(parts)

    items = search_issues(query, per_page=min(args.max, 50))
    ranked = sorted((rank_issue(i) for i in items), key=lambda x: -x["score"])[: args.max]

    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "count": len(ranked),
        "items": ranked,
        "heuristics": "CPPH v0 — see docs/ops/HELP-WANTED-LANE.md",
    }

    text = json.dumps(catalog, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"wrote {args.out} ({len(ranked)} items)", file=sys.stderr)
    else:
        print(text)

    if ranked:
        print("\nTop candidates:", file=sys.stderr)
        for r in ranked[:8]:
            print(f"  [{r['score']:3d}] {r['title'][:70]}  {r['url']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
