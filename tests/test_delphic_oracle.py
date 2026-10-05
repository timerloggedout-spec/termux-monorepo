import importlib.util
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
        {"experiment_id": "a", "executed": True, "attributed": True, "outcome": True},
        {"experiment_id": "b", "executed": True, "attributed": True, "outcome": False},
        {"experiment_id": "b", "executed": True, "attributed": True, "outcome": False},
        {"experiment_id": "c", "executed": False, "attributed": True, "outcome": False},
        {"experiment_id": "d", "executed": True, "attributed": False, "outcome": False},
        {"experiment_id": "e", "executed": True, "attributed": True, "outcome": None},
        {"experiment_id": None, "executed": True, "attributed": True, "outcome": True},
        {"experiment_id": "e", "executed": True, "attributed": True, "outcome": True},
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
                "experiment_id": "x1",
                "executed": True,
                "attributed": True,
                "outcome": True,
                "provider": "gemini",
            },
            {
                "event_id": "e2",
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
    assert len(result["posterior"]["credible_interval_95"]) == 2
    assert len(result["posterior"]["credible_interval_95_approx"]) == 2
    assert "tensor" in result["left_now"]
    assert "constellation" in result["left_now"]
    assert "dag" in result["right_interthreading"]
    assert "markov" in result["right_interthreading"]
    assert result["authority"]["observatory_read_only"] is True
    assert result["authority"]["promotion_authority"] is False
