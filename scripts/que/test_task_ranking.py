"""QUE #5283 task_ranking (method que-task-rank/v1): score components,
claim order vs age order, wall-imminence class, terminal split,
sub-gate rows, backfill determinism. Fixtures only."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_ranking as tr

NOW = datetime(2026, 11, 12, 20, 0, tzinfo=timezone.utc)


def disp(issue, state="queued", tier=0, age_min=0, wall_in_min=None):
    return {"issue": issue, "state": state, "age_min": age_min,
            "tier": {"index": tier, "name": "BASE"},
            "wall_in_min": wall_in_min, "nearest_wall": None}


def test_score_components_from_row_only():
    s = tr.score_dispatch(disp(1, state="escalated", tier=4, age_min=43200))
    assert s["components"] == {"tier": 80.0, "wall": 0.0, "age": 50.0, "state": 40.0}
    assert s["score"] == 170.0


def test_wall_inside_48h_outranks_everything_else():
    imminent = disp(1, wall_in_min=600)                      # 10h to wall
    heavy = disp(2, state="escalated", tier=4, age_min=43200)  # max non-wall
    rows, summary = tr.rank_dispatches([heavy, imminent])
    by_issue = {r["issue"]: r for r in rows}
    assert by_issue[1]["rank"] == 1 and by_issue[2]["rank"] == 2
    assert by_issue[1]["score"] > by_issue[2]["score"]
    assert summary["claim_order"] == [1, 2]


def test_wall_beyond_48h_decays_and_past_wall_is_imminent():
    assert tr.wall_points(49 * 60) < tr.wall_points(600)
    assert tr.wall_points(-30) >= 1000.0  # overdue wall = imminent class
    assert tr.wall_points(201 * 60) == 0.0
    assert tr.wall_points(None) == 0.0


def test_claim_order_excludes_claimed_and_delta_vs_age():
    rows_in = [disp(1, age_min=9000),               # oldest, low score
               disp(2, state="claimed", tier=4, age_min=8000),
               disp(3, state="escalated", tier=2, age_min=100)]
    rows, summary = tr.rank_dispatches(rows_in)
    assert summary["claim_order"] == [3, 1]          # rank order, claimed out
    assert summary["age_order"] == [1, 3]            # age-only order
    delta = {d["issue"]: d for d in summary["delta_vs_age_order"]}
    assert delta[3]["rank"] == 1 and delta[3]["age_rank"] == 2
    assert summary["moved"] == 2
    assert summary["method"] == "que-task-rank/v1" and summary["advisory"] is True
    # input rows are not mutated
    assert "score" not in rows_in[0]


def test_deterministic_rerank_is_backfill_comparable():
    rows_in = [disp(1, age_min=5), disp(2, state="escalated", tier=1, age_min=9)]
    a, sa = tr.rank_dispatches(rows_in)
    b, sb = tr.rank_dispatches(rows_in)
    assert a == b and sa == sb


def test_nearest_wall_from_timebox_tiers():
    tb = {"tiers": [{"tier": 0, "name": "BASE", "at": "2026-11-10T00:00:00Z"},
                    {"tier": 1, "name": "CUSHION", "at": "2026-11-13T09:00:00Z"},
                    {"tier": 4, "name": "FINAL", "at": "2026-11-13T12:00:00Z"}]}
    wall_iso, wall_in = tr.nearest_wall(tb, NOW)
    assert wall_iso == "2026-11-13T09:00:00Z" and wall_in == 13 * 60.0
    past_only = {"tiers": [{"tier": 0, "name": "BASE", "at": "2026-11-01T00:00:00Z"}]}
    wall_iso, wall_in = tr.nearest_wall(past_only, NOW)
    assert wall_in < 0  # overdue
    assert tr.nearest_wall(None, NOW) == (None, None)
    assert tr.nearest_wall({"wall": "2026-11-20T00:00:00Z"}, NOW)[0] == "2026-11-20T00:00:00Z"


def _opp(oid, score, days_to_gate=None):
    return {"id": oid, "score": score, "days_to_gate": days_to_gate,
            "next_gate": None, "rank": 99}


def test_terminal_opportunities_leave_active_ranking():
    rows = [_opp("D1", 115.0, -7.5), _opp("AMD", 60.0, 40.0), _opp("C12", 50.0, 2.0)]
    states = {"D1": "closed", "AMD": "live", "C12": "live"}
    out = tr.rank_opportunities(rows, states, {}, NOW)
    # C12's gate is exactly 48h out -> imminent class -> it outranks
    # AMD's higher score with a 40d gate; D1 (closed, top score,
    # past gate) is out of the active ranking entirely.
    assert [r["id"] for r in out["active"]] == ["C12", "AMD"]
    assert out["terminal"][0]["id"] == "D1"
    assert out["terminal"][0]["rank"] is None


def test_subgate_inside_48h_outranks_pastgate_score():
    # AMD reads as one far row (league wall) but carries the C3 course
    # wall as a sub-gate inside 48h -> wall-imminent through the gate.
    rows = [_opp("OTHER", 95.0, 10.0), _opp("AMD", 40.0, 30.0)]
    states = {"OTHER": "live", "AMD": "live"}
    c3 = (NOW + timedelta(hours=13)).strftime("%Y-%m-%dT%H:%M:%SZ")
    gates = {"AMD": [{"name": "dates.c3_wall", "at": c3}]}
    out = tr.rank_opportunities(rows, states, gates, NOW)
    assert out["active"][0]["id"] == "AMD" and out["active"][0]["wall_48h"] is True
    assert out["gate_rows"][0]["gate"] == "dates.c3_wall"
    assert out["gate_rows"][0]["rank"] == 1
    amd = next(r for r in out["active"] if r["id"] == "AMD")
    assert amd["sub_gates"] == 1 and amd["nearest_wall_hours"] == 13.0
    assert amd["score"] == 40.0  # score of record not recomputed


def test_wall48_outranks_higher_pastgate_score():
    rows = [_opp("PAST", 120.0, -3.9), _opp("NEAR", 30.0, 1.0)]
    states = {"PAST": "live", "NEAR": "live"}
    out = tr.rank_opportunities(rows, states, {}, NOW)
    # PAST's gate is past (<48h) so it is also imminent; tie broken by score
    assert out["active"][0]["wall_48h"] is True
    far = [_opp("FAR", 120.0, 30.0), _opp("NEAR", 30.0, 1.0)]
    out2 = tr.rank_opportunities(far, {"FAR": "live", "NEAR": "live"}, {}, NOW)
    assert out2["active"][0]["id"] == "NEAR"  # 24h wall beats a 120 score at 30d
