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
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "que"))
import task_ranking  # noqa: E402  (QUE #5283 ranking method of record)
import auto_claim  # noqa: E402  (QUE #5286 auto-claim decision logic)

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
    """The entry named on the routing receipt (- entry: D1).
    Filers sometimes write a descriptive string ("D1 StudySprint
    — v0.5.0 batch B of 3 ...") — the raw value is returned here;
    match_entry() resolves it to a timebox key."""
    for c in comments:
        body = c.get("body") or ""
        if RECEIPT_MARKER in body:
            for line in body.splitlines():
                line = line.strip()
                if line.startswith("- entry:"):
                    return line.split(":", 1)[1].strip()
    return None


def match_entry(raw: str | None, timeboxes: dict) -> str | None:
    """Resolve a receipt's entry string to a timebox key: exact
    match, else the longest key the string starts with (the
    descriptive-filing form), else the first token."""
    if not raw:
        return None
    if raw in timeboxes:
        return raw
    for key in sorted(timeboxes, key=len, reverse=True):
        if raw.startswith(key):
            return key
    first = raw.split()[0] if raw.split() else ""
    return first if first in timeboxes else None


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
    raw_entry = entry_of(comments)
    entry = match_entry(raw_entry, timeboxes or {})
    tb = (timeboxes or {}).get(entry) if entry else None
    tier_index, tier_name = current_tier(tb, now)
    tier_count = len((tb or {}).get("tiers") or []) or 5
    if tb:
        flag_min, escalate_min = thresholds_for(
            tier_index, tier_name, tier_count)
    # Timing decision of record (QUE #5286 — owner c.6843045932,
    # QDesk c.6843060529, Cadence countersign c.6843070784): the
    # standard escalation threshold is 15m; a tighter tier frame
    # governs, the standard caps the rest (supersedes BASE 60m).
    escalate_min = min(escalate_min, auto_claim.STANDARD_ESCALATE_MIN)
    base = {"issue": issue["number"], "age_min": round(age_min, 1),
            "entry": entry, "tier": tier_name,
            "flag_min": flag_min, "escalate_min": escalate_min,
            "stall_breach": age_min > auto_claim.STALL_CEILING_MIN}
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


def _tier_frame(verdict):
    """(tier, flag_min, escalate_min) from a classify() verdict,
    with BASE defaults for verdict-less callers."""
    v = verdict or {}
    return (v.get("tier") or "BASE", int(v.get("flag_min", 30)),
            int(v.get("escalate_min", 60)))


def flag_comment(age_min: float, verdict=None) -> str:
    # The verdict parameter is the sweep's call shape (#4362: the
    # builders took one argument fewer than sweep passes, so every
    # flag/escalate action died on TypeError). The comment carries
    # the tier frame + the machine-readable stall-event line the
    # module docstring promises (the #4350 feed collector scans
    # comments for it).
    tier, flag_min, esc_min = _tier_frame(verdict)
    return (
        f"[MUSEai]@{{role:{{dispatch-watchdog}}}} {FLAG_MARKER} — "
        f"this task has sat `dispatch-queued` UNCLAIMED for "
        f"{age_min:.0f} minutes.\n\n"
        "Queued is not owned: no producer has stamped a claim "
        "(claim comment + `dispatch-claimed` label, via "
        "`scripts/dispatch/claim_task.py`). The producing seat "
        "should claim at pickup; the filing seat should confirm a "
        f"claim exists. Escalation follows at {esc_min} minutes "
        "unclaimed.\n\n"
        f"Tier frame: {tier} — thresholds flag {flag_min} min / "
        f"escalate {esc_min} min (priority_timebox, "
        "ops/challenge/desk-feed.json).\n\n"
        f"stall-event: flag tier={tier} age_min={age_min:.0f} "
        f"flag_min={flag_min} escalate_min={esc_min}"
    )


