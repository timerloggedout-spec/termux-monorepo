"""Parity iteration 3 tests (#4416): multi-course on every
surface — the course set intaken through the core's
study_courses machinery, per-course bundles, switching with
per-course persistence isolation, course creation, and a
per-course .ics export. Surfaces 0.4.0; foundation stays 0.5.0.

The web ports (plan + countdown) are executed under node and
checked against the core's own outputs on shared fixtures; the
TUI binds the real core and is driven by pilot.
"""

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_ROOT))

BIO = "BIO 101 — Intro Biology (sample, synthetic)"
STAT = "STAT 210 — Data & Chance (sample, synthetic)"


def _app_js() -> str:
    return (APP_ROOT / "web" / "app.js").read_text(encoding="utf-8")


def _run_js(snippet: str):
    js = _app_js()
    start = js.index("function buildPlanPort")
    end = js.index("/* ---------------- loading + rendering */")
    ports = js[start:end]
    proc = subprocess.run(
        ["node", "-e", ports + "\n" + snippet],
        capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


requires_node = pytest.mark.skipif(
    shutil.which("node") is None, reason="node not available")


# ------------------------------------------------------------ bundle

def test_web_state_carries_the_course_set():
    from web.build_data import emit_state
    state = emit_state(APP_ROOT)
    assert state["surface_version"] == "0.5.0"
    names = [b["course"] for b in state["courses"]]
    assert names == [BIO, STAT]
    intake = state["courses_intake"]
    assert intake["schema"] == "studysprint-courses-receipt/v1"
    assert intake["course_count"] == 2
    assert intake["total_sessions"] == sum(
        b["plan"]["total_sessions"] for b in state["courses"])
    # back-compat: the top level IS the first course's bundle
    assert state["course"] == BIO
    assert state["plan"] == state["courses"][0]["plan"]
    # the second sample's calendar refusal is recorded, not hidden
    assert state["courses"][1]["calendar_geo"] is None
    assert "problem set" in state["courses"][1]["calendar_error"]


def test_per_course_ics_isolated_and_valid():
    from study_courses import validate_ics
    from web.build_data import emit_state
    state = emit_state(APP_ROOT)
    for name, text in state["ics_by_course"].items():
        assert validate_ics(text)["valid"], name
        other = STAT if name == BIO else BIO
        assert other.split(" —")[0] not in text, name
        assert name.split(" —")[0] in text, name


# ------------------------------------------------------------ ports

@requires_node
def test_plan_port_matches_core():
    from study_tools import build_study_plan
    doc = json.loads(
        (APP_ROOT / "examples" / "syllabus_stats.json").read_text())
    core = build_study_plan(doc)
    got = _run_js(
        f"console.log(JSON.stringify(buildPlanPort({json.dumps(doc)})))")
    assert got == core


@requires_node
def test_countdown_port_matches_core():
    from study_courses import exam_countdown
    doc = {"course": "HIST 201", "exam_date": "2026-12-15",
           "weeks": [{"week": 1, "topics": ["causes", "timeline"]},
                     {"week": 2, "topics": ["turning points"]}]}
    now = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)
    core = exam_countdown(doc, now)
    got = _run_js(
        "console.log(JSON.stringify(examCountdownPort("
        f"{json.dumps(doc)}, '2026-11-03')))")
    assert got == core


@requires_node
def test_storage_keys_are_per_course():
    got = _run_js(
        "console.log(JSON.stringify(["
        "courseStorageKey('studysprint-sr', 'BIO 101'),"
        "courseStorageKey('studysprint-sr', 'STAT 210'),"
        "courseStorageKey('ss.checkins', 'BIO 101')]))")
    assert got[0] != got[1]
    assert got[0].endswith("::BIO 101")
    assert got[2].startswith("ss.checkins::")


def test_web_switcher_and_creation_ship():
    html = (APP_ROOT / "web" / "index.html").read_text()
    for marker in ('id="course-switch"', 'id="course-countdown"',
                   'id="course-ics"', 'id="new-course-json"',
                   'id="new-course-add"'):
        assert marker in html, marker
    js = _app_js()
    for fn in ("buildPlanPort", "examCountdownPort",
               "courseStorageKey", "bundleFromSyllabusPort",
               "activateCourse", "initCourses"):
        assert f"function {fn}" in js, fn
    # persistence writes are namespaced -- the only bare legacy
    # key left is the one-time adoption READ
    assert 'setItem("studysprint-sr",' not in js
    assert 'setItem("ss.checkins",' not in js
    assert 'getItem("studysprint-sr")' in js  # adoption read


# ------------------------------------------------------------ TUI

def test_tui_course_set_intake():
    import tui
    cs = tui.build_course_set(APP_ROOT)
    intake = cs["intake"]
    assert intake["course_count"] == 2
    assert [b["course"] for b in cs["bundles"]] == [BIO, STAT]
    assert set(cs["ics"]) == {BIO, STAT}


def test_tui_switch_isolates_and_create(tmp_path, monkeypatch):
    import tui
    monkeypatch.setattr(tui, "user_courses_dir", lambda: tmp_path / "courses")
    from tui import StudySprintTUI

    def _text(app, sel):
        return str(app.query_one(sel).render())

    async def scenario():
        app = StudySprintTUI(root=APP_ROOT, export_dir=tmp_path / "exp")
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            # check in on BIO (the active course)
            await pilot.click("#checkin-done")
            await pilot.pause()
            assert app.checkin_log.get("entries")
            bio_entries = len(app.checkin_log["entries"])
            # switch to STAT: its check-ins are its own (empty)
            await pilot.click("#--content-tab-tab-courses")
            await pilot.pause()
            app.query_one("#course-select").value = STAT
            await pilot.pause()
            await pilot.click("#course-switch")
            await pilot.pause()
            assert app.state["course"] == STAT
            assert not app.checkin_log.get("entries")
            assert "probability" in _text(app, "#plan-text").lower() \
                or "sampling" in _text(app, "#plan-text").lower() \
                or "data" in _text(app, "#plan-text").lower()
            assert "▶ " + STAT in _text(app, "#courses-text")
            # back to BIO: the check-in is still there
            app.query_one("#course-select").value = BIO
            await pilot.pause()
            await pilot.click("#course-switch")
            await pilot.pause()
            assert len(app.checkin_log["entries"]) == bio_entries
            # create a course: it persists as a syllabus doc and
            # joins the set on rebuild
            await pilot.click("#--content-tab-tab-courses")
            app.query_one("#new-course-name").value = "HIST 201"
            app.query_one("#new-course-exam").value = "2026-12-15"
            app.query_one("#new-course-topics").value = "causes, timeline"
            await pilot.click("#new-course-create")
            await pilot.pause()
            assert (tmp_path / "courses" / "hist-201.json").exists()
            names = [b["course"] for b in app.course_set["bundles"]]
            assert "HIST 201" in names
            cd = next(c["countdown"] for c in
                      app.course_set["intake"]["courses"]
                      if c["course"] == "HIST 201")
            assert cd["exam_date"] == "2026-12-15"
            assert cd["urgency"] != "unset"

    asyncio.run(scenario())
