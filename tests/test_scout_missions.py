import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("scout_missions", Path("scripts/scout_missions.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_creates_parallel_scouts_and_oversight_classes():
    roster = {
        "schema": "agent-scout-roster/v1",
        "observed_at": "2026-08-27T00:00:00Z",
        "candidates": [
            {"provider": "openrouter", "model": "stealth/ox-alpha", "status": "candidate"},
            {"provider": "deepseek", "model": "example", "status": "observed"},
        ],
    }
    result = MODULE.build(roster)
    assert len(result["scouts"]) == len(MODULE.SCOUTS)
    assert len(result["oversight_classes"]) >= 5
    assert all(item["proposal_only"] for item in result["scouts"])
    assert result["governance"]["manager_decides"] is True
    assert result["governance"]["correctness_over_latency"] is True


def test_oversight_is_not_model_admission():
    result = MODULE.build({"candidates": []})
    assert "oversight_classes" in result
    assert result["governance"]["evidence_required_for_promotion"] is True
