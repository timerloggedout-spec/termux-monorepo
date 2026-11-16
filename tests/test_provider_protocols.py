"""Offline protocol and production wiring contracts for specialized providers."""
import json
import pytest

from llm_api_hub.server import provider_protocols as p
from llm_api_hub.server import research_providers as runtime
from scripts import provider_catalog_protocols as catalog
from scripts import provider_model_catalog as production_catalog


def test_cloudflare_url_is_fixed_and_account_id_validated():
    account = 'a' * 32
    assert p.cloudflare_chat_url(account) == f'https://api.cloudflare.com/client/v4/accounts/{account}/ai/v1/chat/completions'
    for bad in ('', 'a' * 31, '../' + 'a' * 32, None, 'https://other-host.invalid'):
        with pytest.raises(p.ProtocolError, match='invalid_account_id'):
            p.cloudflare_chat_url(bad)


def test_cohere_request_and_response_normalization():
    req = p.build_chat_request('cohere', 'command-a-03-2025', {
        'model': 'command-a-03-2025', 'messages': [{'role': 'user', 'content': 'hi'}],
        'stream': False, 'temperature': 0.2, 'irrelevant': 'discard', 'top_p': 0.9, 'stop': 'END',
    })
    assert req['model'] == 'command-a-03-2025'
    assert req['p'] == 0.9 and req['stop_sequences'] == ['END'] and req['stream'] is False
    assert 'irrelevant' not in req
    got = p.normalize_chat_response('cohere', {'id': 'x', 'finish_reason': 'COMPLETE',
        'message': {'content': [{'type': 'text', 'text': 'hello'}]}}, 'command-a-03-2025')
    assert got['choices'][0]['message']['content'] == 'hello'
    assert got['choices'][0]['finish_reason'] == 'stop'


def test_actual_complete_wires_cohere_translation_and_cloudflare_account(monkeypatch):
    monkeypatch.setattr(runtime, 'authorize', lambda *_: 'synthetic-token')
    calls = []
    def post(url, payload, key, timeout, **kw):
        calls.append((url, payload, kw))
        return {'choices': [{'message': {'content': 'ok'}}]}
    monkeypatch.setattr(runtime, 'post_json', post)
    payload = {'model': 'command-a-03-2025', 'messages': [{'role': 'user', 'content': 'hi'}], 'top_p': 0.8}
    runtime.complete('cohere', payload['model'], payload, 1)
    assert calls[-1][0] == 'https://api.cohere.com/v2/chat'
    assert calls[-1][1]['p'] == 0.8 and calls[-1][2]['response_provider'] == 'cohere'
    monkeypatch.setenv('CLOUDFLARE_ACCOUNT_ID', 'a' * 32)
    payload = {'model': '@cf/meta/model', 'messages': [{'role': 'user', 'content': 'hi'}]}
    runtime.complete('cloudflare', payload['model'], payload, 1)
    assert calls[-1][0].endswith('/' + 'a' * 32 + '/ai/v1/chat/completions')
    assert calls[-1][1]['model'] == '@cf/meta/model'


def test_transport_normalizes_native_cohere_json(monkeypatch):
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, _limit): return json.dumps({'message': {'content': [{'type': 'text', 'text': 'ok'}]}}).encode()
    class Opener:
        def open(self, _req, timeout): return Response()
    monkeypatch.setattr(runtime.urllib.request, 'build_opener', lambda *_: Opener())
    got = runtime.post_json('https://api.cohere.com/v2/chat', {}, 'synthetic', 1, response_provider='cohere', model='exact')
    assert got['choices'][0]['message']['content'] == 'ok' and got['model'] == 'exact'


def test_cohere_catalog_follows_fixed_url_pages_without_token_leak(monkeypatch):
    urls = []
    def get(url, token):
        urls.append(url)
        assert token == 'synthetic'
        return ({'models': [{'name': 'command-first'}], 'next_page_token': 'a/b?x=1'} if len(urls) == 1 else {'models': [{'name': 'command-second'}]}), {}
    monkeypatch.setattr(production_catalog, 'get_json', get)
    rows, _ = production_catalog.poll('cohere', 'synthetic')
    assert [r['id'] for r in rows] == ['command-first', 'command-second']
    assert all(url.startswith('https://api.cohere.com/v1/models?') for url in urls)
    assert 'page_token=a%2Fb%3Fx%3D1' in urls[1]
    assert all('synthetic' not in url for url in urls)


def test_catalog_fixed_urls_preserve_cloudflare_model_ids():
    account = '0' * 32
    assert catalog.endpoint('cloudflare', account).endswith(f'accounts/{account}/ai/models/search')
    assert catalog.endpoint('ollama') == 'https://ollama.com/api/tags'
    rows = catalog.normalize_models('ollama', {'models': [{'name': 'gpt-oss:20b'}]})
    assert rows[0]['id'] == 'gpt-oss:20b' and rows[0]['pricing_classification'] == 'unknown'
    rows = catalog.normalize_models('cloudflare', {'data': [{'id': '@cf/meta/model', 'name': 'Display Name'}]})
    assert rows[0]['id'] == '@cf/meta/model'


def test_catalog_repeated_pagination_fails_closed():
    def get(*_): return {'models': [{'name': 'exact'}], 'next_page_token': 'repeat'}, {}
    with pytest.raises(ValueError, match='invalid_pagination'):
        catalog.poll('cohere', 'synthetic', get)


def test_cloudflare_pagination_is_bounded_and_marketplace_format():
    urls = []
    def get(url, _token):
        urls.append(url)
        count = 100 if len(urls) == 1 else 1
        return {'data': [{'id': f'@cf/meta/model-{len(urls)}-{i}'} for i in range(count)]}, {}
    rows, _ = catalog.poll('cloudflare', 'synthetic', get, 'a' * 32)
    assert len(rows) == 101
    assert 'format=openrouter' in urls[0] and 'page=2' in urls[1]


@pytest.mark.parametrize('provider,body', [
    ('cloudflare', {'success': False, 'errors': [{'message': 'SECRET RESPONSE BODY'}]}),
    ('cohere', {'message': {'content': 'malformed SECRET RESPONSE BODY'}}),
    ('ollama', {'error': 'SECRET RESPONSE BODY'}),
])
def test_bad_response_errors_do_not_reflect_upstream_body(provider, body):
    with pytest.raises(p.ProtocolError) as exc:
        p.normalize_chat_response(provider, body, 'm')
    assert 'SECRET' not in str(exc.value)
