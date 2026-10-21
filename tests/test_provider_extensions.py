"""Synthetic extension transport tests; no live provider calls or credentials."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from llm_api_hub.server import provider_extensions as extensions
from llm_api_hub.server import research_providers as providers


def _admission(path, provider, model):
    path.write_text(json.dumps({"schema": providers.SCHEMA, "entries": [{
        "provider": provider, "model": model, "free_account_verified": True,
        "terms_accepted": True, "data_class": "public",
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }]}))


def _ok_body(model):
    result = {"id": "safe-id", "model": model, "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}
    if model == "lite":
        result["code"] = 0
        result.pop("model")
        result["choices"][0].pop("finish_reason")
    return result


@pytest.mark.parametrize("provider,model,key", [
    ("typhoon", "typhoon-v2.5-30b-a3b-instruct", "OPENTYPHOON_API_KEY"),
    ("unorouter", "test/model:free", "UNOROUTER_API_KEY"),
    ("routeway", "test/model:free", "ROUTEWAY_API_KEY"),
    ("requesty", "nvidia/nemotron-3-super-120b-a12b", "REQUESTY_API_KEY"),
    ("xkiro", "test/model", "XKIRO_API_KEY"),
    ("xfyun", "lite", "XFYUN_API_KEY"),
    ("sealion", "test/model", "SEALION_API_KEY"),
])
def test_complete_sends_fixed_safe_request_and_normalizes(monkeypatch, tmp_path, provider, model, key):
    policy = tmp_path / "policy.json"
    _admission(policy, provider, model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv(key, "synthetic-key")
    captured = {}

    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, n): return json.dumps(_ok_body(model)).encode()

    class Opener:
        def open(self, req, timeout):
            captured.update(url=req.full_url, body=json.loads(req.data), headers=dict(req.header_items()), timeout=timeout)
            return Response()

    monkeypatch.setattr(providers.urllib.request, "build_opener", lambda *args: Opener())
    result = providers.complete(provider, model, {"model": model, "messages": [{"role": "user", "content": "hi"}]}, 2.5)
    assert captured["url"] == extensions.ENDPOINTS[provider][0]
    assert captured["headers"]["Authorization"] == "Bearer synthetic-key"
    assert captured["body"] == {"model": model, "messages": [{"role": "user", "content": "hi"}], "stream": False}
    assert captured["timeout"] == 2.5
    assert result["choices"][0]["message"]["content"] == "ok"


@pytest.mark.parametrize("provider,model,payload", [
    ("typhoon", "typhoon-v2.5-30b-a3b-instruct", {"tools": []}),
    ("typhoon", "typhoon-v2.5-30b-a3b-instruct", {"user": "identifier"}),
    ("unorouter", "m/x", {}),
    ("routeway", "m/x", {}),
    ("requesty", "policy/nvidia/nemotron-3-super-120b-a12b", {}),
    ("xfyun", "pro", {}),
    ("xkiro", "m/x", {"stream": True}),
])
def test_invalid_extension_requests_denied_before_transport(monkeypatch, tmp_path, provider, model, payload):
    policy = tmp_path / "policy.json"
    _admission(policy, provider, model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv(extensions.ENDPOINTS[provider][1][0], "synthetic-key")
    request = {"model": model, "messages": [{"role": "user", "content": "hi"}], **payload}
    monkeypatch.setattr(providers.urllib.request, "build_opener", lambda *a: pytest.fail("network must not be called"))
    with pytest.raises(providers.ProviderAdmissionError) as error:
        providers.complete(provider, model, request, 1)
    assert error.value.status == 400


def test_exact_model_mismatch_denied_before_network(monkeypatch, tmp_path):
    policy = tmp_path / "policy.json"
    _admission(policy, "unorouter", "exact:free")
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv("UNOROUTER_API_KEY", "synthetic")
    monkeypatch.setattr(providers.urllib.request, "build_opener", lambda *a: pytest.fail("network must not be called"))
    with pytest.raises(providers.ProviderAdmissionError):
        providers.complete("unorouter", "other:free", {"model": "other:free", "messages": []}, 1)


def test_extension_registry_matches_fixed_urls_and_no_catalog_for_typhoon():
    assert set(extensions.ENDPOINTS) == {"typhoon", "unorouter", "routeway", "requesty", "xkiro", "xfyun", "sealion"}
    assert "typhoon" not in extensions.CATALOG_ENDPOINTS


def test_bad_typhoon_upstream_response_is_sanitized(monkeypatch, tmp_path):
    provider, model = "typhoon", "typhoon-v2.5-30b-a3b-instruct"
    policy = tmp_path / "policy.json"
    _admission(policy, provider, model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv("OPENTYPHOON_API_KEY", "synthetic")

    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, n): return json.dumps({"model": "wrong", "choices": []}).encode()
    class Opener:
        def open(self, req, timeout): return Response()
    monkeypatch.setattr(providers.urllib.request, "build_opener", lambda *a: Opener())
    with pytest.raises(providers.ProviderAdmissionError) as error:
        providers.complete(provider, model, {"model": model, "messages": [{"role": "user", "content": "hi"}]}, 1)
    assert error.value.code == "upstream_invalid_response"


@pytest.mark.parametrize("provider,model", [
    ("typhoon", "typhoon-v2.5-30b-a3b-instruct"), ("unorouter", "test/model:free"),
    ("routeway", "test/model:free"), ("requesty", "nvidia/nemotron-3-super-120b-a12b"),
    ("xkiro", "test/model"), ("xfyun", "lite"), ("sealion", "test/model"),
])
def test_malformed_upstream_response_fails_closed_for_every_extension(monkeypatch, tmp_path, provider, model):
    policy = tmp_path / "policy.json"
    _admission(policy, provider, model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv(extensions.ENDPOINTS[provider][1][0], "synthetic")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, n): return b'{"not":"a completion"}'
    class Opener:
        def open(self, req, timeout): return Response()
    monkeypatch.setattr(providers.urllib.request, "build_opener", lambda *a: Opener())
    with pytest.raises(providers.ProviderAdmissionError) as error:
        providers.complete(provider, model, {"model": model, "messages": [{"role": "user", "content": "hi"}]}, 1)
    assert error.value.code == "upstream_invalid_response"


@pytest.mark.parametrize("provider,model", [
    ("typhoon", "typhoon-v2.5-30b-a3b-instruct"), ("unorouter", "test/model:free"),
    ("routeway", "test/model:free"), ("requesty", "nvidia/nemotron-3-super-120b-a12b"),
    ("xkiro", "test/model"), ("xfyun", "lite"), ("sealion", "test/model"),
])
def test_new_provider_is_listed_and_called_through_actual_hub(monkeypatch, tmp_path, provider, model):
    import importlib
    from fastapi.testclient import TestClient
    hub = importlib.import_module("llm_api_hub.server.app")
    policy = tmp_path / "policy.json"
    _admission(policy, provider, model)
    monkeypatch.setenv("LLM_API_HUB_PROVIDER_POLICY", str(policy))
    monkeypatch.setenv(extensions.ENDPOINTS[provider][1][0], "synthetic")
    called = []
    def post(url, payload, key, timeout, **kwargs):
        called.append((url, payload, kwargs))
        return _ok_body(model)
    monkeypatch.setattr(providers, "post_json", post)
    with TestClient(hub.app) as client:
        assert provider + "/" + model in [row["id"] for row in client.get("/v1/models").json()["data"]]
        result = client.post("/v1/chat/completions", json={"model": provider + "/" + model, "messages": [{"role": "user", "content": "Reply with exactly: OK"}]})
        assert result.status_code == 200
        assert result.json()["choices"][0]["message"]["content"] == "ok"
    assert called[0][0] == extensions.ENDPOINTS[provider][0]
    assert called[0][1]["model"] == model
    assert called[0][2]["response_provider"] == provider


@pytest.mark.parametrize("payload", [
    {"model": "wrong", "choices": [{}]}, {"model": "m", "choices": [{}]},
    {"model": "m", "choices": [None]},
    {"model": "m", "choices": [{"index": 0, "message": {"role": "assistant", "content": []}}]},
    {"model": "m", "choices": [{"index": 0, "message": {"role": "user", "content": "x"}}]},
    {"model": "m", "choices": [{"index": 0, "message": {"role": "assistant", "content": "x"}, "finish_reason": "tool_calls"}]},
])
def test_malformed_extension_choices_cannot_count_as_success(payload):
    with pytest.raises((ValueError, TypeError)):
        providers._normalize_extension_response(payload, "m")


@pytest.mark.parametrize("field,value", [("temperature", 10**1000), ("temperature", float("nan")), ("top_p", float("inf")), ("max_tokens", True)])
def test_invalid_extension_numbers_fail_with_fixed_error_not_overflow(field, value):
    with pytest.raises(ValueError):
        providers._build_extension_request("xkiro", "v/m", {"model": "v/m", "messages": [{"role": "user", "content": "OK"}], field: value})


@pytest.mark.parametrize("changes", [{"max_tokens": 4097}, {"top_p": 0}])
def test_spark_lite_documented_bounds(changes):
    with pytest.raises(ValueError):
        providers._build_extension_request("xfyun", "lite", {"model": "lite", "messages": [{"role": "user", "content": "OK"}], **changes})


def test_requesty_bare_managed_alias_does_not_select_an_unpinned_provider():
    with pytest.raises(ValueError):
        providers._build_extension_request("requesty", "auto", {"model": "auto", "messages": [{"role": "user", "content": "OK"}]})


@pytest.mark.parametrize("code", [False, 1, 0.0, "0", None])
def test_spark_error_or_ambiguous_code_cannot_succeed(code):
    body = _ok_body("lite")
    body["code"] = code
    with pytest.raises(ValueError):
        providers._normalize_extension_response(body, "lite", "xfyun")


def test_spark_documented_nonstream_response_normalizes_without_model_echo():
    body = _ok_body("lite")
    body["sid"] = "synthetic-trace"
    body["usage"] = {"prompt_tokens": 6, "completion_tokens": 42, "total_tokens": 48}
    result = providers._normalize_extension_response(body, "lite", "xfyun")
    assert result["model"] == "lite"
    assert result["choices"][0]["finish_reason"] == "stop"
    assert result["usage"]["total_tokens"] == 48
    assert "sid" not in result and "code" not in result
