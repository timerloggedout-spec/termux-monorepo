import importlib.util
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "delphic_oracle", ROOT / "scripts" / "delphic_oracle.py"
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def test_posterior_ignores_unattributed_duplicate_missing_and_unknown_outcomes():
    belief, counts = m.posterior([
        {"experiment_id": "a", "source_sha": "sha-a", "event_id": "event-a", "observed_at": "2026-11-14T00:00:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1", "executed": True, "attributed": True, "outcome": True},
        {"experiment_id": "b", "source_sha": "sha-b", "event_id": "event-b", "observed_at": "2026-11-14T00:01:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1", "executed": True, "attributed": True, "outcome": False},
        {"experiment_id": "b", "source_sha": "sha-b", "event_id": "event-b", "observed_at": "2026-11-14T00:01:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1", "executed": True, "attributed": True, "outcome": False},
        {"experiment_id": "c", "executed": False, "attributed": True, "outcome": False},
        {"experiment_id": "d", "executed": True, "attributed": False, "outcome": False},
        {"experiment_id": "e", "executed": True, "attributed": True, "outcome": None},
        {"experiment_id": None, "executed": True, "attributed": True, "outcome": True},
        {"experiment_id": "e", "source_sha": "sha-e", "event_id": "event-e", "observed_at": "2026-11-14T00:02:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1", "executed": True, "attributed": True, "outcome": True},
    ])
    assert belief.alpha == 3.0
    assert belief.beta == 2.0
    assert counts["successes"] == 2
    assert counts["failures"] == 1


def test_exact_beta_interval_matches_wolfram_reference():
    belief = m.Belief(2.0, 2.0)
    assert abs(belief.mean - 0.5) < 1e-12
    assert abs(belief.sd - 0.22360679774997896) < 1e-12
    # Wolfram-verified BetaDistribution[2,2] equal-tail 95% interval,
    # evaluated 2026-10-05.
    lo, hi = belief.interval95
    assert abs(lo - 0.0942993240502461) < 1e-12
    assert abs(hi - 0.9057006759497539) < 1e-12


def test_evi_and_evsi_are_deterministic():
    assert m.evi(0.60, 0.85, 0.10) == 0.15
    assert abs(
        m.expected_value_of_information(
            0.60,
            {"success": 0.5, "failure": 0.5},
            {"success": 0.90, "failure": 0.70},
            0.10,
        ) - 0.10
    ) < 1e-12


def test_review_admission_is_deterministic_and_validates_inputs():
    assert m.adversarial_admission(interval_width=.10) == "not_admitted"
    assert m.adversarial_admission(interval_width=.35) == "advisory"
    assert m.adversarial_admission(interval_width=.35, benchmark_regression=True) == "required"
    assert m.adversarial_admission(interval_width=.05, decision_impact=.95) == "required"
    try:
        m.adversarial_admission(interval_width=float("nan"))
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("expected finite-input validation")


def test_workflow_preserves_two_sides_and_math_contract():
    result = m.workflow({
        "observations": [
            {
                "event_id": "e1",
                "source_sha": "sha-e1",
                "observed_at": "2026-11-14T00:00:00Z",
                "instance_key": "instance-1", "policy_version": "delphic-oracle/v1",
                "experiment_id": "x1",
                "executed": True,
                "attributed": True,
                "outcome": True,
                "provider": "gemini",
            },
            {
                "event_id": "e2",
                "source_sha": "sha-e2",
                "observed_at": "2026-11-14T00:01:00Z",
                "instance_key": "instance-1", "policy_version": "delphic-oracle/v1",
                "experiment_id": "x2",
                "executed": True,
                "attributed": True,
                "outcome": False,
                "provider": "openrouter",
            },
        ],
        "benchmark_regression": False,
    })
    assert result["posterior"]["counts"]["successes"] == 1
    assert 0.0 <= result["posterior"]["one_step_information_gain"]
    assert abs(sum(result["posterior_predictive"]["three_trial_success_pmf"]) - 1.0) < 1e-12
    assert len(result["posterior"]["credible_interval_95"]) == 2
    assert len(result["posterior"]["credible_interval_95_approx"]) == 2
    assert "tensor" in result["left_now"]
    assert "constellation" in result["left_now"]
    assert "dag" in result["right_interthreading"]
    assert "markov" in result["right_interthreading"]
    assert result["authority"]["observatory_read_only"] is True
    assert result["authority"]["promotion_authority"] is False


