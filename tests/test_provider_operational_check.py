"""Readiness is not account entitlement, execution, or a public quota receipt."""
import json
from pathlib import Path
import urllib.error

import pytest
import yaml

from llm_api_hub.server import provider_extensions as ext
from scripts.ops import provider_operational_check as readiness

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    for _, aliases in ext.ENDPOINTS.values():
        for name in aliases:
            monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("LLM_API_HUB_PROVIDER_POLICY", raising=False)


def test_default_check_has_no_network_and_does_not_read_key_values(monkeypatch):
    monkeypatch.setattr(readiness.provider_model_catalog, "poll", lambda *a: pytest.fail("network"))
    report = readiness.check()
    assert report["summary"] == {
        "registered_transports": len(ext.ENDPOINTS), "configured_credentials": 0,
        "admitted_providers": 0, "catalogs_ok": 0, "completion_requests": 0,
        "paid_fallback_allowed": False, "production_admission_changed": False,
    }
    assert all(row["readiness"] == "missing_credential" for row in report["providers"])


def test_quota_managers_consume_only_existing_catalog_responses(monkeypatch):
    seen = []
    calls = []
    original = readiness.provider_quota_managers.catalog_quota_status

    def status(provider, headers, *, observed_at, source=None):
        calls.append((provider, bool(headers)))
        return original(provider, headers, observed_at=observed_at, source=source)

    def poll(provider, token):
        seen.append(provider)
        return [], {"x-ratelimit-remaining-requests": "private-canary"}

    monkeypatch.setattr(readiness.provider_quota_managers, "catalog_quota_status", status)
    monkeypatch.setattr(readiness.provider_model_catalog, "poll", poll)
    report = readiness.check(catalogs=True)
    assert set(seen) == {"routeway", "requesty", "xkiro"}
    assert len(seen) == len(set(seen))
    assert {p for p, has_headers in calls if has_headers} == set(seen)
    assert all(row["quota_manager"]["status"] == "unknown" for row in report["providers"])
    assert "private-canary" not in json.dumps(report)


def test_typhoon_key_alias_configures_transport_but_not_entitlement(monkeypatch):
    monkeypatch.setenv("TYPHOON_API_KEY", "synthetic-never-reported")
    report = readiness.check()
    row = next(row for row in report["providers"] if row["provider"] == "typhoon")
    assert row["credential_present"] is True and row["exact_model_admitted"] is False
    assert row["readiness"] == "admission_required"
    assert "synthetic-never-reported" not in json.dumps(report)


def test_public_catalogs_only_and_raw_failures_never_reflected(monkeypatch):
    seen = []
    def poll(provider, token):
        seen.append((provider, token))
        if provider == "routeway":
            raise urllib.error.HTTPError("https://safe.test", 403, "private-body", {}, None)
        if provider == "xkiro":
            raise ValueError("private-body")
        return [{"account_id": "private-body", "pricing": {"used": "private-body"}}], {"authorization": "private-body"}
    monkeypatch.setattr(readiness.provider_model_catalog, "poll", poll)
    report = readiness.check(catalogs=True)
    rows = {row["provider"]: row for row in report["providers"]}
    assert {provider for provider, _ in seen} == {"routeway", "requesty", "xkiro"}
    assert rows["routeway"]["catalog_status"] == "http_403"
    assert rows["xkiro"]["catalog_status"] == "unavailable"
    assert rows["requesty"]["catalog_status"] == "ok"
    assert rows["typhoon"]["catalog_status"] == rows["xfyun"]["catalog_status"] == "not_documented"
    assert rows["sealion"]["catalog_status"] == "missing_credential"
    assert "private-body" not in json.dumps(report)
    assert all(row["inference_attempted"] is False for row in rows.values())


def test_cli_emits_complete_json_only(capsys):
    assert readiness.main([]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["schema"] == "provider-operational-check/v1"
    assert report["summary"]["completion_requests"] == 0


def test_readiness_job_is_trusted_sha_bound_and_does_not_receive_broad_or_google_credentials():
    workflow = yaml.safe_load((ROOT / ".github/workflows/provider-batch.yml").read_text())
    events = workflow.get("on", workflow.get(True))
    assert events["workflow_dispatch"]["inputs"]["check_operational_providers"]["default"] is False
    assert workflow["permissions"] == {}
    contracts = workflow["jobs"]["contracts"]
    assert all(not step.get("env") for step in contracts["steps"])
    job = workflow["jobs"]["operational_providers"]
    assert job["permissions"] == {"contents": "read"}
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert "github.event.repository.default_branch" in job["if"]
    assert "inputs.check_operational_providers" in job["if"]
    assert job["steps"][0]["with"] == {"ref": "${{ github.sha }}", "persist-credentials": False}
    step = job["steps"][1]
    assert step["run"] == "python3 scripts/ops/provider_operational_check.py --catalogs"
    assert set(step["env"]) == {name for _, aliases in ext.ENDPOINTS.values() for name in aliases}
    assert not {"GH_TOKEN", "GITHUB_TOKEN", "GEMINI_API_KEY", "OPENROUTER_API_KEY"} & set(step["env"])
    assert "check_operational_providers" in workflow["jobs"]["observe"]["if"]
    assert "pull_request_target" not in str(events)
    assert all("upload-artifact" not in str(step.get("uses", "")) for step in job["steps"])
