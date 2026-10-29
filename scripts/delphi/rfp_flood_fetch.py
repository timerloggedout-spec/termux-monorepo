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
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"


def _retry_delay(exc, attempt: int) -> float:
    """Seconds to wait before retrying a transient API failure.

    Honors Retry-After, then X-RateLimit-Reset when the primary bucket
    is empty; otherwise exponential backoff. Capped at 120s so a run
    defers minutes, not the rest of the rate window.
    """
    headers = getattr(exc, "headers", None) or {}
    retry_after = headers.get("Retry-After")
    if retry_after:
        try:
            return min(float(retry_after), 120.0)
        except ValueError:
            pass
    if headers.get("X-RateLimit-Remaining") == "0":
        try:
            reset = float(headers.get("X-RateLimit-Reset", 0))
            if reset:
                return max(0.0, min(reset - time.time(), 120.0))
        except ValueError:
            pass
    return min(5.0 * (3 ** attempt), 120.0)


def get(token: str, url: str):
    """GET one API URL with transient-failure retry.

    Root cause of the 2026-10-29 failure burst: collectors died on the
    first 403 (shared rate bucket exhausted by a workflow_run trigger
    storm) and the traceback reached only the job log, which is not
    API-readable — every failure surfaced as a bare "exit code 1"
    annotation. Retries ride out secondary limits; a final failure is
    emitted as a ::error:: annotation (check-run annotations ARE
    API-readable, the classify_pr debug-capture pattern, PRs
    #2255-#2265) naming status + GitHub's own message.
    """
    last_exc = None
    for attempt in range(4):
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            last_exc = exc
            transient = exc.code in (403, 429) or exc.code >= 500
            if not transient or attempt == 3:
                body = exc.read().decode("utf-8", "replace") if exc.fp else ""
                try:
                    message = json.loads(body).get("message", body[:200])
                except ValueError:
                    message = body[:200]
                print(f"::error::rfp fetch failed status={exc.code} "
                      f"url={url.split('api.github.com')[-1]} message={message}",
                      flush=True)
                raise
            delay = _retry_delay(exc, attempt)
            print(f"::warning::rfp fetch HTTP {exc.code} "
                  f"(attempt {attempt + 1}/4); retrying in {delay:.0f}s",
                  flush=True)
            time.sleep(delay)
        except urllib.error.URLError as exc:
            last_exc = exc
            if attempt == 3:
                print(f"::error::rfp fetch failed url={url.split('api.github.com')[-1]} "
                      f"message={exc}", flush=True)
                raise
            delay = min(5.0 * (3 ** attempt), 120.0)
            print(f"::warning::rfp fetch network error {exc} "
                  f"(attempt {attempt + 1}/4); retrying in {delay:.0f}s",
                  flush=True)
            time.sleep(delay)
    raise last_exc  # pragma: no cover


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
                 "research-silos.json", "research-axes.json",
                 "research-participants.json"):
        src = Path("ops/delphi") / name
        if src.exists():
            shutil.copy(src, cache / name)
    print(f"fetched {len(issues)} open delphi:rfp issues, "
          f"{sum(len(v) for v in comments.values())} comments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
