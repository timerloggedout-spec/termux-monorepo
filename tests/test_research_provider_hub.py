from __future__ import annotations

import importlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from hub_quota_fixture import SeededQuotaClient
from src import telemetry

app_module = importlib.import_module("llm_api_hub.server.app")
providers = importlib.import_module("llm_api_hub.server.research_providers")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(telemetry, "TELEMETRY_LOG", str(tmp_path / "telemetry.jsonl"))
    previous = app_module.admission
    result = SeededQuotaClient(app_module, tmp_path)
    try:
        yield result
    finally:
        app_module.admission = previous


def entry(**updates):
    value = {
        "provider": "groq", "model": "llama-3.3-70b-versatile",
        "free_account_verified": True, "terms_accepted": True,
        "data_class": "public",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=2)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    value.update(updates)
    return value


def policy_file(tmp_path, entries):
    path = tmp_path / "admission.json"
    path.write_text(json.dumps({"schema": "research-provider-admission/v1", "entries": entries}))
    return path


def request_body(model="groq/llama-3.3-70b-versatile", **kwargs):
    return {"model": model, "messages": [{"role": "user", "content": "hello"}], **kwargs}


def test_exact_admission_invokes_pinned_transport_and_supports_sse(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "do-not-leak")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))
    calls = []

    def fake(url, payload, key, timeout):
        calls.append((url, payload, key))
        return {"id": "fixed", "choices": [{"message": {"role": "assistant", "content": "hello back"}, "finish_reason": "stop"}]}

    monkeypatch.setattr(providers, "post_json", fake)
    assert "groq/llama-3.3-70b-versatile" in [m["id"] for m in client.get("/v1/models").json()["data"]]
    response = client.post("/v1/chat/completions", json=request_body(stream=True))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "hello back" in response.text and "data: [DONE]" in response.text
    assert calls[0][0] == providers.ENDPOINTS["groq"][0]
    assert calls[0][1]["model"] == "llama-3.3-70b-versatile"
    assert calls[0][2] == "do-not-leak"


@pytest.mark.parametrize("overrides", [
    {"free_account_verified": False}, {"free_account_verified": "true"},
    {"terms_accepted": False}, {"data_class": "private"},
    {"expires_at": "2000-01-01T00:00:00Z"}, {"model": "llama-*"},
    {"account_type": "paid"}, {"account_type": "trial"},
])
def test_invalid_or_unverified_policy_denied(client, monkeypatch, tmp_path, overrides):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(**overrides)])))
    response = client.post("/v1/chat/completions", json=request_body())
    assert response.status_code == 403


def test_absent_malformed_or_trial_policy_denied_and_not_listed(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.delenv("LLM_API_HUB_PROVIDER_POLICY", raising=False)
    assert client.post("/v1/chat/completions", json=request_body()).status_code == 403
    assert all(not m["id"].startswith("groq/") for m in client.get("/v1/models").json()["data"])
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(bad))
    assert client.post("/v1/chat/completions", json=request_body()).status_code == 403
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(free_account_verified=False)])))
    assert all(not m["id"].startswith("groq/") for m in client.get("/v1/models").json()["data"])


def test_provider_prefix_does_not_fall_through_openrouter(client, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "router")
    monkeypatch.delenv("LLM_API_HUB_PROVIDER_POLICY", raising=False)
    response = client.post("/v1/chat/completions", json=request_body("gemini/some-model"))
    assert response.status_code == 403


@pytest.mark.parametrize("status,expected", [(401, "upstream_auth_error"), (429, "upstream_rate_limited")])
def test_upstream_errors_are_sanitized(client, monkeypatch, tmp_path, status, expected):
    monkeypatch.setenv("GROQ_API_KEY", "super-secret-token")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))

    def fail(*args):
        raise providers.ProviderAdmissionError(502 if status == 401 else status, "native provider authentication failed" if status == 401 else "native provider rate limit reached", expected)

    monkeypatch.setattr(providers, "post_json", fail)
    response = client.post("/v1/chat/completions", json=request_body())
    assert response.status_code == (502 if status == 401 else 429)
    assert "super-secret-token" not in response.text
    assert "Authorization" not in response.text
    assert response.json()["error"]["code"] == expected


