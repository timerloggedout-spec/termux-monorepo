#!/usr/bin/env python3
"""Claim scaffold for help-wanted execution lane.

LIVE path posts claim comment + ensures fork under timerloggedout-spec.
--dry-run exists ONLY for local debugging; Actions must never pass it.

Idempotent: will NOT re-post if our claim marker already exists on the issue.
Skips closed issues unless --allow-closed.

Usage:
  python3 scripts/ci/help_wanted_claim.py --issue https://github.com/owner/repo/issues/123
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

CLAIM_MARKER = "### Claim — termux-monorepo help-wanted lane"
CLAIM_BODY = f"""{CLAIM_MARKER}

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
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")[:600]
        print(f"API {method} {url} -> {e.code}: {err}", file=sys.stderr)
        raise


def parse_issue(ref: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", ref)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    m = re.match(r"([^/]+)/([^/#]+)#(\d+)", ref.strip())
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    raise SystemExit(f"cannot parse issue ref: {ref!r}")


def get_issue(owner: str, repo: str, number: int) -> dict:
    return _api("GET", f"https://api.github.com/repos/{owner}/{repo}/issues/{number}")


def find_existing_claim(owner: str, repo: str, number: int) -> str | None:
    """Return existing claim comment URL if our marker is already present."""
    page = 1
    while page <= 5:
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments"
            f"?per_page=100&page={page}"
        )
        comments = _api("GET", url)
        if not isinstance(comments, list) or not comments:
            break
        for c in comments:
            body = c.get("body") or ""
            user = ((c.get("user") or {}).get("login") or "").lower()
            if CLAIM_MARKER in body and (
                user in ("timerloggedout-spec", "github-actions[bot]")
                or "help-wanted lane" in body.lower()
            ):
                return c.get("html_url") or ""
        if len(comments) < 100:
            break
        page += 1
    return None


def post_claim(owner: str, repo: str, number: int, dry: bool) -> str:
    existing = find_existing_claim(owner, repo, number)
    if existing is not None:
        print(f"claim already present — skipping post: {existing}")
        return existing or "existing-claim"

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments"
    if dry:
        print(f"DRY-RUN would POST claim to {url}")
        return "dry-run"
    out = _api("POST", url, {"body": CLAIM_BODY})
    return out.get("html_url") or ""


def ensure_fork(owner: str, repo: str, dry: bool) -> str:
    try:
        r = subprocess.run(
            ["gh", "repo", "fork", f"{owner}/{repo}", "--clone=false"],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if dry:
            print("DRY-RUN fork:", r.stdout or r.stderr)
            return f"timerloggedout-spec/{repo}"
        if r.returncode == 0 or "already exists" in ((r.stderr or "") + (r.stdout or "")).lower():
            return f"timerloggedout-spec/{repo}"
        print(r.stdout or "", r.stderr or "", file=sys.stderr)
    except FileNotFoundError:
        pass
    try:
        if not dry:
            _api("POST", f"https://api.github.com/repos/{owner}/{repo}/forks", {})
        return f"timerloggedout-spec/{repo}"
    except urllib.error.HTTPError as e:
        if e.code in (422, 403):
            return f"timerloggedout-spec/{repo}"
        raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", required=True, help="URL or owner/repo#n")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="LOCAL DEBUG ONLY — Actions must never pass this",
    )
    ap.add_argument(
        "--allow-closed",
        action="store_true",
        help="Allow claim on closed issues (default: skip closed)",
    )
    args = ap.parse_args()
    if args.dry_run and os.environ.get("GITHUB_ACTIONS") == "true":
        print("REFUSING dry-run inside GitHub Actions", file=sys.stderr)
        return 3
    owner, repo, number = parse_issue(args.issue)
    print(f"target: {owner}/{repo}#{number} live={not args.dry_run}")

    meta = get_issue(owner, repo, number)
    state = (meta.get("state") or "open").lower()
    if state == "closed" and not args.allow_closed:
        print(
            f"SKIP closed issue {owner}/{repo}#{number} "
            f"(closed_at={meta.get('closed_at')}). Use --allow-closed to override.",
            file=sys.stderr,
        )
        print("::notice::claim_skipped_closed=true")
        return 0

    comment_url = post_claim(owner, repo, number, args.dry_run)
    print(f"claim: {comment_url}")
    fork = ensure_fork(owner, repo, args.dry_run)
    print(f"fork: {fork}")
    print("next: contribute job → branch → upstream PR on", f"{owner}/{repo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
