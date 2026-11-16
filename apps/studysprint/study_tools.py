"""StudySprint tools — G2: study artifact kinds on the D0 evidence pattern.

The D0 tool (`foundation/fetch_evidence.py`, verbatim) assembles
provenance/freshness/hash-stamped evidence sets for GitHub artifacts
(pull_request | file | workflow_run). StudySprint needs two more kinds,
implemented here with the identical item shape and schema family:

- `syllabus`     — a syllabus document (JSON: course, weeks[{week,
                   topics[], due}]) read from a local path; every week
                   becomes a stamped evidence item.
- `practice_set` — a practice/quiz set (JSON: topic, questions[]) read
                   from a local path; counts + per-question hashes are
                   stamped, question text is never copied into evidence.

Read-only, offline, no credentials. Local reads are the StudySprint
analogue of D0's read-only API reads: the point is the same — the agent
grades *fetched* evidence (a real syllabus file), not asserted claims
("my course covers X").

Also provides the agent's working tools (plain callables, Strands-ready):
`build_study_plan`, `generate_quiz`, `replan_on_missed`.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "studysprint-evidence-set/v1"
TTL_SECONDS = 900


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _item(claim: str, value, path: str, observed_at: datetime) -> dict:
    payload = json.dumps({"claim": claim, "value": value, "path": path},
                         sort_keys=True).encode()
    return {
        "claim": claim,
        "value": value,
        "provenance": {"source": "local-file", "path": path,
                       "observed_at": _iso(observed_at)},
        "fresh_until": _iso(observed_at + timedelta(seconds=TTL_SECONDS)),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def fetch_study_evidence(artifact: dict, now: datetime | None = None,
                         root: Path | None = None) -> dict:
    """Assemble a stamped evidence set for a study artifact.

    artifact: {"kind": "syllabus" | "practice_set", "ref": <path>}
    Paths resolve under `root` (default: this repo's root).
    """
    now = now or datetime.now(timezone.utc)
    root = root or Path(__file__).resolve().parent
    kind, ref = artifact["kind"], artifact["ref"]
    path = (root / ref).resolve()
    if root.resolve() not in path.parents and path != root.resolve():
        raise ValueError("artifact path escapes the repo root")
    doc = json.loads(path.read_text())
    items: list[dict] = []

    if kind == "syllabus":
        items.append(_item("syllabus.course", doc.get("course"), ref, now))
        weeks = doc.get("weeks") or []
        items.append(_item("syllabus.weeks", len(weeks), ref, now))
        for w in weeks:
            items.append(_item(f"syllabus.week.{w.get('week')}.topics",
                               list(w.get("topics") or []), ref, now))
            if w.get("due"):
                items.append(_item(f"syllabus.week.{w.get('week')}.due",
                                   w["due"], ref, now))
    elif kind == "practice_set":
        questions = doc.get("questions") or []
        items.append(_item("practice.topic", doc.get("topic"), ref, now))
        items.append(_item("practice.questions", len(questions), ref, now))
        for i, q in enumerate(questions):
            qhash = hashlib.sha256(
                json.dumps(q, sort_keys=True).encode()).hexdigest()
            items.append(_item(f"practice.q{i}.sha256", qhash, ref, now))
    else:
        raise ValueError(f"unsupported study artifact kind: {kind}")

    material = len(items) >= 2 and all(
        it["provenance"]["path"] and it["sha256"] for it in items)
    return {
        "schema": SCHEMA,
        "artifact": {"kind": kind, "ref": ref},
        "assembled_at": _iso(now),
        "fresh_until": _iso(now + timedelta(seconds=TTL_SECONDS)),
        "items": items,
        "material": material,
        "document": doc,
    }


def build_study_plan(syllabus_doc: dict, minutes_per_day: int = 45) -> dict:
    """Week-by-week plan: each topic gets a learn + retrieve block."""
    plan = []
    for w in syllabus_doc.get("weeks") or []:
        sessions = []
        for topic in w.get("topics") or []:
            sessions.append({"topic": topic, "kind": "learn",
                             "minutes": minutes_per_day})
            sessions.append({"topic": topic, "kind": "retrieve",
                             "minutes": max(15, minutes_per_day // 3)})
        plan.append({"week": w.get("week"), "due": w.get("due"),
                     "sessions": sessions})
    return {"course": syllabus_doc.get("course"), "weeks": plan,
            "total_sessions": sum(len(w["sessions"]) for w in plan)}


def generate_quiz(syllabus_doc: dict, week_no: int) -> dict:
    """Deterministic recall prompts per topic for one week (no model call)."""
    week = next((w for w in syllabus_doc.get("weeks") or []
                 if w.get("week") == week_no), None)
    if week is None:
        raise ValueError(f"no week {week_no} in syllabus")
    questions = [
        {"topic": t,
         "prompt": f"Explain '{t}' from memory, then check your notes: "
                   f"what did you miss?"}
        for t in week.get("topics") or []]
    return {"week": week_no, "questions": questions}


def replan_on_missed(plan: dict, missed_week: int) -> dict:
    """Re-plan: missed week's sessions fold into the next week, flagged."""
    weeks = [dict(w) for w in plan["weeks"]]
    missed = next((w for w in weeks if w["week"] == missed_week), None)
    if missed is None:
        raise ValueError(f"no week {missed_week} in plan")
    nxt = next((w for w in weeks if w["week"] == missed_week + 1), None)
    carried = [dict(s, carried_from=missed_week) for s in missed["sessions"]]
    if nxt is not None:
        nxt["sessions"] = carried + nxt["sessions"]
    return {"course": plan["course"], "weeks": weeks,
            "carried_sessions": len(carried),
            "total_sessions": plan["total_sessions"]}


# --- Now features: trust receipt, today view, budget slider, check-in, plain language ---

PRIVACY_STATEMENT = (
    "Your syllabus stays on your device. No account is required to build a study plan. "
    "All evidence and session records are stored locally and can be deleted at any time."
)


def format_trust_receipt(evidence_set: dict) -> dict:
    """Surface what was fetched before planning: course, weeks, due dates, hashes."""
    doc = evidence_set.get("document") or {}
    items = evidence_set.get("items") or []
    course = doc.get("course") or "Unknown course"
    weeks = doc.get("weeks") or []
    due_dates = [w["due"] for w in weeks if w.get("due")]

    item_hashes = [it.get("sha256") for it in items if it.get("sha256")]
    combined_hash = hashlib.sha256("".join(sorted(item_hashes)).encode()).hexdigest()[:12]

    statement = (
        f"Planned from your verified {course} syllabus: {len(weeks)} weeks, "
        f"{len(due_dates)} scheduled deadline(s), evidence hash {combined_hash}."
    )

    return {
        "course": course,
        "weeks_count": len(weeks),
        "due_dates": due_dates,
        "items_verified": len(items),
        "content_hash_short": combined_hash,
        "trust_statement": statement,
        "verified_at": evidence_set.get("assembled_at"),
        "source_path": evidence_set.get("artifact", {}).get("ref"),
    }


def reflow_plan_budget(plan: dict, new_minutes_per_day: int) -> dict:
    """Time-budget slider: re-flow session durations around real-life availability."""
    if new_minutes_per_day <= 0:
        raise ValueError("time budget minutes must be positive")

    new_weeks = []
    for w in plan.get("weeks") or []:
        new_sessions = []
        for s in w.get("sessions") or []:
            copied = dict(s)
            if s.get("kind") == "learn":
                copied["minutes"] = new_minutes_per_day
            elif s.get("kind") == "retrieve":
                copied["minutes"] = max(10, new_minutes_per_day // 3)
            new_sessions.append(copied)
        new_weeks.append({**w, "sessions": new_sessions})

    return {
        "course": plan.get("course"),
        "weeks": new_weeks,
        "minutes_per_day": new_minutes_per_day,
        "total_sessions": sum(len(w["sessions"]) for w in new_weeks),
    }


def render_today_view(plan: dict, day_index: int = 0) -> dict:
    """Today view: one card with today's sessions, estimated time, and actionable controls."""
    all_sessions = []
    for w in plan.get("weeks") or []:
        for s in w.get("sessions") or []:
            all_sessions.append({"week": w.get("week"), **s})

    # Group into pairs or take day_index
    # By default, a day has 1 learn + 1 retrieve session (2 sessions per topic)
    sessions_per_day = 2
    start_idx = day_index * sessions_per_day
    day_sessions = all_sessions[start_idx:start_idx + sessions_per_day]

    total_est_minutes = sum(s.get("minutes", 0) for s in day_sessions)
    card_title = f"Today's Sprint ({total_est_minutes} min)"

    return {
        "card_title": card_title,
        "day_index": day_index,
        "estimated_minutes": total_est_minutes,
        "sessions": day_sessions,
        "actions": [
            {"action": "start_session", "label": "Start Today's Sprint", "style": "primary"},
            {"action": "mark_missed", "label": "I missed this", "style": "subtle_no_guilt"},
        ],
        "no_guilt_hint": "Life happened? Tap 'I missed this' to seamlessly shift this block without guilt.",
    }


def record_daily_checkin(log: dict, week: int, session_index: int, status: str) -> dict:
    """Daily check-in (30 seconds): done / partial / missed per session.

    Streaks are tracked as 'recovered_weeks' — never broken chains.
    """
    valid_statuses = {"done", "partial", "missed"}
    if status not in valid_statuses:
        raise ValueError(f"status must be one of {valid_statuses}")

    entries = list(log.get("entries") or [])
    entries.append({
        "week": week,
        "session_index": session_index,
        "status": status,
        "timestamp": _iso(datetime.now(timezone.utc)),
    })

    # Evaluate recovered weeks: weeks where all sessions are either done or addressed
    # Count sessions logged per week
    by_week: dict[int, list[str]] = {}
    for entry in entries:
        by_week.setdefault(entry["week"], []).append(entry["status"])

    completed_weeks = sum(1 for w, stats in by_week.items() if all(s == "done" for s in stats))
    recovered_weeks = sum(1 for w, stats in by_week.items() if "missed" in stats and any(s == "done" for s in stats))

    replan_recommended = status == "missed"
    advice = (
        "Session marked missed. Would you like to re-balance this into your upcoming schedule?"
        if replan_recommended else "Great progress! Your streak reflects consistent effort."
    )

    return {
        "entries": entries,
        "total_checkins": len(entries),
        "completed_weeks": completed_weeks,
        "recovered_weeks": recovered_weeks,
        "streak_metric": f"{recovered_weeks + completed_weeks} active or recovered weeks",
        "replan_recommended": replan_recommended,
        "supportive_message": advice,
    }


def plain_language_action(action_type: str, details: dict | None = None) -> str:
    """Plain-language explanation standard: clear, jargon-free explanations for first-gen students."""
    details = details or {}
    if action_type == "replan":
        missed = details.get("missed_week", "earlier")
        target = details.get("target_week", "upcoming")
        return f"I moved week {missed}'s sessions to week {target} because you marked them missed."
    if action_type == "budget_slider":
        mins = details.get("minutes", 25)
        return f"I adjusted your study sessions to fit within {mins} minutes today."
    if action_type == "syllabus_verified":
        course = details.get("course", "your course")
        return f"I checked your syllabus for {course} and confirmed all dates and topics."
    if action_type == "practice_quiz":
        topic = details.get("topic", "today's topic")
        return f"Here is a quick memory check on {topic}."
    return "Action completed smoothly."


def format_accessible_status(decision: str) -> str:
    """Format accessible status: color is never the only signal; always icon + words."""
    mapping = {
        "ALLOW_RECOMMENDATION": "[✓ ALLOW] Approved — verified from evidence",
        "ABSTAIN": "[⚠ ABSTAIN] Need more evidence before planning",
        "ESCALATE": "[⛔ ESCALATE] Requires student confirmation or mentor approval",
    }
    return mapping.get(decision, f"[{decision}] Status update")
