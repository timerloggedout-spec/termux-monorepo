"""QDesk deadline desk: the 2026-11-11 ARA miss must be impossible to repeat silently."""
import importlib.util
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qdesk", ROOT / "scripts/que/qdesk_deadlines.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

ARA = {"id": "C15", "name": "ARA", "status": "SCREENED OUT this cycle - FAIL eligibility (PI clause)",
       "dates": {"submission_period": "2026-10-01 to 2026-11-11T23:59:00-08:00", "decisions": "February 2027"},
       "gates": "PI must be faculty or a permanent researcher at a 501(c)(3) NGO",
       "institution_gap": {"classification": "INSTITUTION-GAP"}}
HACK = {"id": "D9", "name": "Hack", "status": "registering",
        "dates": {"submissions_open": "2026-11-01T00:00:00-08:00", "deadline": {"at": "2026-11-20T12:00:00-08:00"}},
        "gates": [{"id": "G-1", "label": "Profile complete", "status": "open", "owner": "agency"},
                  {"id": "G-2", "label": "done thing", "status": "met"}]}
COORD = {"events": [HACK], "candidate_events": [ARA]}


def at(s):
    return datetime.fromisoformat(s)


def test_parses_iso_display_and_ranges():
    assert q.parse_instant("Wed 2026-11-11 11:59 PM PST (UTC-08:00)").isoformat() == "2026-11-11T23:59:00-08:00"
    assert q.parse_instant("2026-10-01 to 2026-11-11T23:59:00-08:00").isoformat() == "2026-11-11T23:59:00-08:00"
    assert q.parse_instant({"at": "2026-11-20T12:00:00-08:00"}).hour == 12
    assert q.parse_instant("NOT_ESTABLISHED") is None
    assert q.governing_deadline(HACK)[0] == "deadline"  # *_open keys never govern


def test_candidate_events_are_counted_and_gap_gets_sponsor_tasks():
    plan = q.build(COORD, at("2026-11-01T09:00:00-08:00"))
    assert {e["id"] for e in plan["entries"]} == {"C15", "D9"}
    ids = [t["id"] for t in plan["tasks"] if t["entry"] == "C15"]
    assert "C15:sponsor-shortlist" in ids and "C15:owner-sign-sponsor" in ids
    sign = next(t for t in plan["tasks"] if t["id"] == "C15:owner-sign-sponsor")
    assert sign["hitl"] and sign["owner_packet"] and sign["due"] <= "2026-11-11"
    assert all(not t["hitl"] for t in plan["tasks"] if t["id"] != "C15:owner-sign-sponsor")
    assert [t["id"] for t in plan["tasks"] if t["entry"] == "D9"] == ["D9:gate-g-1"]
    assert any(g.get("milestone") and g["entry"] == "C15" for g in plan["gantt"])


def test_alarm_tiers_fire_once_each_and_missed_escalates():
    seen = None
    fired = []
    for now in ["2026-11-03T00:00:00-08:00", "2026-11-05T00:00:00-08:00", "2026-11-05T02:00:00-08:00",
                "2026-11-10T01:00:00-08:00", "2026-11-11T12:00:00-08:00", "2026-11-12T01:00:00-08:00"]:
        seen = q.build(COORD, at(now), seen)
        fired += [(a["entry"], a["tier"]) for a in seen["alarms"]]
    c15 = [t for e, t in fired if e == "C15"]
    assert c15 == ["T-7d", "T-48h", "T-12h", "MISSED"]
    alarm = q.build(COORD, at("2026-11-11T12:00:00-08:00"))["alarms"]
    a = next(x for x in alarm if x["entry"] == "C15")
    assert a["priority"] == "P0" and a["key"] == "qdesk-deadline:C15:2026-11-11"


def test_done_entries_never_alarm_and_gantt_text_compiles():
    done = {"events": [dict(HACK, status="submitted - PUBLISHED")], "candidate_events": []}
    plan = q.build(done, at("2026-11-19T20:00:00-08:00"))
    assert plan["alarms"] == []
    txt = q.gantt_text(q.build(COORD, at("2026-11-01T09:00:00-08:00")))
    rows = txt.splitlines()
    assert rows and all(len(r.split(" | ")) == 4 for r in rows)


def test_real_coordinator_parses():
    coord = json.load(open(ROOT / "ops/challenge/coordinator.json"))
    plan = q.build(coord, at("2026-11-11T23:30:00-08:00"))
    ids = {e["id"] for e in plan["entries"]}
    assert "C15" in ids and "C14" in ids
    assert any(a["entry"] == "C15" for a in plan["alarms"])