def escalation_comment(issue: dict, age_min: float,
                       verdict=None) -> str:
    author = (issue.get("user") or {}).get("login", "unknown")
    tier, flag_min, esc_min = _tier_frame(verdict)
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
        "filing seat routes it to a named seat directly.\n\n"
        f"Tier frame: {tier} — thresholds flag {flag_min} min / "
        f"escalate {esc_min} min (priority_timebox, "
        "ops/challenge/desk-feed.json).\n\n"
        f"stall-event: escalation tier={tier} "
        f"age_min={age_min:.0f} flag_min={flag_min} "
        f"escalate_min={esc_min}"
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
          timeboxes: dict | None = None,
          feed_sink: list | None = None,
          gap_sink: list | None = None) -> list:
    issues = _get_all(
        f"{API}/repos/{repo}/issues?state=open"
        f"&labels=dispatch-queued", token)
    results = []
    contexts = []
    for issue in issues:
        if "pull_request" in issue:
            continue
        comments = _get_all(
            f"{API}/repos/{repo}/issues/{issue['number']}/comments",
            token)
        verdict = classify(issue, comments, now, flag_min,
                           escalate_min, timeboxes=timeboxes)
        results.append(verdict)
        if feed_sink is not None:
            feed_sink.append(feed_row(issue, comments, verdict,
                                      timeboxes, now))
        contexts.append({"issue": issue, "comments": comments,
                         "verdict": verdict})
    if apply:
        _run_auto_claim(repo, token, now, contexts, timeboxes,
                        gap_sink)
    for ctx in contexts:
        verdict = ctx["verdict"]
        if not apply or not verdict["action"]:
            continue
        if verdict["action"] in ("auto-claimed", "exception-escalated",
                                  "lease-released"):
            continue  # handled by the QUE #5286 leg above
        issue = ctx["issue"]
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


