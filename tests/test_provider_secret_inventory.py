import io
import json
from unittest.mock import patch
import urllib.error

from scripts.ops import provider_secret_inventory as inventory
from scripts import provider_model_catalog


class Reply(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_missing_token_is_explicit():
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        result = inventory.observe(None)
    assert result['reason'] == 'missing_inventory_credential'
    assert result['names'] == []
    assert 'provider_credentials' not in result
    build.assert_not_called()


def test_only_names_are_serialized_and_no_redirects_are_used():
    payload = {'secrets': [{'name': 'HF_TOKEN', 'value': 'never-serialize-me'}, {'name': 'GROQ_API_KEY'}]}
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        build.return_value.open.return_value = Reply(json.dumps(payload).encode())
        result = inventory.observe('synthetic-test-token')
        request = build.return_value.open.call_args.args[0]
        assert request.full_url.startswith(inventory.API + '?')
        assert request.headers['Authorization'] == 'Bearer synthetic-test-token'
        assert isinstance(build.call_args.args[0], type)
    serialized = json.dumps(result)
    assert result['status'] == 'observed'
    assert result['names'] == ['GROQ_API_KEY', 'HF_TOKEN']
    assert 'never-serialize-me' not in serialized
    assert 'synthetic-test-token' not in serialized
    assert 'HF_TOKEN' in json.dumps(result['provider_credentials'])
    assert 'unmatched' not in serialized


def test_provider_credentials_canonical_and_alias_mappings():
    entries = {row['provider']: row for row in inventory.provider_credentials([
        'GEMINI_API_KEY', 'OPENROUTER_API_KEY', 'FELO_AI_API',
        'HF_API_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'OPERATOR_TOKEN', 'DEEPSEEK_API_KEY',
    ])}
    for provider, canonical in {
        'gemini': 'GEMINI_API_KEY', 'openrouter': 'OPENROUTER_API_KEY', 'felo': 'FELO_AI_API',
    }.items():
        assert entries[provider]['environment_variable'] == canonical
        assert entries[provider]['configured_secret_names'] == [canonical]
        assert entries[provider]['status'] == 'configured_entitlement_unverified'
    hf = entries['huggingface']
    assert hf['environment_variable'] == 'HUGGINGFACE_TOKEN'
    assert hf['configured_secret_names'] == ['HUGGING_FACE_HUB_TOKEN', 'HF_API_TOKEN']
    assert entries['groq']['environment_variable'] == 'GROQ_API_KEY'
    assert entries['groq']['configured_secret_names'] == []
    assert entries['groq']['status'] == 'missing_secret'
    assert all(row['provider'] not in {'operator', 'deepseek'} for row in entries.values())
    assert all('OPERATOR_TOKEN' not in row['configured_secret_names'] and
               'DEEPSEEK_API_KEY' not in row['configured_secret_names'] for row in entries.values())


def test_runtime_catalog_secret_alias_parity_except_openrouter_legacy():
    # Runtime availability probe retains its own OpenRouter canonical-only path.
    from scripts import provider_availability_probe
    runtime_aliases = {
        'huggingface': provider_availability_probe.HF_TOKEN_ALIASES,
        'openrouter': ('OPENROUTER_API_KEY',),
    }
    for provider, names in runtime_aliases.items():
        catalog_names = provider_model_catalog.RESOLVE_SECRET_NAMES[provider]
        if provider == 'openrouter':
            assert catalog_names == names
        else:
            assert tuple(names) == tuple(catalog_names)


def test_failure_does_not_serialize_upstream_body_or_partial_names():
    error = urllib.error.HTTPError(inventory.API, 403, 'sensitive upstream text', {}, None)
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        build.return_value.open.side_effect = error
        result = inventory.observe('synthetic-test-token')
    assert result['reason'] == 'http_status_403'
    assert 'sensitive' not in json.dumps(result)
    assert result['names'] == []
    assert 'provider_credentials' not in result


def test_invalid_names_fail_closed():
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        build.return_value.open.return_value = Reply(b'{"secrets":[{"name":"not a name"}]}')
        result = inventory.observe('synthetic-test-token')
    assert result['status'] == 'unavailable'
    assert result['names'] == []
    assert 'provider_credentials' not in result


def test_cli_writes_complete_safe_observation(tmp_path, monkeypatch):
    monkeypatch.delenv('GH_TOKEN', raising=False)
    output = tmp_path / 'inventory.json'
    assert inventory.main(['--output', str(output)]) == 0
    result = json.loads(output.read_text())
    assert result['reason'] == 'missing_inventory_credential'
    assert set(result) == {'schema', 'repository', 'observed_at', 'status', 'reason', 'names'}