def test_text_only_public_payload_rejected_before_transport(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))
    response = client.post("/v1/chat/completions", json={"model": "groq/llama-3.3-70b-versatile", "messages": [{"role": "user", "content": [{"type": "image_url"}]}]})
    assert response.status_code == 400

# Model spellings are asserted against the checked-in MSM-010 research snapshot.
RESEARCH_GROQ_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

@pytest.mark.parametrize("model", RESEARCH_GROQ_MODELS)
def test_actual_qualified_research_ids_admitted_at_endpoint(client, monkeypatch, tmp_path, model):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(model=model)])))
    monkeypatch.setattr(providers, "post_json", lambda *args: {"choices": [{"message": {"content": "ok"}}]})
    response = client.post("/v1/chat/completions", json=request_body("groq/" + model))
    assert response.status_code == 200

@pytest.mark.parametrize("model", ["openai/../bad", "openai/./bad", "openai//bad", "openai/foo?bar", "openai/foo#bar", "openai/foo*", "openai/foo bar", "<model>"])
def test_invalid_ids_denied(client, monkeypatch, tmp_path, model):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(model=model)])))
    response = client.post("/v1/chat/completions", json=request_body("groq/" + model))
    assert response.status_code == 403

@pytest.mark.parametrize("bad", [[], {}, None, True, 7])
def test_malformed_account_status_fails_closed(client, monkeypatch, tmp_path, bad):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(account_status=bad)])))
    assert client.post("/v1/chat/completions", json=request_body()).status_code == 403

def test_conflicting_duplicate_denied(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(), entry(terms_accepted=False)])))
    assert client.post("/v1/chat/completions", json=request_body()).status_code == 403

def test_complete_rejects_payload_model_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))
    with pytest.raises(providers.ProviderAdmissionError):
        providers.complete("groq", "llama-3.3-70b-versatile", {"model": "attacker/model"}, 1)

def test_non_text_tool_payload_rejected(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))
    r = client.post("/v1/chat/completions", json=request_body(tools=[{"type": "function"}]))
    assert r.status_code == 400

def test_retry_after_preserved_safely(client, monkeypatch, tmp_path):
    monkeypatch.setenv("GROQ_API_KEY", "secret")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry()])))
    monkeypatch.setattr(providers, "post_json", lambda *a: (_ for _ in ()).throw(providers.ProviderAdmissionError(429, "limited", "upstream_rate_limited", "17")))
    r = client.post("/v1/chat/completions", json=request_body())
    assert r.status_code == 429 and r.headers["retry-after"] == "17"

@pytest.mark.parametrize(("provider", "model", "secret", "expected_url"), [
    ("huggingface", "openai/gpt-oss-120b:groq", "HF_TOKEN", "https://router.huggingface.co/v1/chat/completions"),
    ("cerebras", "gpt-oss-120b", "CEREBRAS_API_KEY", "https://api.cerebras.ai/v1/chat/completions"),
    ("nvidia", "google/gemma-4-31b-it", "NVIDIA_API_KEY", "https://integrate.api.nvidia.com/v1/chat/completions"),
])
def test_new_provider_uses_fixed_endpoint_and_exact_admission(client, monkeypatch, tmp_path, provider, model, secret, expected_url):
    monkeypatch.setenv(secret, "not-for-output")
    admitted = entry(provider=provider, model=model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [admitted])))
    calls = []
    monkeypatch.setattr(providers, "post_json", lambda url, payload, key, timeout: calls.append((url, payload["model"], key)) or {"choices": [{"message": {"content": "ok"}}]})
    response = client.post("/v1/chat/completions", json=request_body(f"{provider}/{model}"))
    assert response.status_code == 200
    assert calls == [(expected_url, model, "not-for-output")]


