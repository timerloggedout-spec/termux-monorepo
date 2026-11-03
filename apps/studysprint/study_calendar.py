"""StudySprint calendar core — RFP-D1-6 builds ①②③ (issue #4157).

The v0.4.0 core knows courses and countdowns; it does not know
where the student physically is, or when. This module is the
calendar/location record layer the rest of RFP-D1-6 consumes
(build B's maps + temple routes read these records):

1. **Calendar intake** — class meetings {days · times ·
   building/room} and assessments {quiz/midterm/final · date ·
   time · location} normalized into records, mergeable with the
   study_courses plans by course name.
2. **Assessment-frequency engine** — question/card frequency ramps
   as a listed assessment approaches (deterministic tiers). An
   assessment at a SHIFTED time or place (vs the class's usual
   pattern) gets an explicit ramp + a briefing that names the
   shift — the student should never be surprised by a moved exam.
3. **Quiet hours** — the notification engine's class-awareness:
   notifications landing inside a scheduled class are suppressed
   and batched to just before / just after the block.

Claims ceiling (binds copy + receipts): calendar awareness is
LOGISTICS support — pacing, timing, and not being surprised. It
carries no learning-gain claim of its own.

Offline and deterministic given explicit times; any network or
map touch is injected by the consumers, never made here.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

CALENDAR_RECEIPT_SCHEMA = "studysprint-calendar-receipt/v1"
CLAIMS_CEILING = ("logistics support (pacing, timing, no-surprises) "
                  "— no learning-gain claim")

_WEEKDAYS = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4,
             "sat": 5, "sun": 6}


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_hm(value: str) -> time:
    hh, mm = str(value).split(":")
    return time(int(hh), int(mm))


def _receipt(kind: str, now: datetime, **fields) -> dict:
    out = {"schema": CALENDAR_RECEIPT_SCHEMA, "kind": kind,
           "observed_at": _iso(now),
           "claims_ceiling": CLAIMS_CEILING}
    out.update(fields)
    return out


# ------------------------------------------------------------ 1. intake

def intake_calendar(doc: dict, now: datetime) -> dict:
    """Normalize a calendar document into records + a receipt.

    doc: {classes: [{course, days: ["Mon", "Wed"], start: "10:00",
                     end: "11:15", building, room}],
          assessments: [{course, kind: quiz|midterm|final,
                         date: "2026-11-20", time: "18:00",
                         building, room}]}
    Times are local-naive HH:MM paired with the date/weekday; the
    records keep them as given (the consumers own timezones)."""
    classes = []
    for c in doc.get("classes") or []:
        days = sorted(_WEEKDAYS[str(d).strip().lower()[:3]]
                      for d in c.get("days") or [])
        classes.append({
            "course": c.get("course"),
            "days": days,
            "start": c.get("start"), "end": c.get("end"),
            "building": c.get("building"), "room": c.get("room"),
            "location": _location(c),
        })
    assessments = []
    for a in doc.get("assessments") or []:
        kind = str(a.get("kind", "")).lower()
        if kind not in ("quiz", "midterm", "final"):
            raise ValueError(
                f"assessment kind must be quiz|midterm|final, "
                f"got {a.get('kind')!r}")
        assessments.append({
            "course": a.get("course"), "kind": kind,
            "date": a.get("date"), "time": a.get("time"),
            "building": a.get("building"), "room": a.get("room"),
            "location": _location(a),
        })
    receipt = _receipt("calendar-intake", now,
                       classes=len(classes),
                       assessments=len(assessments),
                       courses=sorted({c["course"] for c in classes
                                       if c["course"]}))
    return {"classes": classes, "assessments": assessments,
            "receipt": receipt}


def _location(rec: dict) -> str:
    parts = [str(rec.get("building") or "").strip(),
             str(rec.get("room") or "").strip()]
    return " ".join(p for p in parts if p).strip()


def class_pattern(calendar: dict, course: str) -> dict | None:
    """The course's usual pattern (its first class record) — the
    baseline an assessment is compared against for shift
    detection."""
    for c in calendar.get("classes") or []:
        if c.get("course") == course:
            return c
    return None


# ------------------------------------------- 2. frequency + shift ramps

# Deterministic ramp tiers: (max days away, multiplier, label)
RAMP_TIERS = [(2, 3.0, "final-stretch"), (6, 2.0, "exam-week"),
              (13, 1.5, "ramp-up"), (None, 1.0, "baseline")]


def frequency_ramp(days_away: float) -> dict:
    for cap, mult, label in RAMP_TIERS:
        if cap is None or days_away <= cap:
            return {"multiplier": mult, "tier": label}
    raise AssertionError("unreachable")


def assessment_briefings(calendar: dict, now: datetime) -> list:
    """One briefing per upcoming assessment: the frequency ramp,
    and — when the assessment sits at a shifted time or place vs
    the class pattern — the explicit shift briefing."""
    out = []
    for a in calendar.get("assessments") or []:
        when = datetime.combine(
            datetime.fromisoformat(str(a["date"])).date(),
            _parse_hm(a["time"] or "09:00")).replace(
                tzinfo=now.tzinfo)
        days_away = (when - now).total_seconds() / 86400.0
        ramp = frequency_ramp(max(0.0, days_away))
        pattern = class_pattern(calendar, a.get("course"))
        shifted, changes = False, []
        if pattern is not None:
            usual_times = (pattern.get("start") or "")
            if a.get("time") and usual_times and \
                    a["time"] != usual_times:
                shifted = True
                changes.append(
                    f"time {usual_times} -> {a['time']}")
            if a.get("location") and pattern.get("location") and \
                    a["location"] != pattern["location"]:
                shifted = True
                changes.append(
                    f"place {pattern['location']} -> "
                    f"{a['location']}")
        briefing = None
        if shifted:
            briefing = (
                f"SHIFTED {a['kind']} for {a['course']}: "
                + "; ".join(changes)
                + f". It is on {a['date']} at {a['time']} in "
                  f"{a['location']} — not the usual class pattern. "
                  f"Frequency is ramped ({ramp['tier']}, "
                  f"x{ramp['multiplier']}) and the room is new: "
                  f"plan the trip once before the day.")
        out.append({
            "course": a["course"], "kind": a["kind"],
            "date": a["date"], "time": a["time"],
            "location": a["location"],
            "days_away": round(days_away, 2),
            "ramp": ramp, "shifted": shifted, "changes": changes,
            "briefing": briefing,
        })
    return sorted(out, key=lambda b: b["days_away"])


def frequency_plan(calendar: dict, base_per_day: float,
                   now: datetime) -> dict:
    """Per-course question/card frequency for today: the base rate
    scaled by the NEAREST upcoming assessment's ramp per course."""
    briefings = assessment_briefings(calendar, now)
    plan = {}
    for course in sorted({c["course"] for c in
                          calendar.get("classes") or []
                          if c.get("course")}):
        upcoming = [b for b in briefings
                    if b["course"] == course and b["days_away"] >= 0]
        ramp = upcoming[0]["ramp"] if upcoming else \
            {"multiplier": 1.0, "tier": "baseline"}
        plan[course] = {
            "base_per_day": base_per_day,
            "multiplier": ramp["multiplier"], "tier": ramp["tier"],
            "per_day": round(base_per_day * ramp["multiplier"], 2),
            "driven_by": (f"{upcoming[0]['kind']} on "
                          f"{upcoming[0]['date']}"
                          if upcoming else None),
        }
    return _receipt("frequency-plan", now, plan=plan)


