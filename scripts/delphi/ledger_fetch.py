#!/usr/bin/env python3
"""Fetch the delphi-ledger-feed cache from the GitHub API (stdlib only).

Writes <cache>/issues.json + comments.json for every issue registered
in ops/delphi/ledgers.json (ledgers + living records), and copies
ledgers.json from the working tree. Auth: GITHUB_TOKEN (Actions) or
GH_TOKEN. Repo: GITHUB_REPOSITORY or --repo.

Usage: ledger_fetch.py --cache DIR [--repo owner/name]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"


def get(token: str, url: str):
    """GET with the gate's defer discipline: a shared-token 403/429 is a
    rate-limit defer, not a hard failure (delphi-gate defer_api class).
    Retries with backoff, then raises Defer — main() turns that into a
    notice + exit 0 with NO cache written, and the workflow skips its
    remaining steps when the cache is absent."""
    for attempt in range(4):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            if e.code in (403, 429) and attempt < 3:
                wait = 20 * (2 ** attempt)
                print(f"::notice title=delphi-ledger-fetch::HTTP {e.code} "
                      f"(rate-limit class), retry in {wait}s: {body[:120]}")
                time.sleep(wait)
                continue
            if e.code in (403, 429):
                raise Defer(f"HTTP {e.code} after retries: {body[:200]}")
            raise


class Defer(Exception):
    pass


def paged(token: str, url: str) -> list:
    out, page = [], 1
    while True:
        batch = get(token, f"{url}&per_page=100&page={page}" if "?" in url
                    else f"{url}?per_page=100&page={page}")
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token or not args.repo:
        raise SystemExit("GITHUB_TOKEN/GH_TOKEN and a repo (GITHUB_REPOSITORY or --repo) are required")
    registry_src = Path("ops/delphi/ledgers.json")
    registry = json.loads(registry_src.read_text())
    numbers = sorted({e["issue"] for e in registry.get("ledgers", [])}
                     | {e["issue"] for e in registry.get("living_records", [])})
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    base = f"{API}/repos/{args.repo}"
    issues, comments = [], {}
    try:
        for num in numbers:
            issues.append(get(token, f"{base}/issues/{num}"))
            comments[str(num)] = paged(token, f"{base}/issues/{num}/comments")
    except Defer as e:
        print(f"::notice title=delphi-ledger-fetch::DEFERRED (shared-token "
              f"rate limit, gate defer_api class): {e}; no cache written, "
              f"workflow skips remaining steps")
        return 0
    (cache / "issues.json").write_text(json.dumps(issues))
    (cache / "comments.json").write_text(json.dumps(comments))
    shutil.copy(registry_src, cache / "ledgers.json")
    print(f"fetched {len(issues)} ledger issues, "
          f"{sum(len(v) for v in comments.values())} comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
