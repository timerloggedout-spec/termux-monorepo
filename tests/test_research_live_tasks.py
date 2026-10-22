"""Synthetic safety fixtures only; never used as live experiment observations."""
import datetime as dt
import json
from argparse import Namespace

import pytest
from scripts.model_selection_market import live_task_experiment as mod


def counter(used=2, limit=20, remaining=18):
    return {'data': {'free_model_daily_requests': {'used': used, 'limit': limit, 'remaining': remaining}}}


def test_quota_counter_strict_and_never_converts_credit_balance_to_requests():
    assert mod.parse_daily_counter(counter())['remaining'] == 18
    for bad in ({}, {'data': {'limit_remaining': 100}}, counter(True), counter(2, 20, 17), counter(0, 0, 0)):
        with pytest.raises(ValueError):
            mod.parse_daily_counter(bad)


def test_task_status_is_operational_triage_not_patch_success():
    pr = {'state': 'open', 'merged': False, 'draft': False}
    assert mod.classify_task(pr, ['src/a.py']) == ('OPEN_PATCH', 'review')
    assert mod.classify_task(pr, ['src/a.py'], True) == ('OPEN_PATCH', 'review')
    assert mod.classify_task(pr, ['stake.txt']) == ('OPEN_STAKE', 'implement')
    assert mod.classify_task(pr, ['stake.txt'], True) == ('OPEN_UNVERIFIED', 'inspect')
    assert mod.classify_task({**pr, 'draft': True}, ['src/a.py']) == ('OPEN_DRAFT', 'wait')
    assert mod.classify_task({**pr, 'merged': True}, []) == ('MERGED', 'observe')
    assert mod.classify_task({**pr, 'state': 'closed'}, []) == ('CLOSED_UNMERGED', 'stop')


def test_claim_requires_head_bound_unambiguous_json_including_serialized_wrappers():
    claim = {'head_sha': 'a' * 40, 'status': 'OPEN_PATCH', 'next_action': 'review'}
    text = json.dumps(claim)
    assert mod.parse_claim('answer: ' + text) == claim
    assert mod.parse_claim(json.dumps({'result': text})) == claim
    assert mod.parse_claim(text + json.dumps({**claim, 'head_sha': 'b' * 40})) is None
    assert mod.parse_claim(json.dumps({**claim, 'head_sha': 'abc'})) is None
    assert mod.parse_claim(json.dumps({**claim, 'status': 'SUCCESS'})) is None


