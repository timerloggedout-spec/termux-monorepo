"""Offline tests for the calendar core (study_calendar.py, #4157).

Intake normalization, shift detection + briefings, frequency
ramps, and quiet-hours batching — all deterministic fixtures.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_calendar import (apply_quiet_hours, assessment_briefings,  # noqa: E402
                            frequency_plan, frequency_ramp,
                            intake_calendar)

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)  # a Tuesday

DOC = {
    "classes": [
        {"course": "BIO 101", "days": ["Tue", "Thu"],
         "start": "10:00", "end": "11:15",
         "building": "Science Hall", "room": "204"},
        {"course": "HIST 210", "days": ["Mon"],
         "start": "13:00", "end": "14:30",
         "building": "Liberal Arts", "room": "110"},
    ],
    "assessments": [
        {"course": "BIO 101", "kind": "midterm", "date": "2026-11-05",
         "time": "10:00", "building": "Science Hall", "room": "204"},
        {"course": "BIO 101", "kind": "final", "date": "2026-12-10",
         "time": "18:00", "building": "Gym Annex", "room": "B"},
        {"course": "HIST 210", "kind": "quiz", "date": "2026-11-04",
         "time": "13:00", "building": "Liberal Arts", "room": "110"},
    ],
}


def test_intake_normalizes_records():
    cal = intake_calendar(DOC, NOW)
    assert cal["receipt"]["classes"] == 2
    assert cal["receipt"]["assessments"] == 3
    bio = cal["classes"][0]
    assert bio["days"] == [1, 3]  # Tue, Thu
    assert bio["location"] == "Science Hall 204"
    try:
        intake_calendar({"assessments": [{"kind": "pop-quiz"}]}, NOW)
    except ValueError as e:
        assert "quiz|midterm|final" in str(e)
    else:
        raise AssertionError("bad assessment kind must raise")


def test_briefings_detect_shifts_and_ramp():
    cal = intake_calendar(DOC, NOW)
    briefs = {b["kind"]: b for b in assessment_briefings(cal, NOW)}
    midterm = briefs["midterm"]
    assert midterm["shifted"] is False
    assert midterm["briefing"] is None
    final = briefs["final"]
    assert final["shifted"] is True
    assert any("place" in c for c in final["changes"])
    assert any("time" in c for c in final["changes"])
    assert "Gym Annex B" in final["briefing"]
    quiz = briefs["quiz"]
    assert quiz["days_away"] < midterm["days_away"]
    assert quiz["ramp"]["multiplier"] > midterm["ramp"]["multiplier"]


def test_frequency_tiers_and_plan():
    assert frequency_ramp(1)["multiplier"] == 3.0
    assert frequency_ramp(5)["multiplier"] == 2.0
    assert frequency_ramp(10)["multiplier"] == 1.5
    assert frequency_ramp(30)["multiplier"] == 1.0
    cal = intake_calendar(DOC, NOW)
    plan = frequency_plan(cal, base_per_day=10, now=NOW)
    bio = plan["plan"]["BIO 101"]
    assert bio["driven_by"] == "midterm on 2026-11-05"
    assert bio["per_day"] == 20.0  # 10 x 2.0 (2 days away)
    assert plan["claims_ceiling"].startswith("logistics support")


def test_quiet_hours_batch_during_class():
    cal = intake_calendar(DOC, NOW)
    in_class = datetime(2026, 11, 3, 10, 30, tzinfo=timezone.utc)
    free = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    out = apply_quiet_hours(cal, [{"id": "n1", "at": in_class},
                                  {"id": "n2", "at": free}], NOW)
    assert out["suppressed"] == 1
    assert out["delivered"][0]["id"] == "n2"
    held = out["batched"][0]
    assert held["id"] == "n1" and held["held_by"] == "BIO 101"
    assert held["release_at"].hour == 11 and \
        held["release_at"].minute == 15
