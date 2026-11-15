import json
from pathlib import Path

import pytest

from scripts.ops import provider_validation_stamp as stamp


def receipt(status="inference_validated", no_cost=True):
    return {
        "schema": "provider-inference-validation/v1",
        "provider": "groq",
        "model": "free/chat",
        "validation_status": status,
        "inference_status": "passed" if status == "inference_validated" else "not_attempted",
        "no_cost_verified": no_cost,
        "validation_scope": "policy_gated_no_cost_inference_smoke",
        "terms_accepted": "policy_asserted",
        "entitlement_verified": "policy_asserted",
        "dispatch_eligible": False,
        "diagnosis": "invoke succeeded" if status == "inference_validated" else "no verified free model",
        "experiment_label": "QUE-5454",
        "observed_at": "2026-11-15T13:00:00Z",
        "run_id": "12345",
        "run_attempt": "1",
        "latency_ms": 420,
    }


def test_build_stamp_maps_passed_no_cost_validation_to_completed_free_tier():
    result = stamp.build_stamp(receipt(), run_id="12345", run_attempt="1",
                               run_url="https://github.com/org/repo/actions/runs/12345",
                               experiment_label="QUE-5454")
    assert result["task_class"] == "inference-probe"
    assert result["outcome"]["status"] == "completed"
    assert result["outcome"]["confirmed"] is True
    assert result["quota"]["cost_class"] == "free-tier"
    assert result["usage"]["latency_ms"] == 420


def test_build_stamp_keeps_deferred_quota_class_unestablished():
    result = stamp.build_stamp(receipt("deferred", no_cost=False), run_id="12345", run_attempt="1",
                               run_url="https://github.com/org/repo/actions/runs/12345",
                               experiment_label="QUE-5454")
    assert result["outcome"]["status"] == "deferred"
    assert result["outcome"]["confirmed"] is None
    assert result["quota"]["cost_class"] == "not_established"


def test_build_stamp_rejects_experiment_label_mismatch():
    with pytest.raises(ValueError, match="receipt_experiment_label_mismatch"):
        stamp.build_stamp(receipt(), run_id="12345", run_attempt="1",
                          run_url="https://github.com/org/repo/actions/runs/12345",
                          experiment_label="OTHER")


def test_dispatch_stamp_posts_workflow_dispatch_without_logging_token():
    captured = {}

    class Response:
        status = 204
        def __enter__(self): return self
        def __exit__(self, *args): return False

    def opener(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode())
        captured["timeout"] = timeout
        return Response()

    result = stamp.build_stamp(receipt(), run_id="12345", run_attempt="1",
                               run_url="https://github.com/org/repo/actions/runs/12345",
                               experiment_label="QUE-5454")
    assert stamp.dispatch_stamp(result, repository="org/repo", token="fixture-token", opener=opener) == 204
    assert captured["url"].endswith("/actions/workflows/dispatch-stamp-fanout.yml/dispatches")
    assert captured["body"]["ref"] == "master"
    inner = json.loads(captured["body"]["inputs"]["stamp"])
    assert inner["provider"] == "groq"
    assert inner["dispatch_id"] == "provider-validation-12345-1-groq"
    assert "fixture-token" not in json.dumps(captured["body"])


def test_dry_run_reads_receipts_without_token_or_network(tmp_path, monkeypatch, capsys):
    artifact = tmp_path / "provider-validation-groq"
    artifact.mkdir()
    (artifact / "receipt.json").write_text(json.dumps(receipt()))
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert stamp.main([
        "--receipts-dir", str(tmp_path), "--repository", "org/repo",
        "--run-id", "12345", "--run-attempt", "1",
        "--run-url", "https://github.com/org/repo/actions/runs/12345",
        "--experiment-label", "QUE-5454", "--dry-run",
    ]) == 0
    output = capsys.readouterr().out
    assert '"provider": "groq"' in output
    assert "provider_validation_stamps_emitted=0" in output


def test_build_stamp_rejects_unsafe_experiment_label():
    with pytest.raises(ValueError, match="experiment_label_invalid"):
        stamp.build_stamp(receipt(), run_id="12345", run_attempt="1",
                          run_url="https://github.com/org/repo/actions/runs/12345",
                          experiment_label="QUE-5454\nmalicious")

def test_smoke_receipt_cannot_claim_dispatch_eligibility():
    value = receipt()
    value["dispatch_eligible"] = True
    with pytest.raises(ValueError, match="smoke_receipt_cannot_assert_dispatch_eligibility"):
        stamp.build_stamp(value, run_id="12345", run_attempt="1",
                          run_url="https://github.com/org/repo/actions/runs/12345",
                          experiment_label="QUE-5454")