"""Regression tests for the RFP-D1-8 set-2 build (item #4330):
scheduler integrity (#4231 FSRS generation pin + core/web battery,
#4232 SM-2 pass boundary) and the web contract fixes (#4228 Today
actions, #4230 per-topic reader bodies, #4234 pre-flip grading,
#4237 load failure state)."""
import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent


def _app_js() -> str:
    return (APP_ROOT / "web" / "app.js").read_text(encoding="utf-8")


# ------------------------------------------------------------- #4231

def test_fsrs_generation_pinned_to_library_defaults():
    import study_sr
    from fsrs.scheduler import DEFAULT_PARAMETERS
    # The pin IS the generation: if a py-fsrs upgrade changes its
    # defaults, this test fails instead of the schedules drifting.
    assert tuple(DEFAULT_PARAMETERS) == study_sr.FSRS_PARAMETERS
    scheduler = study_sr.FSRSScheduler()._scheduler()
    assert scheduler.enable_fuzzing is False
    assert tuple(scheduler.parameters) == study_sr.FSRS_PARAMETERS


def test_fsrs_receipt_and_export_name_the_generation():
    import study_sr
    card = study_sr.build_cards([{"q": "x", "a": "y"}])[0]
    _state, receipt = study_sr.review_card(card, None, 3, "fsrs")
    assert receipt["fsrs_generation"] == study_sr.FSRS_GENERATION
    ux = study_sr.export_ux_state([card], {})
    assert ux["generation"] == study_sr.FSRS_GENERATION
    assert ux["parameters"] == list(study_sr.FSRS_PARAMETERS)


def test_web_fsrs_port_carries_the_pinned_generation():
    import study_sr
    js = _app_js()
    weights = re.search(r"const FSRS_W = \[([^\]]+)\]", js).group(1)
    parsed = tuple(float(x) for x in weights.replace("\n", " ").split(",")
                   if x.strip())
    assert parsed == study_sr.FSRS_PARAMETERS
    assert f'FSRS_GENERATION = "{study_sr.FSRS_GENERATION}"' in js


@pytest.mark.skipif(shutil.which("node") is None,
                    reason="node not available")
