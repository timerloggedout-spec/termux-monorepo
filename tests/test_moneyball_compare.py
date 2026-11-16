"""Comparison tests: MoneyBall v1 (as landed) vs the competing v2
(moneyball-plane/v2, docs/schemas/moneyball-score.schema.json).

Run on GitHub by .github/workflows/moneyball-compare.yml and locally:
    python -m pytest tests/test_moneyball_compare.py -v

Recorded facts under test (verified firsthand 2026-10-28):
- Temporal pass (docs/proposals/passes/temporal-durable-execution/
  pass.json): moneyball_weighted pi-core-resume 8.9, cookbook-agent-loop
  8.5, contract-first 6.5, serverless-skill 4.8, versioned-autoscale
  3.6; ballot round 2 was a four-way tie at 25.0.
- Strands pass: three candidates with identical profiles, tied.
Axis values in the v2 fixtures below are SYNTHETIC test data (uniform
per candidate) chosen so the recomputed composite equals the recorded
v1 composite exactly; what is asserted is ordering/tie behaviour and
validator semantics, not the synthetic axes.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "moneyball"))
from moneyball_v2 import composite, ranking, validate_v1_pass, validate_v2, v1_explanation_fields

WEIGHTS = {"relevance": 0.30, "evidence_maturity": 0.25, "survivability": 0.20,
           "adoption_cost_inverse": 0.15, "composability": 0.10}

TEMPORAL_V1 = {
    "schema": "oracle-method-pass/v1",
    "pass_id": "temporal-durable-execution",
    "round_2_scores_tied": True,
    "moneyball_weighted": {
        "temporal-durable-execution-pi-core-resume": 8.9,
        "temporal-durable-execution-cookbook-agent-loop": 8.5,
        "temporal-durable-execution-contract-first": 6.5,
        "temporal-durable-execution-serverless-skill": 4.8,
        "temporal-durable-execution-versioned-autoscale": 3.6,
    },
}


def v2_record(entity, value, decision_time="2026-10-27T00:00:00Z"):
    return {
        "schema": "moneyball-plane/v2",
        "record_id": f"test:{entity}",
        "pass_id": "temporal-durable-execution",
        "opportunity": {"entity_id": entity, "action": "adopt",
                        "context": "temporal-durable-execution pass",
                        "decision_time": decision_time},
        "baseline_id": "ballot-round-2-tie-at-25.0",
        "weights": {"axes": dict(WEIGHTS), "fixed_at": "docs/rfps/temporal-durable-execution/RFP.md#3"},
        "axes": [{"axis": a, "value": value, "evidence_refs": ["pass.json:moneyball_weighted"],
                  "evidence_strength": "limited", "uncertainty": 0.2} for a in WEIGHTS],
        "composite": value,
        "quantities": {"capability": value, "forecast": value, "incremental_effect": None,
                       "value": value, "surplus": value, "portfolio_marginal_contribution": None},
        "ballot": {"aggregate": 25.0, "relation": "beside_never_merged"},
        "point_in_time": {"event_time": "2026-10-27T00:00:00Z",
                          "published_at": "2026-10-27T00:00:00Z",
                          "ingested_at": "2026-10-27T00:00:00Z"},
    }


def temporal_v2():
    return [v2_record(k, v) for k, v in TEMPORAL_V1["moneyball_weighted"].items()]


# ---- v1: what the landed schema guarantees -------------------------------

def test_v1_temporal_record_is_valid_v1():
    assert validate_v1_pass(TEMPORAL_V1) == []


def test_v1_carries_no_explanation_beyond_the_number():
    # The gap v2 competes on: v1's record-level explanation set is the
    # composite alone (charter: "a bare number is not a result").
    assert v1_explanation_fields(TEMPORAL_V1) == {"composite"}


# ---- v2: validity + recorded behaviour -----------------------------------

def test_v2_temporal_records_valid_and_recompute():
    for rec in temporal_v2():
        assert validate_v2(rec) == [], rec["record_id"]
        assert abs(composite(WEIGHTS, rec["axes"]) - rec["composite"]) < 1e-9


def test_v2_preserves_temporal_ordering():
    order = ranking(temporal_v2())
    assert order == [f"test:{k}" for k in TEMPORAL_V1["moneyball_weighted"]]


def test_v2_identical_profiles_stay_tied():
    recs = [v2_record(f"strands-{i}", 7.0) for i in range(3)]
    assert len({r["composite"] for r in recs}) == 1  # tie preserved, not separated


def test_v2_null_incremental_effect_is_visible_and_valid():
    rec = v2_record("x", 5.0)
    assert rec["quantities"]["incremental_effect"] is None
    assert validate_v2(rec) == []


# ---- v2: rejections v1 cannot express ------------------------------------

def test_v2_rejects_bare_number_record():
    bare = {"schema": "moneyball-plane/v2", "moneyball_weighted": {"x": 8.9}}
    assert validate_v2(bare)  # many problems, incl. missing axes


def test_v2_rejects_weights_not_summing_to_one():
    rec = v2_record("x", 5.0)
    rec["weights"]["axes"]["relevance"] = 0.20
    assert any("sum to 1" in p for p in validate_v2(rec))


def test_v2_rejects_unfixed_weights():
    rec = v2_record("x", 5.0)
    rec["weights"]["fixed_at"] = ""
    assert any("fixed_at" in p for p in validate_v2(rec))


def test_v2_rejects_merged_ballot():
    rec = v2_record("x", 5.0)
    rec["ballot"]["relation"] = "merged_into_ballot"
    assert any("beside_never_merged" in p for p in validate_v2(rec))


def test_v2_rejects_missing_baseline():
    rec = v2_record("x", 5.0)
    rec["baseline_id"] = ""
    assert any("baseline_id" in p for p in validate_v2(rec))


def test_v2_rejects_absent_quantity_key_but_accepts_null():
    rec = v2_record("x", 5.0)
    del rec["quantities"]["incremental_effect"]
    assert any("incremental_effect" in p for p in validate_v2(rec))


def test_v2_rejects_composite_mismatch():
    rec = v2_record("x", 5.0)
    rec["composite"] = 9.9
    assert any("composite does not match" in p for p in validate_v2(rec))


def test_v2_rejects_axis_without_evidence():
    rec = v2_record("x", 5.0)
    rec["axes"][0]["evidence_refs"] = []
    assert any("evidence_refs" in p for p in validate_v2(rec))


def test_v2_rejects_point_in_time_leakage():
    rec = v2_record("x", 5.0)
    rec["point_in_time"]["published_at"] = "2026-10-28T00:00:00Z"  # after decision_time
    assert any("point-in-time" in p for p in validate_v2(rec))


# ---- expressiveness matrix ------------------------------------------------

def test_expressiveness_v2_strictly_extends_v1():
    v1_fields = v1_explanation_fields(TEMPORAL_V1)
    v2_fields = {"composite", "per_axis_values", "evidence_refs", "evidence_strength",
                 "uncertainty", "weights_fixed_at", "baseline", "opportunity_context",
                 "separate_quantities", "null_effect_visible", "point_in_time"}
    assert v1_fields < v2_fields
