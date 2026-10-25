"""MSM-024: transport discovery never fabricates account or execution evidence."""
import copy
import json
from pathlib import Path
from scripts.model_selection_market import provider_batch as batch
from llm_api_hub.server import research_providers as runtime
from scripts import provider_model_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "tashfeenahmed/freellmapi"
NEW_FAMILIES = {"typhoon", "unorouter", "routeway", "requesty", "xkiro", "xfyun", "sealion"}


def inputs():
    research = json.loads((ROOT / "data/model-selection-market/provider-recon.json").read_text())
    observation = {"schema": "provider-model-catalog/v5", "models": [], "provider_observations": {}}
    return research, observation


def test_typhoon_reference_links_actual_transport_without_fabricating_account():
    research, observation = inputs()
    original = copy.deepcopy(research)
    result = batch.reconcile(research, observation)
    row = next(r for r in result["candidates"] if r["provider_key"] == "typhoon")
    assert row["source_repo"] == SOURCE
    assert row["service_disposition"] == "chat_transport_available"
    assert row["native_provider"] == "typhoon"
    assert row["native_chat_adapter"] is True
    assert row["catalog_adapter"] is row["runtime_eligible"] is False
    assert row["quota_remaining"] is row["model_id"] is None
    assert row["status"] == "not_an_individual_model"
    assert "offline_protocol_adapter" not in row
    assert "typhoon" in runtime.ENDPOINTS and "typhoon" not in catalog.ENDPOINTS
    assert research == original


def test_new_families_preserve_model_denominators_and_unknown_execution():
    result = batch.reconcile(*inputs())
    proxy = result["summary"]["by_source"][SOURCE]
    assert proxy["research_records"] == 76
    assert proxy["individual_model_claims"] == proxy["runtime_eligible"] == 0
    assert len(proxy["chat_transport_families"]) == len(batch.SOURCE_PROVIDER_MAP[SOURCE])
    assert NEW_FAMILIES <= set(proxy["chat_transport_families"])
    dispositions = proxy["service_reference_coverage"]["by_disposition"]
    assert dispositions["chat_transport_available"] == len(batch.SOURCE_PROVIDER_MAP[SOURCE])
    assert "offline_protocol_legal_hold" not in dispositions
    assert sum(dispositions.values()) == proxy["research_records"]
    for row in result["candidates"]:
        if row["source_repo"] == SOURCE and row["provider_key"] in NEW_FAMILIES:
            assert row["native_chat_adapter"] is True
            assert row["runtime_eligible"] is False and row["quota_remaining"] is None
            assert row["catalog_adapter"] == (row["provider_key"] not in {"typhoon", "xfyun"})
    directory = result["summary"]["by_source"]["mnfst/awesome-free-llm-apis"]
    assert directory["individual_model_claims"] == 128
    assert len(directory["chat_transport_families"]) == 16
    longcat = next(r for r in result["candidates"] if r["provider_key"] == "longcat")
    assert longcat["service_disposition"] == "unmapped_service_reference"


def test_only_exact_source_scoped_service_alias_gets_transport_link():
    research, observation = inputs()
    template = next(r for r in research["model_candidates"] if r["provider_key"] == "typhoon")
    for changed in ({"source_repo": "mnfst/awesome-free-llm-apis"}, {"provider_key": "typhoon-proxy"}):
        research["model_candidates"] = [dict(template, **changed)]
        row = batch.reconcile(research, observation)["candidates"][0]
        assert row["native_provider"] is None
        assert "offline_protocol_adapter" not in row


def test_dashboard_and_workflow_describe_transport_not_offline_development_hold():
    dashboard = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert 'id="provider-development"' in dashboard
    assert "TYPHOON-FREE-API-CONTRACT.md" in dashboard
    assert "registered HTTP text transport" in dashboard
    assert "legal/data-use review required" not in dashboard
    workflow = (ROOT / ".github/workflows/provider-batch.yml").read_text()
    assert "python3 -m pytest -q tests/test_typhoon_protocol.py tests/test_typhoon_discovery.py" in workflow
    assert "tests/test_provider_extensions.py" in workflow
    assert "scripts/ops/provider_operational_check.py --catalogs" in workflow
    assert "tests/fixtures/typhoon/**" in workflow
