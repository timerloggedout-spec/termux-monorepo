"""Real checked-in research and active workflow contracts for MSM-010."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
import yaml

from scripts.model_selection_market import provider_batch as batch

ROOT = Path(__file__).resolve().parents[1]


def research():
    return json.loads((ROOT / 'data/model-selection-market/provider-recon.json').read_text())


def catalog():
    return {'schema': 'provider-model-catalog/v5', 'models': [], 'provider_observations': {}}


def test_every_real_research_candidate_has_a_disposition_without_activation():
    source = research()
    report = batch.reconcile(source, catalog())
    assert report['summary']['candidates'] == len(source['model_candidates']) == 195
    assert report['sources'] == source['sources']
    assert len(report['research_sha256']) == 64
    assert all(row['runtime_eligible'] is False and row['quota_remaining'] is None for row in report['candidates'])
    assert sum(report['summary']['by_status'].values()) == 195
    assert 'adapter_not_implemented' not in report['summary']['by_status']
    assert report['summary']['by_status']['catalog_adapter_not_implemented'] == 3
    assert batch.reconcile(deepcopy(source), catalog()) == report


def test_exact_identity_catalog_observation_is_not_free_entitlement():
    source = research()
    candidate = next(c for c in source['model_candidates'] if c['provider_key'] == 'groq' and c.get('model_id'))
    live = catalog()
    live['provider_observations']['groq'] = {}
    live['models'] = [{'provider': 'groq', 'id': candidate['model_id'], 'raw_source': 'groq:/v1/models', 'pricing_classification': 'unknown'}]
    report = batch.reconcile(source, live)
    matched = next(c for c in report['candidates'] if c['provider_key'] == 'groq' and c['model_id'] == candidate['model_id'])
    assert matched['status'] == 'observed_in_catalog'
    assert matched['native_chat_adapter'] is True
    assert matched['runtime_eligible'] is False
    assert matched['pricing_classification'] == 'unknown'
    live['models'][0]['id'] += '-similar'
    report = batch.reconcile(source, live)
    assert not any(c['status'] == 'observed_in_catalog' for c in report['candidates'])


def test_documented_model_injection_does_not_become_live_catalog_evidence():
    live = catalog()
    live['provider_observations']['groq'] = {}
    candidate = next(c for c in research()['model_candidates'] if c['provider_key'] == 'groq')
    live['models'] = [{'provider': 'groq', 'id': candidate['model_id'], 'raw_source': 'groq:/v1/models + documented-model-page'}]
    assert not any(c['status'] == 'observed_in_catalog' for c in batch.reconcile(research(), live)['candidates'])


@pytest.mark.parametrize('mutation', ['schema', 'duplicate', 'runtime', 'catalog'])
def test_malformed_input_fails_closed(mutation):
    source, live = research(), catalog()
    if mutation == 'schema': source['schema_version'] = 'unknown'
    if mutation == 'duplicate': source['model_candidates'].append(source['model_candidates'][0])
    if mutation == 'runtime': source['model_candidates'][0]['runtime_eligible'] = True
    if mutation == 'catalog': live['models'] = [{'provider': 'groq', 'id': []}]
    with pytest.raises(ValueError):
        batch.reconcile(source, live)


def test_cli_invalid_input_does_not_replace_existing_output(tmp_path):
    src, cat, out = (tmp_path / name for name in ['source.json', 'catalog.json', 'out.json'])
    src.write_text(json.dumps(research()))
    cat.write_text(json.dumps(catalog()))
    assert batch.main(['--research', str(src), '--catalog', str(cat), '--output', str(out)]) == 0
    previous = out.read_bytes()
    cat.write_text('{}')
    with pytest.raises(ValueError):
        batch.main(['--research', str(src), '--catalog', str(cat), '--output', str(out)])
    assert out.read_bytes() == previous


def test_production_observation_uses_trusted_master_and_separate_secret_scopes():
    path = ROOT / '.github/workflows/provider-batch.yml'
    workflow = yaml.safe_load(path.read_text())
    # YAML 1.1 parses the GitHub key `on` as True.
    triggers = workflow.get('on', workflow.get(True))
    assert set(triggers) == {'workflow_dispatch', 'pull_request', 'push'}
    assert workflow['permissions'] == {}
    jobs = workflow['jobs']
    assert jobs['contracts']['permissions'] == {'contents': 'read'}
    assert all('env' not in step for step in jobs['contracts']['steps'])
    observe = jobs['observe']
    assert "github.event_name == 'workflow_dispatch'" in observe['if']
    assert 'github.event.repository.default_branch' in observe['if']
    assert observe['permissions'] == {'contents': 'read', 'pull-requests': 'read'}
    steps = observe['steps']
    assert steps[0]['with']['ref'] == '${{ github.event.repository.default_branch }}'
    assert steps[0]['with']['persist-credentials'] is False
    provider_step = next(s for s in steps if 'GROQ_API_KEY' in s.get('env', {}))
    assert 'GH_TOKEN' not in provider_step['env']
    assert 'chat/completions' not in provider_step['run']
    assert 'coverage.json' in provider_step['run']
    inventory_step = next(s for s in steps if 'provider_secret_inventory.py' in s.get('run', ''))
    assert set(inventory_step['env']) == {'GH_TOKEN'}
    assert 'secrets.OPERATOR' in inventory_step['env']['GH_TOKEN']
    assert 'credential-names.json' in inventory_step['run']
    assert 'CEREBRAS_API_KEY' in provider_step['env']
    review_step = next(s for s in steps if 'matrix-review.json' in s.get('run', ''))
    assert set(review_step['env']) == {'GH_TOKEN', 'FEEDBACK_AUTH_CONTEXT'}
    assert 'secrets.OPERATOR' in review_step['env']['GH_TOKEN']
    assert review_step['env']['GH_TOKEN'].endswith('|| github.token }}')
    assert 'github-feedback-auth.json' in review_step['run']
    assert 'repository-permissions.json' in review_step['run']
    assert 'gh api rate_limit' in review_step['run']
    assert review_step['run'].count('--paginate --slurp') == 4
    assert 'matrix-review.json' in review_step['run']
    for step in steps:
        assert 'write' not in str(step.get('env', {})).lower()
    assert 'secrets: inherit' not in path.read_text()
    assert 'pull_request_target' not in path.read_text()


def test_per_source_denominators_do_not_count_provider_classes_as_models():
    summary = batch.reconcile(research(), catalog())['summary']['by_source']
    directory = summary['mnfst/awesome-free-llm-apis']
    assert directory['research_records'] == 123
    assert directory['individual_model_claims'] == 117
    assert directory['static_or_aggregate_references'] == 6
    assert directory['gated_native_chat_model_claims'] == 101
    assert directory['legacy_openrouter_model_claims'] == 16
    assert len(directory['catalog_adapter_families']) == 15
    assert len(directory['chat_transport_families']) == 16
    proxy = summary['tashfeenahmed/freellmapi']
    assert proxy['research_records'] == 72
    assert proxy['individual_model_claims'] == 0
    assert proxy['static_or_aggregate_references'] == 72
    assert proxy['chat_transport_families'] == sorted(set(batch.SOURCE_PROVIDER_MAP['tashfeenahmed/freellmapi'].values()))
    assert proxy['runtime_eligible'] == directory['runtime_eligible'] == 0


def test_reconciliation_native_provider_registry_matches_real_dispatch():
    from llm_api_hub.server.research_providers import ENDPOINTS
    assert batch.NATIVE_CHAT_PROVIDERS == frozenset(ENDPOINTS)


def test_keyless_research_observation_is_explicit_and_has_no_secret_environment():
    import yaml
    workflow = yaml.safe_load((ROOT / '.github/workflows/provider-batch.yml').read_text())
    events = workflow.get('on', workflow.get(True))
    assert events['workflow_dispatch']['inputs']['observe_public_research']['default'] is False
    step = next(s for s in workflow['jobs']['observe']['steps'] if 'public-research-service.json' in s.get('run', ''))
    assert step['if'] == 'inputs.observe_public_research'
    assert not step.get('env')
    assert '--source awesome-free-llm-apis' in step['run']
    assert 'GH_TOKEN' not in step['run'] and 'API_KEY' not in step['run']


def test_reviewed_freellmapi_aliases_do_not_execute_or_admit_services():
    source = research()
    template = next(c for c in source['model_candidates'] if c['source_repo'] == 'tashfeenahmed/freellmapi')
    source['model_candidates'] = [dict(template, provider_key=key, provider_name=key)
                                  for key in batch.SOURCE_PROVIDER_MAP['tashfeenahmed/freellmapi']]
    report = batch.reconcile(source, catalog())
    assert len(report['candidates']) == 23
    for row in report['candidates']:
        assert row['service_disposition'] == 'chat_transport_available'
        assert row['runtime_eligible'] is False and row['quota_remaining'] is None
        assert row['model_id'] is None
        assert row['status'] == 'not_an_individual_model'
    summary = report['summary']['by_source']['tashfeenahmed/freellmapi']
    assert summary['individual_model_claims'] == summary['observed_model_claims'] == 0
    assert summary['service_reference_coverage'] == {
        'total': 23, 'by_disposition': {'chat_transport_available': 23}}


def test_source_aliases_never_fuzzy_match_or_cross_key_namespaces():
    source = research()
    template = next(c for c in source['model_candidates'] if c['source_repo'] == 'tashfeenahmed/freellmapi')
    source['model_candidates'] = [dict(template, provider_key=key, provider_name=key)
                                  for key in ['zhipu', 'groq-proxy', 'custom', 'unknown', 'firecrawl']]
    report = batch.reconcile(source, catalog())
    rows = {r['provider_key']: r for r in report['candidates']}
    assert rows['custom']['native_provider'] is None
    assert rows['custom']['service_disposition'] == 'custom_configuration_placeholder'
    for key in ['zhipu', 'groq-proxy', 'unknown']:
        assert rows[key]['native_provider'] is None
        assert rows[key]['service_disposition'] == 'unmapped_service_reference'
    assert rows['firecrawl']['service_disposition'] == 'fixed_public_research_only'
    assert rows['firecrawl']['native_chat_adapter'] is False
    assert rows['firecrawl']['research_service_adapter'] == 'firecrawl_fixed_public_research'
    source['model_candidates'] = [dict(template, source_repo='mnfst/awesome-free-llm-apis',
                                       provider_key='google', provider_name='Google')]
    assert batch.reconcile(source, catalog())['candidates'][0]['native_provider'] is None


def test_service_gaps_remain_visible_instead_of_hiding_behind_non_model_status():
    report = batch.reconcile(research(), catalog())
    proxy = report['summary']['by_source']['tashfeenahmed/freellmapi']
    coverage = proxy['service_reference_coverage']
    assert coverage['total'] == proxy['static_or_aggregate_references']
    assert sum(coverage['by_disposition'].values()) == coverage['total']
    assert coverage['by_disposition']['unmapped_service_reference'] > 0
    assert coverage['by_disposition']['fixed_public_research_only'] == 1
    assert all('service_disposition' not in row for row in report['candidates']
               if row['model_key'] != 'provider-catalog')
