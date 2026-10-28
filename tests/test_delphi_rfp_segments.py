"""Delphi RFP segmentation feed (#1865-lane follow-on, owner directive
2026-10-27): every census issue lands in exactly one segment; counts
agree with the checked-in census snapshot; research segments are
complete per silo; the gate outcome is carried as an admission record
with its source pointer, never as a comparison result.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"


def _feed() -> dict:
    p = DATA / "delphi-rfp-feed.json"
    assert p.exists(), "delphi-rfp-feed.json missing — run the collector"
    return json.loads(p.read_text())


def _census() -> dict:
    return json.loads(
        (ROOT / "scripts/delphi/rfp_census_observation.json").read_text())


def test_collector_runs():
    r = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/delphi/rfp_segment_feed.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert _feed()["schema"] == "delphi-rfp-feed/v1"


def test_every_census_issue_assigned_exactly_once():
    feed, census = _feed(), _census()
    assert feed["totals"]["open_delphi_rfp"] == census["open_total"]
    assert feed["totals"]["census_issues"] == len(census["issues"])
    nums = []
    for seg in feed["research_segments"]:
        nums += [m["number"] for m in seg["members"].values() if m]
    nums += [m["number"] for m in feed["quota_segment"]["members"]]
    nums += [s["members"]["self"]["number"] for s in feed["meta_segments"]
             if s["members"]["self"]]
    nums += [u["number"] for u in feed["unassigned"]]
    assert sorted(nums) == sorted(i["number"] for i in census["issues"])
    assert len(nums) == len(set(nums)), "an issue is in two segments"


def test_research_segments_complete_per_silo():
    feed = _feed()
    silos = json.loads(
        (ROOT / "ops/delphi/research-silos.json").read_text())["silos"]
    assert [s["segment_id"] for s in feed["research_segments"]] == \
        [s["id"] for s in silos]
    for seg in feed["research_segments"]:
        assert seg["progress"]["expected"] == 4
        assert set(seg["members"]) == \
            {"baseline", "rnd", "selected", "control"}


def test_gate_outcome_is_admission_record_not_result():
    feed = _feed()
    outcomes = feed["recorded_outcomes"]
    assert outcomes and "1487" in outcomes[0]["record"]
    for seg in feed["research_segments"]:
        if seg["members"]["baseline"]:
            assert seg["status"]["gate_award"] == "parked"
            assert seg["status"]["axes_status"][
                "produced_output_results_validated"] == "pending"
    # Criteria are the three axes — the gate is not among them.
    assert feed["classes"]["research-silos"]["criteria"] == [
        "produced_output_results_validated",
        "feature_extractions",
        "consensus_implementation"]
