"""Iteration 4 (#4417): hardening (opt-in) + §1b completion.

Pins: both surfaces' book bundles agree with the core pipeline
on the real demonstration book (Darwin, Origin of Species 6th
ed., Ch. XIV + the book's own Glossary + Index); the single-file
ingest path reports the same three counts; the web hardening
ports are battery-pinned to study_hardening (node-executed);
the TUI's Book expansion + Hardening refusal/plan/record run
the real core functions under pilot.
"""

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
WEB = ROOT / "web"

from study_hardening import (HARDENING_CEILING, RECALL_CEILING,  # noqa: E402
                             plan_hardening_drill, reinstatement_script,
                             varied_context_plan)
from study_pipeline import ingest_any  # noqa: E402

NOW = datetime(2026, 11, 3, 9, 0, tzinfo=timezone.utc)
EXPECTED_COUNTS = {"terms": 62, "with_definitions": 62,
                   "with_index_refs": 2}


def test_book_bundles_agree_with_core():
    import tui
    from web.build_data import _book_bundle
    web_book = _book_bundle(ROOT)
    tui_book = tui.build_book_bundle(ROOT)
    assert web_book["counts"] == EXPECTED_COUNTS
    assert tui_book["counts"] == EXPECTED_COUNTS
    for term, pages in (("embryology", [386]),
                        ("morphology", [382])):
        for book in (web_book, tui_book):
            tap = book["taps"][term]
            assert tap["index_pages"] == pages
            assert tap["definition"]
            assert tap["sections"]
    assert len(web_book["annotations"]) == 2
    assert len(tui_book["annotations"]) == 2
    for a in web_book["annotations"]:
        assert a["target"]["selector"]["type"] == \
            "TextQuoteSelector"
        assert a["target"]["selector"]["exact"]


def test_single_file_ingest_reports_the_three_counts():
    out = ingest_any(str(ROOT / "examples" /
                         "textbook_origin_full.txt"))
    assert out["flow"] == "textbook"
    assert out["term_bank"] == EXPECTED_COUNTS
    assert out["sr_cards"] == EXPECTED_COUNTS["terms"]


def test_state_carries_book_and_version():
    state = json.loads((WEB / "data" / "state.json").read_text())
    assert state["surface_version"] == "0.5.1"
    assert state["book"]["counts"] == EXPECTED_COUNTS


def test_web_hardening_ports_match_core():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node not available")
    app_js = (WEB / "app.js").read_text()
    start = app_js.index("function computeDayIndex")
    end = app_js.index("/* ---------------- loading")
    helpers = app_js[start:end]
    core_plan = varied_context_plan(6)
    core_script = reinstatement_script("the exam room", "BIO 101")
    core_drill = plan_hardening_drill("drill-1", 3, True, NOW)
    core_refusal = plan_hardening_drill("drill-1", 1, False, NOW)
    script = helpers + f"""
const assert = require("assert");
assert.deepStrictEqual(variedContextPlanPort(6),
  {json.dumps(core_plan)});
assert.deepStrictEqual(
  reinstatementScriptPort("the exam room", "BIO 101"),
  {json.dumps(core_script)});
const drill = planHardeningDrillPort("drill-1", 3, true);
assert.strictEqual(drill.status, "planned");
assert.strictEqual(drill.name, {json.dumps(core_drill["name"])});
assert.deepStrictEqual(drill.pressure,
  {json.dumps(core_drill["pressure"])});
assert.strictEqual(drill.no_guilt,
  {json.dumps(core_drill["no_guilt"])});
const refusal = planHardeningDrillPort("drill-1", 1, false);
assert.strictEqual(refusal.status, "refused");
assert.strictEqual(refusal.reason,
  {json.dumps(core_refusal["reason"])});
assert.strictEqual(HARDENING_CEILING,
  {json.dumps(HARDENING_CEILING)});
assert.strictEqual(RECALL_CEILING, {json.dumps(RECALL_CEILING)});
assert.strictEqual(sha256Hex("drill-1"),
  {json.dumps(__import__("hashlib").sha256(b"drill-1").hexdigest())});
console.log("ports ok");
"""
    proc = subprocess.run([node, "-e", script], capture_output=True,
                          text=True)
    assert proc.returncode == 0, proc.stderr
    assert "ports ok" in proc.stdout


def test_tui_book_and_hardening_pilot(tmp_path):
    textual = pytest.importorskip("textual")  # noqa: F841
    import tui
    from textual.widgets import Button, Label, Select, Static

    async def run():
        app = tui.StudySprintTUI(root=ROOT, export_dir=tmp_path)
        async with app.run_test() as pilot:
            # Book: expansion payload for an indexed term.
            sel = app.query_one("#book-term", Select)
            sel.value = "morphology"
            await pilot.pause()
            app.query_one("#book-show", Button).press()
            await pilot.pause()
            payload = str(app.query_one(
                "#book-payload", Static).render())
            assert "Morphology" in payload
            assert "382" in payload
            receipt = str(app.query_one(
                "#book-receipt", Static).render())
            assert "62 terms mined" in receipt
            assert "2 with index refs" in receipt
            # Hardening: refusal while OFF (the default).
            app.query_one("#hardening-plan", Button).press()
            await pilot.pause()
            out = str(app.query_one(
                "#hardening-plan-out", Static).render())
            assert "Refused" in out and "opt-in only" in out
            # Opt in -> a real plan; record -> supportive close.
            app.query_one("#hardening-toggle", Button).press()
            await pilot.pause()
            assert app.hardening_opt_in is True
            app.query_one("#hardening-plan", Button).press()
            await pilot.pause()
            out = str(app.query_one(
                "#hardening-plan-out", Static).render())
            assert "conceptualization" in out
            app.query_one("#hardening-record", Button).press()
            await pilot.pause()
            result = str(app.query_one(
                "#hardening-result", Label).render())
            assert "not a verdict" in result

    asyncio.run(run())
