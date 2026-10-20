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
    assert report['summary']['candidates'] == len(source['model_candidates']) == 160
    assert report['sources'] == source['sources']
    assert len(report['research_sha256']) == 64
    assert all(row['runtime_eligible'] is False and row['quota_remaining'] is None for row in report['candidates'])
    assert sum(report['summary']['by_status'].values()) == 160
    assert 'adapter_not_implemented' in report['summary']['by_status']
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
    review_step = next(s for s in steps if 'GH_TOKEN' in s.get('env', {}))
    assert review_step['env'] == {'GH_TOKEN': '${{ github.token }}'}
    assert review_step['run'].count('--paginate --slurp') == 4
    assert 'matrix-review.json' in review_step['run']
    for step in steps:
        assert 'write' not in str(step.get('env', {})).lower()
    assert 'secrets: inherit' not in path.read_text()
    assert 'pull_request_target' not in path.read_text()
