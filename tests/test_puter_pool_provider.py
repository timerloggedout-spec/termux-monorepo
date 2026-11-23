from __future__ import annotations

import importlib
import json
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

