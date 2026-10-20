#!/usr/bin/env python3
"""Re-request review on foreign open PRs that still have CHANGES_REQUESTED after our push.

Usage:
  python3 scripts/ci/help_wanted_rerequest.py --pr https://github.com/vedantnimbarte/zero/pull/81
  python3 scripts/ci/help_wanted_rerequest.py --all-foreign
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

API = "https://api.github.com"
TOKEN = (
    os.environ.get("OPERATOR_GITHUB_TOKEN")
    or os.environ.get("OPERATOR_TOKEN")
    or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or ""
)
AUTHOR = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")


def api(method: str, path: str, body: dict | None = None):
    url = path if path.startswith("http") else f"{API}{path}"
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "termux-help-wanted-rerequest",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def parse_pr(url: str) -> tuple[str, str, int]:
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not m:
        raise SystemExit(f"bad pr url: {url}")
    return m.group(1), m.group(2), int(m.group(3))


def rerequest(owner: str, repo: str, number: int) -> bool:
    # find reviewers who requested changes
    st, reviews = api("GET", f"/repos/{owner}/{repo}/pulls/{number}/reviews")
    reviewers = []
    if st == 200:
        for r in reviews or []:
            if r.get("state") == "CHANGES_REQUESTED":
                u = (r.get("user") or {}).get("login")
                if u and u not in reviewers:
                    reviewers.append(u)
    if not reviewers:
        # fallback: repo owner
        reviewers = [owner] if owner != AUTHOR else []
    if not reviewers:
        print(f"no reviewers for {owner}/{repo}#{number}")
        return False
    st, _ = api(
        "POST",
        f"/repos/{owner}/{repo}/pulls/{number}/requested_reviewers",
        {"reviewers": reviewers[:5]},
    )
    ok = st in (200, 201)
    print(f"rerequest {owner}/{repo}#{number} reviewers={reviewers} -> {st}")
    # comment
    api(
        "POST",
        f"/repos/{owner}/{repo}/issues/{number}/comments",
        {
            "body": (
                "### Help-wanted follow-up — re-request review\n\n"
                "Head was updated to address feedback. Re-requesting review.\n\n"
                "— termux-monorepo help-wanted lane\n"
            )
        },
    )
    return ok


def main() -> int:
    if not TOKEN:
        print("no token", file=sys.stderr)
        return 1
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr", default="")
    ap.add_argument("--all-foreign", action="store_true")
    args = ap.parse_args()
    targets = []
    if args.pr:
        targets.append(parse_pr(args.pr))
    if args.all_foreign:
        q = f"author:{AUTHOR} is:pr is:open review:changes_requested -repo:timerloggedout-spec/termux-monorepo"
        st, data = api("GET", f"/search/issues?q={urllib.parse.quote(q)}&per_page=20")
        if st == 200:
            for it in data.get("items") or []:
                parts = (it.get("repository_url") or "").rstrip("/").split("/")
                targets.append((parts[-2], parts[-1], int(it["number"])))
    if not targets:
        print("no targets")
        return 0
    ok = 0
    for o, r, n in targets:
        if rerequest(o, r, n):
            ok += 1
    print(json.dumps({"targets": len(targets), "ok": ok}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
