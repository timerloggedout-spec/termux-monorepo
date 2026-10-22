import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.quota_publication import SCHEMA, build_payload, _safe_url

ROOT = Path(__file__).resolve().parents[1]


def fixture_data():
    registry = {"services": [
        {"id": "google.api", "provider": "google", "limit": 15, "unit": "RPM", "window": "minute", "reset": "midnight", "source": "https://ai.google.dev/gemini-api/docs/rate-limits", "account_id": "ACCT_SECRET", "notes": "NOTE_SECRET", "authorization": "Bearer SECRET", "dimensions": {"token_count": 123, "project_id": "PROJECT_SECRET"}},
        {"id": "github.api.github_token", "provider": "github", "limit": 1000, "unit": "requests/hour", "source": "https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api"},
        {"id": "hidden.quota", "provider": "openrouter", "limit": 99},
    ]}
    coverage = {"provider_families": [
        {"provider_family": "gemini", "status": "documented", "documented_limit": 15, "scope": "PROJECT_SECRET", "official_evidence": ["https://ai.google.dev/gemini-api/docs/rate-limits"], "arbitrary_note": "NOTE_SECRET", "quota_capability": {"dimensions": "token_count", "user_id": "USER_SECRET"}},
        {"provider_family": "github", "status": "ok", "account_id": "ACCT_SECRET"},
        {"provider_family": "openrouter", "status": "ok"},
    ], "coverage_counts": {"provider_families": 999}, "mapping_capability_counts": {"actual_mapping": 999}}
    readings = {"readings": [
        {"resource_id": "google.api", "used": 6, "remaining": 9, "observed_at": "2026-01-01T00:00:00Z", "scope": "PROJECT_SECRET", "error": "ERROR_SECRET", "nested": {"token_count": 444, "api_key": None}},
        {"resource_id": "quota:google.api", "service_id": "google.api", "used": 7, "remaining": 8},
        {"resource_id": "openrouter.quota", "used": 77, "user_id": "USER_SECRET"},
    ]}
    return registry, coverage, readings


def test_default_public_values_and_recursively_strip_secrets_and_freeform_fields():
    payload = build_payload(*fixture_data(), {"schema": SCHEMA, "families": {}})
    assert payload["registry"]["services"][0]["provider"] == "gemini"
    row = next(x for x in payload["readings"]["readings"] if x["resource_id"] == "google.api")
    assert row["provider_family"] == "gemini" and row["used"] == 6
    assert "scope" not in row and "error" not in row
    serialized = json.dumps(payload)
    for sentinel in ("ACCT_SECRET", "PROJECT_SECRET", "USER_SECRET", "KEY_SECRET", "SECRET", "NOTE_SECRET", "ERROR_SECRET"):
        assert sentinel not in serialized
    assert "token_count" in serialized
    assert "api_key" not in serialized and "authorization" not in serialized
    assert "arbitrary_note" not in serialized


def test_private_family_removes_rows_and_recomputes_counts():
    config = {"schema": SCHEMA, "families": {"openrouter": {"visibility": "private", "fields": {}}}}
    payload = build_payload(*fixture_data(), config)
    assert not any(x.get("provider") == "openrouter" for x in payload["registry"]["services"])
    assert not any(x.get("provider_family") == "openrouter" for x in payload["coverage"]["provider_families"])
    assert payload["visibility"]["families"]["openrouter"]["visibility"] == "private"
    assert payload["coverage"]["coverage_counts"]["provider_families"] == 2
    assert payload["coverage"]["mapping_capability_counts"]["actual_mapping"] == 0


def test_nested_field_controls_and_null_secret_keys_are_omitted():
    config = {"schema": SCHEMA, "families": {"gemini": {"visibility": "public", "fields": {"usage": "private", "availability": "private", "scope": "public", "sources": "private"}}}}
    reg, cov, readings = fixture_data()
    readings["readings"][0]["nested"].update({"api_key": None, "authorization": None})
    payload = build_payload(reg, cov, readings, config)
    row = next(x for x in payload["readings"]["readings"] if x.get("provider_family") == "gemini")
    assert "used" not in row and "remaining" not in row and "scope" not in row
    assert "api_key" not in json.dumps(payload) and "authorization" not in json.dumps(payload)
    assert "source" not in next(x for x in payload["registry"]["services"] if x["provider"] == "gemini")


def test_private_github_skips_observation():
    calls = []
    config = {"schema": SCHEMA, "families": {"github": {"visibility": "private", "fields": {}}}}
    payload = build_payload(*fixture_data(), config, observe_github=True, token="TOKEN", observer=lambda *a, **kw: calls.append(1))
    assert calls == []
    assert not any(x.get("provider_family") == "github" for x in payload["readings"]["readings"])


def test_github_observation_rows_join_registry_and_project_well_typed_evidence():
    calls = []
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    def observe(token, **kwargs):
        calls.append((token, kwargs))
        return {"observed_at": now, "token": "RAW_SECRET", "resources": {
            "core": {"used": 2, "limit": 1000, "remaining": 998, "reset": 4102444800, "account_id": "ACCOUNT_SECRET"},
            "graphql": {"used": 0, "limit": 1000, "remaining": 1000, "reset": 4102444800}}}
    registry = json.loads((ROOT / "ops/quota/registry.json").read_text())
    cov = {"provider_families": [{"provider_family":"github", "quota_mapping":{"status":"implemented_passive_parser", "source_kind":"official_endpoint_metadata", "dimensions":"requests_only"}, "static_mapping_state":"static_roster_link_only", "manager_status":"implemented_passive_adapter", "runtime_manager_state":"implemented_opt_in_private_service"}]}
    payload = build_payload(registry, cov, {"readings":[]}, {"schema":SCHEMA,"families":{}}, observe_github=True, token="SYNTHETIC", observer=observe)
    assert len(calls) == 1
    rows = [x for x in payload["readings"]["readings"] if x.get("provider_family") == "github"]
    assert {r["resource_id"] for r in rows} == {"github.api.github_token", "github.api.graphql"}
    for row in rows:
        assert row["status"] == "ok" and row["horizon"] == "H0" and row["evidence_status"] == "confirmed"
        assert row["observed_at"] == now and row["reset"].endswith("Z") and type(row["used"]) is int
    assert payload["coverage"]["provider_families"][0]["quota_mapping"]["dimensions"] == "requests_only"
    for field in ("static_mapping_state", "manager_status", "runtime_manager_state"):
        assert field in payload["coverage"]["provider_families"][0]
    serialized = json.dumps(payload)
    assert all(secret not in serialized for secret in ("SYNTHETIC", "RAW_SECRET", "ACCOUNT_SECRET"))


