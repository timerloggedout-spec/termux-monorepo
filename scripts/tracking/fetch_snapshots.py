#!/usr/bin/env python3
"""Refresh the tracking observation snapshots (workflow-side, network).

Writes (stamped API reads — the surface-feeds observation pattern):
  scripts/tracking/pr_feed_snapshot.json
    {schema, read_at, merged[<=150 recent], open[<=200]} from the GitHub
    PR API using GH_TOKEN/GITHUB_TOKEN (in Actions: the workflow token).
  scripts/tracking/lane_events_snapshot.json
    {schema, read_at, status, count, events[<=200 latest]} from Neon
    lane_events via SQL-over-HTTP (Neon serverless endpoint derived from
    LANE_EVENTS_DATABASE_URL host). No secret set -> status=not_configured
    (a named gap in the feed, never a failure). Values are never printed.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts" / "tracking"
REPO = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _gh(path: str, token: str):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "repo-tracking-collect"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _slim(pr: dict, merged: bool) -> dict:
    return {
        "number": pr.get("number"), "title": pr.get("title"),
        "merged_at": pr.get("merged_at"), "updated_at": pr.get("updated_at"),
        "created_at": pr.get("created_at"),
        "merge_commit_sha": pr.get("merge_commit_sha"),
        "head_ref": (pr.get("head") or {}).get("ref"),
        "author": (pr.get("user") or {}).get("login"),
        "labels": [l.get("name") for l in pr.get("labels", []) if isinstance(l, dict)],
        "html_url": pr.get("html_url"), "merged": merged,
    }


def fetch_prs(token: str) -> dict:
    merged, page = [], 1
    while len(merged) < 150 and page <= 3:
        batch = _gh(f"/repos/{REPO}/pulls?state=closed&sort=updated&direction=desc"
                    f"&per_page=100&page={page}", token)
        for pr in batch:
            if pr.get("merged_at"):
                merged.append(_slim(pr, True))
        if len(batch) < 100:
            break
        page += 1
    open_prs, page = [], 1
    while len(open_prs) < 200 and page <= 2:
        batch = _gh(f"/repos/{REPO}/pulls?state=open&sort=updated&direction=desc"
                    f"&per_page=100&page={page}", token)
        open_prs += [_slim(pr, False) for pr in batch]
        if len(batch) < 100:
            break
        page += 1
    return {"schema": "tracking-pr-feed-snapshot/v1", "read_at": _now(),
            "repo": REPO, "merged": merged[:150], "open": open_prs[:200]}


def fetch_lane_events() -> dict:
    url = os.environ.get("LANE_EVENTS_DATABASE_URL", "").strip()
    base = {"schema": "tracking-lane-events-snapshot/v1", "read_at": _now(),
            "status": "not_configured", "count": None, "events": []}
    if not url:
        return base
    try:
        host = urllib.parse.urlparse(url).hostname
        if not host:
            base["status"] = "bad_url"
            return base
        query = ("SELECT lane, workflow, event_type, conclusion, subject_url, head_sha, "
                 "occurred_at::text AS occurred_at FROM lane_events "
                 "ORDER BY occurred_at DESC LIMIT 200")
        count_q = "SELECT count(*)::int AS n FROM lane_events"
        def _sql(q):
            req = urllib.request.Request(
                f"https://{host}/sql",
                data=json.dumps({"query": q, "params": []}).encode(), method="POST",
                headers={"Neon-Connection-String": url, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        rows = _sql(query).get("rows", [])
        cnt = _sql(count_q).get("rows", [{}])
        base.update({"status": "ok", "count": cnt[0].get("n") if cnt else None,
                     "events": rows})
        return base
    except Exception as e:  # never fail the collect; record the class only
        base["status"] = f"error:{type(e).__name__}"
        return base


def main() -> int:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    OUT.mkdir(parents=True, exist_ok=True)
    if token:
        (OUT / "pr_feed_snapshot.json").write_text(json.dumps(fetch_prs(token), indent=1) + "\n")
        print("pr_feed_snapshot refreshed")
    else:
        print("::warning::no GH token; pr snapshot untouched")
    (OUT / "lane_events_snapshot.json").write_text(json.dumps(fetch_lane_events(), indent=1) + "\n")
    print("lane_events_snapshot refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