def test_fsrs_battery_core_vs_web_port(tmp_path):
    """Identical review sequences through the core (py-fsrs via
    study_sr) and the web port must agree on stability, difficulty,
    state, step and due — the #4231 alignment, proven not asserted."""
    import study_sr
    card = study_sr.build_cards([{"q": "battery", "a": "card"}])[0]
    t0 = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
    seqs = {
        "A": [(0, 3), (10, 3), (1440, 3), (6 * 1440, 4), (30 * 1440, 1),
              (10, 3), (1440, 3), (20 * 1440, 2)],
        "D": [(0, 2), (1, 1), (1, 3), (11, 3), (1440, 1), (10, 3),
              (1440, 4), (7 * 1440, 3)],
    }
    expected = {}
    for name, seq in seqs.items():
        st, now, rows = None, t0, []
        for mins, grade in seq:
            now = now + timedelta(minutes=mins)
            st, _r = study_sr.review_card(card, st, grade, "fsrs",
                                          now=now)
            ts = study_sr.to_ts_fsrs_state(st, now=now)
            rows.append({
                "at_min": int((now - t0).total_seconds() // 60),
                "grade": grade, "stability": ts["stability"],
                "difficulty": ts["difficulty"], "state": ts["state"],
                "step": ts["step"], "due": ts["due"]})
        expected[name] = rows
    (tmp_path / "expected.json").write_text(json.dumps(expected))
    script = r"""
const fs = require("fs");
let src = fs.readFileSync(process.argv[2], "utf8");
src = src.slice(0, src.indexOf("async function load()"));
global.document = { addEventListener() {}, querySelector: () => null,
  querySelectorAll: () => [] };
global.localStorage = { getItem: () => null, setItem() {},
  removeItem() {} };
eval(src + ";global.__x = {fsrsReview};");
const fsrsReview = global.__x.fsrsReview;
const expected = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
const T0 = Date.parse("2026-01-05T12:00:00Z");
let fails = 0;
for (const rows of Object.values(expected)) {
  let st = null;
  for (const row of rows) {
    st = fsrsReview(st, row.grade, T0 + row.at_min * 60000);
    const close = (a, b) =>
      Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
    if (!close(st.stability, row.stability) ||
        !close(st.difficulty, row.difficulty) ||
        st.state !== row.state ||
        (st.step ?? null) !== (row.step ?? null) ||
        Math.abs(Date.parse(st.due) - Date.parse(row.due)) > 1000) {
      fails++;
    }
  }
}
process.exit(fails ? 1 : 0);
"""
    (tmp_path / "battery.js").write_text(script)
    proc = subprocess.run(
        ["node", str(tmp_path / "battery.js"),
         str(APP_ROOT / "web" / "app.js"),
         str(tmp_path / "expected.json")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


# ------------------------------------------------------------- #4232

def test_sm2_maps_preserve_the_core_pass_boundary():
    # Surface buttons 1..4 map to SM-2 qualities {1, 2, 3, 5} on
    # BOTH surfaces: Hard (2) stays a reset, per the core's rule.
    assert "{ 1: 1, 2: 2, 3: 3, 4: 5 }" in _app_js()
    assert "{1: 1, 2: 2, 3: 3, 4: 5}" in (
        APP_ROOT / "tui.py").read_text(encoding="utf-8")
    import study_sr
    card = study_sr.build_cards([{"q": "x", "a": "y"}])[0]
    now = datetime(2026, 1, 5, tzinfo=timezone.utc)
    state, _ = study_sr.review_card(card, None, 4, "sm2", now=now)
    state, _ = study_sr.review_card(card, state, 4, "sm2",
                                    now=now + timedelta(days=1))
    assert state["repetitions"] == 2
    state, receipt = study_sr.review_card(
        card, state, 2, "sm2", now=now + timedelta(days=7))
    # quality 2 < 3: repetitions reset, interval back to 1 day.
    assert state["repetitions"] == 0
    assert receipt["interval_days"] == 1


# ------------------------------------------------------------- #4228

def test_today_actions_render_from_state():
    js = _app_js()
    assert "state.today" in js and "actions" in js
    assert 'id="action-start"' in js and 'id="action-missed"' in js
    from web.build_data import emit_state
    state = emit_state(APP_ROOT)
    labels = [a["label"] for a in state["today"]["actions"]]
    assert any("Start" in label for label in labels)
    assert any("missed" in label.lower() for label in labels)


# ------------------------------------------------------------- #4230

def test_reader_sections_teach_their_topics():
    from web.build_data import emit_state
    sections = emit_state(APP_ROOT)["reader"]["sections"]
    assert len(sections) == 6
    texts = [s["text"] for s in sections]
    assert len(set(texts)) == 6  # no two sections share a body
    by_title = {s["title"]: s["text"] for s in sections}
    assert "chlorophyll" in by_title["photosynthesis"]
    assert "Okazaki" in by_title["DNA replication"]
    assert "customs post" in by_title["membranes"]


def test_tui_reader_sections_teach_their_topics():
    from tui import build_state
    sections = build_state(APP_ROOT)["sections"]
    assert len({s.content for s in sections}) == 6
    by_title = {s.title: s.content for s in sections}
    assert "semi-conservative" in by_title["DNA replication"]


# ------------------------------------------------------------- #4234

def test_grading_is_gated_on_the_flip():
    js = _app_js()
    assert "!state.flipped" in js  # grade() guard
    assert "b.disabled = true" in js  # showCard locks the buttons
    from tui import StudySprintTUI
    src = (APP_ROOT / "tui.py").read_text(encoding="utf-8")
    grade_body = src[src.index("def _grade"):]
    assert "if not self.card_flipped:" in grade_body


# ------------------------------------------------------------- #4237

def test_load_failure_state_exists():
    js = _app_js()
    assert 'id="load-error"' in js
    assert 'id="load-retry"' in js
    assert "Couldn't load your course data" in js
    assert "if (!state.data || !state.flipped) return;" in js
