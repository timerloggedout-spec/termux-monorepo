#!/usr/bin/env python3
"""Poll open FOREIGN PRs we authored for CHANGES_REQUESTED; notify + evidence.

Excludes timerloggedout-spec/termux-monorepo (internal). Help-wanted is external.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
AUTHOR = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")
# Never follow up on our own monorepo PRs — those are not help-wanted foreign work.
EXCLUDE_REPOS = {
    "timerloggedout-spec/termux-monorepo",
}
TOKEN = (
    os.environ.get("OPERATOR_GITHUB_TOKEN")
    or os.environ.get("OPERATOR_TOKEN")
    or os.environ.get("ARCHWIZ_GITHUB_TOKEN")
    or os.environ.get("GITHUB_TOKEN")
    or ""
)
MARKER = "### Help-wanted follow-up — termux-monorepo"


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
            "User-Agent": "termux-help-wanted-followup",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"HTTP {e.code} {path}: {err[:400]}", file=sys.stderr)
        return e.code, {}


def search_changes_requested() -> list[dict]:
    # -repo: excludes monorepo from search
    q = (
        f"author:{AUTHOR} is:pr is:open review:changes_requested "
        f"-repo:timerloggedout-spec/termux-monorepo"
    )
    status, data = api("GET", f"/search/issues?q={urllib.parse.quote(q)}&per_page=30")
    if status != 200:
        return []
    items = []
    for it in data.get("items") or []:
        repo_url = it.get("repository_url") or ""
        parts = repo_url.rstrip("/").split("/")
        full = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else ""
        if full in EXCLUDE_REPOS:
            continue
        items.append(it)
    return items


def already_followed_up(owner: str, repo: str, number: int) -> bool:
    status, comments = api("GET", f"/repos/{owner}/{repo}/issues/{number}/comments?per_page=50")
    if status != 200:
        return False
    for c in comments or []:
        if MARKER in (c.get("body") or ""):
            return True
    return False


def post_followup(owner: str, repo: str, number: int, review_summary: str) -> str | None:
    body = (
        f"{MARKER}\n\n"
        f"Detected **CHANGES_REQUESTED** on this open external PR.\n\n"
        f"{review_summary}\n\n"
        f"Next: revise the head branch and re-request review.\n\n"
        f"— `timerloggedout-spec/termux-monorepo` help-wanted-followup\n"
    )
    status, data = api("POST", f"/repos/{owner}/{repo}/issues/{number}/comments", {"body": body})
    if status in (200, 201):
        return data.get("html_url")
    return None


def latest_changes_review(owner: str, repo: str, number: int) -> str:
    status, reviews = api("GET", f"/repos/{owner}/{repo}/pulls/{number}")
    # reviews endpoint
    status, reviews = api("GET", f"/repos/{owner}/{repo}/pulls/{number}/reviews")
    if status != 200:
        return "(could not load reviews)"
    for r in reversed(reviews or []):
        if r.get("state") == "CHANGES_REQUESTED":
            body = (r.get("body") or "").strip()
            user = (r.get("user") or {}).get("login")
            excerpt = body[:1200] + ("…" if len(body) > 1200 else "")
            return f"Latest review by @{user}:\n\n> " + excerpt.replace("\n", "\n> ")
    return "(no CHANGES_REQUESTED body found)"


def append_evidence(rows: list[dict]) -> None:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = Path(f"docs/ops/generated/help-wanted-evidence/{day}.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for row in rows:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")


def main() -> int:
    if not TOKEN:
        print("No token", file=sys.stderr)
        return 1
    items = search_changes_requested()
    print(f"found {len(items)} FOREIGN open PRs with CHANGES_REQUESTED")
    rows = []
    for it in items:
        repo_url = it.get("repository_url") or ""
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        number = int(it["number"])
        html = it.get("html_url")
        if already_followed_up(owner, repo, number):
            print(f"skip already followed {html}")
            rows.append(
                {
                    "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "kind": "followup_skip_idempotent",
                    "issue": html,
                    "ok": True,
                    "lane": "help-wanted-followup",
                    "foreign": True,
                }
            )
            continue
        summary = latest_changes_review(owner, repo, number)
        url = post_followup(owner, repo, number, summary)
        ok = bool(url)
        print(f"{'ok' if ok else 'fail'} followup {html} -> {url}")
        rows.append(
            {
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "kind": "followup_changes_requested",
                "issue": html,
                "ok": ok,
                "comment_url": url,
                "lane": "help-wanted-followup",
                "foreign": True,
            }
        )
    if rows:
        append_evidence(rows)
    print(json.dumps({"processed": len(rows), "found": len(items)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
