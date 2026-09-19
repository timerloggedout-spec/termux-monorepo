#!/usr/bin/env python3
"""Claim scaffold for help-wanted execution lane.

Given an issue URL or owner/repo#n:
  - posts a claim comment (attribution)
  - checks/creates fork under timerloggedout-spec
  - prints next steps for branch + PR

Stdlib + gh when available. YOLO-safe: claim is explicit, no silent force-push.

Usage:
  python3 scripts/ci/help_wanted_claim.py --issue https://github.com/owner/repo/issues/123
  python3 scripts/ci/help_wanted_claim.py --issue owner/repo#123 --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

CLAIM_BODY = """### Claim — termux-monorepo help-wanted lane

Taking a look at this issue as part of our external evaluation + contribution lane.

- Lane: help-wanted / CPPH ranked
- Actor: timerloggedout-spec (agentic)
- Will open a focused PR if a clean fix is in scope

If someone is already actively working this, say so and we will yield.
"""


def _headers() -> dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "termux-monorepo-help-wanted-claim",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h


def _api(method: str, url: str, body: dict | None = None) -> Any:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def parse_issue(ref: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    m = re.match(r"([^/]+)/([^/#]+)#(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse issue ref: {ref}")


def post_claim(owner: str, repo: str, number: int, dry: bool) -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments"
    if dry:
        print(f"DRY-RUN would POST claim to {url}")
        return "dry-run"
    out = _api("POST", url, {"body": CLAIM_BODY})
    return out.get("html_url") or ""


def ensure_fork(owner: str, repo: str, dry: bool) -> str:
    # Prefer gh if present
    try:
        r = subprocess.run(
            ["gh", "repo", "fork", f"{owner}/{repo}", "--clone=false"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if dry:
            print("DRY-RUN fork:", r.stdout or r.stderr)
            return f"timerloggedout-spec/{repo}"
        if r.returncode == 0 or "already exists" in (r.stderr or "").lower():
            return f"timerloggedout-spec/{repo}"
    except FileNotFoundError:
        pass
    # API fallback
    try:
        if not dry:
            _api("POST", f"https://api.github.com/repos/{owner}/{repo}/forks", {})
        return f"timerloggedout-spec/{repo}"
    except urllib.error.HTTPError as e:
        if e.code in (422, 403):
            return f"timerloggedout-spec/{repo}"  # may already exist
        raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, help="URL or owner/repo#n")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    owner, repo, number = parse_issue(args.issue)
    print(f"target: {owner}/{repo}#{number}")
    comment_url = post_claim(owner, repo, number, args.dry_run)
    print(f"claim: {comment_url}")
    fork = ensure_fork(owner, repo, args.dry_run)
    print(f"fork: {fork}")
    print("next: clone fork → branch fix/... → implement → gh pr create --repo", f"{owner}/{repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
