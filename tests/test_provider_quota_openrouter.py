"""Synthetic-only tests for private OpenRouter key observation; never contacts network."""
import datetime as dt
import json
from types import SimpleNamespace

import pytest
from scripts import provider_quota_service as service

NOW = dt.datetime(2030, 4, 5, 12, tzinfo=dt.timezone.utc)
SCOPE = "key:synthetic"


def payload(**overrides):
    data = {"free_model_daily_requests": {"used": 2, "limit": 10, "remaining": 8},
            "limit_remaining": 3.75,
            "effective_budget": {"remaining_usd": 1.25, "resets_at": "2030-04-05T12:00:30Z"},
            "is_free_tier": True,
            "label": "IDENTITY CANARY", "hash": "HASH CANARY", "email": "EMAIL CANARY"}
    data.update(overrides)
    return {"data": data}


def observe(value=None, status=200):
    calls = []
    def request(**kw):
        calls.append(kw)
        return SimpleNamespace(status_code=status, json=lambda: value)
    result = service.observe_service("openrouter.key", "synthetic-key", scope=SCOPE, now=NOW, request=request)
    return result, calls


def test_success_sanitizes_counters_budget_and_tier_without_identity_or_entitlement():
    result, calls = observe(payload())
    assert result["status"] == "observed" and result["request_quota"] == "observed"
    assert result["signals"]["free_model_daily_used"] == 2
    assert result["signals"]["free_model_daily_limit"] == 10
    assert result["signals"]["free_model_daily_remaining"] == 8
    assert result["signals"]["openrouter_key_limit_remaining_usd"] == 3.75
    assert result["signals"]["openrouter_effective_budget_remaining_usd"] == 1.25
    assert result["signals"]["openrouter_is_free_tier"] is True
    assert result["entitlement"] == "unknown" and result["runtime_admission"] == "unchanged"
    assert result["valid_until"] == "2030-04-05T12:00:30Z"
    assert len(calls) == 1 and calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://openrouter.ai/api/v1/key" and calls[0]["allow_redirects"] is False
    encoded = json.dumps(result)
    for secret in ("IDENTITY CANARY", "HASH CANARY", "EMAIL CANARY", "synthetic-key"):
        assert secret not in encoded


def test_missing_or_invalid_daily_counters_leave_request_quota_unknown_but_other_signal_observed():
    for counters in (None, {"used": 1, "limit": 3}, {"used": True, "limit": 3, "remaining": 2},
                     {"used": 2, "limit": 3, "remaining": 2}):
        data = payload(limit_remaining=4)
        if counters is None: data["data"].pop("free_model_daily_requests")
        else: data["data"]["free_model_daily_requests"] = counters
        result, _ = observe(data)
        assert result["status"] == "observed"
        assert result["request_quota"] == "unknown"
        assert not any(k.startswith("free_model_daily_") for k in result["signals"])


def test_absent_budget_reset_does_not_infer_a_reset():
    data = payload(effective_budget={"remaining_usd": 0.5})
    result, _ = observe(data)
    assert result["valid_until"] == "2030-04-05T12:01:00Z"
    assert "openrouter_effective_budget_resets_at" not in result["signals"]


@pytest.mark.parametrize("status", [401, 429, 302, 500])
def test_http_errors_redirects_and_rate_limits_unknown_without_retry(status):
    result, calls = observe(payload(), status)
    assert result["status"] == "unknown" and len(calls) == 1


def test_transport_network_exception_is_unknown_without_detail_or_retry():
    calls = []
    def fail(**kw):
        calls.append(kw)
        raise OSError("NETWORK CANARY")
    result = service.observe_service("openrouter.key", "synthetic", scope=SCOPE, now=NOW, request=fail)
    assert result["status"] == "unknown" and len(calls) == 1
    assert "NETWORK CANARY" not in json.dumps(result)


@pytest.mark.parametrize("bad", [{"data": {"label": "raw"}}, {"data": {"free_model_daily_requests": {"used": 1, "limit": 2, "remaining": 0}}},
                                  {"data": {"limit_remaining": float("nan")}}, {"data": {"free_model_daily_requests": {"used": -1, "limit": 2, "remaining": 3}}}])
def test_invalid_payload_yields_unknown_or_partial_safe_observation(bad):
    result, _ = observe(bad)
    assert result["status"] in {"unknown", "observed"}
    assert "raw" not in json.dumps(result)
    assert result["request_quota"] == "unknown"