def test_expected_value_of_information_rejects_non_finite_scalar_inputs():
    import math
    import pytest
    for current, cost in ((math.nan, 0.0), (0.0, math.inf)):
        with pytest.raises(ValueError):
            m.expected_value_of_information(current, {"yes": 1.0}, {"yes": 2.0}, cost)


def test_posterior_holds_conflicting_duplicate_experiment_outcomes():
    identity = {
        "source_sha": "sha-1", "event_id": "event-1",
        "observed_at": "2026-11-14T00:00:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1",
        "executed": True, "attributed": True, "experiment_id": "exp-1",
    }
    belief, counts = m.posterior([
        {**identity, "outcome": True},
        {**identity, "event_id": "event-2", "outcome": False},
    ])
    assert belief.alpha == 1.0 and belief.beta == 1.0
    assert counts["conflicts"] == 1
    assert counts["successes"] == counts["failures"] == 0


def test_posterior_ignores_rows_missing_required_provenance_identity():
    belief, counts = m.posterior([{
        "experiment_id": "missing-source", "event_id": "event-1",
        "observed_at": "2026-11-14T00:00:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1",
        "executed": True, "attributed": True, "outcome": True,
    }])
    assert belief.alpha == 1.0 and belief.beta == 1.0
    assert counts["successes"] == 0


def test_workflow_rejects_mixed_instance_observations():
    base = {
        "source_sha": "sha", "observed_at": "2026-11-14T00:00:00Z",
        "executed": True, "attributed": True, "outcome": True,
    }
    with pytest.raises(ValueError, match="one non-empty instance_key"):
        m.workflow({"observations": [
            {**base, "event_id": "e1", "experiment_id": "x1", "instance_key": "instance-1"},
            {**base, "event_id": "e2", "experiment_id": "x2", "instance_key": "instance-2"},
        ]})


def test_workflow_emits_replayable_provenance_digests():
    payload = {"observations": [{
        "event_id": "e1", "source_sha": "sha-e1",
        "observed_at": "2026-11-14T00:00:00Z", "instance_key": "instance-1", "policy_version": "delphic-oracle/v1",
        "experiment_id": "x1", "executed": True, "attributed": True,
        "outcome": True, "provider": "gemini",
    }]}
    first = m.workflow(payload)["provenance"]
    second = m.workflow(payload)["provenance"]
    for key in ("algorithm_id", "algorithm_version", "input_digest",
                "parameters_digest", "output_digest"):
        assert first[key] == second[key]
    assert first["runtime_ms"] >= 0
    assert first["executed_at"]


def test_workflow_holds_conflicting_experiment_outcomes():
    common = {
        "experiment_id": "exp-conflict",
        "source_sha": "sha-conflict",
        "observed_at": "2026-11-14T00:00:00Z",
        "instance_key": "instance-1",
        "policy_version": "delphic-oracle/v1",
        "executed": True,
        "attributed": True,
        "provider": "gemini",
    }
    result = m.workflow({"observations": [
        {**common, "event_id": "event-1", "outcome": True},
        {**common, "event_id": "event-2", "outcome": False},
    ]})
    assert result["posterior"]["status"] == "HELD_CONFLICTING_DUPLICATE_OUTCOMES"
    assert result["posterior"]["counts"]["conflicts"] == 1
    assert result["adversarial_review"]["admission"] == "advisory"


def test_inconclusive_evidence_does_not_suppress_required_review():
    result = m.workflow({"observations": [], "decision_impact": 0.95})
    assert result["posterior"]["status"] == "INCONCLUSIVE_NO_ADMISSIBLE_OBSERVATIONS"
    assert result["adversarial_review"]["admission"] == "required"
