import io
import json
import pytest
from scripts import model_performance_index

def test_percentile_fast():
    assert model_performance_index.percentile_fast([], 0.95) is None
    assert model_performance_index.percentile_fast([42], 0.95) == 42
    vals = [10, 20, 30, 40, 50]
    # percentile_fast expects sorted list
    assert model_performance_index.percentile_fast(vals, 0.5) == 30.0
    assert model_performance_index.percentile_fast(vals, 0.95) == 48.0

def test_main_execution(monkeypatch, capsys):
    sample_lines = [
        json.dumps({
            "experiment_id": "exp-1",
            "route_status": "succeeded",
            "task_outcome": "PASS",
            "provider": "gemini",
            "requested_model": "gemini-2.5-flash",
            "role": "triage",
            "latency_ms": 120,
            "requests_used": 1,
            "correctness": 1.0,
            "integration_success": 1.0,
            "reviewer_acceptance": 0.9,
            "warning_count": 0,
            "error_count": 0
        }),
        json.dumps({
            "experiment_id": "exp-2",
            "route_status": "failed",
            "task_outcome": "FAIL",
            "provider": "gemini",
            "requested_model": "gemini-2.5-flash",
            "role": "triage",
            "latency_ms": 400,
            "requests_used": 1,
            "error_class": "rate_limit",
            "warning_count": 1,
            "error_count": 1
        }),
        json.dumps({
            "experiment_id": "exp-3",
            "route_status": "skipped",
            "provider": "gemini",
            "requested_model": "gemini-2.5-flash",
            "role": "triage"
        }),
        # Duplicate experiment_id exp-1 should be overwritten
        json.dumps({
            "experiment_id": "exp-1",
            "route_status": "succeeded",
            "task_outcome": "PASS",
            "provider": "gemini",
            "requested_model": "gemini-2.5-flash",
            "role": "triage",
            "latency_ms": 100,
            "requests_used": 1,
            "correctness": 1.0,
            "integration_success": 1.0,
            "reviewer_acceptance": 1.0,
            "warning_count": 0,
            "error_count": 0
        }),
    ]

    monkeypatch.setattr("sys.stdin", io.StringIO("\n".join(sample_lines)))
    model_performance_index.main()

    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["schema_version"] == 2
    assert data["observations"] == 3
    assert len(data["models"]) == 1

    model_stat = data["models"][0]
    assert model_stat["provider"] == "gemini"
    assert model_stat["model"] == "gemini-2.5-flash"
    assert model_stat["role"] == "triage"
    assert model_stat["attempts"] == 2
    assert model_stat["succeeded"] == 1
    assert model_stat["skipped"] == 1
    assert model_stat["provider_failures"] == 1
    assert model_stat["success_rate"] == 0.5
    assert model_stat["task_pass"] == 1
    assert model_stat["task_fail"] == 0
    assert model_stat["execution_score_v2"] is not None

def test_invalid_status(monkeypatch):
    sample = json.dumps({"route_status": "invalid_status"})
    monkeypatch.setattr("sys.stdin", io.StringIO(sample))
    with pytest.raises(SystemExit) as exc:
        model_performance_index.main()
    assert "invalid route_status" in str(exc.value)

def test_invalid_outcome(monkeypatch):
    sample = json.dumps({"route_status": "succeeded", "task_outcome": "INVALID"})
    monkeypatch.setattr("sys.stdin", io.StringIO(sample))
    with pytest.raises(SystemExit) as exc:
        model_performance_index.main()
    assert "invalid task_outcome" in str(exc.value)
