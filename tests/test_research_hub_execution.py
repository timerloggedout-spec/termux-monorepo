"""Real pinned Research -> hub -> durable quota -> logger, with no live inference."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib
import json
import os
from pathlib import Path
import sqlite3
import threading

from fastapi.testclient import TestClient
import pytest

from hub_quota_fixture import seed_quota
from llm_api_hub.server.admission import AdmissionDenied, QuotaAdmission, bind_canonical_observation
from scripts.provider_quota_managers import normalize_observation
from src import telemetry
from src.advanced_research_adapter import execute, PIN

hub = importlib.import_module("llm_api_hub.server.app")
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "integrations/swarms/advanced-research"


@pytest.fixture
def boundary(tmp_path, monkeypatch):
    monkeypatch.delenv("LLM_API_HUB_KEY", raising=False)
    log = tmp_path / "telemetry.jsonl"
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(log))
    manager = seed_quota(tmp_path / "quota.json", ["wrapper/deepseek"], remaining=20)
    monkeypatch.setattr(hub, "admission", manager)
    def forbidden(*args, **kwargs):
        raise AssertionError("live provider access forbidden")
    monkeypatch.setattr(hub.runtime, "complete_upstream", forbidden)
    monkeypatch.setattr(hub.research_providers, "complete", forbidden)
    monkeypatch.setattr(hub.runtime, "_get_dispatcher", forbidden)
    return TestClient(hub.app), manager, log


def body(attempt="attempt-1", **extra):
    return {"model": "wrapper/deepseek", "messages": [{"role": "user", "content": "sensitive prompt never logged"}],
            "max_tokens": 40, "run_id": "run-1", "job_id": "job-1", "request_id": attempt + "-request",
            "attempt_id": attempt, "adapter": "advanced-research", "source_revision": PIN, **extra}


def states(manager):
    with sqlite3.connect(manager.db_path) as db:
        return db.execute("SELECT state,sent,amount,actual_tokens FROM reservations ORDER BY created").fetchall()


def events(log):
    return [json.loads(line)["correlation"] for line in log.read_text().splitlines()]


def test_deny_causes_no_inference_then_admit_reconcile_and_retry_no_dispatch(boundary, tmp_path, monkeypatch):
    client, manager, log = boundary
    calls = []
    monkeypatch.setattr(hub.runtime, "complete_wrapper", lambda *a: calls.append(1) or "ok")
    monkeypatch.setattr(hub, "admission", QuotaAdmission(db_path=tmp_path / "absent.sqlite"))
    assert client.post("/v1/chat/completions", json=body()).status_code == 429
    assert calls == []
    assert events(log)[-1]["outcome"] == "DENIED"
    monkeypatch.setattr(hub, "admission", manager)
    assert client.post("/v1/chat/completions", json=body()).status_code == 200
    assert client.post("/v1/chat/completions", json=body()).status_code == 429
    assert calls == [1]
    assert states(manager)[0][:3] == ("charged", 1, 1)
    complete = [e for e in events(log) if e["event"] == "execution_complete"][0]
    assert complete["outcome"] == "UNKNOWN"
    assert complete["run_id"] == "run-1" and complete["attempt_id"] == "attempt-1"
    assert "sensitive prompt" not in log.read_text()


def test_prompt_cost_prevents_known_token_quota_overspend(boundary, tmp_path, monkeypatch):
    client, manager, log = boundary
    records = json.loads(manager.records_path.read_text())
    records["records"][0]["remaining_tokens"] = 100
    manager.records_path.write_text(json.dumps(records))
    bounded = QuotaAdmission(manager.records_path, tmp_path / "prompt-cost.sqlite")
    monkeypatch.setattr(hub, "admission", bounded)
    calls = []
    monkeypatch.setattr(hub.runtime, "complete_wrapper", lambda *a: calls.append(1) or "ok")
    request = body()
    assert hub.quota_token_budget(hub.ChatCompletionRequest(**request)) > 100
    response = client.post("/v1/chat/completions", json=request)
    assert response.status_code == 429
    assert calls == []
    assert states(bounded) == []
    assert events(log)[-1]["outcome"] == "DENIED"


def test_429_persists_cooldown_and_unknown_usage_across_restart(boundary, monkeypatch):
    client, manager, log = boundary
    calls = []
    def rate_limited(*args):
        calls.append(1)
        raise hub.research_providers.ProviderAdmissionError(429, "do not log raw credentials", "upstream_rate_limited", "120")
    monkeypatch.setattr(hub.runtime, "complete_wrapper", rate_limited)
    first = client.post("/v1/chat/completions", json=body())
    assert first.status_code == 429
    assert first.headers["retry-after"] == "120"
    monkeypatch.setattr(hub, "admission", QuotaAdmission(manager.records_path, manager.db_path))
    assert client.post("/v1/chat/completions", json=body("attempt-2")).status_code == 429
    assert calls == [1]
    assert states(manager)[0][0] == "charged"
    assert "raw credentials" not in log.read_text()
    assert "execution_failed" in {e["event"] for e in events(log)}


def test_actual_usage_is_reconciled_and_cancel_keeps_ambiguous_charge(boundary, monkeypatch):
    client, manager, log = boundary
    def fake_upstream(provider, request):
        return hub.completion_response(request.model, "ok", {"total_tokens": 7})
    monkeypatch.setattr(hub.runtime, "complete_upstream", fake_upstream)
    # Separate exact model identity; still the real manager and no provider network.
    monkeypatch.setattr(hub, "admission", seed_quota(manager.records_path, ["openrouter/fixture"]))
    request = body(model="openrouter/fixture")
    assert client.post("/v1/chat/completions", json=request).status_code == 200
    assert states(manager)[0][3] == 7
    monkeypatch.setattr(hub, "admission", seed_quota(manager.records_path, ["wrapper/deepseek", "openrouter/fixture"]))
    def cancelled(*args):
        raise InterruptedError("cancelled with private upstream text")
    monkeypatch.setattr(hub.runtime, "complete_wrapper", cancelled)
    with pytest.raises(InterruptedError):
        client.post("/v1/chat/completions", json=body("attempt-cancel"))
    assert states(manager)[-1][0] == "charged"
    terminal = events(log)[-1]
    assert terminal["event"] == "execution_cancelled" and terminal["outcome"] == "CANCELLED"
    assert "private upstream text" not in log.read_text()


def test_concurrent_hub_callers_do_not_overspend(boundary, monkeypatch):
    client, manager, log = boundary
    monkeypatch.setattr(hub, "admission", seed_quota(manager.records_path, ["wrapper/deepseek"], remaining=1))
    calls = []
    monkeypatch.setattr(hub.runtime, "complete_wrapper", lambda *a: calls.append(1) or "ok")
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda i: client.post("/v1/chat/completions", json=body(f"concurrent-{i}")).status_code, range(6)))
    assert results.count(200) == 1 and results.count(429) == 5 and calls == [1]


def test_canonical_normalized_signal_is_consumed_with_verified_binding(tmp_path):
    now = datetime.now(timezone.utc)
    observation = normalize_observation("groq", headers={"x-ratelimit-remaining-requests": "2"}, observed_at=now.isoformat(), scope="fixture-account-requests")
    row = bind_canonical_observation(observation, account_id="free-fixture", provider="groq", model="groq/fixture",
        remaining_field="remaining_requests", reset_at=(now + timedelta(hours=1)).isoformat(),
        verified_account=True, verified_free_account=True, provider_model_mapping={"groq/fixture": "groq"})
    path = tmp_path / "canonical.json"
    path.write_text(json.dumps({"schema_version": 1, "records": [row]}))
    manager = QuotaAdmission(path, tmp_path / "canonical.sqlite")
    assert manager.reserve("groq", "groq/fixture", attempt_id="one")
    assert manager.reserve("groq", "groq/fixture", attempt_id="two")
    with pytest.raises(AdmissionDenied):
        manager.reserve("groq", "groq/fixture", attempt_id="three")


def test_genuine_pinned_research_consumes_real_hub_quota_and_emits_correlated_terminal_events(boundary, monkeypatch):
    client, manager, log = boundary
    def fake(provider, request):
        content = " ".join(str(m.content) for m in request.messages)
        if "director" in content.lower():
            return json.dumps({"queries": ["bounded fixture query"]})
        return "fixture answer from evidence"
    monkeypatch.setattr(hub.runtime, "complete_wrapper", fake)
    def infer(model, messages, max_tokens, correlation):
        response = client.post("/v1/chat/completions", json={"model": "wrapper/deepseek", "messages": messages, "max_tokens": max_tokens, **correlation})
        if response.status_code != 200:
            raise RuntimeError("fixture hub admission denied")
        return response.json()["choices"][0]["message"]["content"]
    result = execute(query="bounded fixture query", enabled=True, agents=1, tokens=128,
                     deadline_seconds=5, source_root=SOURCE, inference=infer, model="wrapper/deepseek",
                     search=lambda query: "fixture-source-evidence", correlation_id="genuine-run")
    assert result["source_revision"] == PIN
    assert result["inference_calls"] >= 1 and result["search_calls"] == 1
    recorded = events(log)
    terminal = [e for e in recorded if e["event"] == "execution_complete"]
    assert len(terminal) == result["inference_calls"]
    assert all(e["run_id"] == "genuine-run" and e["source_revision"] == PIN and e["outcome"] == "UNKNOWN" for e in terminal)
    assert all(row[0] == "charged" for row in states(manager))
    from scripts.telemetry.research_evidence import ingest
    ledger = log.with_name("research-3l0.jsonl")
    samples = ingest(log, ledger)
    assert len(samples) == len(terminal)
    assert all(sample["confidence"] == 0 and sample["provenance"]["execution"]["run_id"] == "genuine-run" for sample in samples)
    destination = os.environ.get("RESEARCH_PAPER_EVIDENCE_DIR")
    if destination:
        directory = Path(destination)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "research-hub-events.jsonl").write_text(log.read_text())
        (directory / "research-3l0.jsonl").write_text(ledger.read_text())
        (directory / "research-quota-reconciliation.json").write_text(json.dumps({"fixture": "genuine-pinned-source-through-real-hub", "source_revision": PIN, "inference": "fake-only", "reservations": states(manager)}, sort_keys=True) + "\n")
