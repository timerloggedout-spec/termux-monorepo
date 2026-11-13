#!/usr/bin/env python3
"""QUE task-plane prioritization (QUE #5283): score + rank + claim
order for the dispatch registry feed and the opportunity feed.

Method of record: ``que-task-rank/v1``. The method is a pure function
of feed-row content (never of wall-clock at rank time), so historical
rows re-rank deterministically under the same method version and
rankings stay comparable across versions (backfill doctrine): a
method change bumps METHOD, and re-running this module over archived
rows reproduces the new ranking exactly.

Hard boundary (filing): ranking orders; it never admits, defers,
merges, or claims. Admission thresholds and governor deferral rules
are Cadence custody and are not touched here. Claim order derived
from rank is ADVISORY until a QDesk/Desk decision stamp on #5283
binds it; the delta vs age-order is published every cycle so the
difference is visible before it binds.

Dispatch score components (all derived from the row itself):
- tier: priority_timebox tier index x 20 (BASE 0 .. FINAL 4).
- wall: nearest wall/landing proximity. A wall inside 48h (or past)
  is the imminent class and outranks every non-imminent score; beyond
  48h the term decays linearly to zero at 200h.
- age: age_min, capped at 30 days, scaled to 50.
- state: escalated +40 (escalation weighs up), queued +10,
  claimed 0 (claimed weighs neutral).
"""
from __future__ import annotations

from datetime import datetime, timezone

METHOD = "que-task-rank/v1"
WALL_IMMINENT_H = 48.0
STATE_POINTS = {"escalated": 40.0, "queued": 10.0, "claimed": 0.0}
TERMINAL_STATE_PREFIXES = ("closed", "complete", "landed", "done",
                           "terminal", "cancel", "withdraw")


def parse_iso(value):
    """Parse an ISO-8601 instant (Z or offset) -> aware datetime|None."""
    if not value or not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        when = datetime.fromisoformat(text)
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


def iso(when: datetime) -> str:
    return when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def nearest_wall(timebox, now):
    """(iso, wall_in_min) of the dispatch's nearest wall: the soonest
    upcoming tier instant of its entry's priority_timebox, else the
    most recent past one (an overdue wall), else (None, None). A
    timebox-level `wall` field is the fallback when no tier carries
    an instant."""
    if not timebox:
        return None, None
    instants = []
    for tier in timebox.get("tiers") or []:
        when = parse_iso(tier.get("at") or tier.get("from"))
        if when is not None:
            instants.append(when)
    if not instants:
        when = parse_iso(timebox.get("wall"))
        if when is not None:
            instants.append(when)
    if not instants:
        return None, None
    future = [t for t in instants if t >= now]
    nearest = min(future) if future else max(instants)
    return iso(nearest), round((nearest - now).total_seconds() / 60.0, 1)


def wall_points(wall_in_min):
    """Derived proximity term. Imminent class (<=48h, incl. overdue)
    starts at 1000 so it outranks any non-imminent combination
    (max tier 80 + age 50 + state 40 + decay 152 < 1000)."""
    if wall_in_min is None:
        return 0.0
    hours = wall_in_min / 60.0
    if hours <= WALL_IMMINENT_H:
        return 1000.0 + max(0.0, WALL_IMMINENT_H - min(hours, WALL_IMMINENT_H))
    return max(0.0, 200.0 - hours)


def score_dispatch(row) -> dict:
    """Score one dispatch feed row from its own fields only."""
    tier = row.get("tier") or {}
    tier_index = tier.get("index") or 0
    age_min = row.get("age_min") or 0
    components = {
        "tier": round(float(tier_index) * 20.0, 3),
        "wall": round(wall_points(row.get("wall_in_min")), 3),
        "age": round(min(float(age_min), 43200.0) / 43200.0 * 50.0, 3),
        "state": STATE_POINTS.get(row.get("state"), 0.0),
    }
    return {"score": round(sum(components.values()), 3),
            "components": components}


