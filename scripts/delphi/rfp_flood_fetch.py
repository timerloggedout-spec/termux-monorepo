#!/usr/bin/env python3
"""Fetch the delphi-rfp-feed cache from the GitHub API (stdlib only).

Writes <cache>/issues.json + comments.json for every open issue
labeled delphi:rfp, and copies ops/delphi/{surfaces,panel}.json from
the working tree when present. Auth: GITHUB_TOKEN (Actions) or
GH_TOKEN. Repo: GITHUB_REPOSITORY or --repo.

Usage: rfp_flood_fetch.py --cache DIR [--repo owner/name]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import urllib.request
from pathlib import Path

API = "https://api.github.com"


def get(token: str, url: str):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


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
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    base = f"{API}/repos/{args.repo}"
    issues = [i for i in paged(token, f"{base}/issues?state=open&labels=delphi:rfp")
              if "pull_request" not in i]
    (cache / "issues.json").write_text(json.dumps(issues))
    comments = {}
    for issue in issues:
        comments[str(issue["number"])] = paged(
            token, f"{base}/issues/{issue['number']}/comments")
    (cache / "comments.json").write_text(json.dumps(comments))
    for name in ("surfaces.json", "panel.json", "rfp-segments.json",
                 "research-silos.json"):
        src = Path("ops/delphi") / name
        if src.exists():
            shutil.copy(src, cache / name)
    print(f"fetched {len(issues)} open delphi:rfp issues, "
          f"{sum(len(v) for v in comments.values())} comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
