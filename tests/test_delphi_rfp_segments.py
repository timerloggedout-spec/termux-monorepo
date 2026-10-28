"""Delphi RFP segmentation, inside delphi-rfp-feed/v1.

Owner collision rule: ONE feed, ONE collector. Segmentation rides
inside the flood collector (rfp_flood_feed.py) from
ops/delphi/rfp-segments.json — no second collector, no second feed.
Pins: every entry carries exactly one segment; the segments block
accounts for every RFP; research segments match the silo registry;
segment rollups count members/states only (no score fields).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "apps/help-wanted-dashboard/data/delphi-rfp-feed.json"


def _feed() -> dict:
    return json.loads(FEED.read_text())


def test_every_entry_in_exactly_one_segment():
    f = _feed()
    seg = f["segments"]
    members = [n for s in seg["segments"] for n in s["members"]]
    members += seg["unassigned"]
    assert sorted(members) == sorted(r["number"] for r in f["rfps"])
    assert len(members) == len(set(members))
    for r in f["rfps"]:
        owner = [s["segment_id"] for s in seg["segments"]
                 if r["number"] in s["members"]]
        assert r.get("segment") == (owner[0] if owner else None)


def test_research_segments_match_silo_registry():
    f = _feed()
    silos = json.loads(
        (ROOT / "ops/delphi/research-silos.json").read_text())["silos"]
    research = [s for s in f["segments"]["segments"]
                if s["class"] == "research-silos"]
    assert sorted(s["segment_id"] for s in research) == \
        sorted(s["id"] for s in silos)
    for s in research:
        assert len(s["members"]) == 4  # baseline + 3 variants
        assert s["axes_total"] == 3
    assert f["segments"]["classes"]["research-silos"]["criteria"] == [
        "produced_output_results_validated",
        "feature_extractions",
        "consensus_implementation"]


def test_rollups_count_states_never_scores():
    f = _feed()
    for s in f["segments"]["segments"]:
        assert set(s) <= {"segment_id", "class", "members", "by_status",
                          "gate_scored", "axes_recorded", "axes_total"}
        assert sum(s["by_status"].values()) == len(s["members"])
        assert s["gate_scored"] == len(s["members"]) - \
            s["by_status"].get("unscored", 0)


def test_collector_reads_segments_config(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rfp_flood_feed", ROOT / "scripts/delphi/rfp_flood_feed.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg, silos = mod._segments_config(tmp_path)
    assert cfg is not None and silos is not None  # working-tree fallback
    assert set(cfg["classes"]) == {"research-silos", "quota-surfaces",
                                   "meta-process"}
