import datetime as dt
import json
import math
from pathlib import Path

import pytest
from scripts import provider_quota_coverage as coverage


def test_provider_families_exhaust_registry_and_no_alias_hiding():
    result = coverage.build_coverage()
    families = {r["provider_family"]: r for r in result["provider_families"]}
    assert set(families) == set(coverage._providers())
    assert "gemini" in families and "google" not in families
    assert families["gemini"]["quota_manager_owner"] == "Manager"
    assert families["gemini"]["observation_method"] == "official_documentation_only; no passive parser"
    assert families["ollama"]["covered"] is False
    assert families["cloudflare"]["covered"] is False  # D1/Queues is not an inference quota
    assert families["openrouter"]["reader_service_ids"] == ["openrouter.free_models"]
    assert all(r["evidence_state"] == "unknown" for r in families.values())
    assert all(r["private_balance"] == "not_published" for r in families.values())
    assert families["gemini"]["free_entitlement"] is None


def test_optional_manager_metadata_is_allowlisted_and_not_live(tmp_path, monkeypatch):
    (tmp_path / "ops/quota").mkdir(parents=True)
    (tmp_path / "ops/quota/registry.json").write_text(json.dumps({"services": []}))
    (tmp_path / "ops/quota/provider-managers.json").write_text(json.dumps({"provider_families": [{
        "provider_family": "p", "status": "implemented_passive_adapter",
        "source": "https://docs.example.test/quota", "scope": "organization/model",
        "reset": "unknown", "signals": [{"path": "data.remaining", "field": "remaining", "token": "nope"}],
        "account_id": "private-value", "remaining": 4, "arbitrary": {"secret": "x"}
    }]}))
    monkeypatch.setattr(coverage, "_providers", lambda: ["p"])
    row = coverage.build_coverage(tmp_path)["provider_families"][0]
    assert row["mapping_state"] == "missing_provider_registry_mapping"
    assert row["manager_status"] == "implemented_passive_adapter"
    assert row["evidence_state"] == "unknown"
    assert row["scope"] == "organization/model"
    assert row["official_evidence"] == ["https://docs.example.test/quota"]
    assert row["documented_signals"] == [{"path": "data.remaining", "field": "remaining"}]
    encoded = json.dumps(row)
    assert "private-value" not in encoded and '"account_id":' not in encoded and '"arbitrary":' not in encoded
    assert '"remaining": 4' not in encoded
    assert row["private_balance"] == "not_published"


def test_unknown_provider_fails_closed():
    assert coverage.evaluate("unknown", "m", []) == {"admit": "deny", "reason": "unknown_provider"}


def test_evaluator_boundaries_and_reason_only_output(monkeypatch):
    monkeypatch.setattr(coverage, "_providers", lambda: ["p"])
    now = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
    row = {"provider": "p", "model": "m", "limit": 100, "used": 10,
           "observed_at": "2025-01-01T00:00:00Z", "reset_at": "2025-01-02T00:00:00Z",
           "evidence_status": "confirmed", "horizon": "H0",
           "api_key": "do-not-disclose", "prompt": "private"}
    assert coverage.evaluate("p", "m", [row], now=now)["admit"] == "allow"
    for alter, reason in [({"observed_at": "2025-01-01T00:02:00Z"}, "future_evidence"),
                          ({"reset_at": "2025-01-01T00:00:00Z"}, "reset_due_refresh_required"),
                          ({"used": 90}, "safety_budget_exhausted"),
                          ({"used": float("nan")}, "invalid_numeric_bounds")]:
        changed = dict(row, **alter)
        assert coverage.evaluate("p", "m", [changed], now=now)["reason"] == reason
    response = coverage.evaluate("p", "m", [row], now=now)
    assert set(response) == {"admit", "reason"}
    encoded = json.dumps(response)
    assert "do-not-disclose" not in encoded and "private" not in encoded and "100" not in encoded


def test_unknown_provider_with_well_formed_evidence_is_denied(monkeypatch):
    monkeypatch.setattr(coverage, "_providers", lambda: ["known"])
    row = _valid_row()
    assert coverage.evaluate("unknown", "m", [row], now=_now())["reason"] == "unknown_provider"


def _now():
    return dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)


def _valid_row(**changes):
    return {"provider": "p", "model": "m", "limit": 100, "used": 10,
            "observed_at": "2025-01-01T00:00:00Z", "reset_at": "2025-01-02T00:00:00Z",
            "evidence_status": "confirmed", "horizon": "H0", **changes}


