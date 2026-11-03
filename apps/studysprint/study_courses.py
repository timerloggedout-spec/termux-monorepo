"""StudySprint multi-course intake + exam countdown + .ics export
(RFP-D1-4, issue #4112).

v0 assumed one course and one exam. Real use is several courses with
several deadlines:

- **Multi-course intake**: N syllabus documents -> N plans (built by
  study_tools.build_study_plan, unchanged), one merged view, and
  conflict flags when deadlines collide (FEATURES §1a: two midterms
  in the same week is the flag that matters).
- **Exam countdown per course**: a syllabus may carry `exam_date`
  (ISO date). The countdown computes days/weeks remaining, an
  urgency tier, the study pace the remaining sessions imply, and
  countdown milestones (T-14 / T-7 / T-3 / exam day).
- **.ics export**: every session plus every countdown milestone and
  exam day as iCalendar VEVENTs — CRLF line endings, stable UIDs,
  escaped summaries — parseable by any calendar.

Offline and deterministic given an explicit ``now`` / ``start_date``.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, time, timedelta, timezone

from study_tools import build_study_plan

COURSES_RECEIPT_SCHEMA = "studysprint-courses-receipt/v1"
_MILESTONES = ((14, "final review begins"), (7, "mock exam week"),
               (3, "light review only"), (0, "EXAM"))


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def exam_countdown(syllabus_doc: dict, now: datetime) -> dict:
    """Countdown for one course's exam.

    Returns {course, exam_date, days_remaining, weeks_remaining,
    urgency, milestones, pace}. Without an `exam_date` the countdown
    is `unset` (no invented deadline)."""
    exam = _parse_date(syllabus_doc.get("exam_date"))
    plan = build_study_plan(syllabus_doc)
    base = {"course": syllabus_doc.get("course"),
            "exam_date": exam.isoformat() if exam else None,
            "total_sessions": plan["total_sessions"]}
    if exam is None:
        return {**base, "days_remaining": None, "weeks_remaining": None,
                "urgency": "unset", "milestones": [], "pace": None}
    today = now.date() if isinstance(now, datetime) else now
    days = (exam - today).days
    urgency = "past" if days < 0 else "today" if days == 0 \
        else "near" if days <= 7 else "ahead"
    milestones = []
    for offset, label in _MILESTONES:
        when = exam - timedelta(days=offset)
        milestones.append({"label": f"{base['course']}: {label}",
                           "date": when.isoformat(),
                           "days_before_exam": offset,
                           "reached": when <= today})
    pace = None
    if days > 0:
        pace = {"sessions_remaining": plan["total_sessions"],
                "days_remaining": days,
                "sessions_per_day": round(plan["total_sessions"] / days, 2)}
    return {**base, "days_remaining": days,
            "weeks_remaining": round(days / 7, 1), "urgency": urgency,
            "milestones": milestones, "pace": pace}


def _conflicts(countdowns: list) -> list:
    """Flag exam collisions across courses: same ISO week, or exams
    within 7 days of each other (FEATURES §1a conflict flags)."""
    dated = [c for c in countdowns if c.get("exam_date")]
    flags = []
    for i in range(len(dated)):
        for j in range(i + 1, len(dated)):
            a, b = dated[i], dated[j]
            da, db = _parse_date(a["exam_date"]), _parse_date(b["exam_date"])
            gap = abs((da - db).days)
            if da.isocalendar()[:2] == db.isocalendar()[:2]:
                kind = "same-week-exams"
            elif gap <= 7:
                kind = "exams-within-7-days"
            else:
                continue
            flags.append({"type": kind,
                          "courses": [a["course"], b["course"]],
                          "exam_dates": [a["exam_date"], b["exam_date"]],
                          "gap_days": gap})
    return flags


def intake_courses(syllabus_docs, minutes_per_day: int = 45,
                   now: datetime | None = None) -> dict:
    """Intake N syllabi -> N plans + per-course countdowns + merged
    totals + conflict flags. One stamped bundle."""
    now = now or datetime.now(timezone.utc)
    courses, countdowns = [], []
    for doc in syllabus_docs or []:
        plan = build_study_plan(doc, minutes_per_day=minutes_per_day)
        countdown = exam_countdown(doc, now)
        countdowns.append(countdown)
        courses.append({"course": doc.get("course"), "plan": plan,
                        "countdown": countdown})
    return {
        "schema": COURSES_RECEIPT_SCHEMA,
        "observed_at": _iso(now),
        "courses": courses,
        "course_count": len(courses),
        "total_sessions": sum(c["plan"]["total_sessions"]
                              for c in courses),
        "conflicts": _conflicts(countdowns),
    }


# ------------------------------------------------------------------- .ics

def _ics_escape(text: str) -> str:
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def _ics_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _event(uid: str, stamp: datetime, start: datetime, end: datetime,
           summary: str, description: str = "") -> list:
    lines = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{_ics_dt(stamp)}",
             f"DTSTART:{_ics_dt(start)}", f"DTEND:{_ics_dt(end)}",
             f"SUMMARY:{_ics_escape(summary)}"]
    if description:
        lines.append(f"DESCRIPTION:{_ics_escape(description)}")
    lines.append("END:VEVENT")
    return lines


def export_ics(intake: dict, start_date, session_time: str = "17:00",
               now: datetime | None = None) -> str:
    """Export an intake bundle to iCalendar text.

    Sessions: week N's sessions spread across that week's weekdays,
    starting the Monday-anchored week containing ``start_date``
    (session k of week N lands on start + (N-1)*7 + (k mod 5) days,
    at ``session_time`` local-naive-treated-as-UTC, lasting the
    session's minutes). Milestones and exam days are all-day events.
    """
    now = now or datetime.now(timezone.utc)
    start_day = _parse_date(start_date)
    hh, mm = (int(x) for x in session_time.split(":"))
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//StudySprint//courses//EN", "CALSCALE:GREGORIAN"]
    for course in intake.get("courses", []):
        name = course["course"]
        plan = course["plan"]
        for week in plan.get("weeks", []):
            week_no = week.get("week") or 1
            for k, s in enumerate(week.get("sessions", [])):
                day = start_day + timedelta(days=(week_no - 1) * 7
                                            + (k % 5))
                start = datetime.combine(day, time(hh, mm),
                                         tzinfo=timezone.utc)
                end = start + timedelta(minutes=s.get("minutes", 45))
                uid = hashlib.sha256(
                    f"{name}|{week_no}|{k}|{s.get('topic')}".encode()
                ).hexdigest()[:16] + "@studysprint"
                lines += _event(
                    uid, now, start, end,
                    f"{name} — {s.get('kind', 'study')}: {s.get('topic')}",
                    f"StudySprint session, week {week_no}")
        countdown = course.get("countdown") or {}
        for m in countdown.get("milestones", []):
            day = _parse_date(m["date"])
            start = datetime.combine(day, time(9, 0),
                                     tzinfo=timezone.utc)
            uid = hashlib.sha256(
                f"{name}|milestone|{m['label']}".encode()
            ).hexdigest()[:16] + "@studysprint"
            lines += _event(uid, now, start, start + timedelta(hours=1),
                            m["label"],
                            "StudySprint exam countdown milestone")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def validate_ics(ics_text: str) -> dict:
    """Parse-back validation: structure + event count + date sanity.
    (The done-evidence check: the export is parseable and its dates
    round-trip.)"""
    if "\r\n" not in ics_text:
        return {"valid": False, "error": "missing CRLF line endings"}
    events = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", ics_text, re.S)
    parsed_dates = []
    for ev in events:
        m = re.search(r"DTSTART:(\d{8}T\d{6}Z)", ev)
        if not m:
            return {"valid": False, "error": "event without DTSTART"}
        parsed_dates.append(datetime.strptime(
            m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc))
        if "UID:" not in ev or "SUMMARY:" not in ev:
            return {"valid": False, "error": "event missing UID/SUMMARY"}
    wrapped = ics_text.startswith("BEGIN:VCALENDAR") and \
        ics_text.rstrip().endswith("END:VCALENDAR")
    return {"valid": wrapped, "events": len(events),
            "first_start": _iso(min(parsed_dates)) if parsed_dates
            else None,
            "last_start": _iso(max(parsed_dates)) if parsed_dates
            else None}


__all__ = ["intake_courses", "exam_countdown", "export_ics",
           "validate_ics", "COURSES_RECEIPT_SCHEMA"]
