"""StudySprint state recall + adaptive hardening — RFP-D1-6 ⑥
(issue #4159), as its own mode.

Two legs, one discipline: the claims ceilings are IN the receipts.

**State/time/environment recall (encoding specificity, Tulving).**
The context effect is modest (meta-analytic d ≈ 0.28), so the
design is NOT single-room matching. It is (a) varied-context
practice — sessions rotate across places/times/materials so the
memory is not welded to one room — and (b) mental reinstatement
of the exam room (Smith 1979): a short script the student runs
mentally before the exam to re-create the encoding context.

**Adaptive hardening (stress inoculation, Meichenbaum SIT;
working-memory protection under pressure, Jha et al. MMFT).**
Graduated timed drills under exam-like pressure, in SIT phases:
1 conceptualization (learn the format, untimed) → 2 skills
acquisition/rehearsal (timed, calm) → 3 application (timed +
graduated pressure elements). HARDENING IS OPT-IN ONLY — off by
default, the flag rides every receipt — and NO-GUILT binds:
pressure never carries penalties. There are no score deductions
in this module at all; a miss is recorded as "not yet", and every
drill closes with a supportive line. Ceiling: performance under
stress / anxiety — NOT recall gains.

Deterministic: pressure elements are chosen by a seeded rotation
(drill id), so a drill is receipt-reproducible.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

HARDENING_RECEIPT_SCHEMA = "studysprint-hardening-receipt/v1"
RECALL_CEILING = ("context effects are modest (encoding "
                  "specificity, meta d~0.28): varied-context "
                  "practice + mental reinstatement, not "
                  "single-room matching")
HARDENING_CEILING = ("performance under stress/anxiety — not "
                     "recall gains")

DEFAULT_CONTEXTS = [
    {"place": "library desk", "time_of_day": "morning",
     "materials": "paper + pen"},
    {"place": "kitchen table", "time_of_day": "evening",
     "materials": "laptop"},
    {"place": "campus bench", "time_of_day": "afternoon",
     "materials": "phone cards"},
    {"place": "quiet room", "time_of_day": "morning",
     "materials": "printed notes"},
]

PRESSURE_MENU = [
    "visible countdown",
    "ambient exam-hall sounds",
    "strict per-question pacing",
    "one mid-drill interruption card",
    "unfamiliar room (or a picture of one)",
]


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt(kind: str, now: datetime, **fields) -> dict:
    out = {"schema": HARDENING_RECEIPT_SCHEMA, "kind": kind,
           "observed_at": _iso(now)}
    out.update(fields)
    return out


# ------------------------------------------------- varied-context recall

def varied_context_plan(sessions: int,
                        contexts=None) -> dict:
    """Assign a rotating practice context per session: never the
    same place twice in a row when avoidable (rotation by stride,
    deterministic)."""
    contexts = list(contexts or DEFAULT_CONTEXTS)
    if sessions <= 0 or not contexts:
        return {"assignments": []}
    stride = 2 if len(contexts) > 2 else 1
    assignments, last_place = [], None
    idx = 0
    for i in range(sessions):
        ctx = contexts[idx % len(contexts)]
        if ctx["place"] == last_place and len(contexts) > 1:
            idx += 1
            ctx = contexts[idx % len(contexts)]
        assignments.append({"session": i + 1, **ctx})
        last_place = ctx["place"]
        idx += stride
    return {"assignments": assignments,
            "claims_ceiling": RECALL_CEILING}


def reinstatement_script(exam_room: str, course: str) -> dict:
    """The Smith (1979) mental-reinstatement script for exam day:
    re-create the room in the mind, then begin."""
    steps = [
        f"Close your eyes. Picture {exam_room} — the door, the "
        f"clock, where you will sit.",
        "Hear the room: paper, chairs, the invigilator's voice.",
        f"Now picture the first {course} question arriving, and "
        "yourself starting calmly — you have practiced in many "
        "rooms, and this one is just another.",
        "Open your eyes. Begin with the question you know best.",
    ]
    return {"course": course, "exam_room": exam_room,
            "steps": steps, "claims_ceiling": RECALL_CEILING}


# ------------------------------------------------------------ hardening

SIT_PHASES = [
    {"phase": 1, "name": "conceptualization",
     "timed": False, "pressure": [],
     "brief": "Learn the drill format. No clock, no pressure — "
              "just see how it works."},
    {"phase": 2, "name": "rehearsal",
     "timed": True, "pressure": [],
     "brief": "Timed, calm. Practice the skills: pacing, "
              "breathing, moving on from a hard question."},
    {"phase": 3, "name": "application",
     "timed": True, "pressure": "graduated",
     "brief": "Timed with exam-like pressure elements, added "
              "one at a time. The drill is practice — nothing here "
              "can hurt your grade."},
]


def _pressure_for(drill_id: str, count: int) -> list:
    """Deterministic 'randomized' pressure selection: seeded by
    the drill id so the drill is receipt-reproducible."""
    seed = int(hashlib.sha256(str(drill_id).encode()).hexdigest()[:8],
               16)
    picks, seen = [], set()
    i = 0
    while len(picks) < min(count, len(PRESSURE_MENU)):
        pick = PRESSURE_MENU[(seed + i * 3) % len(PRESSURE_MENU)]
        if pick not in seen:
            picks.append(pick)
            seen.add(pick)
        i += 1
    return picks


def plan_hardening_drill(drill_id: str, phase: int,
                         opt_in: bool, now: datetime) -> dict:
    """Plan one hardening drill. OPT-IN ONLY: without opt_in the
    plan is a refusal receipt (the mode is off by default and no
    drill exists). NO-GUILT: nothing in a plan or result carries
    penalties — by construction there is no penalty field."""
    base = _receipt("hardening-plan", now, drill_id=drill_id,
                    opt_in=bool(opt_in),
                    claims_ceiling=HARDENING_CEILING)
    if not opt_in:
        return {**base, "status": "refused",
                "reason": "hardening is opt-in only; this drill "
                          "was not created"}
    if phase not in (1, 2, 3):
        raise ValueError(f"SIT phase must be 1, 2, or 3, got "
                         f"{phase!r}")
    spec = dict(SIT_PHASES[phase - 1])
    if spec["pressure"] == "graduated":
        spec["pressure"] = _pressure_for(drill_id, count=phase - 1)
    return {**base, "status": "planned", **spec,
            "no_guilt": "pressure carries no penalties; a miss is "
                        "'not yet', never a failure"}


def record_drill_result(drill_id: str, answered: int,
                        not_yet: int, opt_in: bool,
                        now: datetime) -> dict:
    """Record a drill's outcome in no-guilt terms: answered +
    'not yet' counts, a supportive close, and NO score, deduction,
    or penalty field — by construction."""
    return _receipt(
        "hardening-result", now, drill_id=drill_id,
        opt_in=bool(opt_in), answered=answered, not_yet=not_yet,
        claims_ceiling=HARDENING_CEILING,
        close="Drill done. The 'not yet' pile is a study list, "
              "not a verdict — it gets smaller every round.")


__all__ = ["varied_context_plan", "reinstatement_script",
           "plan_hardening_drill", "record_drill_result",
           "SIT_PHASES", "PRESSURE_MENU", "DEFAULT_CONTEXTS",
           "RECALL_CEILING", "HARDENING_CEILING",
           "HARDENING_RECEIPT_SCHEMA"]
