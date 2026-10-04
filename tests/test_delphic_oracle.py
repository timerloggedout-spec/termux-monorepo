import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("delphic_oracle", ROOT / "scripts" / "delphic_oracle.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_posterior_ignores_admission_unknown_and_duplicate():
    belief, counts = m.posterior([
        {"experiment_id":"a","executed":True,"attributed":True,"outcome":True},
        {"experiment_id":"b","executed":True,"attributed":True,"outcome":False},
        {"experiment_id":"b","executed":True,"attributed":True,"outcome":False},
        {"experiment_id":"c","executed":False,"attributed":True,"outcome":False},
        {"experiment_id":"d","executed":True,"attributed":False,"outcome":False},
        {"experiment_id":"e","executed":True,"attributed":True,"outcome":None},
    ])
    assert belief.alpha == 2.0
    assert belief.beta == 2.0
    assert counts["successes"] == 1
    assert counts["failures"] == 1

def test_evi_and_review_admission_are_deterministic():
    assert m.evi(0.60, 0.85, 0.10) == 0.15
    assert m.adversarial_admission(interval_width=.10) == "not_admitted"
    assert m.adversarial_admission(interval_width=.35) == "advisory"
    assert m.adversarial_admission(interval_width=.35, benchmark_regression=True) == "required"
    assert m.adversarial_admission(interval_width=.05, decision_impact=.95) == "required"

def test_workflow_preserves_two_sides_and_authority_boundary():
    result = m.workflow({
        "observations":[
            {"event_id":"e1","experiment_id":"x1","executed":True,"attributed":True,"outcome":True,"provider":"gemini"},
            {"event_id":"e2","experiment_id":"x2","executed":True,"attributed":True,"outcome":False,"provider":"openrouter"},
        ],
        "benchmark_regression":False,
    })
    assert result["posterior"]["counts"]["successes"] == 1
    assert "tensor" in result["left_now"]
    assert "constellation" in result["left_now"]
    assert "dag" in result["right_interthreading"]
    assert "markov" in result["right_interthreading"]
    assert result["authority"]["observatory_read_only"] is True
    assert result["authority"]["promotion_authority"] is False
