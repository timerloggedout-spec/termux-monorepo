"""All snapshot coverage claims must be backed by a production transport."""
import json
from pathlib import Path

from llm_api_hub.server import research_providers as runtime
from scripts.model_selection_market import provider_batch as coverage

ROOT = Path(__file__).resolve().parents[1]


def test_no_exact_research_claim_is_silently_omitted():
    snapshot = json.loads((ROOT / 'data/model-selection-market/provider-recon.json').read_text())
    report = coverage.reconcile(snapshot, {'schema': 'provider-model-catalog/v5', 'models': [], 'provider_observations': {}})
    individual = [r for r in report['candidates'] if r['model_id'] and not r['model_id'].startswith('aggregate:')]
    assert len(individual) == 106
    for row in individual:
        if row['native_chat_adapter']:
            assert row['native_provider'] in runtime.ENDPOINTS
        assert row['runtime_eligible'] is False
    # Legacy OpenRouter is deliberately outside research-provider admission.
    assert sum(r['native_provider'] == 'openrouter' for r in individual) == 17


def test_all_native_routes_deny_missing_policy_before_network(monkeypatch):
    monkeypatch.delenv('LLM_API_HUB_PROVIDER_POLICY', raising=False)
    monkeypatch.setattr(runtime, 'post_json', lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network attempted')))
    for provider in runtime.ENDPOINTS:
        try:
            runtime.complete(provider, 'synthetic-exact-model', {'model': 'synthetic-exact-model', 'messages': [{'role': 'user', 'content': 'public'}]}, 1)
        except runtime.ProviderAdmissionError as error:
            assert error.status == 403
        else:
            raise AssertionError(f'{provider} bypassed exact-account admission')


def test_all_117_claims_have_transports_but_no_automatic_admission():
    snapshot = json.loads((ROOT / 'data/model-selection-market/provider-recon.json').read_text())
    report = coverage.reconcile(snapshot, {'schema': 'provider-model-catalog/v5', 'models': [], 'provider_observations': {}})
    directory = report['summary']['by_source']['mnfst/awesome-free-llm-apis']
    assert directory['gated_native_chat_model_claims'] + directory['legacy_openrouter_model_claims'] + 4 == directory['individual_model_claims'] == 106
    assert len(directory['chat_transport_families']) == 15 and directory['provider_families'] == 16
    assert len(directory['catalog_adapter_families']) == 14  # Z.ai remains unverified; ModelScope is runtime-observed.
    assert report['summary']['runtime_eligible'] == 0


def test_llm7_public_catalog_without_token_is_not_account_admission(monkeypatch, tmp_path):
    from scripts import provider_model_catalog as catalog
    monkeypatch.delenv('LLM7_API_TOKEN', raising=False)
    calls = []
    def fake_get(url, token):
        calls.append((url, token))
        return {'data': [{'id': 'synthetic-live-model'}]}, {}
    monkeypatch.setattr(catalog, 'get_json', fake_get)
    target = tmp_path / 'public-catalog.json'
    assert catalog.main(['--providers', 'llm7', '--output', str(target)]) == 0
    doc = json.loads(target.read_text())
    assert calls == [('https://api.llm7.io/v1/models', None)]
    assert doc['provider_observations']['llm7']['secret_env_resolved'] is None
    assert doc['provider_observations']['llm7']['catalog_authentication'] == 'documented_public_get'
    assert doc['models'][0]['pricing_classification'] == 'unknown'
