from __future__ import annotations

import importlib
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

protocol = importlib.import_module("llm_api_hub.server.puter_pool_protocol")
providers = importlib.import_module("llm_api_hub.server.research_providers")
app_module = importlib.import_module("llm_api_hub.server.app")


@pytest.mark.parametrize("base", [
    "http://127.0.0.1:3000", "http://localhost:3000/", "https://[::1]:3000",
])
def test_chat_url_accepts_loopback_origins(base):
    assert protocol.chat_url(base).endswith("/v1/chat/completions")


@pytest.mark.parametrize("base", [
    "https://example.com", "http://192.0.2.1:3000", "http://127.0.0.1:3000/path",
    "http://user:pass@127.0.0.1:3000", "http://127.0.0.1:3000?x=1",
])
def test_chat_url_rejects_remote_or_ambiguous_origins(base):
    with pytest.raises(protocol.PuterPoolProtocolError):
        protocol.chat_url(base)


def _entry(model="gpt-5.6-sol"):
    return {
        "provider": "puter_pool", "model": model,
        "free_account_verified": True, "terms_accepted": True,
        "data_class": "public",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def _policy(tmp_path, entries):
    path = tmp_path / "puter-pool-admission.json"
    path.write_text(json.dumps({"schema": "research-provider-admission/v1", "entries": entries}), encoding="utf-8")
    return path


def test_puter_pool_complete_uses_local_x_api_key_and_exact_admission(monkeypatch, tmp_path):
    monkeypatch.setenv("PUTER_POOL_API_KEY", "synthetic-local-key")
    monkeypatch.setenv("PUTER_POOL_BASE_URL", "http://127.0.0.1:3333")
    monkeypatch.setenv("PUTER_POOL_EVENT_OUT", str(tmp_path / "direct-events.jsonl"))
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(_policy(tmp_path, [_entry()])))
    calls = []
    def fake(url, payload, key, timeout, **kwargs):
        calls.append((url, payload, key, timeout, kwargs))
        return {"id": "local", "choices": [{"message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}
    monkeypatch.setattr(providers, "post_json", fake)
    payload = {"model": "gpt-5.6-sol", "messages": [{"role": "user", "content": "synthetic"}], "stream": False}
    result = providers.complete("puter_pool", "gpt-5.6-sol", payload, 4.0)
    assert result["choices"][0]["message"]["content"] == "ok"
    assert calls == [("http://127.0.0.1:3333/v1/chat/completions", payload, "synthetic-local-key", 4.0, {"auth_header": "x-api-key"})]


def test_puter_pool_endpoint_override_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("PUTER_POOL_API_KEY", "synthetic-local-key")
    monkeypatch.setenv("PUTER_POOL_BASE_URL", "https://example.com")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(_policy(tmp_path, [_entry()])))
    monkeypatch.setattr(providers, "post_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("transport invoked")))
    with pytest.raises(providers.ProviderAdmissionError) as exc:
        providers.complete("puter_pool", "gpt-5.6-sol", {"model": "gpt-5.6-sol"}, 2.0)
    assert exc.value.code == "provider_endpoint_invalid"


def test_puter_pool_requires_explicit_exact_model_policy(monkeypatch, tmp_path):
    monkeypatch.setenv("PUTER_POOL_API_KEY", "synthetic-local-key")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(_policy(tmp_path, [_entry("different-model")])))
    with pytest.raises(providers.ProviderAdmissionError) as exc:
        providers.complete("puter_pool", "gpt-5.6-sol", {"model": "gpt-5.6-sol"}, 2.0)
    assert exc.value.code == "provider_not_admitted"



def test_live_hub_dispatch_emits_per_request_que_doe_temporal_event(monkeypatch, tmp_path):
    received = {}

    class PoolChatHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            received["path"] = self.path
            received["api_key"] = self.headers.get("x-api-key")
            length = int(self.headers.get("content-length", "0"))
            received["body"] = json.loads(self.rfile.read(length))
            body = json.dumps({
                "id": "pool-response-7",
                "choices": [{"message": {"role": "assistant", "content": "synthetic reply"}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 7},
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), PoolChatHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    event_path = tmp_path / "agent_telemetry_stream.json"
    monkeypatch.setenv("PUTER_POOL_API_KEY", "synthetic-local-key")
    monkeypatch.setenv("PUTER_POOL_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("PUTER_POOL_EVENT_OUT", str(event_path))
    monkeypatch.setenv("LLM_API_HUB_KEY", "synthetic-hub-key")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(_policy(tmp_path, [_entry()])))
    try:
        client = TestClient(app_module.app)
        response = client.post(
            "/v1/chat/completions",
            headers={
                "Authorization": "Bearer synthetic-hub-key",
                "x-task-or-entry-ref": "QUE-42",
                "x-doe-run-id": "DOE-17",
                "x-workflow-run-id": "GHA-99",
                "x-run-attempt": "2",
                "x-temporal-workflow-id": "puter-pool-observability",
                "x-temporal-run-id": "temporal-run-7",
                "x-request-id": "request-42",
            },
            json={"model": "puter_pool/gpt-5.6-sol", "messages": [{"role": "user", "content": "PRIVATE PROMPT"}]},
        )
        assert response.status_code == 200
        assert received["path"] == "/v1/chat/completions"
        assert received["api_key"] == "synthetic-local-key"
        assert received["body"]["model"] == "gpt-5.6-sol"
        event = json.loads(event_path.read_text(encoding="utf-8").splitlines()[-1])
        assert event["event_type"] == "provider.inference.completed"
        assert event["provider_id"] == "g4f.puter"
        attrs = event["attributes"]
        assert attrs["exact_model_id"] == "gpt-5.6-sol"
        assert attrs["task_or_entry_ref"] == "QUE-42"
        assert attrs["doe_run_id"] == "DOE-17"
        assert attrs["workflow_run_id"] == "GHA-99"
        assert attrs["run_attempt"] == 2
        assert attrs["temporal_workflow_id"] == "puter-pool-observability"
        assert attrs["temporal_run_id"] == "temporal-run-7"
        assert attrs["request_id"] == "request-42"
        assert attrs["input_tokens"] == 5
        assert attrs["output_tokens"] == 7
        assert "PRIVATE PROMPT" not in event_path.read_text(encoding="utf-8")
        assert "synthetic reply" not in event_path.read_text(encoding="utf-8")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