def test_missing_github_token_skips_observer():
    calls = []
    payload = build_payload(*fixture_data(), {"schema":SCHEMA,"families":{}}, observe_github=True, observer=lambda *a, **kw: calls.append(1))
    assert calls == []
    assert all(r["status"] == "unknown" for r in payload["readings"]["readings"] if r.get("provider_family") == "github")


def test_safe_urls_require_official_hosts_and_static_paths():
    assert _safe_url("https://ai.google.dev/gemini-api/docs/rate-limits")
    for url in ("https://evil.example/docs", "https://docs.github.com/account-user-123", "https://docs.github.com/x?token=secret"):
        assert _safe_url(url) is None


def test_repository_registry_coverage_and_historical_readings_integrate():
    registry = json.loads((ROOT / "ops/quota/registry.json").read_text())
    coverage = json.loads((ROOT / "apps/help-wanted-dashboard/data/provider-quota-coverage.json").read_text())
    readings = json.loads((ROOT / "apps/help-wanted-dashboard/data/quota.json").read_text())
    config = json.loads((ROOT / "ops/quota/public-visibility.json").read_text())
    payload = build_payload(registry, coverage, readings, config)
    assert len(payload["coverage"]["provider_families"]) == 27
    assert payload["coverage"]["mapping_capability_counts"] == {
        "actual_mapping": 2, "passive_parser": 6,
        "documentation_only": 18, "unknown_or_unsupported": 3,
    }
    public_ids = {service["id"] for service in payload["registry"]["services"]}
    assert all(row["resource_id"] in public_ids for row in payload["readings"]["readings"])
    assert {row["resource_id"] for row in payload["readings"]["readings"]} == {
        "vercel.deployments", "openrouter.free_models", "github.actions.minutes"
    }
    assert payload["coverage"]["coverage_counts"]["provider_families"] == 27


def test_nonfinite_and_bool_numbers_are_rejected():
    reg, cov, _ = fixture_data()
    payload = build_payload(reg, cov, {"readings":[{"resource_id":"google.api","used":True,"remaining":float("nan"),"limit":float("inf")}]})
    row = next(x for x in payload["readings"]["readings"] if x["resource_id"] == "google.api")
    assert not {"used", "remaining", "limit"} & row.keys()


def test_unknown_visibility_groups_rejected():
    config = {"schema": SCHEMA, "families": {"github": {"visibility": "public", "fields": {"raw": "public"}}}}
    with pytest.raises(ValueError): build_payload(*fixture_data(), config)


def test_usage_and_availability_are_independently_private_in_published_payload():
    reg, cov, readings = fixture_data()
    for hidden, removed, kept in [('usage', 'used', 'remaining'), ('availability', 'remaining', 'used')]:
        payload = build_payload(reg, cov, readings, {'schema': SCHEMA, 'families': {'gemini': {'visibility': 'public', 'fields': {hidden: 'private'}}}})
        row = payload['readings']['readings'][0]
        assert removed not in row and kept in row
    config = {'schema': SCHEMA, 'families': {'gemini': {'visibility': 'public', 'fields': {'limits': 'private'}}}}
    payload = build_payload(reg, cov, {'readings': [{'resource_id': 'google.api', 'free_model_daily_limit': 400, 'free_model_daily_used': 1}]}, config)
    assert 'free_model_daily_limit' not in payload['readings']['readings'][0]
    assert payload['readings']['readings'][0]['free_model_daily_used'] == 1


def test_dynamic_rows_cannot_smuggle_private_strings_in_safe_sounding_fields():
    reg, cov, _ = fixture_data()
    row = {'resource_id': 'google.api', 'used': 7, 'metric': 'opaquecredentialvalue',
           'unit': 'opaquecredentialvalue', 'scope': 'opaqueidentifier',
           'source': 'https://docs.github.com/opaqueidentifier',
           'observed_at': 'opaqueidentifier', 'reset': 'opaqueidentifier', 'status': 'opaqueidentifier'}
    payload = build_payload(reg, cov, {'readings': [row]})
    result = payload['readings']['readings'][0]
    assert result == {'resource_id': 'google.api', 'provider_family': 'gemini', 'used': 7}
    assert 'opaqueidentifier' not in json.dumps(payload) and 'opaquecredentialvalue' not in json.dumps(payload)


def test_private_reset_fields_are_absent_even_when_null():
    reg, cov, _ = fixture_data()
    config = {'schema': SCHEMA, 'families': {'gemini': {'visibility': 'public', 'fields': {'reset': 'private'}}}}
    result = build_payload(reg, cov, {'readings': [{'resource_id': 'google.api', 'used': 1, 'reset': None, 'observed_at': None}]}, config)
    assert not {'reset', 'observed_at'} & result['readings']['readings'][0].keys()
