import io
import json
from unittest.mock import patch
import urllib.error

from scripts.ops import provider_secret_inventory as inventory


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
    assert result['status'] == 'observed'
    assert result['names'] == ['GROQ_API_KEY', 'HF_TOKEN']
    assert 'never-serialize-me' not in json.dumps(result)
    assert 'synthetic-test-token' not in json.dumps(result)


def test_failure_does_not_serialize_upstream_body_or_partial_names():
    error = urllib.error.HTTPError(inventory.API, 403, 'sensitive upstream text', {}, None)
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        build.return_value.open.side_effect = error
        result = inventory.observe('synthetic-test-token')
    assert result['reason'] == 'http_status_403'
    assert 'sensitive' not in json.dumps(result)
    assert result['names'] == []


def test_invalid_names_fail_closed():
    with patch.object(inventory.urllib.request, 'build_opener') as build:
        build.return_value.open.return_value = Reply(b'{"secrets":[{"name":"not a name"}]}')
        result = inventory.observe('synthetic-test-token')
    assert result['status'] == 'unavailable'
    assert result['names'] == []


def test_cli_writes_complete_safe_observation(tmp_path, monkeypatch):
    monkeypatch.delenv('GH_TOKEN', raising=False)
    output = tmp_path / 'inventory.json'
    assert inventory.main(['--output', str(output)]) == 0
    assert json.loads(output.read_text())['reason'] == 'missing_inventory_credential'