def rank_dispatches(rows):
    """Annotate dispatch rows with score + rank; return (rows, summary).

    Rows are copied, never mutated in place; the returned list keeps
    the input order (the feed keeps its own sort). Rank is global
    across states; claim_order lists unclaimed issues in rank order;
    the delta compares claim order against the age-only order it
    replaces."""
    annotated = []
    for row in rows:
        entry = dict(row)
        entry.update(score_dispatch(row))
        annotated.append(entry)
    order = sorted(annotated, key=lambda r: (-r["score"], r.get("issue") or 0))
    for rank, entry in enumerate(order, start=1):
        entry["rank"] = rank
    unclaimed = [e for e in order if e.get("state") != "claimed"]
    claim_order = [e.get("issue") for e in unclaimed]
    age_order_rows = sorted(unclaimed,
                            key=lambda r: (-(r.get("age_min") or 0), r.get("issue") or 0))
    age_rank = {e.get("issue"): i + 1 for i, e in enumerate(age_order_rows)}
    delta = []
    for pos, entry in enumerate(unclaimed, start=1):
        if age_rank.get(entry.get("issue")) != pos:
            delta.append({"issue": entry.get("issue"), "rank": pos,
                          "age_rank": age_rank.get(entry.get("issue")),
                          "delta": age_rank.get(entry.get("issue")) - pos})
    summary = {
        "method": METHOD,
        "advisory": True,  # binds only on the QDesk/Desk stamp (#5283 point 4)
        "claim_order": claim_order,
        "age_order": [e.get("issue") for e in age_order_rows],
        "delta_vs_age_order": delta,
        "moved": len(delta),
    }
    return annotated, summary


def is_terminal_state(state) -> bool:
    text = str(state or "").strip().lower()
    return any(text.startswith(p) for p in TERMINAL_STATE_PREFIXES)


def rank_opportunities(rows, states, gates_by_id, now):
    """Re-rank opportunity-priority feed rows (QUE #5283 points 2+3).

    - Terminal/closed opportunities leave the active ranking; they
      are returned separately with their state, never on top.
    - Sub-opportunity gates (gates_by_id: id -> [{name, at}]) become
      their own ranked rows and contribute their nearest wall to the
      parent row (a parent whose next_gate is far but which carries a
      near sub-gate is wall-imminent through the sub-gate).
    - A wall inside 48h (incl. past) outranks any past-gate score:
      active sort is (wall-imminent first, then the feed's score of
      record, then id). Scores themselves are NOT recomputed — the
      score of record stays the cycle's {gate-proximity + prep + tier}
      stamp; ranking is additive."""
    gate_rows = []
    for opp_id, gates in (gates_by_id or {}).items():
        for gate in gates or []:
            when = parse_iso(gate.get("at"))
            if when is None:
                continue
            gate_rows.append({"id": opp_id, "gate": gate.get("name"),
                              "at": iso(when),
                              "hours_to": round((when - now).total_seconds() / 3600.0, 2)})
    gate_rows.sort(key=lambda g: (g["at"], str(g["id"]), str(g["gate"])))
    for rank, gate in enumerate(gate_rows, start=1):
        gate["rank"] = rank

    active, terminal = [], []
    for row in rows:
        entry = dict(row)
        state = (states or {}).get(entry.get("id"))
        entry["state"] = state
        gates = [g for g in gate_rows if g["id"] == entry.get("id")]
        walls = [g["hours_to"] for g in gates]
        if entry.get("days_to_gate") is not None:
            walls.append(float(entry["days_to_gate"]) * 24.0)
        nearest_h = min(walls) if walls else None
        entry["nearest_wall_hours"] = nearest_h
        entry["wall_48h"] = bool(nearest_h is not None and nearest_h <= WALL_IMMINENT_H)
        entry["sub_gates"] = len(gates)
        entry["rank_method"] = METHOD
        if is_terminal_state(state):
            entry["rank"] = None
            entry["active"] = False
            terminal.append(entry)
        else:
            entry["active"] = True
            active.append(entry)
    active.sort(key=lambda e: (not e["wall_48h"], -(e.get("score") or 0), str(e.get("id"))))
    for rank, entry in enumerate(active, start=1):
        entry["rank"] = rank
    return {"active": active, "terminal": terminal, "gate_rows": gate_rows}
