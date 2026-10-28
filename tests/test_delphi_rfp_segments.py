"""Delphi RFP segmentation, inside delphi-rfp-feed/v1.

Owner collision rule: ONE feed, ONE collector. Segmentation rides
inside the flood collector (rfp_flood_feed.py) from
ops/delphi/rfp-segments.json — no second collector, no second feed.
Pins: every queue entry carries exactly one segment; research
segments describe the 12 PARTICIPANTS (owner reclassification,
PR #2039) from ops/delphi/research-participants.json — arms, not
queue members; segment rollups count members/states only (no score
fields); research axes states come from the axes record.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEED = ROOT / "apps/help-wanted-dashboard/data/delphi-rfp-feed.json"


def _feed() -> dict:
    return json.loads(FEED.read_text())


def test_every_queue_entry_in_exactly_one_segment():
    f = _feed()
    seg = f["segments"]
    entry_numbers = {r["number"] for r in f["rfps"]}
    membered = [n for s in seg["segments"] for n in s["members"]
                if n in entry_numbers]
    membered += seg["unassigned"]
    assert sorted(membered) == sorted(entry_numbers)
    assert len(membered) == len(set(membered))
    for r in f["rfps"]:
        owner = [s["segment_id"] for s in seg["segments"]
                 if r["number"] in s["members"]]
        assert r.get("segment") == (owner[0] if owner else None)


def test_research_segments_are_the_participants():
    f = _feed()
    parts = json.loads(
        (ROOT / "ops/delphi/research-participants.json").read_text())
    research = [s for s in f["segments"]["segments"]
                if s["class"] == "research-silos"]
    assert sorted(s["segment_id"] for s in research) == \
        sorted(p["silo_id"] for p in parts["participants"])
    by_id = {p["silo_id"]: p for p in parts["participants"]}
    for s in research:
        p = by_id[s["segment_id"]]
        filings = [p["filings"]["baseline"],
                   *p["filings"]["arms"].values()]
        assert s["kind"] == "participant"
        assert sorted(s["members"]) == sorted(filings)
        assert {a["number"]: a["arm"] for a in s["arms"]} == {
            p["filings"]["baseline"]: "baseline",
            **{n: a for a, n in p["filings"]["arms"].items()}}
        assert s["by_status"] == {"participant": 4}
        assert s["gate_scored"] == 0  # gate does not score participants


def test_rollups_count_states_never_scores():
    f = _feed()
    for s in f["segments"]["segments"]:
        assert sum(s["by_status"].values()) == len(s["members"])
        unscored = s["by_status"].get("unscored", 0)
        participant = s["by_status"].get("participant", 0)
        assert s["gate_scored"] == \
            len(s["members"]) - unscored - participant
        assert not ({"score", "mean", "average", "rank"}
                    & set(s.keys()))


def test_axes_states_come_from_the_axes_record():
    """Cycle-1 axes record (ops/delphi/research-axes.json) is the
    home the silo spec names; participant segments carry its counts."""
    f = _feed()
    rec = json.loads(
        (ROOT / "ops/delphi/research-axes.json").read_text())
    assert rec["schema"] == "delphi.research-axes.v1"
    for s in f["segments"]["segments"]:
        if s["class"] != "research-silos":
            continue
        silo_rec = rec["silos"][s["segment_id"]]
        recorded = sum(1 for v in silo_rec.values()
                       if isinstance(v, dict) and "state" in v)
        assert s["axes_recorded"] == recorded
        assert s["axes_total"] == 3
