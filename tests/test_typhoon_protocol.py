"""Synthetic tests for the offline Typhoon protocol; no network or credentials."""
import ast
import json
from pathlib import Path
import socket

import pytest

from llm_api_hub.server import typhoon_protocol as typhoon

FIXTURES = Path(__file__).parent / "fixtures" / "typhoon"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_request_fixture_and_no_auth_material():
    out = typhoon.build_chat_request(fixture("chat_request.json"))
    assert out["stream"] is False
    assert out["model"] == "typhoon-v2.5-30b-a3b-instruct"
    assert "Authorization" not in out and "api_key" not in out


@pytest.mark.parametrize("patch,code", [
    ({"model": None}, "unsupported_model"),
    ({"model": "openrouter/typhoon"}, "unsupported_model"),
    ({"tools": []}, "unsupported_property"),
    ({"base_url": "https://untrusted.invalid"}, "unsupported_property"),
    ({"stream": True}, "streaming_unsupported"),
    ({"stream": 1}, "streaming_unsupported"),
    ({"messages": []}, "invalid_messages"),
    ({"messages": [{"role": "developer", "content": "synthetic"}]}, "invalid_message"),
    ({"messages": [{"role": "user", "content": [{"type": "image_url"}]}]}, "invalid_message"),
    ({"max_tokens": True}, "invalid_value"),
])
def test_unsupported_or_malformed_request_fields(patch, code):
    payload = fixture("chat_request.json")
    payload.update(patch)
    with pytest.raises(typhoon.TyphoonProtocolError) as error:
        typhoon.build_chat_request(payload)
    assert error.value.code == code


def test_response_fixture_minimal_normalization():
    result = typhoon.normalize_chat_response(fixture("chat_response.json"), "typhoon-v2.5-30b-a3b-instruct")
    assert result["choices"][0]["message"]["content"] == "Hello."
    assert result["usage"]["total_tokens"] == 9


def test_mismatched_response_model_is_not_accepted():
    with pytest.raises(typhoon.TyphoonProtocolError, match="^response_model_mismatch$"):
        typhoon.normalize_chat_response(fixture("chat_response.json"), "typhoon-v2.1-12b-instruct")


def test_public_contract_is_fresh_and_does_not_invent_remaining_or_reset():
    first = typhoon.public_documentation_contract()
    first["models"].clear()
    second = typhoon.public_documentation_contract()
    assert second["models"] == list(typhoon.MODELS)
    assert second["credential_env_name"] == "OPENTYPHOON_API_KEY"
    assert second["documented_public_rate_caps"] == {"requests_per_second": 5, "requests_per_minute": 200}
    assert second["quota_unknowns"] and second["legal_hold_reasons"] == []
    assert "8K" in second["context_and_output_caps"]
    assert "128K/56K" in second["context_and_output_caps"]
    assert "quota_remaining" not in second and "reset_at" not in second


def test_rate_limit_documented_timestamp_only():
    assert typhoon.normalize_provider_error(429, fixture("rate_limited.json")) == {"code":"rate_limited", "retry_hint":"2026-10-21T12:00:00Z"}


@pytest.mark.parametrize("field,values", [("temperature",[-.01,2.01]),("top_p",[-.01,1.01]),("presence_penalty",[-2.01,2.01]),("frequency_penalty",[-2.01,2.01]),("repetition_penalty",[.99,2.01])])
def test_numeric_bounds(field, values):
    for value in values:
        p=fixture("chat_request.json"); p[field]=value
        with pytest.raises(typhoon.TyphoonProtocolError): typhoon.build_chat_request(p)


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), -float("inf"), 10**1000])
def test_numeric_nonfinite_and_bool_rejected(value):
    p=fixture("chat_request.json"); p["temperature"]=value
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.build_chat_request(p)


@pytest.mark.parametrize("role", [[], {}, None, 123])
def test_request_role_type_uses_fixed_protocol_error(role):
    payload = fixture("chat_request.json")
    payload["messages"][0]["role"] = role
    with pytest.raises(typhoon.TyphoonProtocolError, match="^invalid_message$"):
        typhoon.build_chat_request(payload)


def test_stop_limit_and_no_invented_token_cap():
    p=fixture("chat_request.json"); p["stop"]=["a","b","c","d"]
    assert len(typhoon.build_chat_request(p)["stop"]) == 4
    p["stop"].append("e")
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.build_chat_request(p)
    p=fixture("chat_request.json"); p["max_tokens"]=10**10
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.build_chat_request(p)


@pytest.mark.parametrize("value", [["assistant"], {"x":1}])
def test_unhashable_response_values_fixed_errors(value):
    body=fixture("chat_response.json"); body["choices"][0]["message"]["role"]=value
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response(body,"typhoon-v2.5-30b-a3b-instruct")
    body=fixture("chat_response.json"); body["choices"][0]["finish_reason"]=value
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response(body,"typhoon-v2.5-30b-a3b-instruct")
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response({},value)


def test_choice_and_usage_invariants():
    body=fixture("chat_response.json"); body["choices"][0]["index"]=-1
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response(body,"typhoon-v2.5-30b-a3b-instruct")
    body=fixture("chat_response.json"); body["choices"].append(dict(body["choices"][0]))
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response(body,"typhoon-v2.5-30b-a3b-instruct")
    body=fixture("chat_response.json"); body["usage"]["total_tokens"]+=1
    with pytest.raises(typhoon.TyphoonProtocolError): typhoon.normalize_chat_response(body,"typhoon-v2.5-30b-a3b-instruct")


def test_retry_secret_never_reflected_and_invalid_timestamp_not_parsed():
    secret="SECRET-SHOULD-NEVER-ESCAPE"
    for msg in [f"Rate limit exceeded. Please retry after 2026-02-30T12:00:00Z", f"Rate limit exceeded. Please retry after 2026-10-21T12:00:00Z suffix", secret]:
        out=typhoon.normalize_provider_error(429,{"error":{"type":"rate_limit_error","code":"rate_limit_exceeded","message":msg,"retry_after":secret},"retry_after":secret})
        assert out=={"code":"rate_limited"} and secret not in repr(out)


def test_no_environment_or_network_access(monkeypatch):
    def denied(*a,**kw): raise AssertionError("environment/network access denied")
    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr("os.getenv", denied)
    monkeypatch.setattr("os.environ.get", denied)
    assert typhoon.build_chat_request(fixture("chat_request.json"))["stream"] is False
    tree=ast.parse(Path(typhoon.__file__).read_text())
    forbidden={"requests","urllib","httpx","socket","os"}
    imports={alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node,(ast.Import,ast.ImportFrom)) for alias in node.names}
    assert not imports & forbidden


def test_registered_but_requires_explicit_exact_admission():
    assert typhoon.public_documentation_contract()["runtime_eligible"] is True
    from llm_api_hub.server import research_providers
    assert research_providers.ENDPOINTS["typhoon"] == (typhoon.ENDPOINT, ("OPENTYPHOON_API_KEY", "TYPHOON_API_KEY"))
