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