def test_catalog_requires_fresh_explicit_free_variant_and_every_price_zero(tmp_path):
    rows = [
        {'provider': 'openrouter', 'id': 'paid:free', 'pricing_classification': 'paid', 'pricing': {'prompt': '0', 'completion': '0'}},
        {'provider': 'openrouter', 'id': 'vendor/ok:free', 'pricing_classification': 'free_zero_price', 'pricing': {'prompt': '0', 'completion': '0'}},
        {'provider': 'openrouter', 'id': 'fee:free', 'pricing_classification': 'free_zero_price', 'pricing': {'prompt': '0', 'completion': '0', 'request': '1'}},
        {'provider': 'openrouter', 'id': 'not-free', 'pricing_classification': 'free_zero_price', 'pricing': {'prompt': '0', 'completion': '0'}},
    ]
    path = tmp_path / 'catalog.json'
    mod.write_json(path, {'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'models': rows})
    assert mod.get_free_catalog(path) == 'openrouter/vendor/ok:free'
    for model in ('paid:free', 'fee:free', 'not-free'):
        with pytest.raises(ValueError):
            mod.get_free_catalog(path, model)
    mod.write_json(path, {'observed_at': '2020-01-01T00:00:00Z', 'models': rows})
    with pytest.raises(ValueError):
        mod.get_free_catalog(path)


def test_private_github_source_is_rejected_before_file_metadata_or_inference(monkeypatch):
    calls = []
    def read(command, endpoint):
        calls.append(endpoint)
        return {'base': {'repo': {'private': True}}}
    monkeypatch.setattr(mod, 'gh_json', read)
    with pytest.raises(ValueError, match='public_source_not_verified'):
        mod.safe_snapshot('https://github.com/example/private/pull/1', 'gh')
    assert len(calls) == 1
    assert not mod.valid_pr_url('https://github.com/evil/repo/pull/1?token=secret')
    assert not mod.valid_pr_url('https://github.com.evil.test/x/y/pull/1')


def test_canonical_publication_uses_real_schema_and_drops_account_payload(tmp_path):
    private = tmp_path / 'private'
    private.mkdir()
    payload = counter()
    payload['data']['label'] = 'fake-sensitive-key-label'
    model = 'openrouter/vendor/model:free'
    mod.publish_counter(private, payload, model)
    path = private / 'observations.json'
    text = path.read_text()
    assert 'fake-sensitive-key-label' not in text
    record = json.loads(text)['records'][0]
    assert record['remaining'] == 18 and record['model'] == model
    assert record['scope'] == 'account:free_model_daily_requests'
    assert path.stat().st_mode & 0o777 == 0o600


def test_missing_secret_blocks_actual_runner_before_provider_or_hub_calls(tmp_path, monkeypatch):
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    tasks = []
    for index, context in enumerate(mod.CONTEXTS):
        facts = {'url': f'https://github.com/example/repo/pull/{index + 1}', 'head_sha': 'a' * 40,
                 'state': 'open', 'merged': False, 'draft': False, 'filepaths': ['src/a.py'], 'files_truncated': False}
        tasks.append({'context': context, 'facts': facts, 'snapshot_sha256': mod.digest(facts)})
    monkeypatch.setattr(mod, 'collect_tasks', lambda *a: (tasks, []))
    monkeypatch.setattr(mod, 'get_free_catalog', lambda *a: 'openrouter/fake:free')
    def forbidden(*a, **k):
        raise AssertionError('No provider or hub request allowed without credentials')
    monkeypatch.setattr(mod.urllib.request, 'build_opener', forbidden)
    monkeypatch.setattr(mod, 'execute_pilot', forbidden)
    catalog = tmp_path / 'catalog.json'
    catalog.write_text('{}')
    args = Namespace(output=str(tmp_path / 'out'), gh_command='gh', pairs_per_context=1,
                     exclude_pr='1541', mode='pilot', catalog=str(catalog), model=None)
    assert mod.run(args) == 0
    result = json.loads((tmp_path / 'out/evaluation.json').read_text())
    assert result['status'] == 'BLOCKED'
    assert result['reason'] == 'provider_credential_missing'
    assert result['inference_requests_dispatched'] == 0


def test_canonical_hub_client_explicit_completion_bound(monkeypatch):
    from llm_api_hub.clients import openai_compat as client
    observed = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'{"choices":[]}'
    def open_request(request, **kwargs):
        observed.append(json.loads(request.data))
        return Response()
    monkeypatch.setattr(client.urllib.request, 'urlopen', open_request)
    client.chat_completions([{'role': 'user', 'content': 'fake safety fixture'}], max_tokens=256)
    assert observed[0]['max_tokens'] == 256
    with pytest.raises(ValueError):
        client.chat_completions([], max_tokens=True)


def test_end_to_end_offline_pilot_uses_real_running_hub_quota_research_and_paper_journal(tmp_path, monkeypatch):
    """Synthetic public-shaped fixtures only; not production tasks or source-corpus evidence."""
    import csv
    import io

    from llm_api_hub.server import app as hub
    from src.advanced_research_adapter import PIN

    fake_counter = {'data': {'free_model_daily_requests': {'used': 0, 'limit': 1000, 'remaining': 1000}}}
    model = 'openrouter/fixture-public-model:free'
    fake_candidate_sha = 'c' * 40
    tasks = []
    for index, context in enumerate(mod.CONTEXTS):
        # Deliberately public-URL-shaped, but wholly fabricated fixtures; never fetched.
        facts = {
            'url': f'https://github.com/fake-public-fixture-{index}/synthetic-repo/pull/{index + 41}',
            'title': 'Synthetic fixture PR; no real source corpus',
            'state': 'open', 'merged': False, 'draft': False,
            'head_sha': 'a' * 40, 'changed_files': 1,
            'filepaths': ['src/synthetic_fixture.py'], 'files_truncated': False,
        }
        tasks.append({'context': context, 'facts': facts, 'snapshot_sha256': mod.digest(facts)})

    monkeypatch.setenv('OPENROUTER_API_KEY', 'fake-fixture-key-never-used-upstream')
    monkeypatch.setenv('LLM_API_HUB_KEY', 'outer-fixture-key-restored-by-monkeypatch')
    monkeypatch.setattr(mod, 'collect_tasks', lambda *args: (tasks, []))
    real_check_output = mod.subprocess.check_output
    def fixture_revision(command, **kwargs):
        if command == ['git', 'rev-parse', 'HEAD']:
            return fake_candidate_sha + ('\n' if kwargs.get('text') else '').encode() if not kwargs.get('text') else fake_candidate_sha + '\n'
        return real_check_output(command, **kwargs)
    monkeypatch.setattr(mod.subprocess, 'check_output', fixture_revision)
    monkeypatch.setattr(mod, 'fetch_counter', lambda key: (fake_counter, mod.parse_daily_counter(fake_counter)))
    monkeypatch.setattr(mod, 'throttle', lambda private: None)
    # Only replace the actual provider boundary. Keep the app, HTTP client/socket,
    # admission controller, reservation SQLite, and pinned child runtime real.
    def fake_completion(provider, request):
        system = str(request.messages[0].content)
        if system.startswith('Director'):
            answer = json.dumps({'queries': ['synthetic bounded fixture query']})
        else:
            answer = json.dumps({'head_sha': 'a' * 40, 'status': 'OPEN_PATCH', 'next_action': 'review'})
        return hub.completion_response(request.model, answer, {'total_tokens': 7})
    monkeypatch.setattr(hub.runtime, 'complete_upstream', fake_completion)

    private = tmp_path / 'private-quota'
    private.mkdir(mode=0o700)
    private.chmod(0o700)
    mod.publish_counter(private, fake_counter, model)
    output = tmp_path / 'pilot-output'
    output.mkdir()
    catalog = tmp_path / 'fixture-catalog.json'
    catalog.write_text(json.dumps({
        'observed_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'models': [{'provider': 'openrouter', 'id': 'fixture-public-model:free',
                    'pricing_classification': 'free_zero_price',
                    'pricing': {'prompt': '0', 'completion': '0'}}],
    }))
    # Legacy entrypoint configuration is also made local before the runner applies
    # its own events.jsonl destination; monkeypatch restores this environment later.
    monkeypatch.setenv('TERMUX_TELEMETRY_LOG', str(output / 'legacy-events.jsonl'))
    monkeypatch.setenv('GITHUB_RUN_ID', 'synthetic-offline-run')
    args = Namespace(output=str(output), gh_command='unused-never-called', pairs_per_context=1,
                     exclude_pr='1541', mode='pilot', catalog=str(catalog), model=None)
    assert mod.run(args) == 0

    result = json.loads((output / 'evaluation.json').read_text())
    assert result['status'] == 'SCREENING_COMPLETE'
    assert result['research_source_revision'] == PIN
    assert [item['outcome'] for item in result['attempts']] == ['PASS'] * 4
    assert {item['arm'] for item in result['attempts']} == {'control', 'candidate'}
    assert result['inference_requests_dispatched'] == 3 * len(tasks)
    assert result['unsettled_sent_requests'] == 0
    assert result['request_reservation_states'] == {'charged': 6}

    plan_record = json.loads((output / 'plan.json').read_text())
    assert plan_record['plan']['screening'] is True
    assert plan_record['plan']['planned_looks'] == [1] and plan_record['plan']['sample_cap'] == 1
    assert plan_record['plan']['control_arm'] == 'control'
    assert plan_record['plan']['candidate_arm'] == 'candidate'
    assert plan_record['candidate_sha'] == fake_candidate_sha

    evidence_path = output / '3l0-execution.jsonl'
    evidence = [json.loads(line) for line in evidence_path.read_text().splitlines()]
    assert len(evidence) == 6
    assert all(sample['confidence'] == 0 for sample in evidence)
    assert all(sample['provenance']['task_outcome'] == 'UNKNOWN' for sample in evidence)
    journal_path = output / 'paper-market.jsonl'
    snapshot = mod.json.loads((output / 'paper-market.json').read_text())
    from scripts.model_selection_market.market import MarketGraph
    from scripts.model_selection_market.paper_wallet import validate_csv
    replay = MarketGraph(journal=str(journal_path)).snapshot()
    assert replay == snapshot
    with (output / 'paper-market.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    account_rows = [row for row in rows if row['record_type'] == 'account']
    assert account_rows and all(int(row['balance']) >= 0 and int(row['reserved']) >= 0 and int(row['available']) >= 0 for row in account_rows)
    assert all(int(row['balance']) == int(row['reserved']) + int(row['available']) for row in account_rows)
    with (output / 'paper-market.csv').open(newline='') as stream:
        assert validate_csv(io.StringIO(stream.read()), replay)
    # The runner removes its private reservation DB after the pilot; persisted
    # returned metrics prove all dispatched reservations were charged and settled.
    assert result['request_reservation_states'] == {'charged': 6}
    assert result['unsettled_sent_requests'] == 0
    telemetry_text = (output / 'events.jsonl').read_text()
    assert 'synthetic bounded fixture query' not in telemetry_text
    assert 'synthetic_fixture.py' not in telemetry_text
