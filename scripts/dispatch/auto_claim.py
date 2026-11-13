#!/usr/bin/env python3
"""QUE auto-claim + auto-resolve (QUE #5286): close the escalation
stall. Pure decision logic for the dispatch watchdog's claim leg;
the watchdog performs the API effects.

Timing decision of record (owner c.6843045932, QDesk decision
c.6843060529, Cadence countersign c.6843070784 — binding on landing):
claim AT escalation, in the same watchdog pass, in #5283 rank order
(que-task-rank/v1); precedence {tighter priority_timebox tier >
wall-bound <=48h claim-on-admission > standard unclaimed >15m};
stall_escalation is same-pass as the claim; a stall reaching 30m
unclaimed emits a stall_ceiling_breach stall event; a claim stops
the stall clock; post-claim escalation is exception-only.

Hard boundary: value-class / owner-gated work is NEVER auto-claimed
(it escalates by design, with the reason stamped). A machine claim
resolves the STALL, never the task: completion still needs its own
done-evidence.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

AUTO_CLAIM_MARKER = "<!-- auto-claim:v1 -->"
LEASE_RELEASE_MARKER = "<!-- auto-claim-lease-release:v1 -->"
CLAIM_FAILED_MARKER = "auto-claim-failed:"
STANDARD_ESCALATE_MIN = 15       # timing decision: supersedes BASE 60
STALL_CEILING_MIN = 30           # stall-to-claim ceiling (breach = event)
WALL_ADMISSION_MIN = 48 * 60     # wall-bound <=48h claims on admission
# Lease windows per claim class (claim-machinery defaults of this
# build, not governor thresholds): a claim with no execution state
# change inside its window releases back to the pool for re-claim.
LEASE_WINDOW_MIN = {"executor": 120, "seat-queue": 240, "named-executor": 240}
GATED_LABELS = {"value-class", "owner-gated", "owner-hand"}
GATED_MARKERS = ("participation_set", "countersign-required", "owner-hand")

_CLAIM_CLASS_RE = re.compile(r"claim-class:\s*(executor|seat-queue|named:\s*\S+)",
                             re.I)
_EXECUTOR_OF_RECORD_RE = re.compile(r"executor of record:\s*([^\n·|]+)", re.I)
_SWARM_ROUTE_RE = re.compile(r'"route":\s*"([^"]+)"')
_LEASE_RE = re.compile(r"^- auto-claim: class=(\S+) claimant=(\S+) "
                       r"lease_expires=(\S+)", re.M)


def _bodies(issue, comments):
    yield issue.get("body") or ""
    for c in comments:
        yield c.get("body") or ""


def is_gated(issue, comments) -> str | None:
    """Reason string when the filing is value-class / owner-gated
    (never auto-claimed), else None."""
    labels = {l.get("name") for l in issue.get("labels") or []
              if isinstance(l, dict)}
    hit = labels & GATED_LABELS
    if hit:
        return f"gated label: {sorted(hit)[0]}"
    for body in _bodies(issue, comments):
        for marker in GATED_MARKERS:
            if marker in body:
                return f"gated marker: {marker}"
    return None


def claim_class_of(issue, comments):
    """(claim_class, claimant) the filing's stamp names, else
    (None, None). An explicit `claim-class:` line wins; then a named
    executor of record; then the SWARM-DISPATCH route stamp
    (build-dispatch -> executor, project-task-dispatch -> the QDesk
    seat queue)."""
    for body in _bodies(issue, comments):
        m = _CLAIM_CLASS_RE.search(body)
        if m:
            raw = m.group(1).strip()
            if raw.lower().startswith("named:"):
                return "named-executor", raw.split(":", 1)[1].strip()
            if raw.lower() == "executor":
                return "executor", "dispatch-executor"
            return "seat-queue", "qdesk-seat-queue"
    for body in _bodies(issue, comments):
        m = _EXECUTOR_OF_RECORD_RE.search(body)
        if m:
            return "named-executor", m.group(1).strip()
    body = issue.get("body") or ""
    m = _SWARM_ROUTE_RE.search(body)
    if m:
        if m.group(1) == "build-dispatch":
            return "executor", "dispatch-executor"
        return "seat-queue", "qdesk-seat-queue"
    return None, None


def failed_claim_count(comments) -> int:
    return sum((c.get("body") or "").count(CLAIM_FAILED_MARKER)
               for c in comments)


def lease_of(comments):
    """(claim_class, claimant, lease_expires datetime) parsed from
    the auto-claim comment, else None. Manual claims carry no lease
    and are never reclaimed by this machinery."""
    for c in comments:
        m = _LEASE_RE.search(c.get("body") or "")
        if m:
            try:
                expires = datetime.strptime(
                    m.group(3), "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc)
            except ValueError:
                return None
            return m.group(1), m.group(2), expires
    return None


def has_execution_activity(comments, claim_at: datetime) -> bool:
    """Any non-watchdog comment after the claim = execution state
    change (the claimant or another seat is moving the task)."""
    for c in comments:
        created = c.get("created_at")
        if not created:
            continue
        try:
            when = datetime.strptime(
                created, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        if when > claim_at and "dispatch-watchdog" not in (c.get("body") or ""):
            return True
    return False


def auto_claim_comment(*, claim_class, claimant, rank, score, now,
                       trigger) -> str:
    """claim_task.py-shaped claim (claim_of() parses it verbatim):
    PRODUCER CLAIM header + claimed-at line, with the auto-claim
    machine lines the lease parser and the feed read."""
    stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    expires = now + timedelta(minutes=LEASE_WINDOW_MIN[claim_class])
    expires_s = expires.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"[MUSEai]@{{role:{{dispatch-watchdog}}}} PRODUCER CLAIM — "
        f"auto-claim by rank (QUE #5286).\n\n"
        f"- resolved provider: repo-machinery\n"
        f"- producer: dispatch-watchdog auto-claim for the "
        f"{claim_class} class (claimant of record: {claimant})\n"
        f"- claimed at: {stamp}\n"
        f"- auto-claim: class={claim_class} claimant={claimant} "
        f"lease_expires={expires_s}\n"
        f"- rank: {rank} (que-task-rank/v1 score {score}); "
        f"trigger: {trigger}\n\n"
        f"State: `dispatch-queued` -> `dispatch-claimed` (label "
        f"applied with this claim; `dispatch-escalated` removed — "
        f"the stall is resolved by this claim, the task is not: "
        f"completion still requires its own done-evidence). Lease: "
        f"no execution state change by {expires_s} releases the "
        f"claim back to the pool for re-claim by rank.\n\n"
        f"stall-resolved: auto-claim resolves the open stall "
        f"(claim at {stamp})\n"
        f"{AUTO_CLAIM_MARKER}"
    )


def lease_release_comment(*, claim_class, claimant, now) -> str:
    stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"[MUSEai]@{{role:{{dispatch-watchdog}}}} LEASE RELEASE — "
        f"the auto-claim by {claimant} ({claim_class} class) expired "
        f"with no execution state change inside its lease window "
        f"({stamp}). The claim is released back to the pool for "
        f"re-claim by rank; the stall reopens.\n\n"
        f"stall-event: lease-release class={claim_class} "
        f"claimant={claimant}\n"
        f"{LEASE_RELEASE_MARKER}"
    )


def plan(candidates, now):
    """Plan one watchdog pass. candidates: [{issue, comments,
    verdict, score_row}] where score_row carries the #5283 rank
    inputs {tier:{index}, age_min, state, wall_in_min}. Returns
    {claims: [...], exceptions: [...], releases: [...]} — claims in
    rank order (highest score first)."""
    claims, exceptions, releases = [], [], []
    for cand in candidates:
        issue, comments, verdict = cand["issue"], cand["comments"], cand["verdict"]
        state = verdict.get("state")
        if state == "claimed":
            lease = lease_of(comments)
            if lease and now > lease[2]:
                claim = cand.get("claim") or {}
                claimed_at = claim.get("at_dt")
                if claimed_at and not has_execution_activity(comments, claimed_at):
                    releases.append({"issue": issue["number"],
                                     "claim_class": lease[0],
                                     "claimant": lease[1]})
            continue
        escalated = verdict.get("action") == "escalate" or state == "escalated"
        admission = (cand.get("wall_in_min") is not None
                     and cand["wall_in_min"] <= WALL_ADMISSION_MIN)
        if not (escalated or admission):
            continue
        gated = is_gated(issue, comments)
        if gated:
            exceptions.append({"issue": issue["number"], "reason": gated,
                               "kind": "gated"})
            continue
        claim_class, claimant = claim_class_of(issue, comments)
        if claim_class is None:
            exceptions.append({"issue": issue["number"],
                               "reason": "no claim class named by the filing's stamp",
                               "kind": "unplaceable"})
            continue
        if failed_claim_count(comments) >= 2:
            exceptions.append({"issue": issue["number"],
                               "reason": "claim rejected twice",
                               "kind": "rejected"})
            continue
        scored = dict(cand["score_row"])
        claims.append({"issue": issue["number"], "claim_class": claim_class,
                       "claimant": claimant,
                       "trigger": "escalation" if escalated else "wall-admission",
                       "score": scored.get("score")})
    claims.sort(key=lambda c: (-(c["score"] or 0), c["issue"]))
    for rank, claim in enumerate(claims, start=1):
        claim["rank"] = rank
    return {"claims": claims, "exceptions": exceptions, "releases": releases}


def gap_records(plan_result, now):
    """SIE intake records for one pass: the stall gap class with
    counts (QUE #5286 point 5)."""
    stamp = now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = []
    for claim in plan_result["claims"]:
        records.append({"at": stamp, "kind": "auto_claimed",
                        "issue": claim["issue"],
                        "claim_class": claim["claim_class"],
                        "claimant": claim["claimant"],
                        "trigger": claim["trigger"], "rank": claim["rank"]})
    for exc in plan_result["exceptions"]:
        records.append({"at": stamp, "kind": "placement_failed",
                        "issue": exc["issue"], "reason": exc["reason"],
                        "exception_kind": exc["kind"]})
    for rel in plan_result["releases"]:
        records.append({"at": stamp, "kind": "lease_released",
                        "issue": rel["issue"],
                        "claim_class": rel["claim_class"],
                        "claimant": rel["claimant"]})
    return records


def gap_feed(records, now):
    counts = {"auto_claimed": 0, "placement_failed": 0, "lease_released": 0}
    for rec in records:
        counts[rec["kind"]] = counts.get(rec["kind"], 0) + 1
    return {"schema": "que.stall-gap/v1",
            "generated_at": now.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            "gap_class": "escalation-stall",
            "consumer": "SIE self-repair loop (learn-ledger intake)",
            "counts_this_cycle": counts,
            "records": records}