@pytest.fixture(autouse=True)
def _known_provider(monkeypatch, request):
    if request.node.name == "test_provider_families_exhaust_registry_and_no_alias_hiding":
        return
    monkeypatch.setattr(coverage, "_providers", lambda: ["p"])


@pytest.mark.parametrize("field,value", [("used", True), ("limit", False), ("used", math.inf),
                                          ("limit", -math.inf), ("used", math.nan), ("limit", 0)])
def test_invalid_numeric_values_are_denied(field, value):
    assert coverage.evaluate("p", "m", [_valid_row(**{field: value})], now=_now())["admit"] == "deny"


@pytest.mark.parametrize("changes,reason", [
    ({"evidence_status": "unconfirmed"}, "unconfirmed_or_unauthorized_evidence"),
    ({"horizon": "H1"}, "unconfirmed_or_unauthorized_evidence"),
    ({"observed_at": None}, "unknown_reset_or_timestamp"),
    ({"observed_at": "2024-12-31T23:54:59Z"}, "stale_evidence"),
    ({"observed_at": "2025-01-01T00:00:01Z"}, "future_evidence"),
    ({"observed_at": "2025-01-01T00:00:00"}, "unknown_reset_or_timestamp"),
    ({"reset_at": "2025-01-02T00:00:00"}, "unknown_reset_or_timestamp"),
    ({"reset_at": None}, "unknown_reset_or_timestamp"),
    ({"reset_at": "2024-12-31T23:59:59Z"}, "reset_due_refresh_required"),
])
def test_evidence_authority_and_time_boundaries(changes, reason):
    row = _valid_row(**changes)
    assert coverage.evaluate("p", "m", [row], now=_now())["reason"] == reason


@pytest.mark.parametrize("bad_now", [dt.datetime(2025, 1, 1), "2025-01-01T00:00:00Z"])
def test_naive_or_malicious_now_denied(bad_now):
    assert coverage.evaluate("p", "m", [_valid_row()], now=bad_now)["reason"] == "invalid_now"


@pytest.mark.parametrize("cooldown", [1, 60])
def test_positive_retry_after_cooldown_denies(cooldown):
    assert coverage.evaluate("p", "m", [_valid_row()], now=_now(), cooldown_seconds=cooldown)["reason"] == "cooldown_active"


@pytest.mark.parametrize("value", [True, math.inf, math.nan, -1])
def test_invalid_cooldown_denied(value):
    assert coverage.evaluate("p", "m", [_valid_row()], now=_now(), cooldown_seconds=value)["admit"] == "deny"


@pytest.mark.parametrize("ttl", [0, -1, 901, True, math.inf, math.nan])
def test_invalid_ttl_denied(ttl):
    assert coverage.evaluate("p", "m", [_valid_row()], now=_now(), max_age_seconds=ttl)["admit"] == "deny"


def test_exact_one_request_safety_margin_and_duplicate_rows():
    exact = _valid_row(limit=10, used=8)
    assert coverage.evaluate("p", "m", [exact], now=_now(), safety=0.9)["admit"] == "allow"
    over = _valid_row(limit=10, used=8.01)
    assert coverage.evaluate("p", "m", [over], now=_now(), safety=0.9)["reason"] == "safety_budget_exhausted"
    assert coverage.evaluate("p", "m", [exact, dict(exact)], now=_now())["reason"] == "duplicate_or_missing_evidence"


def test_public_metadata_excludes_sensitive_field_names_and_values():
    public = coverage._safe_public({"provider_family": "p", "used": 5, "remaining": 2, "api_key": "secret", "nested": {"prompt": "text", "safe": True}})
    encoded = json.dumps(public)
    assert "secret" not in encoded and "text" not in encoded
    assert "used" not in encoded and public["nested"] == {"safe": True}


@pytest.mark.parametrize("model", ["", "<model>", "*", "p/../m", "a b", "m\n", "a\\b"])
def test_invalid_model_identities_fail_closed(model):
    assert coverage.evaluate("p", model, [_valid_row(model=model)], now=_now())["reason"] == "invalid_provider_or_model"


def test_oversized_numeric_controls_fail_closed():
    huge = 10 ** 1000
    assert coverage.evaluate("p", "m", [_valid_row()], now=_now(), safety=huge)["admit"] == "deny"
    assert coverage.evaluate("p", "m", [_valid_row(limit=huge)], now=_now())["admit"] == "deny"
