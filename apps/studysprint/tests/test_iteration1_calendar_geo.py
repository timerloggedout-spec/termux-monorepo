"""Parity iteration 1 (#4414): calendar + geography bound on all
surfaces — the core assembler, TUI state + panes, web state +
views. Surfaces 0.2.0; foundation stays 0.5.0."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)


def _assembled():
    from study_geo import surface_calendar_geo
    doc = json.loads((ROOT / "examples" / "calendar.json").read_text())
    syllabus = json.loads((ROOT / "examples" / "syllabus.json").read_text())
    topics = [t for w in syllabus["weeks"] for t in w.get("topics") or []]
    return surface_calendar_geo(doc, NOW, topics=topics)


def test_assembler_binds_calendar_and_geo():
    cg = _assembled()
    # briefings: the quiz ramps final-stretch; the final is SHIFTED
    quiz, _, final = cg["briefings"]
    assert quiz["kind"] == "quiz" and quiz["ramp"]["tier"] == "final-stretch"
    assert final["shifted"] is True
    assert "Gym Annex B" in final["briefing"]
    assert "time 10:00 -> 18:00" in final["briefing"]
    # frequency follows the nearest assessment
    assert cg["frequency_plan"]["BIO 101"]["multiplier"] == 3.0
    # quiet hours: the in-class probe is batched to the block end
    q = cg["quiet_hours"]
    assert q["suppressed"] == 1
    assert q["batched"][0]["release_at"].endswith("11:15:00Z")
    # routes: every assessment gets one, with a leave-by time
    assert len(cg["routes"]) == 3
    assert all(r["depart_by"] for r in cg["routes"])
    assert cg["routes"][-1]["destination"] == "Gym Annex B"
    # temple route places topics on the walk, cues narrate them
    placements = cg["temple_route"]["placements"]
    assert [p["locus"] for p in placements] == [
        "dorm door", "library steps", "lab bench"]
    assert len(cg["audio_cues"]) == 3
    json.dumps(cg)  # the whole assembly is JSON-ready for state


def test_assembler_without_coords_draws_no_routes():
    from study_geo import surface_calendar_geo
    doc = json.loads((ROOT / "examples" / "calendar.json").read_text())
    del doc["coords"]
    cg = surface_calendar_geo(doc, NOW)
    assert cg["routes"] == []          # omitted, never faked
    assert len(cg["locations"]) == 2   # locations still bind


def test_tui_state_and_panes_carry_calendar_geo():
    import tui
    state = tui.build_state()
    assert state["calendar_geo"] is not None
    cal = tui._calendar_text(state)
    assert "Science Hall 204" in cal and "SHIFTED" in cal
    routes = tui._routes_text(state)
    assert "Gym Annex B" in routes and "temple" in routes.lower()
    assert "dorm door" in routes


def test_web_state_and_views_carry_calendar_geo():
    state = json.loads((ROOT / "web" / "data" / "state.json").read_text())
    assert state["calendar_geo"]["briefings"], "state carries briefings"
    html = (ROOT / "web" / "index.html").read_text()
    assert 'data-view="calendar"' in html and 'data-view="routes"' in html
    assert 'id="view-calendar"' in html and 'id="view-routes"' in html
    app = (ROOT / "web" / "app.js").read_text()
    assert "renderCalendar" in app and "renderRoutes" in app
    assert "calendar_geo" in app