def test_public_status_allowlist_drops_private_canaries():
    result, _ = observe(payload())
    result["scope"] = "SCOPE CANARY"
    result["signals"]["private"] = "SIGNAL CANARY"
    public = service.public_status(result)
    assert set(public) == {"service_id", "provider_family", "status", "observed_at", "request_quota"}
    assert public["request_quota"] == "observed"
    assert "CANARY" not in json.dumps(public)


def test_public_status_quota_enum_is_sanitized_and_ollama_allowlist_unchanged():
    result, _ = observe(payload())
    result["request_quota"] = "PRIVATE STATUS CANARY"
    public = service.public_status(result)
    assert public["request_quota"] == "unknown"
    ollama = {"service_id": "ollama.balance", "observed_at": "2030-04-05T12:00:00Z",
              "request_quota": "observed"}
    assert set(service.public_status(ollama)) == {"service_id", "provider_family", "status", "observed_at"}
    assert "request_quota" not in service.public_status(ollama)


def test_cli_opt_in_required_before_any_observation(tmp_path, monkeypatch, capsys):
    directory = tmp_path / "private"
    directory.mkdir(mode=0o700); directory.chmod(0o700)
    target = directory / "out.json"
    called = []
    monkeypatch.setattr(service, "observe_service", lambda *a, **kw: called.append(1))
    args = ["--service", "openrouter.key", "--scope", SCOPE, "--private-out", str(target)]
    with pytest.raises(SystemExit): service.main(args)
    assert not called and not target.exists() and not capsys.readouterr().out


def test_default_transport_fixed_host_path_and_tls(monkeypatch):
    events = []
    class Resp:
        status = 200
        def getheader(self, name): return None
        def read(self, n): return b'{"data":{"is_free_tier":false}}'
    class Conn:
        def __init__(self, host, *, timeout, context): events.append(("connect", host, context))
        def request(self, method, path, *, headers): events.append(("request", method, path, headers))
        def getresponse(self): return Resp()
        def close(self): events.append(("close",))
    monkeypatch.setattr(service.http.client, "HTTPSConnection", Conn)
    result = service.observe_service("openrouter.key", "test", scope=SCOPE, now=NOW)
    assert result["status"] == "observed"
    assert events[0][1] == "openrouter.ai" and events[0][2] is not None
    assert events[1][1:3] == ("GET", "/api/v1/key")
    assert [x[0] for x in events] == ["connect", "request", "close"]


@pytest.mark.parametrize("body", [b'{"data":{},"data":{}}', b'{"data":{"x":NaN}}'])
def test_http_parser_rejects_duplicate_keys_and_nonfinite(monkeypatch, body):
    class Resp:
        status = 200
        def getheader(self, name): return None
        def read(self, n): return body
    class Conn:
        def __init__(self, *a, **kw): pass
        def request(self, *a, **kw): pass
        def getresponse(self): return Resp()
        def close(self): pass
    monkeypatch.setattr(service.http.client, "HTTPSConnection", Conn)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        service.https_request(method="GET", url=service.OPENROUTER_KEY_URL,
            headers={"Authorization": "Bearer x"}, timeout=5, allow_redirects=False,
            max_response_bytes=service.MAX_RESPONSE_BYTES)


def test_empty_and_null_only_data_do_not_establish_observation():
    for body in ({"data": {}}, {"data": {"limit_remaining": None}},
                 {"data": {"effective_budget": {"remaining_usd": None}}}):
        result, _ = observe(body)
        assert result["status"] == "unknown"
        assert result["signals"] == {}


def test_openrouter_scope_status_is_key_specific():
    result, _ = observe(payload())
    assert result["scope_status"] == "credential_selected_key_account_identity_unverified"


def test_expired_explicit_budget_reset_is_unknown_without_signals():
    result, _ = observe(payload(effective_budget={"remaining_usd": 1.0, "resets_at": "2030-04-05T11:59:59Z"}))
    assert result["status"] == "unknown"
    assert result["reason"] == "source_reset_due_refresh_required"
    assert result["signals"] == {}
    assert result["valid_until"] is None
    assert result["request_quota"] == "unknown"
    assert service.public_status(result)["request_quota"] == "unknown"


def test_negative_finite_usd_remaining_is_preserved_as_budget_not_request_quota():
    result, _ = observe(payload(limit_remaining=-2.5, effective_budget={"remaining_usd": -0.75}))
    assert result["status"] == "observed"
    assert result["signals"]["openrouter_key_limit_remaining_usd"] == -2.5
    assert result["signals"]["openrouter_effective_budget_remaining_usd"] == -0.75
    assert result["request_quota"] == "observed"