def _run_auto_claim(repo: str, token: str, now: datetime,
                    contexts: list, timeboxes: dict | None,
                    gap_sink: list | None) -> None:
    """QUE #5286 leg of the sweep: plan auto-claims in #5283 rank
    order, execute claims / lease releases / exception escalations,
    and emit the SIE gap records. Mutates verdicts in place."""
    candidates = []
    for ctx in contexts:
        verdict = ctx["verdict"]
        tb = (timeboxes or {}).get(verdict.get("entry")) \
            if verdict.get("entry") else None
        _, wall_in_min = task_ranking.nearest_wall(tb, now)
        claim = claim_of(ctx["comments"])
        at_dt = None
        if claim and claim.get("at"):
            try:
                at_dt = datetime.strptime(
                    claim["at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc)
            except (ValueError, TypeError):
                at_dt = None
        tier_index = TIER_LADDER.index(verdict["tier"]) \
            if verdict.get("tier") in TIER_LADDER else 0
        feed_state = _FEED_STATES.get(verdict["state"], "queued")
        score_row = {"tier": {"index": tier_index},
                     "age_min": verdict["age_min"], "state": feed_state,
                     "wall_in_min": wall_in_min}
        score_row["score"] = task_ranking.score_dispatch(score_row)
        candidates.append({
            "issue": ctx["issue"], "comments": ctx["comments"],
            "verdict": verdict, "score_row": score_row,
            "wall_in_min": wall_in_min,
            "claim": {"at_dt": at_dt} if claim else None})
    plan_result = auto_claim.plan(candidates, now)
    ctx_by_issue = {c["issue"]["number"]: c for c in contexts}

    for rel in plan_result["releases"]:
        ctx = ctx_by_issue[rel["issue"]]
        base = f"{API}/repos/{repo}/issues/{rel['issue']}"
        try:
            _request("POST", f"{base}/comments", token,
                     {"body": auto_claim.lease_release_comment(
                         claim_class=rel["claim_class"],
                         claimant=rel["claimant"], now=now)})
            _request("DELETE", f"{base}/labels/dispatch-claimed",
                     token)
            ctx["verdict"]["action"] = "lease-released"
        except Exception as exc:
            ctx["verdict"]["action"] = f"ERROR: {exc}"
            ctx["verdict"]["state"] = "error"

    for claim in plan_result["claims"]:
        ctx = ctx_by_issue[claim["issue"]]
        verdict = ctx["verdict"]
        base = f"{API}/repos/{repo}/issues/{claim['issue']}"
        try:
            _request("POST", f"{base}/comments", token,
                     {"body": auto_claim.auto_claim_comment(
                         claim_class=claim["claim_class"],
                         claimant=claim["claimant"],
                         rank=claim["rank"], score=claim["score"],
                         now=now, trigger=claim["trigger"])})
            _request("POST", f"{base}/labels", token,
                     {"labels": ["dispatch-claimed"]})
            try:
                _request("DELETE", f"{base}/labels/dispatch-escalated",
                         token)
            except Exception:
                pass  # label may not be present; the claim stands
            verdict["action"] = "auto-claimed"
            verdict["state"] = "claimed"
        except Exception as exc:
            try:
                _request("POST", f"{base}/comments", token,
                         {"body": "[MUSEai]@{role:{dispatch-watchdog}} "
                                  f"auto-claim-failed: {exc}"})
            except Exception:
                pass
            verdict["action"] = f"ERROR: {exc}"
            verdict["state"] = "error"
            plan_result["exceptions"].append(
                {"issue": claim["issue"], "kind": "rejected",
                 "reason": f"claim POST failed: {exc}"})

    for exc in plan_result["exceptions"]:
        ctx = ctx_by_issue.get(exc["issue"])
        if ctx is None or ctx["verdict"].get("action") != "escalate":
            continue  # already-escalated exceptions never re-fire
        verdict = ctx["verdict"]
        base = f"{API}/repos/{repo}/issues/{exc['issue']}"
        try:
            body = escalation_comment(ctx["issue"],
                                      verdict["age_min"], verdict)
            body += (f"\n\nauto-claim: NOT PLACED — {exc['reason']} "
                     f"(QUE #5286: escalation is the exception; the "
                     f"reason is stamped, never silence).")
            if verdict.get("stall_breach"):
                body += (f"\n\nstall-event: stall_ceiling_breach "
                         f"age_min={verdict['age_min']:.0f} "
                         f"ceiling_min={auto_claim.STALL_CEILING_MIN}")
            _request("POST", f"{base}/comments", token,
                     {"body": body})
            _request("POST", f"{base}/labels", token,
                     {"labels": ["dispatch-escalated"]})
            verdict["action"] = "exception-escalated"
        except Exception as exc2:
            verdict["action"] = f"ERROR: {exc2}"
            verdict["state"] = "error"

    if gap_sink is not None:
        gap_sink.extend(auto_claim.gap_records(plan_result, now))


# ------------------------------------------------- dispatch-state feed (#4350)
# Schema dispatch-state-feed/v1: the web-visible stamp of the state this
# sweep already computes. The collector reuses classify / current_tier /
# thresholds_for / has_claim verbatim -- it re-derives NOTHING. Absent
# values stay null, never zero-filled. The watchdog writes the feed ONLY
# when its content changed (generated_at excluded), and the workflow
# commits that write (canon + dashboard mirror, byte-identical).
FEED_SCHEMA = "dispatch-state-feed/v1"
FEED_PATHS = ("ops/challenge/dispatch-state-feed.json",
              "apps/tribute-dashboard/data/dispatch-state-feed.json")
_FEED_STATES = {"claimed": "claimed", "escalated": "escalated"}


def claim_of(comments: list) -> dict | None:
    """The claim of record from the first PRODUCER CLAIM comment:
    {by, at} -- by = the claiming role (header or `- role:` line, else
    the `- producer:` line), at = the comment's `- claimed at:` stamp,
    else the comment's own creation time. None when no claim comment
    exists (a label-only claim carries no by/at of record)."""
    for c in comments:
        body = c.get("body") or ""
        if CLAIM_MARKER not in body:
            continue
        by = None
        for pat in (r"@\{role:\{([^}]+)\}\}", r"^-\s*role:\s*(.+)$",
                    r"^-\s*producer:\s*(.+)$"):
            m = re.search(pat, body, re.M)
            if m:
                by = m.group(1).strip()
                break
        m = re.search(r"^-\s*claimed at:\s*(\S+)", body, re.M)
        out = {"by": by, "at": m.group(1) if m else c.get("created_at")}
        if c.get("html_url"):
            out["ref"] = c["html_url"]
        return out
    return None


def stall_events_of(comments: list) -> list:
    """Machine stall events: one {at, kind} per `stall-event:` line in
    the issue's comments (at = the carrying comment's creation time,
    kind = the line's first token after the marker)."""
    out = []
    for c in comments:
        for line in (c.get("body") or "").splitlines():
            line = line.strip()
            if line.startswith(STALL_EVENT_MARKER):
                rest = line[len(STALL_EVENT_MARKER):].strip()
                kind = rest.split()[0].rstrip(":,") if rest else "stall"
                out.append({"at": c.get("created_at"), "kind": kind})
    return out


def feed_row(issue: dict, comments: list, verdict: dict,
             timeboxes: dict | None, now: datetime) -> dict:
    """One feed row for an open dispatch, from the sweep's verdict."""
    tb = (timeboxes or {}).get(verdict.get("entry")) \
        if verdict.get("entry") else None
    tier_index, tier_name = current_tier(tb, now)
    wall_iso, wall_in_min = task_ranking.nearest_wall(tb, now)
    claim = claim_of(comments)
    stalls = stall_events_of(comments)
    if claim:
        # QUE #5286 point 2: a claim resolves the STALL (never the
        # task) -- open stall events close with the claim as their
        # resolution ref, and the stall clock stops.
        for event in stalls:
            event["resolved"] = True
            event["resolution"] = (
                f"claim by {claim.get('by')} at {claim.get('at')}"
                + (f" ({claim['ref']})" if claim.get("ref") else ""))
    return {
        "issue": issue["number"],
        "title": issue.get("title"),
        "entry": entry_of(comments),
        "state": _FEED_STATES.get(verdict["state"], "queued"),
        "claim": claim,
        "age_min": verdict["age_min"],
        "nearest_wall": wall_iso,
        "wall_in_min": wall_in_min,
        "tier": {"index": tier_index, "name": tier_name},
        "thresholds_min": {"flag": verdict["flag_min"],
                           "escalate": verdict["escalate_min"]},
        "stall_events": stalls,
    }


def build_feed(rows: list, now: datetime) -> dict:
    counts = {"queued": 0, "claimed": 0, "escalated": 0}
    for r in rows:
        counts[r["state"]] += 1
    # QUE #5283: score + rank on every dispatch (method
    # que-task-rank/v1, additive -- counts/measurement unchanged).
    # Ranking derives from row content only, so the write-on-change
    # fingerprint below stays a content gate, not a clock gate.
    ranked, ranking = task_ranking.rank_dispatches(rows)
    return {"schema": FEED_SCHEMA,
            "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "dispatch-watchdog",
            # frozen envelope (#4350 schema freeze): counts keyed by
            # state EXACTLY -- the distribution chart consumes the
            # keys directly, so no extra keys (no total) ride along
            "counts": counts,
            "ranking": ranking,
            "dispatches": sorted(ranked, key=lambda r: r["issue"])}


def feed_fingerprint(feed: dict) -> str:
    """Content identity excluding generated_at: the change gate."""
    stable = {k: v for k, v in feed.items() if k != "generated_at"}
    return json.dumps(stable, sort_keys=True)


def write_feed(feed: dict, root: str = ".") -> bool:
    """Stamp the feed at BOTH paths (byte-identical) ONLY when its
    content changed vs the canon file of record. Returns True when a
    write landed."""
    canon = os.path.join(root, FEED_PATHS[0])
    try:
        with open(canon, encoding="utf-8") as fh:
            existing = json.load(fh)
        if feed_fingerprint(existing) == feed_fingerprint(feed):
            return False
    except (OSError, ValueError):
        pass
    blob = json.dumps(feed, indent=1, sort_keys=True) + "\n"
    for rel in FEED_PATHS:
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(blob)
    return True


def render_table(results: list) -> str:
    lines = ["issue | entry | tier | state | age_min | action",
             "--- | --- | --- | --- | --- | ---"]
    for r in sorted(results, key=lambda r: r["issue"]):
        lines.append(f"#{r['issue']} | {r.get('entry') or '—'} | "
                     f"{r.get('tier') or '—'} | {r['state']} | "
                     f"{r['age_min']} | {r['action'] or '—'}")
    return "\n".join(lines)


GAP_FEED_PATH = "ops/que/feeds/stall-gap-feed.json"


def write_gap_feed(feed: dict) -> bool:
    """Write-on-change for the SIE stall-gap feed (QUE #5286 point
    5): same content gate as the dispatch-state feed. Returns True
    when a write landed."""
    path = os.path.join(_repo_root(), GAP_FEED_PATH)
    existing = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            existing = json.load(fh)
    if existing is not None and \
            _feed_fingerprint(existing) == _feed_fingerprint(feed):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(feed, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return True


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
    feed_rows: list = []
    gap_records: list = []
    results = sweep(args.repo, token, now, args.flag_min,
                    args.escalate_min, apply=not args.dry_run,
                    timeboxes=timeboxes, feed_sink=feed_rows,
                    gap_sink=gap_records)
    if not args.dry_run:
        stamped = write_feed(build_feed(feed_rows, now))
        print(f"dispatch-state feed: {'stamped (content changed)' if stamped else 'unchanged — no write'} "
              f"({len(feed_rows)} open dispatch(es))")
        gap_stamped = write_gap_feed(auto_claim.gap_feed(gap_records,
                                                          now))
        print(f"stall-gap feed: {'stamped (content changed)' if gap_stamped else 'unchanged — no write'} "
              f"({len(gap_records)} gap record(s) this cycle)")
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
