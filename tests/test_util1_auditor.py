import importlib.util
import json
from pathlib import Path


SCRIPT = Path("experiments/doe/util-1-provider-rotation/scripts/util1_auditor.py")


def load_auditor():
    spec = importlib.util.spec_from_file_location("util1_auditor_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_agentrouter_dispatch_projection_preserves_model_protocol_and_correlation(tmp_path):
    auditor = load_auditor()
    auditor.ROOT = tmp_path
    auditor.FEED = tmp_path / "desk-feed.json"
    auditor.REG = tmp_path / "registry.json"
    auditor.OUT = tmp_path / "records"
    auditor.REG.write_text(json.dumps({"services": [{"provider": "agentrouter"}]}))
    auditor.FEED.write_text(json.dumps({
        "dispatches": [{
            "id": "entry-42",
            "provider": "agentrouter",
            "selection_reason": "approved rotation",
            "ts": "2026-11-05T12:00:00Z",
            "model_id": "account-pool/model-alpha",
            "protocol": "openai-compatible",
            "workflow_id": "provider-inference",
            "run_id": "123456789",
            "run_attempt": 2,
            "temporal_workflow_id": "temporal-abc",
            "request_id": "req-abc",
            "doe_campaign_id": "util-1-provider-rotation",
            "experiment_instance_key": "agentrouter/model-alpha",
            "input_tokens": 120,
            "output_tokens": 45,
            "total_tokens": 165,
            "quota_tokens": 165,
            "usage_cost": 0.001,
            "latency_ms": 840,
            "time_to_first_token_ms": 190,
            "tokens_per_second": 53.5,
        }]
    }))

    assert auditor.main() == 0
    record = json.loads((auditor.OUT / "latest-audit.json").read_text())["scored"][0]
    assert record["model_id"] == "account-pool/model-alpha"
    assert record["protocol"] == "openai-compatible"
    assert record["workflow_id"] == "provider-inference"
    assert record["run_id"] == "123456789"
    assert record["run_attempt"] == 2
    assert record["temporal_workflow_id"] == "temporal-abc"
    assert record["request_id"] == "req-abc"
    assert record["doe_campaign_id"] == "util-1-provider-rotation"
    assert record["experiment_instance_key"] == "agentrouter/model-alpha"
    assert record["usage"]["input_tokens"] == 120
    assert record["usage"]["quota_tokens"] == 165
    assert record["usage"]["latency_ms"] == 840
