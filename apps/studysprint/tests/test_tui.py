"""Textual pilot tests for the TUI surface (tui.py, issue #4095).

Boots the app headless and drives the real widgets: check-in on
Today, SR flip + grade producing a scheduler-named receipt, reader
stepping, and both exports landing on disk.
"""

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("textual")

from tui import TUI_VERSION, build_state  # noqa: E402


def test_build_state_uses_core():
    state = build_state(ROOT)
    assert state["plan"]["total_sessions"] > 0
    assert state["cards"]  # SR cards from the practice set
    assert state["sections"]  # reader sections
    assert state["trust_receipt"] is not None
    assert TUI_VERSION == "0.3.0"


def _run(coro_fn):
    return asyncio.run(coro_fn())


async def _activate(app, pilot, pane):
    # click the tab in the tab bar (setting TabbedContent.active
    # directly does not survive a prior button click's focus)
    await pilot.click(f"#--content-tab-{pane}")
    await pilot.pause()


def _text(app, selector):
    widget = app.query_one(selector)
    return str(getattr(widget, "content", widget))


def test_tui_checkin_and_sr_grade(tmp_path):
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            # Today is the first tab; check in "done"
            await pilot.click("#checkin-done")
            await pilot.pause()
            status = _text(app, "#checkin-status")
            assert "done" in str(status)
            assert app.checkin_log["entries"][0]["status"] == "done"
            # SR: flip then grade Good (3) -> fsrs receipt
            await _activate(app, pilot, "tab-sr")
            await pilot.click("#sr-flip")
            await pilot.pause()
            back = _text(app, "#sr-back")
            assert back and "flip" not in back
            await pilot.click("#grade-3")
            await pilot.pause()
            receipt = _text(app, "#sr-receipt")
            assert "scheduler=fsrs" in receipt
            # scheduler switch to SM-2 and grade again
            select = app.query_one("#sr-scheduler")
            select.value = "sm2"
            await pilot.pause()
            # grading is flip-gated (#4234): flip the fresh card
            # before grading it under SM-2
            await pilot.click("#sr-flip")
            await pilot.pause()
            await pilot.click("#grade-4")
            await pilot.pause()
            receipt2 = _text(app, "#sr-receipt")
            assert "scheduler=sm2" in receipt2

    _run(scenario)


def test_tui_reader_and_exports(tmp_path):
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            await _activate(app, pilot, "tab-reader")
            await pilot.click("#reader-start")
            await pilot.pause()
            status = _text(app, "#reader-status")
            assert "Reading:" in status
            await pilot.click("#reader-step")
            await pilot.pause()
            word = _text(app, "#reader-word")
            assert word  # a token is on screen
            await _activate(app, pilot, "tab-export")
            await pilot.click("#export-apkg")
            await pilot.pause()
            assert (tmp_path / "studysprint.apkg").exists()
            await pilot.click("#export-vault")
            await pilot.pause()
            vault_notes = list(
                (tmp_path / "vault" / "StudySprint SR").glob("*.md"))
            assert len(vault_notes) >= 2  # cards + index
            status = _text(app, "#export-status")
            assert "Vault surface written" in status

    _run(scenario)


def test_tui_ingest_screen_confirm_gate(tmp_path):
    from tui import StudySprintTUI
    syllabus = tmp_path / "syllabus.txt"
    syllabus.write_text(
        "BIO 101\nMon Wed 10:00-11:15, Science Building, Room 204\n"
        "Midterm: 2026-11-20 18:00, Science Building\n",
        encoding="utf-8")

    async def scenario():
        app = StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            await _activate(app, pilot, "tab-ingest")
            app.query_one("#ingest-path").value = str(syllabus)
            await pilot.click("#ingest-go")
            await pilot.pause()
            result = str(_text(app, "#ingest-result"))
            assert "Syllabus parsed" in result
            assert "1 class meeting" in result
            placement = str(_text(app, "#ingest-placement"))
            assert "Not placed" in placement  # confirm gate holds
            await pilot.click("#ingest-confirm")
            await pilot.pause()
            placement = str(_text(app, "#ingest-placement"))
            assert "Placed on the calendar" in placement

    _run(scenario)


def test_sr_state_is_per_card_and_accumulates(tmp_path):
    """#4224: grading card B must not touch card A's state, and
    re-grading card A continues from A's own history."""
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            await _activate(app, pilot, "tab-sr")
            await pilot.click("#sr-flip")
            await pilot.click("#grade-4")
            await pilot.pause()
            assert len(app.card_states) == 1
            key_a = next(iter(app.card_states))
            state_a = app.card_states[key_a]
            # second card: grade it too
            await pilot.click("#sr-flip")
            await pilot.click("#grade-4")
            await pilot.pause()
            assert len(app.card_states) == 2
            assert app.card_states[key_a] is state_a  # untouched
            # back to card A (2-card deck wraps): re-grade; A's
            # state is replaced by A's OWN next state
            await pilot.click("#sr-flip")
            await pilot.click("#grade-1")
            await pilot.pause()
            assert app.card_states[key_a] is not state_a
    _run(scenario)


def test_checkin_records_today_and_persists(tmp_path):
    """#4223: the check-in lands on today's real week/day and
    survives a restart (loaded back from disk)."""
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            await pilot.click("#checkin-done")
            await pilot.pause()
            entries = app.checkin_log.get("entries") or []
            assert entries
            today = app.state["today"]
            assert entries[-1]["week"] == \
                today["sessions"][0]["week"]
            assert entries[-1]["session_index"] == \
                today["day_index"]
            assert (tmp_path / "checkin-log.json").exists()
            return len(entries)
    count = _run(scenario)
    app2 = StudySprintTUI(root=ROOT, export_dir=tmp_path)
    loaded = app2.checkin_log.get("entries") or []
    assert len(loaded) == count
