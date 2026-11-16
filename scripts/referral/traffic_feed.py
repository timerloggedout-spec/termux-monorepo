#!/usr/bin/env python3
"""Landing traffic feed collector (traffic-feed/1).

Reads the GitHub Traffic API for the landing repo
(timerloggedout-spec/timerloggedout-spec.github.io) — views, uniques,
per-day counts, top referrers, top paths over the trailing 14 days —
and writes data/traffic-feed.json INTO the landing repo (contents API).

Honesty rules (contract: docs/ops/REFERRAL-AUTOMATION.md):
- Numbers are the Traffic API's own; nothing is estimated or padded.
- The API window is 14 days; the feed says so.
- Per-?ch= visit counts are NOT measurable from GitHub-native data
  (Pages exposes no access log); campaign attribution is measured at
  redemption (rotation ledger), never inferred from visits.

Auth: GH_TOKEN env (a token with read access to the landing repo's
traffic and write access to its contents). Exits non-zero with a
plain message when the token cannot read traffic (403) — a failed
collect must be loud, never a silent zero feed.
"""
import base64
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
LANDING = "timerloggedout-spec/timerloggedout-spec.github.io"
FEED_PATH = "data/traffic-feed.json"


def call(method, path, token, body=None):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=data, timeout=60) as resp:
        return json.loads(resp.read().decode() or "{}")


def main():
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("GH_TOKEN not set — cannot collect.", file=sys.stderr)
        return 2
    try:
        views = call("GET", f"/repos/{LANDING}/traffic/views", token)
        referrers = call("GET", f"/repos/{LANDING}/traffic/popular/referrers", token)
        paths = call("GET", f"/repos/{LANDING}/traffic/popular/paths", token)
    except urllib.error.HTTPError as e:
        print(f"traffic API read failed: HTTP {e.code} — the token likely "
              "lacks traffic access on the landing repo.", file=sys.stderr)
        return 1

    feed = {
        "schema": "traffic-feed/1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": f"github-traffic-api: {LANDING}",
        "window_days": 14,
        "views": {
            "count": views.get("count", 0),
            "uniques": views.get("uniques", 0),
            "per_day": [
                {"day": v["timestamp"][:10], "count": v["count"], "uniques": v["uniques"]}
                for v in views.get("views", [])
            ],
        },
        "referrers": [
            {"referrer": r["referrer"], "count": r["count"], "uniques": r["uniques"]}
            for r in (referrers or [])
        ],
        "paths": [
            {"path": p["path"], "title": p.get("title", ""), "count": p["count"], "uniques": p["uniques"]}
            for p in (paths or [])
        ],
        "note": ("Counts are the GitHub Traffic API's trailing-14-day record for the "
                 "landing repo. Per-campaign (?ch=) visit counts are not measurable "
                 "from GitHub-native data; campaign attribution is measured at "
                 "redemption in the rotation ledger, not inferred from visits."),
    }

    raw = json.dumps(feed, indent=1).encode()
    sha = None
    try:
        cur = call("GET", f"/repos/{LANDING}/contents/{FEED_PATH}", token)
        sha = cur.get("sha")
        if base64.b64decode(cur["content"]) == raw:
            print("traffic feed unchanged — no write.")
            return 0
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    body = {
        "message": f"chore(traffic): refresh traffic-feed ({feed['generated_at']})",
        "content": base64.b64encode(raw).decode(),
    }
    if sha:
        body["sha"] = sha
    call("PUT", f"/repos/{LANDING}/contents/{FEED_PATH}", token, body)
    print(f"traffic feed written: views={feed['views']['count']} "
          f"uniques={feed['views']['uniques']} referrers={len(feed['referrers'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