# ------------------------------------------------------- 3. quiet hours

def _class_blocks_on(calendar: dict, day) -> list:
    """(start_dt, end_dt, course) blocks for a given date."""
    blocks = []
    for c in calendar.get("classes") or []:
        if day.weekday() in (c.get("days") or []):
            start = datetime.combine(day, _parse_hm(c["start"]))
            end = datetime.combine(day, _parse_hm(c["end"]))
            blocks.append((start, end, c.get("course")))
    return sorted(blocks)


def apply_quiet_hours(calendar: dict, notifications,
                      now: datetime) -> dict:
    """Suppress notifications landing inside a class block; batch
    them to just AFTER the block ends (one batch per block), and
    say so on the receipt. Notifications: [{id, at: datetime}].
    Naive/aware consistency is the caller's (times are compared as
    given)."""
    delivered, batched = [], []
    for note in notifications or []:
        at = note["at"]
        hit = None
        for start, end, course in _class_blocks_on(calendar,
                                                   at.date()):
            start = start.replace(tzinfo=at.tzinfo)
            end = end.replace(tzinfo=at.tzinfo)
            if start <= at < end:
                hit = (end, course)
                break
        if hit is None:
            delivered.append({"id": note["id"], "at": at,
                              "status": "delivered"})
        else:
            batched.append({"id": note["id"], "at": at,
                            "status": "batched",
                            "release_at": hit[0],
                            "held_by": hit[1]})
    return _receipt("quiet-hours", now,
                    delivered=delivered, batched=batched,
                    suppressed=len(batched))


__all__ = ["intake_calendar", "class_pattern", "frequency_ramp",
           "assessment_briefings", "frequency_plan",
           "apply_quiet_hours", "RAMP_TIERS", "CALENDAR_RECEIPT_SCHEMA",
           "CLAIMS_CEILING"]
