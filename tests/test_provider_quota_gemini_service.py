"""Offline integration tests: no Google account, credential, or inference access."""
import datetime as dt
import json
from unittest.mock import patch

import pytest
from zoneinfo import ZoneInfoNotFoundError

from scripts import provider_quota_coverage as coverage
from scripts import provider_quota_managers as managers
from scripts import provider_quota_service as service

NOW = dt.datetime(2026, 10, 21, 15, 0, tzinfo=dt.timezone.utc)


def test_missing_project_evidence_remains_unknown_without_network():
    with patch.object(service, "https_request", side_effect=AssertionError("network forbidden")):
        observation = service.observe_gemini_quota(scope="fixture-project", now=NOW)
    assert observation["provider_family"] == "gemini"
    assert observation["status"] == "unknown"
    assert observation["runtime_admission"] == "unchanged"
    assert service.public_status(observation)["request_quota"] == "unknown"
    assert "gemini.project_model" not in service.SERVICES  # No implicit GET or CLI permission.


@pytest.mark.parametrize("payload", [[], "PRIVATE-CANARY", True, 123])
def test_malformed_private_input_is_unknown_and_not_reflected(payload):
    observation = service.observe_gemini_quota(payload, scope="fixture-project", now=NOW)
    assert observation["status"] == "unknown"
    assert "PRIVATE-CANARY" not in json.dumps(observation)


def test_public_projection_never_exposes_account_or_counter_claims():
    observation = {"service_id": "gemini.project_model", "observed_at": NOW.isoformat(),
                   "status": "observed", "request_quota": "observed", "tier": "tier_3",
                   "billing_status": "PRIVATE-BILLING-CANARY", "scope": "PRIVATE-PROJECT-CANARY",
                   "api_key": "PRIVATE-KEY-CANARY", "signals": {"used": 731921}}
    result = service.public_status(observation)
    assert result["status"] == result["request_quota"] == "unknown"
    assert set(result) == {"service_id", "provider_family", "observed_at", "status", "request_quota"}
    assert "CANARY" not in json.dumps(result)
    assert "731921" not in json.dumps(result)
    assert "tier_3" not in json.dumps(result)


def test_registry_identifies_offline_parser_not_live_service():
    row = managers.load_managers()["gemini"]
    assert row["status"] == "implemented_passive_adapter"
    assert "project" in row["scope"]
    assert "America/Los_Angeles" in row["reset"]
    observation = managers.normalize_observation(
        "gemini", metadata={}, observed_at=NOW.isoformat(), scope="fixture-project")
    assert observation["status"] == "unknown"


def test_flat_confirmed_counter_cannot_bypass_gemini_binding_or_token_checks(monkeypatch):
    monkeypatch.setattr(coverage, "_providers", lambda: ["gemini"])
    evidence = [{"provider": "gemini", "model": "gemini-3.1-flash-lite",
                 "limit": 100, "used": 0, "evidence_status": "confirmed", "horizon": "H0",
                 "observed_at": NOW.isoformat(), "reset_at": (NOW + dt.timedelta(days=1)).isoformat(),
                 "tier": "free", "project_verified": True, "entitlement": "free"}]
    result = coverage.evaluate("gemini", "gemini-3.1-flash-lite", evidence, now=NOW)
    assert result == {"admit": "deny", "reason": "gemini_project_binding_and_current_quota_unverified"}


def test_service_is_not_added_to_automatic_collectors():
    from scripts import quota_poll
    assert not any("gemini" in key.lower() for key in quota_poll.LIVE)


@pytest.mark.parametrize("now", ["PRIVATE-CLOCK-CANARY", dt.datetime(2026, 10, 21), True, 123])
def test_invalid_service_clock_returns_unknown_without_reflecting_input(now):
    result = service.observe_gemini_quota(scope="fixture-project", now=now)
    assert result["status"] == "unknown"
    assert result["observed_at"] is None
    assert service.public_status(result)["observed_at"] is None
    assert "PRIVATE-CLOCK-CANARY" not in json.dumps(result)


def test_service_keeps_source_observation_time_not_wrapper_collection_time():
    source_time = NOW - dt.timedelta(minutes=10)
    payload = {"source_kind": "aistudio_project_quota", "project_alias": "fixture-project",
               "credential_alias": "fixture-credential", "model": "gemini-synthetic-model",
               "tier": "unknown", "entitlement": "unknown", "dimensions": {},
               "observed_at": source_time.isoformat()}
    result = service.observe_gemini_quota(payload, scope="fixture-project", now=NOW)
    assert result["observed_at"] == source_time.isoformat().replace("+00:00", "Z")
    assert result["status"] == "unknown"
    assert result["binding_status"] == "unknown"


def test_project_service_returns_unknown_when_timezone_data_is_unavailable(monkeypatch):
    from scripts import provider_quota_gemini as gemini

    monkeypatch.setattr(gemini, "ZoneInfo", lambda name: (_ for _ in ()).throw(
        ZoneInfoNotFoundError(name)))
    result = service.observe_gemini_quota(
        {"source_kind": "aistudio_project_quota", "project_alias": "fixture-project",
         "credential_alias": "fixture-credential", "model": "gemini-synthetic-model",
         "tier": "unknown", "entitlement": "unknown",
         "dimensions": {"rpd": {"limit": 2, "used": 0, "remaining": 2,
                                   "window": {"kind": "pacific_day", "start": "2026-10-21T07:00:00Z",
                                              "end": "2026-10-22T07:00:00Z"}}}},
        scope="fixture-project", now=NOW)
    assert result["status"] == "unknown"
    assert result["request_quota"] == "unknown"
    assert result["runtime_admission"] == "unchanged"
