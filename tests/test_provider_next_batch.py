"""MSM-016: new providers cannot inherit administrator credentials or admission."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from scripts import provider_model_catalog as catalog
from llm_api_hub.server import research_providers as runtime


@pytest.mark.parametrize('provider,secret,body,auth', [
    ('modelscope', 'MODELSCOPE_TOKEN', {'object': 'list', 'data': [{'id': 'owner/Exact-Model'}]}, 'observed_public_get'),
    ('ovhcloud', 'OVHCLOUD_API_KEY', {'data': [{'id': 'gpt-oss-20b', 'available': False}]}, 'documented_public_get'),
])
def test_public_catalog_never_forwards_inference_key_or_claims_account_access(monkeypatch, tmp_path, provider, secret, body, auth):
    monkeypatch.setenv(secret, 'synthetic-inference-secret-do-not-forward')
    monkeypatch.setenv('GH_TOKEN', 'synthetic-admin-secret-do-not-forward')
    calls = []
    def fake(url, token):
        calls.append((url, token))
        return body, {}
    monkeypatch.setattr(catalog, 'get_json', fake)
    out = tmp_path / 'catalog.json'
    assert catalog.main(['--providers', provider, '--output', str(out)]) == 0
    assert calls == [(catalog.ENDPOINTS[provider], None)]
    doc = json.loads(out.read_text())
    observed = doc['provider_observations'][provider]
    assert observed['catalog_authentication'] == auth and observed['secret_env_resolved'] is None
    assert doc['models'][0]['pricing_classification'] == 'unknown'
    assert 'synthetic-' not in out.read_text()
    if provider == 'modelscope':
        assert observed['catalog_contract_source'] == 'provider_runtime_observation'
    else:
        assert doc['models'][0]['active'] is False


@pytest.mark.parametrize('provider,valid', [('ovhcloud', True), ('sambanova', False)])
def test_only_reviewed_array_catalog_is_wrapped(monkeypatch, provider, valid):
    class Response:
        headers = {}
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, _size): return b'[{"id":"exact","available":true}]'
    class Opener:
        def open(self, request, timeout):
            assert not request.has_header('Authorization')
            return Response()
    monkeypatch.setattr(catalog.urllib.request, 'build_opener', lambda *_: Opener())
    if valid:
        payload, _ = catalog._request(catalog.ENDPOINTS[provider])
        assert payload['data'][0]['id'] == 'exact'
    else:
        with pytest.raises(ValueError, match='invalid_response_shape'):
            catalog._request(catalog.ENDPOINTS[provider])


def test_sambanova_official_catalog_preserves_exact_metadata(monkeypatch):
    payload = {'object': 'list', 'data': [{'id': 'Meta-Llama-3.3-70B-Instruct', 'context_length': 131072,
                'max_completion_tokens': 8192, 'pricing': {'prompt': 0.000001, 'completion': 0.000002}}]}
    calls = []
    def fake(url, token):
        calls.append((url, token))
        return payload, {}
    monkeypatch.setattr(catalog, 'get_json', fake)
    rows, _ = catalog.poll('sambanova', 'synthetic-provider-key')
    assert calls == [('https://api.sambanova.ai/v1/models', 'synthetic-provider-key')]
    assert rows[0]['id'] == 'Meta-Llama-3.3-70B-Instruct'
    assert rows[0]['max_output_tokens'] == 8192 and rows[0]['context_length'] == 131072
    assert rows[0]['pricing_classification'] == 'paid'  # Catalog price does not establish a free account.


def test_sambanova_requires_separate_provider_key_even_with_admin_access(monkeypatch, tmp_path):
    model = 'Meta-Llama-3.3-70B-Instruct'
    path = tmp_path / 'synthetic-admission.json'
    path.write_text(json.dumps({'schema': runtime.SCHEMA, 'entries': [{
        'provider': 'sambanova', 'model': model, 'free_account_verified': True,
        'terms_accepted': True, 'data_class': 'public',
        'expires_at': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
    }]}))
    monkeypatch.setenv('LLM_API_HUB_PROVIDER_POLICY', str(path))
    monkeypatch.setenv('GH_TOKEN', 'synthetic-administrator-key')
    monkeypatch.delenv('SAMBANOVA_API_KEY', raising=False)
    with pytest.raises(runtime.ProviderAdmissionError) as error:
        runtime.authorize('sambanova', model)
    assert error.value.status == 503
    monkeypatch.setenv('SAMBANOVA_API_KEY', 'synthetic-provider-key')
    calls = []
    def fake(url, payload, key, timeout):
        calls.append((url, key))
        return {'choices': [{'message': {'content': 'synthetic reply'}}]}
    monkeypatch.setattr(runtime, 'post_json', fake)
    runtime.complete('sambanova', model, {'model': model, 'messages': [{'role': 'user', 'content': 'public synthetic'}]}, 1)
    assert calls == [('https://api.sambanova.ai/v1/chat/completions', 'synthetic-provider-key')]
