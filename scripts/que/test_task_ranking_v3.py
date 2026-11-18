"""Focused deterministic tests for que-task-rank/v3-compounding."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_ranking_v3 as v3


def evidence(scale=1.0):
    return {
        "dimensions": {key: min(1.0, scale) for key in v3.WEIGHTS},
        "costs": {"execution_effort": 0.2, "elapsed_delay": 0.2,
                  "coordination_rework": 0.1},
        "realization": 0.8,
    }


def test_weights_and_full_score_are_deterministic():
    assert sum(v3.WEIGHTS.values()) == 100.0
    first = v3.score_compounding(evidence())
    second = v3.score_compounding(evidence())
    assert first == second
    assert first["eligible"] is True
    assert first["benefit_points"] == 100.0
    assert first["normalized_effort"] == 0.5
    assert first["raw_efficiency"] == 16000.0


def test_missing_invalid_and_boolean_values_are_not_zero_imputed():
    for bad in (None, True, float("nan"), float("inf"), -0.1, 1.1, "bad"):
        sample = evidence()
        sample["dimensions"]["downstream_unlock"] = bad
        result = v3.score_compounding(sample)
        assert result["eligible"] is False
        assert "dimensions.downstream_unlock" in result["missing"]


def test_missing_rows_fall_back_to_v1_and_never_mix_claim_order():
    result = v3.rank_compounding(
        [{"issue": 10, "v1_score": 20, "v1_rank": 2},
         {"issue": 11, "v1_score": 30, "v1_rank": 1}],
        {10: evidence()},
    )
    assert result["complete_coverage"] is False
    assert result["eligible_count"] == 1
    assert result["v1_fallback"][0]["issue"] == 11
    assert result["claim_order"] is None
    assert result["claim_order_binding"] is False


def test_wall_imminence_is_lexicographic_inside_candidate_arm():
    result = v3.rank_compounding(
        [{"issue": 1, "v1_score": 1, "wall_in_min": 49 * 60},
         {"issue": 2, "v1_score": 0, "wall_in_min": 48 * 60}],
        {1: evidence(1.0), 2: evidence(0.1)},
    )
    assert result["eligible"][0]["issue"] == 2
    assert result["eligible"][0]["wall_imminent"] is True


def test_duplicate_issue_ids_rejected():
    try:
        v3.rank_compounding([{"issue": 1}, {"issue": 1}], {})
    except ValueError:
        return
    raise AssertionError("duplicate issue IDs must fail closed")


def test_percentiles_are_cohort_local_and_ties_are_equal():
    result = v3.rank_compounding(
        [{"issue": 1}, {"issue": 2}, {"issue": 3}],
        {1: evidence(0.5), 2: evidence(0.5), 3: evidence(1.0)},
    )
    by_id = {row["issue"]: row for row in result["eligible"]}
    assert by_id[1]["cohort_percentile"] == by_id[2]["cohort_percentile"]
    assert by_id[3]["cohort_percentile"] > by_id[1]["cohort_percentile"]