@pytest.mark.parametrize("model", [
    "google/gemma-4-31b-it",
    "mistralai/mistral-large-2-instruct",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "openai/gpt-oss-20b",
])
def test_nvidia_research_ids_use_gated_native_route(client, monkeypatch, tmp_path, model):
    monkeypatch.setenv("NVIDIA_NIM_API_KEY", "nim-alias-key")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(provider="nvidia", model=model)])))
    calls = []
    monkeypatch.setattr(providers, "post_json", lambda url, payload, key, timeout: calls.append((url, payload["model"], key)) or {"choices": [{"message": {"content": "ok"}}]})
    response = client.post("/v1/chat/completions", json=request_body("nvidia/" + model))
    assert response.status_code == 200
    assert calls == [("https://integrate.api.nvidia.com/v1/chat/completions", model, "nim-alias-key")]

@pytest.mark.parametrize(("provider", "model", "secret", "expected_url"), [
    ("aion", "aion-labs/aion-3.5", "AION_API_KEY", "https://api.aionlabs.ai/v1/chat/completions"),
    ("llm7", "turbo", "LLM7_API_TOKEN", "https://api.llm7.io/v1/chat/completions"),
    ("zai", "glm-5.3", "ZAI_API_KEY", "https://api.z.ai/api/paas/v4/chat/completions"),
    ("modelscope", "Qwen/Qwen3.5-35B-A3B", "MODELSCOPE_TOKEN", "https://api-inference.modelscope.ai/v1/chat/completions"),
    ("siliconflow", "openai/gpt-oss-120b", "SILICONFLOW_API_KEY", "https://api.siliconflow.com/v1/chat/completions"),
    ("kilo", "google/gemma-4-26b-a4b-it:free", "KILO_API_KEY", "https://ai-gateway.kilo.ai/api/v1/chat/completions"),
])
def test_remaining_openai_compatible_routes_use_fixed_official_endpoint(client, monkeypatch, tmp_path, provider, model, secret, expected_url):
    monkeypatch.setenv(secret, "not-for-output")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy_file(tmp_path, [entry(provider=provider, model=model)])))
    calls = []
    monkeypatch.setattr(providers, "post_json", lambda url, payload, key, timeout: calls.append((url, payload["model"], key)) or {"choices": [{"message": {"content": "ok"}}]})
    response = client.post("/v1/chat/completions", json=request_body(f"{provider}/{model}"))
    assert response.status_code == 200
    assert calls == [(expected_url, model, "not-for-output")]


@pytest.mark.parametrize('provider', sorted(providers.ENDPOINTS))
def test_every_registered_native_prefix_reaches_admission_not_router(client, monkeypatch, provider):
    monkeypatch.delenv('LLM_API_HUB_PROVIDER_POLICY', raising=False)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'synthetic-router-key')
    response = client.post('/v1/chat/completions', json=request_body(f'{provider}/synthetic-exact-model'))
    assert response.status_code == 403
    assert response.json()['error']['code'] == 'provider_not_admitted'


def test_cloudflare_missing_account_is_not_listed_or_sent(client, monkeypatch, tmp_path):
    monkeypatch.setenv('CLOUDFLARE_API_TOKEN', 'synthetic-cf')
    monkeypatch.delenv('CLOUDFLARE_ACCOUNT_ID', raising=False)
    model = '@cf/meta/synthetic-model'
    monkeypatch.setenv('LLM_API_HUB_PROVIDER_POLICY', str(policy_file(tmp_path, [entry(provider='cloudflare', model=model)])))
    response = client.post('/v1/chat/completions', json=request_body(f'cloudflare/{model}'))
    assert response.status_code == 503
    assert f'cloudflare/{model}' not in [r['id'] for r in client.get('/v1/models').json()['data']]
