"""Cognitive-fitness slice tests (issue #4966).

Pins the FINAL fit slice to its spec:
  (1) next_order is a core-owned state field (latest check-in's
      directive; phase-derived before any check-in);
  (2) the typed check-in is merged into core state -- validated
      against CHECKIN_Qs, every question required, persisted in
      the core state block (no browser-local fork);
  (3) phase advances by session count (12 per phase) and is
      surfaced on the existing plan view from core state;
  (4) A2 constants land as DATA verbatim (PHASES / DRILLS /
      CHECKIN_Qs) -- durations and weekly counts from PHASES,
      never the artifact's 45-minute deploy hardcode;
  Judges riders: check-in validation present; stats average
  only entries carrying a value (no silent zero-drag).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import study_cogfit as cog  # noqa: E402

VALID = {
    "executive_output": 8,
    "motor_precision": 7,
    "dual_task_load": 6,
    "resets": 2,
    "breakthrough": "None today",
    "state": "Neutral",
    "next_order": "Hold the pattern through the second set.",
}


# ---------------------------------------------------------------- (4) data
def test_constants_shape_and_values():
    assert len(cog.PHASES) == 6
    assert [p["duration"] for p in cog.PHASES] == [45, 50, 55, 60, 55, 60]
    assert [p["sessions"] for p in cog.PHASES] == [3, 3, 3, 4, 3, 3]
    assert len(cog.DRILLS) == 21
    assert len(cog.CHECKIN_Qs) == 7
    assert [q["id"] for q in cog.CHECKIN_Qs] == [
        "executive_output", "motor_precision", "dual_task_load",
        "resets", "breakthrough", "state", "next_order"]
    for phase in cog.PHASES:
        for drill_id in phase["drillIds"]:
            assert drill_id in cog.DRILLS


def test_no_forbidden_carryover():
    src = (ROOT / "study_cogfit.py").read_text()
    for token in ("caeo_history", "eap_history", "localStorage.getItem",
                  "localStorage.setItem", "gcal.mcp",
                  "api.anthropic.com"):
        assert token not in src


# ------------------------------------------------------- (3) phase by count
def test_phase_progression_boundaries():
    cases = {0: "p1", 11: "p1", 12: "p2", 24: "p3", 36: "p4",
             48: "p5", 59: "p5", 60: "p6", 500: "p6"}
    for count, phase_id in cases.items():
        proj = cog.phase_for_session_count(count)
        assert proj["phase_id"] == phase_id, count
        assert proj["session_count"] == count
    assert cog.phase_for_session_count(12)["sessions_into_phase"] == 0
    assert cog.phase_for_session_count(13)["sessions_into_phase"] == 1
    with pytest.raises(ValueError):
        cog.phase_for_session_count(-1)


# ------------------------------------------------------ (2) typed check-in
def test_validate_checkin_accepts_and_normalizes():
    out = cog.validate_checkin({**VALID, "next_order": "  Hold it.  "})
    assert out["next_order"] == "Hold it."
    assert out["resets"] == 2


def test_validate_checkin_refuses_empty_and_partial():
    with pytest.raises(ValueError):
        cog.validate_checkin({})
    partial = dict(VALID)
    del partial["state"]
    with pytest.raises(ValueError):
        cog.validate_checkin(partial)


def test_validate_checkin_refuses_bad_values():
    for bad in ({"executive_output": 11}, {"executive_output": True},
                {"resets": -1}, {"resets": 1.5},
                {"breakthrough": "Invented drill"},
                {"state": "Invented state"},
                {"next_order": "   "}, {"surprise": 1}):
        with pytest.raises(ValueError):
            cog.validate_checkin({**VALID, **bad})


def test_record_checkin_rebuilds_state_and_keeps_input_intact():
    s0 = cog.cogfit_state()
    s1 = cog.record_checkin(s0, VALID, timestamp="2026-11-05T05:00:00Z")
    assert s0["session_count"] == 0  # refused-or-not, input untouched
    assert s1["session_count"] == 1
    assert s1["checkins"][0]["session"] == 1
    assert s1["checkins"][0]["date"] == "2026-11-05T05:00:00Z"
    with pytest.raises(ValueError):
        cog.record_checkin(s1, {})
    assert s1["session_count"] == 1


def test_twelve_checkins_advance_phase():
    state = cog.cogfit_state()
    for _ in range(12):
        state = cog.record_checkin(state, VALID)
    assert state["phase"]["phase_id"] == "p2"
    assert state["phase"]["sessions_into_phase"] == 0


# ------------------------------------------------------------ (1) next_order
def test_next_order_core_owned():
    s0 = cog.cogfit_state()
    assert s0["next_order"]  # phase-derived before any check-in
    assert "1-Back" in s0["next_order"]
    s1 = cog.record_checkin(s0, VALID)
    assert s1["next_order"] == VALID["next_order"]
    s2 = cog.record_checkin(
        s1, {**VALID, "next_order": "Attack the Stroop reversal."})
    assert s2["next_order"] == "Attack the Stroop reversal."


# ------------------------------------------------------------- stats rider
def test_stats_ignore_partial_entries():
    full = {"executive_output": 10, "dual_task_load": 4}
    partial = {"dual_task_load": 8}  # no executive_output at all
    stats = cog.checkin_stats([full, partial])
    assert stats["executive_output"] == {"count": 1, "average": 10.0}
    assert stats["dual_task_load"] == {"count": 2, "average": 6.0}
    assert stats["total_checkins"] == 2


# --------------------------------------------------------- surface + schema
def test_emit_state_carries_cogfit():
    pytest.importorskip("fsrs")
    sys.path.insert(0, str(ROOT / "web"))
    import build_data
    state = build_data.emit_state()
    assert state["cogfit"]["session_count"] == 0
    assert state["cogfit"]["phase"]["phase_id"] == "p1"
    assert state["cogfit"]["next_order"]


def test_committed_state_carries_cogfit():
    committed = json.loads(
        (ROOT / "web" / "data" / "state.json").read_text())
    assert committed["cogfit"] == cog.cogfit_state()


def test_plan_view_renders_core_cogfit():
    app_js = (ROOT / "web" / "app.js").read_text()
    assert "state.data.cogfit" in app_js
    assert "Next Session Order" in app_js
    assert "caeo_history" not in app_js
    assert "eap_history" not in app_js


def test_payloads_schema_carries_cogfit_defs():
    schema = json.loads(
        (ROOT / "strands-aws" / "schemas" / "payloads.schema.json")
        .read_text())
    defs = schema["$defs"]
    for name in ("CogfitCheckinEntry", "CogfitPhase", "CogfitState"):
        assert name in defs
    entry = defs["CogfitCheckinEntry"]
    assert set(entry["required"]) >= {
        q["id"] for q in cog.CHECKIN_Qs} | {"session"}
    state_def = defs["CogfitState"]
    assert state_def["properties"]["checkins"]["items"]["$ref"] == \
        "#/$defs/CogfitCheckinEntry"
