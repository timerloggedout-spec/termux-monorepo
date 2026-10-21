"""MSM-023: held protocol discovery never becomes transport or account evidence."""
import copy
import json
from pathlib import Path

from scripts.model_selection_market import provider_batch as batch
from llm_api_hub.server import research_providers as runtime
from scripts import provider_model_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "tashfeenahmed/freellmapi"


def inputs():
    research = json.loads((ROOT / "data/model-selection-market/provider-recon.json").read_text())
    empty_catalog = {"schema": "provider-model-catalog/v5", "models": [], "provider_observations": {}}
    return research, empty_catalog


def test_existing_typhoon_reference_links_offline_code_not_live_transport():
    research, observation = inputs()
    original = copy.deepcopy(research)
    result = batch.reconcile(research, observation)
    row = next(r for r in result["candidates"] if r["provider_key"] == "typhoon")
    assert row["source_repo"] == SOURCE
    assert row["service_disposition"] == "offline_protocol_legal_hold"
    assert row["native_provider"] is None
    assert row["native_chat_adapter"] is row["catalog_adapter"] is row["runtime_eligible"] is False
    assert row["quota_remaining"] is row["model_id"] is None
    assert row["status"] == "not_an_individual_model"
    held = row["offline_protocol_adapter"]
    assert held["account_entitlement"] == "unverified"
    assert held["live_inference"] == "not_attempted"
    assert (ROOT / held["implementation_path"]).is_file()
    assert (ROOT / held["documentation_path"]).is_file()
    assert "typhoon" not in runtime.ENDPOINTS
    assert "typhoon" not in catalog.ENDPOINTS
    assert research == original  # Preserve pinned third-party evidence, not first-party rewrites.
    held["status"] = "tampered"
    assert batch.OFFLINE_PROTOCOL_MAP[(SOURCE, "typhoon")]["status"] == "offline_protocol_legal_hold"


def test_denominators_preserve_live_families_and_separate_one_held_protocol():
    result = batch.reconcile(*inputs())
    proxy = result["summary"]["by_source"][SOURCE]
    assert proxy["research_records"] == 72
    assert proxy["individual_model_claims"] == proxy["runtime_eligible"] == 0
    assert len(proxy["chat_transport_families"]) == 16
    assert proxy["service_reference_coverage"] == {"total": 72, "by_disposition": {
        "chat_transport_available": 16, "custom_configuration_placeholder": 1,
        "fixed_public_research_only": 1, "offline_protocol_legal_hold": 1,
        "unmapped_service_reference": 53,
    }}
    directory = result["summary"]["by_source"]["mnfst/awesome-free-llm-apis"]
    assert directory["individual_model_claims"] == 117
    assert len(directory["chat_transport_families"]) == 16
    longcat = next(r for r in result["candidates"] if r["provider_key"] == "longcat")
    assert longcat["service_disposition"] == "unmapped_service_reference"
    assert "offline_protocol_adapter" not in longcat


def test_only_exact_source_scoped_service_reference_gets_linked():
    research, observation = inputs()
    template = next(r for r in research["model_candidates"] if r["provider_key"] == "typhoon")
    research["model_candidates"] = [dict(template, source_repo="mnfst/awesome-free-llm-apis")]
    assert "offline_protocol_adapter" not in batch.reconcile(research, observation)["candidates"][0]
    research["model_candidates"] = [dict(template, provider_key="typhoon-proxy")]
    assert "offline_protocol_adapter" not in batch.reconcile(research, observation)["candidates"][0]
    research["model_candidates"] = [dict(template, model_key="not-a-service", model_id="exact-synthetic-model")]
    assert "offline_protocol_adapter" not in batch.reconcile(research, observation)["candidates"][0]


def test_dashboard_and_matrix_link_hold_separately_and_ci_runs_fixtures():
    dashboard = (ROOT / "apps/help-wanted-dashboard/quota.html").read_text()
    assert 'id="held-discovery"' in dashboard
    assert "TYPHOON-FREE-API-CONTRACT.md" in dashboard
    assert "Not included in active transport, quota-service or live-manager counts" in dashboard
    for document in ("RESOURCE-IMPLEMENTATION-MATRIX.md", "PROVIDER-SERVICE-EXPANSION.md"):
        assert "TYPHOON-FREE-API-CONTRACT.md" in (ROOT / "docs/ops" / document).read_text()
    workflow = (ROOT / ".github/workflows/provider-batch.yml").read_text()
    assert "python3 -m pytest -q tests/test_typhoon_protocol.py tests/test_typhoon_discovery.py" in workflow
    assert "tests/fixtures/typhoon/**" in workflow
    # There is no Typhoon account/key/job wiring alongside the offline tests.
    assert "OPENTYPHOON_API_KEY" not in workflow
    assert "TYPHOON_API_KEY" not in workflow
