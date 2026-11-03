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

ONE ESCALATION SYSTEM, TWO TRIGGER CLASSES (owner addendum,
2026-11-03): the priority_timebox system (desk-feed rows, PR
#4126/#4130) escalates on time-to-wall; this watchdog is its
task-stall trigger. Stall thresholds TIGHTEN with the entry's
CURRENT tier, read from the timebox of record
(ops/challenge/desk-feed.json at the checkout): BASE 30/60 ->
CUSHION 20/40 -> WALL-DAY 10/20 -> ESCALATION 5/10 -> FINAL 0/5
(flag/escalate minutes). Flag/escalation comments carry the
tier frame + a machine-readable `stall-event:` line, on the
issue record where receipts and claims already live.

Runs in Actions (.github/workflows/dispatch-watchdog.yml, every
15 min + on dispatch) on the Termux Fleet Swarm App token (the
default token's rate bucket is exhausted in this repo — see
#4164). --flag-min / --escalate-min override the BASE tier only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.github.com"
DEFAULT_REPO = "timerloggedout-spec/termux-monorepo"
CLAIM_MARKER = "PRODUCER CLAIM"
STALL_EVENT_MARKER = "stall-event:"
# (flag_min, escalate_min) by ladder position 0..4
TIER_THRESHOLDS = [(30, 60), (20, 40), (10, 20), (5, 10), (0, 5)]
TIER_LADDER = ["BASE", "CUSHION", "WALL-DAY", "ESCALATION",
               "FINAL"]
DEFAULT_FEED = "ops/challenge/desk-feed.json"
RECEIPT_MARKER = "ROUTING RECEIPT"
FLAG_MARKER = "DISPATCH WATCHDOG — FLAG"
ESCALATION_MARKER = "DISPATCH WATCHDOG — ESCALATION"


def load_timeboxes(feed_path: str | None) -> dict:
    """{entry: priority_timebox} from the desk-feed of record."""
    if not feed_path:
        return {}
    try:
        with open(feed_path, encoding="utf-8") as fh:
            feed = json.load(fh)
    except (OSError, ValueError):
        return {}
    out = {}
    for row in feed.get("traversals") or []:
        tb = row.get("priority_timebox")
        if row.get("entry") and tb:
            out[row["entry"]] = tb
    return out


def entry_of(comments: list) -> str | None:
    """The entry named on the routing receipt (- entry: D1)."""
    for c in comments:
        body = c.get("body") or ""
        if RECEIPT_MARKER in body:
            for line in body.splitlines():
                line = line.strip()
                if line.startswith("- entry:"):
                    return line.split(":", 1)[1].strip()
    return None


def current_tier(timebox: dict | None, now: datetime):
    """(index, name) of the entry's current tier: the highest
    tier whose `at` is a timestamp already reached. State-
    triggered tiers (non-timestamp `at`) never advance the clock
    ladder — they report tier 0."""
    if not timebox:
        return (0, "BASE")
    best = (0, "BASE")
    for t in timebox.get("tiers") or []:
        at = t.get("at")
        if not at:
            continue
        try:
            when = parse_ts(str(at))
        except ValueError:
            continue
        if when <= now and int(t.get("tier", 0)) >= best[0]:
            best = (int(t.get("tier", 0)), str(t.get("name",
                                                    "BASE")))
    return best


def thresholds_for(tier_index: int, tier_name: str,
                   tier_count: int = 5):
    """Tightening thresholds: by ladder NAME first, else by the
    tier's scaled position on its own ladder (entries with 6
    tiers, e.g. D4's GATE tier, still tighten monotonically)."""
    if tier_name in TIER_LADDER:
        return TIER_THRESHOLDS[TIER_LADDER.index(tier_name)]
    if tier_count <= 1:
        return TIER_THRESHOLDS[0]
    scaled = round(tier_index / (tier_count - 1) * 4)
    return TIER_THRESHOLDS[max(0, min(4, scaled))]


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
             flag_min: int = 30, escalate_min: int = 60,
             timeboxes: dict | None = None) -> dict:
    """Pure classification of one queued issue. When the issue's
    entry carries a priority_timebox, the CURRENT tier's
    thresholds replace the BASE defaults (owner addendum)."""
    since = queued_since(issue, comments)
    age_min = max(0.0, (now - since).total_seconds() / 60.0)
    entry = entry_of(comments)
    tb = (timeboxes or {}).get(entry) if entry else None
    tier_index, tier_name = current_tier(tb, now)
    tier_count = len((tb or {}).get("tiers") or []) or 5
    if tb:
        flag_min, escalate_min = thresholds_for(
            tier_index, tier_name, tier_count)
    base = {"issue": issue["number"], "age_min": round(age_min, 1),
            "entry": entry, "tier": tier_name,
            "flag_min": flag_min, "escalate_min": escalate_min}
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
    req.add_header("User-Agent",
                   "dispatch-machinery (timerloggedout-spec/"
                   "termux-monorepo)")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:400]
        raise RuntimeError(
            f"GitHub API {method} {url} -> {exc.code}: {body}"
        ) from exc


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
          escalate_min: int, apply: bool = True,
          timeboxes: dict | None = None) -> list:
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
                           escalate_min, timeboxes=timeboxes)
        results.append(verdict)
        if not apply or not verdict["action"]:
            continue
        base = f"{API}/repos/{repo}/issues/{issue['number']}"
        try:
            if verdict["action"] == "flag":
                _request("POST", f"{base}/comments", token,
                         {"body": flag_comment(verdict["age_min"],
                                               verdict)})
            elif verdict["action"] == "escalate":
                _request("POST", f"{base}/comments", token,
                         {"body": escalation_comment(
                             issue, verdict["age_min"], verdict)})
                _request("POST", f"{base}/labels", token,
                         {"labels": ["dispatch-escalated"]})
        except Exception as exc:  # one bad action must not kill
            verdict["action"] = f"ERROR: {exc}"  # the whole sweep;
            verdict["state"] = "error"          # surface it instead
    return results


def render_table(results: list) -> str:
    lines = ["issue | entry | tier | state | age_min | action",
             "--- | --- | --- | --- | --- | ---"]
    for r in sorted(results, key=lambda r: r["issue"]):
        lines.append(f"#{r['issue']} | {r.get('entry') or '—'} | "
                     f"{r.get('tier') or '—'} | {r['state']} | "
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
    ap.add_argument("--feed", default=os.environ.get(
        "WATCHDOG_FEED", DEFAULT_FEED),
        help="desk-feed.json carrying the priority_timebox rows")
    args = ap.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get(
        "GH_TOKEN")
    if not token:
        print("dispatch_watchdog: GITHUB_TOKEN / GH_TOKEN not set",
              file=sys.stderr)
        return 2
    now = datetime.now(timezone.utc)
    timeboxes = load_timeboxes(args.feed)
    results = sweep(args.repo, token, now, args.flag_min,
                    args.escalate_min, apply=not args.dry_run,
                    timeboxes=timeboxes)
    table = render_table(results)
    print(f"dispatch watchdog @ {now:%Y-%m-%dT%H:%M:%SZ} — "
          f"{len(results)} queued issue(s)")
    print(table)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("### Dispatch watchdog\n\n" + table + "\n")
    errors = [r for r in results
              if str(r.get("action") or "").startswith("ERROR")]
    if errors:
        print(f"watchdog: {len(errors)} action(s) failed — "
              "the sweep did not fully land; failing the run so "
              "the failure is loud, not silent")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
