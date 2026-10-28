"""Delphi RFP segmentation feed: a rollup layer over the feed of
record (delphi-rfp-feed/v1). Pins: every source RFP lands in exactly
one segment; research segments match the silo registry; member
statuses are the feed of record's awards, read — not re-derived;
research criteria are the three axes and every axis state comes from
the source feed's comparison_axes.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"


def _seg_feed() -> dict:
    p = DATA / "delphi-rfp-segments-feed.json"
    assert p.exists(), "segments feed missing — run the collector"
    return json.loads(p.read_text())


def _source() -> dict:
    return json.loads((DATA / "delphi-rfp-feed.json").read_text())


def test_collector_runs():
    r = subprocess.run(
        [sys.executable,
         str(ROOT / "scripts/delphi/rfp_segment_feed.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    f = _seg_feed()
    assert f["schema"] == "delphi-rfp-segments-feed/v1"
    assert f["sources"]["feed_of_record_schema"] == "delphi-rfp-feed/v1"


def test_every_source_rfp_assigned_exactly_once():
    seg, src = _seg_feed(), _source()
    nums = []
    for s in seg["research_segments"]:
        nums += [m["number"] for m in s["members"].values() if m]
    nums += [m["number"] for m in seg["quota_segment"]["members"]]
    nums += [s["member"]["number"] for s in seg["meta_segments"]
             if s["member"]]
    nums += [u["number"] for u in seg["unassigned"]]
    assert sorted(nums) == sorted(e["number"] for e in src["rfps"])
    assert len(nums) == len(set(nums))
    assert seg["totals"]["source_by_status"] == \
        src["summary"]["by_status"]


def test_member_statuses_match_feed_of_record():
    seg, src = _seg_feed(), _source()
    by_number = {e["number"]: e for e in src["rfps"]}
    for s in seg["research_segments"]:
        assert set(s["members"]) == \
            {"baseline", "rnd", "selected", "control"}
        for m in s["members"].values():
            if m:
                assert m["status"] == by_number[m["number"]]["status"]
    silos = json.loads(
        (ROOT / "ops/delphi/research-silos.json").read_text())["silos"]
    assert [s["segment_id"] for s in seg["research_segments"]] == \
        [s["id"] for s in silos]


def test_axes_states_come_from_source():
    seg, src = _seg_feed(), _source()
    by_surface = {e["surface_id"]: e for e in src["rfps"]}
    assert seg["classes"]["research-silos"]["criteria"] == [
        "produced_output_results_validated",
        "feature_extractions",
        "consensus_implementation"]
    for s in seg["research_segments"]:
        base = by_surface[s["segment_id"]]
        for axis, state in s["axes_status"].items():
            raw = base["comparison_axes"][axis]
            assert state == ("pending" if str(raw).startswith("pending")
                             else "recorded"), (s["segment_id"], axis)
