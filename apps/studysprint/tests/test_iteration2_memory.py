"""Parity iteration 2 tests (#4415): the §1c memory methods on
every surface — palace walk, Feynman explain-back, retrievability
notifications, Leitner rotation in SR, interleaving in the plan
view. Surfaces 0.3.0; foundation stays 0.5.0.

The web ports are executed under node and checked against the
core's own outputs on shared fixtures (the set-2 battery pattern);
the TUI binds the real core functions and is driven by pilot.
"""

import asyncio
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_ROOT))

NOW = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def _app_js() -> str:
    return (APP_ROOT / "web" / "app.js").read_text(encoding="utf-8")


def _run_js(snippet: str):
    """Extract the memory ports from app.js and run them in node."""
    js = _app_js()
    start = js.index("const LEITNER_INTERVALS")
    end = js.index("/* ---------------- pure helpers")
    ports = js[start:end]
    proc = subprocess.run(
        ["node", "-e", ports + "\n" + snippet],
        capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


requires_node = pytest.mark.skipif(
    shutil.which("node") is None, reason="node not available")


# ------------------------------------------------------------ bundle

def test_web_state_carries_the_memory_bundle():
    from web.build_data import emit_state
    state = emit_state(APP_ROOT)
    mem = state["memory"]
    palace = mem["palace"]
    assert palace["placements"], "palace placements ship"
    assert palace["source"] == "temple-route"  # it-1 routes bind
    assert palace["claims_ceiling"]
    topics = [t["topic"] for t in mem["feynman_topics"]]
    assert len(topics) == 6 and "membranes" in topics
    assert all(t["evidence"] for t in mem["feynman_topics"])


def test_tui_state_carries_the_same_palace():
    from tui import build_state
    state = build_state(APP_ROOT)
    palace = state["memory"]["palace"]
    assert palace["source"] == "temple-route"
    from web.build_data import emit_state
    web_palace = emit_state(APP_ROOT)["memory"]["palace"]
    assert palace["placements"] == web_palace["placements"]


# ------------------------------------------------- leitner (JS port)

@requires_node
def test_leitner_port_matches_core():
    import study_memory
    card = type("C", (), {"card_id": "x"})()
    cases = []
    for st, grade in [(None, 1), ({"box": 3}, 1), ({"box": 5}, 1),
                      ({"box": 4}, 0), ({"box": 1}, 0)]:
        core_state, core_receipt = study_memory.leitner_review(
            card, st, grade, NOW)
        cases.append({"state": st, "grade": grade,
                      "box": core_receipt["box"],
                      "interval": core_receipt["interval_days"],
                      "plain": core_receipt["plain_language"]})
    out = _run_js(
        "const cases = " + json.dumps(cases) + ";"
        "const now = new Date('2026-11-03T12:00:00Z');"
        "console.log(JSON.stringify(cases.map((c) => {"
        "  const r = leitnerReview(c.state, c.grade, now);"
        "  return { box: r.box, interval: r.interval_days,"
        "           plain: r.plain_language }; })))")
    for got, want in zip(out, cases):
        assert got == {"box": want["box"],
                       "interval": want["interval"],
                       "plain": want["plain"]}


# ---------------------------------------------------- walk (JS port)

@requires_node
def test_walk_port_matches_core():
    import study_memory
    palace = {"placements": [
        {"item": x} for x in ["cells", "membranes", "chlorophyll"]]}
    recalled = ["cells", "chlorophyll", "membranes"]
    core = study_memory.walk_review(palace, recalled, NOW)
    out = _run_js(
        "console.log(JSON.stringify(walkScore("
        "['cells','membranes','chlorophyll'], "
        "['cells','chlorophyll','membranes'])))")
    assert out["correct_in_position"] == core["correct_in_position"]
    assert out["recalled_out_of_order"] == core["recalled_out_of_order"]
    assert out["missed"] == core["missed"]
    assert out["ordered_recall"] == core["ordered_recall"]


# ------------------------------------------------- feynman (JS port)

@requires_node
def test_feynman_port_matches_core():
    import study_memory
    evidence = ["The cell membrane controls what enters and "
                "leaves the cell, using selective permeability "
                "and transport proteins."]
    explanation = "The membrane controls what enters the cell."
    core = study_memory.explain_back("membranes", explanation,
                                     evidence, NOW)
    out = _run_js(
        "console.log(JSON.stringify(explainBack('membranes', "
        + json.dumps(explanation) + ", [" + json.dumps(evidence[0])
        + "])))")
    assert out["verdict"] == core["verdict"]
    assert out["coverage"] == core["coverage"]
    assert out["missing_terms"] == core["missing_terms"]
    out2 = _run_js(
        "console.log(JSON.stringify(explainBack('x', 'anything', [])))")
    assert out2["verdict"] == "abstain"


# ------------------------------------------- retrievability (JS port)

@requires_node
def test_retrievability_port_matches_core():
    import study_memory
    core = study_memory.fsrs_retrievability(2.3065, 10.0)
    out = _run_js(
        "console.log(JSON.stringify(coreRetrievability(2.3065, 10)))")
    assert abs(out - core) < 1e-9
    assert study_memory.fsrs_retrievability(0, 5) == 0.0


# ---------------------------------------------- interleave (JS port)

@requires_node
def test_interleave_port_matches_core_order():
    import study_memory

    class Card:
        def __init__(self, topic):
            self.tags = [topic]
            self.card_id = topic

        def to_dict(self):
            return {"front": self.card_id}

    quiz = {"cells": ["q1", "q2"], "membranes": ["q3"],
            "dna": ["q4", "q5", "q6"]}
    core = study_memory.interleave_sessions(
        quiz, [Card("cells"), Card("dna")])
    core_topics = [i["topic"] for i in core["items"]]
    items = []
    for topic, qs in quiz.items():
        items += [{"kind": "quiz", "topic": topic} for _ in qs]
    items += [{"kind": "card", "topic": "cells"},
              {"kind": "card", "topic": "dna"}]
    out = _run_js(
        "console.log(JSON.stringify(interleaveOrder("
        + json.dumps(items) + ").map((i) => i.topic)))")
    assert out == core_topics


# ------------------------------------------------------- surface pins

def test_web_surface_ships_memory_view_and_leitner():
    html = (APP_ROOT / "web" / "index.html").read_text()
    assert 'data-view="memory"' in html
    assert 'id="view-memory"' in html
    assert '<option value="leitner">Leitner boxes</option>' in html
    js = _app_js()
    for fn in ("leitnerReview", "walkScore", "explainBack",
               "coreRetrievability", "interleaveOrder",
               "renderMemory", "gradeLeitner"):
        assert f"function {fn}" in js, fn
    state = json.loads(
        (APP_ROOT / "web" / "data" / "state.json").read_text())
    assert state["surface_version"] == "0.4.0"
    assert state["memory"]["palace"]["placements"]


# ------------------------------------------------------------ TUI

def _run(coro_fn):
    return asyncio.run(coro_fn())


def _text(app, selector):
    widget = app.query_one(selector)
    return str(getattr(widget, "content", widget))


def test_tui_memory_tab_and_leitner(tmp_path):
    pytest.importorskip("textual")
    from tui import StudySprintTUI

    async def scenario():
        app = StudySprintTUI(root=APP_ROOT, export_dir=tmp_path)
        async with app.run_test(size=(110, 42)) as pilot:
            await pilot.pause()
            # Memory tab: palace renders from the core bundle
            await pilot.click("#--content-tab-tab-memory")
            await pilot.pause()
            assert "dorm door" in _text(app, "#palace-text")
            # walk: type the placed items in route order
            placed = [p["item"] for p in
                      app.state["memory"]["palace"]["placements"]]
            app.query_one("#walk-input").value = ", ".join(placed)
            await pilot.click("#walk-score")
            await pilot.pause()
            assert "ordered recall 1.0" in _text(app, "#walk-result")
            # Feynman: explain membranes with its own key terms
            app.query_one("#feynman-topic").value = "membranes"
            app.query_one("#feynman-input").value = (
                "The cell membrane controls what enters and "
                "leaves the cell.")
            await pilot.click("#feynman-grade")
            await pilot.pause()
            assert "Verdict:" in _text(app, "#feynman-result")
            # SR: Leitner scheduler, flip, knew it -> box 2
            await pilot.click("#--content-tab-tab-sr")
            await pilot.pause()
            app.query_one("#sr-scheduler").value = "leitner"
            await pilot.pause()
            await pilot.click("#sr-flip")
            await pilot.pause()
            await pilot.click("#grade-leitner-1")
            await pilot.pause()
            receipt = _text(app, "#sr-receipt")
            assert "scheduler=leitner" in receipt
            assert "box 2" in receipt
            # the 1-4 buttons in leitner mode give the hint
            await pilot.click("#sr-flip")
            await pilot.pause()
            await pilot.click("#grade-3")
            await pilot.pause()
            assert "Leitner grades in boxes" in _text(
                app, "#sr-receipt")

    _run(scenario)


def test_tui_plan_shows_interleaved_session():
    from tui import _interleaved_text, build_state
    text = _interleaved_text(build_state(APP_ROOT))
    assert "Interleaved session" in text
    assert "same-topic joins" in text
