"""Offline tests for multi-course intake / countdown / .ics
(study_courses.py, RFP-D1-4). All dates fixed — deterministic."""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_courses import (exam_countdown, export_ics,  # noqa: E402
                           intake_courses, validate_ics)

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)

BIO = {"course": "BIO 101", "exam_date": "2026-11-17",
       "weeks": [{"week": 1, "due": "quiz 1",
                  "topics": ["cell structure", "membranes"]},
                 {"week": 2, "due": "midterm",
                  "topics": ["photosynthesis"]}]}
HIST = {"course": "HIST 210", "exam_date": "2026-11-20",
        "weeks": [{"week": 1, "due": "essay",
                   "topics": ["causes of WWI"]}]}
CHEM = {"course": "CHEM 110",  # no exam_date: countdown unset
        "weeks": [{"week": 1, "due": "lab", "topics": ["stoichiometry"]}]}


def test_countdown_math_and_milestones():
    cd = exam_countdown(BIO, NOW)
    assert cd["days_remaining"] == 14
    assert cd["weeks_remaining"] == 2.0
    assert cd["urgency"] == "ahead"
    labels = [m["label"] for m in cd["milestones"]]
    assert labels[0].endswith("final review begins")
    assert labels[-1].endswith("EXAM")
    first = cd["milestones"][0]
    assert first["date"] == "2026-11-03" and first["reached"] is True
    exam = cd["milestones"][-1]
    assert exam["date"] == "2026-11-17" and exam["days_before_exam"] == 0
    assert cd["pace"]["sessions_remaining"] == cd["total_sessions"]
    assert cd["pace"]["sessions_per_day"] == round(
        cd["total_sessions"] / 14, 2)


def test_countdown_unset_today_and_past():
    unset = exam_countdown(CHEM, NOW)
    assert unset["urgency"] == "unset" and unset["milestones"] == []
    today = exam_countdown({**BIO, "exam_date": "2026-11-03"}, NOW)
    assert today["days_remaining"] == 0 and today["urgency"] == "today"
    past = exam_countdown({**BIO, "exam_date": "2026-11-01"}, NOW)
    assert past["days_remaining"] == -2 and past["urgency"] == "past"
    assert past["pace"] is None


def test_intake_multiple_courses_and_totals():
    bundle = intake_courses([BIO, HIST, CHEM], now=NOW)
    assert bundle["course_count"] == 3
    assert [c["course"] for c in bundle["courses"]] == [
        "BIO 101", "HIST 210", "CHEM 110"]
    per_course = [c["plan"]["total_sessions"] for c in bundle["courses"]]
    assert bundle["total_sessions"] == sum(per_course)
    assert all(c["plan"]["course"] == c["course"]
               for c in bundle["courses"])
    assert bundle["schema"] == "studysprint-courses-receipt/v1"


def test_conflict_flags_same_week_and_close():
    bundle = intake_courses([BIO, HIST], now=NOW)  # Nov 17 vs Nov 20
    kinds = {f["type"] for f in bundle["conflicts"]}
    assert kinds == {"same-week-exams"}
    far = intake_courses(
        [BIO, {**HIST, "exam_date": "2026-12-20"}], now=NOW)
    assert far["conflicts"] == []
    close = intake_courses(
        [{**BIO, "exam_date": "2026-11-16"},
         {**HIST, "exam_date": "2026-11-23"}], now=NOW)  # Mon vs next Mon
    assert {f["type"] for f in close["conflicts"]} == {
        "exams-within-7-days"}


def test_export_ics_validates_and_dates_correct():
    bundle = intake_courses([BIO, HIST], now=NOW)
    ics = export_ics(bundle, "2026-11-02", now=NOW)  # a Monday
    assert ics.startswith("BEGIN:VCALENDAR")
    assert "\r\n" in ics
    check = validate_ics(ics)
    assert check["valid"] is True
    sessions = bundle["total_sessions"]
    milestones = sum(len(c["countdown"]["milestones"])
                     for c in bundle["courses"])
    assert check["events"] == sessions + milestones
    # first BIO session: week 1, first weekday (Mon 2026-11-02) 17:00Z
    assert "DTSTART:20261102T170000Z" in ics
    # BIO exam day milestone lands on the exam date at 09:00Z
    assert "DTSTART:20261117T090000Z" in ics
    assert "SUMMARY:BIO 101: EXAM" in ics


def test_export_ics_deterministic_uids_and_escaping():
    bundle = intake_courses([BIO], now=NOW)
    a = export_ics(bundle, "2026-11-02", now=NOW)
    b = export_ics(bundle, "2026-11-02", now=NOW)
    assert a == b  # same inputs -> identical export (stable UIDs)
    weird = intake_courses(
        [{**BIO, "course": "BIO, 101; hard"}], now=NOW)
    ics = export_ics(weird, "2026-11-02", now=NOW)
    assert "BIO\\, 101\\; hard" in ics  # summaries escaped per RFC 5545
    assert validate_ics(ics)["valid"] is True


def test_validate_ics_rejects_bad_text():
    assert validate_ics("BEGIN:VCALENDAR\nBEGIN:VEVENT\nEND:VEVENT")[
        "valid"] is False
    assert validate_ics("BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")[
        "events"] == 0
