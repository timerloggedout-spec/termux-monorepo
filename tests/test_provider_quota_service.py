"""Contract tests for the opt-in provider quota observation service.

All responses and clocks here are synthetic; tests must never contact a provider.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import stat
from pathlib import Path

import pytest

from scripts import provider_quota_service as service


NOW = dt.datetime(2030, 4, 5, 12, 0, tzinfo=dt.timezone.utc)
SCOPE = "team:synthetic"


class Response:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def modern_payload(*, start="2030-04-01T00:00:00Z", until="2030-05-01T00:00:00Z"):
    return {
        "included": {
            "balance_usd": 2.5,
            "allowance_usd": 10,
            "period": {"from": start, "until": until},
        },
        "purchased": {"balance_usd": 1.25},
    }


def legacy_payload(*, session_reset="2030-04-06T00:00:00Z", weekly_reset="2030-04-10T00:00:00Z"):
    return {
        "included": {
            "session": {"remaining_percent": 55, "resets_at": session_reset},
            "weekly": {"remaining_percent": 75, "resets_at": weekly_reset},
        },
        "purchased": {"balance_usd": 1.25},
    }


def observing(payload):
    calls = []

    def request(**kwargs):
        calls.append(kwargs)
        return Response(payload)

    result = service.observe_service(
        "ollama.balance", "synthetic-not-a-real-key", scope=SCOPE,
        now=NOW, request=request,
    )
    return result, calls


def test_modern_observation_uses_usd_and_current_period():
    result, calls = observing(modern_payload())
    assert result["schema"] == "provider-quota-service-observation/v1"
    assert result["service_id"] == "ollama.balance"
    assert result["provider_family"] == "ollama"
    assert result["status"] == "observed"
    assert result["runtime_admission"] == "unchanged"
    assert result["scope_status"] == "credential_selected_user_or_team_identity_unverified"
    assert result["signals"]["ollama_included_balance_usd"] == 2.5
    assert result["signals"]["ollama_included_allowance_usd"] == 10
    assert result["signals"]["ollama_purchased_balance_usd"] == 1.25
    assert result["valid_until"] == "2030-04-05T12:01:00Z"
    assert calls and calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://ollama.com/api/balance"
    assert calls[0]["allow_redirects"] is False


def test_legacy_observation_retains_percentages_and_utc_resets():
    result, _ = observing(legacy_payload())
    assert result["status"] == "observed"
    assert result["signals"]["ollama_session_remaining_percent"] == 55
    assert result["signals"]["ollama_weekly_remaining_percent"] == 75
    assert result["signals"]["ollama_session_resets_at"].startswith("2030-04-06")


@pytest.mark.parametrize("payload", [
    modern_payload(start="2030-03-01T00:00:00Z", until="2030-04-01T00:00:00Z"),
    modern_payload(start="2030-04-06T00:00:00Z", until="2030-05-01T00:00:00Z"),
    legacy_payload(session_reset="2030-04-04T00:00:00Z"),
    legacy_payload(weekly_reset="2030-04-05T12:00:00Z"),
])
def test_expired_or_future_quota_windows_are_unknown(payload):
    result, calls = observing(payload)
    assert calls
    assert result["status"] == "unknown"


def test_malformed_and_http_error_are_unknown_without_provider_detail():
    result, _ = observing({"included": "malformed"})
    assert result["status"] == "unknown"
    assert "malformed" not in result["reason"].lower() or result["reason"]

    def rate_limited(**kwargs):
        return type("Response", (), {"status_code": 429, "text": "PRIVATE RESPONSE CANARY"})()

    result = service.observe_service("ollama.balance", "synthetic-key", scope=SCOPE, now=NOW, request=rate_limited)
    assert result["status"] == "unknown"
    assert "PRIVATE RESPONSE CANARY" not in json.dumps(result)


@pytest.mark.parametrize("service_id,scope", [
    ("missing", SCOPE), ("ollama.balance", ""), ("ollama.balance", "bad scope"),
    ("ollama.balance", "x" * 129),
])
def test_invalid_id_or_scope_rejected_before_network(service_id, scope):
    called = False

    def request(**kwargs):
        nonlocal called
        called = True
        return Response(modern_payload())

    with pytest.raises(ValueError):
        service.observe_service(service_id, "synthetic-key", scope=scope, now=NOW, request=request)
    assert not called


def test_bad_or_empty_key_is_unknown_and_does_not_call_transport():
    for key in ("", "has\ncontrol", "x" * 4097):
        result = service.observe_service("ollama.balance", key, scope=SCOPE, now=NOW,
                                         request=lambda **kwargs: pytest.fail("called for invalid key"))
        assert result["status"] == "unknown"


def test_public_projection_is_allowlisted_and_drops_private_canaries():
    observation, _ = observing(modern_payload())
    observation["reason"] = "REASON CANARY"
    observation["scope"] = "SCOPE CANARY"
    observation["signals"]["private"] = "SIGNAL CANARY"
    public = service.public_status(observation)
    assert set(public) <= {"service_id", "provider_family", "status", "observed_at"}
    assert public["service_id"] == "ollama.balance"
    serialized = json.dumps(public)
    for canary in ("REASON CANARY", "SCOPE CANARY", "SIGNAL CANARY", "synthetic-not-a-real-key"):
        assert canary not in serialized


def private_observation():
    return {
        "schema": "provider-quota-service-observation/v1",
        "service_id": "ollama.balance", "provider_family": "ollama",
        "observed_at": NOW.isoformat(), "scope": SCOPE,
        "scope_status": "credential_selected_user_or_team_identity_unverified",
        "status": "observed", "reason": "synthetic reason",
        "signals": {"ollama_purchased_balance_usd": 1.25},
        "runtime_admission": "unchanged",
    }


def test_private_output_mode_0600_and_exclusive(tmp_path):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    parent.chmod(0o700)
    target = parent / "observation.json"
    service.write_private(target, private_observation())
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert json.loads(target.read_text())["scope"] == SCOPE
    with pytest.raises((FileExistsError, ValueError, OSError)):
        service.write_private(target, private_observation())


def test_private_output_rejects_unsafe_parent_and_symlink(tmp_path):
    loose = tmp_path / "loose"
    loose.mkdir(mode=0o755)
    loose.chmod(0o755)
    with pytest.raises((ValueError, PermissionError, OSError)):
        service.write_private(loose / "out.json", private_observation())

    private = tmp_path / "private"
    private.mkdir(mode=0o700)
    private.chmod(0o700)
    target = private / "link.json"
    target.symlink_to(tmp_path / "victim")
    with pytest.raises((ValueError, FileExistsError, OSError)):
        service.write_private(target, private_observation())
    assert not (tmp_path / "victim").exists()


def test_private_output_rejects_tracked_repository_path():
    repo_root = Path(__file__).resolve().parents[1]
    with pytest.raises((ValueError, PermissionError, OSError)):
        service.write_private(repo_root / "tests" / "should-not-be-created.json", private_observation())


def test_cli_requires_explicit_opt_in_and_outputs_status_only(tmp_path, monkeypatch, capsys):
    parent = tmp_path / "private"
    parent.mkdir(mode=0o700)
    parent.chmod(0o700)
    destination = parent / "private.json"
    monkeypatch.setenv("OLLAMA_API_KEY", "synthetic-key")
    monkeypatch.setattr(service, "observe_service", lambda *a, **kw: private_observation())
    with pytest.raises(SystemExit):
        service.main(["--service", "ollama.balance", "--scope", SCOPE,
                      "--private-out", str(destination)])
    assert not destination.exists()
    assert capsys.readouterr().out == ""

    status = service.main(["--service", "ollama.balance", "--scope", SCOPE,
                           "--private-out", str(destination), "--observe"])
    assert status == 0
    out = capsys.readouterr().out
    assert "ollama.balance" in out
    assert SCOPE not in out and "synthetic reason" not in out
    assert "ollama_purchased_balance_usd" not in out
    assert destination.exists()


def test_default_observation_uses_one_fixed_https_get_and_closes(monkeypatch):
    events = []

    class FakeResponse:
        status = 200

        def getheader(self, name):
            return None

        def read(self, size):
            events.append(("read", size))
            return json.dumps(modern_payload()).encode()

    class FakeConnection:
        def __init__(self, host, *, timeout, context):
            events.append(("connect", host, timeout, context))

        def request(self, method, path, *, headers):
            events.append(("request", method, path, headers))

        def getresponse(self):
            return FakeResponse()

        def close(self):
            events.append(("close",))

    monkeypatch.setattr(service.http.client, "HTTPSConnection", FakeConnection)
    result = service.observe_service("ollama.balance", "synthetic-key", scope=SCOPE, now=NOW)
    assert result["status"] == "observed"
    assert [event[0] for event in events] == ["connect", "request", "read", "close"]
    assert events[0][1] == "ollama.com"
    assert events[1][1:3] == ("GET", "/api/balance")
    assert events[1][3]["Authorization"] == "Bearer synthetic-key"
    assert events[2][1] == service.MAX_RESPONSE_BYTES + 1


@pytest.mark.parametrize("body,content_length", [
    (b'{"x":1,"x":2}', None),
    (b'{"x":NaN}', None),
    (b"{}", str(service.MAX_RESPONSE_BYTES + 1)),
    (b"x" * (service.MAX_RESPONSE_BYTES + 1), None),
])
def test_https_transport_rejects_duplicate_nonfinite_or_oversized_json(monkeypatch, body, content_length):
    closed = []

    class FakeResponse:
        status = 200

        def getheader(self, name):
            return content_length

        def read(self, size):
            assert size == service.MAX_RESPONSE_BYTES + 1
            return body[:size]

    class FakeConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            pass

        def getresponse(self):
            return FakeResponse()

        def close(self):
            closed.append(True)

    monkeypatch.setattr(service.http.client, "HTTPSConnection", FakeConnection)
    with pytest.raises((ValueError, json.JSONDecodeError)):
        service.https_request(method="GET", url=service.OLLAMA_BALANCE_URL,
                              headers={"Authorization": "Bearer synthetic"}, timeout=5,
                              allow_redirects=False, max_response_bytes=service.MAX_RESPONSE_BYTES)
    assert closed == [True]


def test_https_transport_non_200_does_not_read_body_and_closes(monkeypatch):
    events = []

    class FakeResponse:
        status = 429

        def getheader(self, name):
            return None

        def read(self, size):
            pytest.fail("non-200 response body must not be read")

    class FakeConnection:
        def __init__(self, *args, **kwargs):
            pass

        def request(self, *args, **kwargs):
            events.append("request")

        def getresponse(self):
            return FakeResponse()

        def close(self):
            events.append("close")

    monkeypatch.setattr(service.http.client, "HTTPSConnection", FakeConnection)
    response = service.https_request(method="GET", url=service.OLLAMA_BALANCE_URL,
                                     headers={"Authorization": "Bearer synthetic"}, timeout=5,
                                     allow_redirects=False, max_response_bytes=service.MAX_RESPONSE_BYTES)
    assert response.status_code == 429
    assert events == ["request", "close"]


def test_balance_registry_does_not_enter_legacy_router_weights():
    from scripts import quota_poll
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "ops/quota/registry.json").read_text())
    row = next(s for s in registry["services"] if s["id"] == "ollama.balance")
    assert row["lane"] == "model-balance"
    record = quota_poll.record(row, None, NOW)
    assert record["lane_id"] not in {"quota-model", "quota-deploy", "quota-data"}
    assert "ollama.balance" not in quota_poll.LIVE
    assert all(fn.__module__ != service.__name__ for fn in quota_poll.MULTI)
