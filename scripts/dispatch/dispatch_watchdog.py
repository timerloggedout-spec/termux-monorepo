#!/usr/bin/env python3
"""Dispatch watchdog — the unclaimed-aging sweep.

The project-task intake queues tasks (`dispatch-queued`) but does
not execute them; a task executes when a producer claims it (see
claim_task.py: claim comment + `dispatch-claimed` label). Before
this watchdog existed, an unclaimed task was indistinguishable from
an owned one — the 2026-11-03 D1 surface stall sat ~2h because of
exactly that. This sweep makes unclaimed aging LOUD:

- unclaimed age > flag threshold (default 30 min): a FLAG comment
  on the issue (once).
- unclaimed age > escalate threshold (default 60 min): an
  ESCALATION comment naming the filing seat (the issue author) +
  the `dispatch-escalated` label (once).

Age is measured from the routing-receipt comment (when the task
entered the queue), falling back to the issue's creation time.
A task counts as claimed when the `dispatch-claimed` label is
present OR any comment carries the PRODUCER CLAIM marker.

Every run prints the full queued set with its state — claimed,
watching, flagged, escalated — which is the acceptance evidence
that the sweep sees the queue correctly.

Runs in Actions (.github/workflows/dispatch-watchdog.yml, every
15 min + on dispatch) with the workflow token; thresholds via
--flag-min / --escalate-min or WATCHDOG_FLAG_MIN /
WATCHDOG_ESCALATE_MIN.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"
CLAIM_MARKER = "PRODUCER CLAIM"
RECEIPT_MARKER = "ROUTING RECEIPT"
FLAG_MARKER = "DISPATCH WATCHDOG — FLAG"
ESCALATION_MARKER = "DISPATCH WATCHDOG — ESCALATION"


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def queued_since(issue: dict, comments: list) -> datetime:
    """When the task entered the queue: the routing receipt's
    timestamp, else the issue creation time."""
    stamps = [parse_ts(c["created_at"]) for c in comments
              if RECEIPT_MARKER in (c.get("body") or "")]
    if stamps:
        return min(stamps)
    return parse_ts(issue["created_at"])


def has_claim(issue: dict, comments: list) -> bool:
    labels = {l["name"] for l in issue.get("labels") or []}
    if "dispatch-claimed" in labels:
        return True
    return any(CLAIM_MARKER in (c.get("body") or "")
               for c in comments)


def _posted(comments: list, marker: str) -> bool:
    return any(marker in (c.get("body") or "") for c in comments)


def classify(issue: dict, comments: list, now: datetime,
             flag_min: int = 30, escalate_min: int = 60) -> dict:
    """Pure classification of one queued issue."""
    since = queued_since(issue, comments)
    age_min = max(0.0, (now - since).total_seconds() / 60.0)
    base = {"issue": issue["number"], "age_min": round(age_min, 1)}
    if has_claim(issue, comments):
        return {**base, "state": "claimed", "action": None}
    if _posted(comments, ESCALATION_MARKER):
        return {**base, "state": "escalated", "action": None}
    if age_min > escalate_min:
        return {**base, "state": "unclaimed", "action": "escalate"}
    if age_min > flag_min and not _posted(comments, FLAG_MARKER):
        return {**base, "state": "unclaimed", "action": "flag"}
    if age_min > flag_min:
        return {**base, "state": "flagged", "action": None}
    return {**base, "state": "watching", "action": None}


def flag_comment(age_min: float) -> str:
    return (
        f"[MUSEai]@{{role:{{dispatch-watchdog}}}} {FLAG_MARKER} — "
        f"this task has sat `dispatch-queued` UNCLAIMED for "
        f"{age_min:.0f} minutes.\n\n"
        "Queued is not owned: no producer has stamped a claim "
        "(claim comment + `dispatch-claimed` label, via "
        "`scripts/dispatch/claim_task.py`). The producing seat "
        "should claim at pickup; the filing seat should confirm a "
        "claim exists. Escalation follows at 60 minutes unclaimed."
    )


def escalation_comment(issue: dict, age_min: float) -> str:
    author = (issue.get("user") or {}).get("login", "unknown")
    return (
        f"[MUSEai]@{{role:{{dispatch-watchdog}}}} "
        f"{ESCALATION_MARKER} — this task has sat `dispatch-queued` "
        f"UNCLAIMED for {age_min:.0f} minutes (filing seat: "
        f"@{author}).\n\n"
        "Escalated per the dispatch claim/lease mechanism: a "
        "form-only filing with no claim stalls silently without "
        "this signal (instance of record: the 2026-11-03 D1 "
        "surface stall, issue #4164). Remedy: a producing seat "
        "claims via `scripts/dispatch/claim_task.py`, or the "
        "filing seat routes it to a named seat directly."
    )


def _request(method: str, url: str, token: str, payload=None):
    data = json.dumps(payload).encode() if payload is not None \
        else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode() or "{}")


def _get_all(url: str, token: str) -> list:
    out, page = [], 1
    while True:
        batch = _request("GET", f"{url}&per_page=100&page={page}"
                         if "?" in url else
                         f"{url}?per_page=100&page={page}", token)
        if not batch:
            return out
        out.extend(batch)
        page += 1


def sweep(repo: str, token: str, now: datetime, flag_min: int,
          escalate_min: int, apply: bool = True) -> list:
    issues = _get_all(
        f"{API}/repos/{repo}/issues?state=open"
        f"&labels=dispatch-queued", token)
    results = []
    for issue in issues:
        if "pull_request" in issue:
            continue
        comments = _get_all(
            f"{API}/repos/{repo}/issues/{issue['number']}/comments",
            token)
        verdict = classify(issue, comments, now, flag_min,
                           escalate_min)
        results.append(verdict)
        if not apply or not verdict["action"]:
            continue
        base = f"{API}/repos/{repo}/issues/{issue['number']}"
        if verdict["action"] == "flag":
            _request("POST", f"{base}/comments", token,
                     {"body": flag_comment(verdict["age_min"])})
        elif verdict["action"] == "escalate":
            _request("POST", f"{base}/comments", token,
                     {"body": escalation_comment(
                         issue, verdict["age_min"])})
            _request("POST", f"{base}/labels", token,
                     {"labels": ["dispatch-escalated"]})
    return results


def render_table(results: list) -> str:
    lines = ["issue | state | age_min | action",
             "--- | --- | --- | ---"]
    for r in sorted(results, key=lambda r: r["issue"]):
        lines.append(f"#{r['issue']} | {r['state']} | "
                     f"{r['age_min']} | {r['action'] or '—'}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo",
                    default=os.environ.get("GITHUB_REPOSITORY",
                                           DEFAULT_REPO))
    ap.add_argument("--flag-min", type=int,
                    default=int(os.environ.get("WATCHDOG_FLAG_MIN",
                                               "30")))
    ap.add_argument("--escalate-min", type=int,
                    default=int(os.environ.get(
                        "WATCHDOG_ESCALATE_MIN", "60")))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get(
        "GH_TOKEN")
    if not token:
        print("dispatch_watchdog: GITHUB_TOKEN / GH_TOKEN not set",
              file=sys.stderr)
        return 2
    now = datetime.now(timezone.utc)
    results = sweep(args.repo, token, now, args.flag_min,
                    args.escalate_min, apply=not args.dry_run)
    table = render_table(results)
    print(f"dispatch watchdog @ {now:%Y-%m-%dT%H:%M:%SZ} — "
          f"{len(results)} queued issue(s)")
    print(table)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("### Dispatch watchdog\n\n" + table + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
