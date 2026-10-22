import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'antigravity'))
from telemetry import MAX_EVENT_BYTES, normalize, quota_snapshot, steering


class AdapterTests(unittest.TestCase):
    def run_events(self, *events):
        return normalize(map(json.dumps, events), run_id='invocation-1')

    def test_final_totals_not_added_to_steps(self):
        result = self.run_events(
            {'event': 'init', 'conversation_id': 'c1', 'init': {'model': 'test-model'}},
            {'event': 'step_update', 'step_update': {'usage': {'total_tokens': 8}}},
            {'event': 'result', 'result': {'status': 'SUCCESS', 'usage': {'total_tokens': 8}}})
        self.assertEqual(result['usage']['total_tokens'], 8)
        self.assertIsNone(result['usage']['input_tokens'])
        self.assertIsNone(result['cost_usd'])
        self.assertEqual(result['quota']['status'], 'unknown')

    def test_duplicate_result_not_counted_twice(self):
        event = {'event': 'result', 'result': {'usage': {'total_tokens': 3}}}
        self.assertEqual(self.run_events(event, event)['usage']['total_tokens'], 3)

    def test_incomplete_does_not_promote_steps(self):
        record = self.run_events({'event': 'step_update', 'step_update': {'usage': {'total_tokens': 9}}})
        self.assertEqual(record['status'], 'INCOMPLETE')
        self.assertIsNone(record['usage']['total_tokens'])

    def test_malformed_and_invalid_counts(self):
        record = normalize(['garbage', '[]', json.dumps({'event': 'result', 'result': {
            'usage': {'input_tokens': True, 'output_tokens': -1, 'total_tokens': 1.5}}})])
        self.assertEqual(record['malformed_events'], 2)
        self.assertTrue(all(v is None for v in record['usage'].values()))

    def test_quota_evidence_and_staleness(self):
        now = dt.datetime(2026, 10, 22, tzinfo=dt.timezone.utc)
        raw = {'source': 'manual:/usage', 'model': 'm', 'remaining': 20,
               'unit': 'percent', 'observed_at': now.isoformat()}
        self.assertEqual(quota_snapshot(raw, 'm', now)['status'], 'observed')
        self.assertEqual(quota_snapshot(raw, 'other', now)['status'], 'unknown')
        self.assertEqual(quota_snapshot(raw, 'm', now + dt.timedelta(minutes=16))['status'], 'stale')
        raw['remaining'] = 101
        self.assertEqual(quota_snapshot(raw, 'm', now)['status'], 'unknown')

    def test_expired_reset_and_future_observation(self):
        now = dt.datetime(2026, 10, 22, tzinfo=dt.timezone.utc)
        raw = {'source': 'manual:/usage', 'model': 'm', 'remaining': 0, 'unit': 'requests',
               'observed_at': now.isoformat(), 'reset_at': now.isoformat()}
        self.assertEqual(quota_snapshot(raw, 'm', now)['status'], 'stale')
        self.assertEqual(quota_snapshot(raw, 'm', now - dt.timedelta(seconds=1))['status'], 'unknown')

    def test_three_lines_and_no_prompt_logging(self):
        record = self.run_events({'event': 'result', 'result': {'response': 'PRIVATE PROMPT',
                                 'status': 'SUCCESS', 'usage': {}}})
        self.assertEqual(len(steering(record).splitlines()), 3)
        self.assertNotIn('PRIVATE', json.dumps(record))

    def test_model_unknown_without_observation(self):
        self.assertIsNone(self.run_events({'event': 'init', 'init': {}})['model'])

    def test_account_scope_required_for_quota_join(self):
        raw = {'source': 'manual:/usage', 'model': 'm', 'remaining': 2, 'unit': 'requests',
               'observed_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'account_scope': 'owner'}
        self.assertEqual(normalize([], 'm', raw)['quota']['status'], 'unknown')
        self.assertEqual(normalize([], 'm', raw, account_scope='collaborator')['quota']['status'], 'unknown')
        self.assertEqual(normalize([], 'm', raw, account_scope='owner')['quota']['status'], 'observed')

    def test_hostile_structures_and_nonfinite_json_are_malformed(self):
        record = normalize([None, 5, b'\xff', b'{"event":"result","result":NaN}', '{"x": Infinity}', '{"x": []}'])
        self.assertEqual(record['malformed_events'], 5)
        self.assertEqual(record['status'], 'INCOMPLETE')
        self.assertIsNone(record['model'])

    def test_oversized_event_rejected_but_result_retained(self):
        good = json.dumps({'event': 'result', 'result': {'status': 'SUCCESS', 'usage': {'total_tokens': 4}}})
        huge = json.dumps({'event': 'step_update', 'private': 'x' * MAX_EVENT_BYTES})
        record = normalize([huge, good])
        self.assertEqual(record['malformed_events'], 1)
        self.assertEqual(record['status'], 'SUCCESS')
        self.assertEqual(record['usage']['total_tokens'], 4)

    def test_bounded_strings_and_control_characters(self):
        injected = 'model\nSECOND\rTHIRD\x1b[31m'
        record = normalize([json.dumps({'event': 'init', 'conversation_id': injected,
                                        'init': {'model': injected}}),
                            json.dumps({'event': 'result', 'result': {'status': 'OK\nFORGED',
                                        'usage': {}}})], run_id='R' * 500,
                     account_scope='A' * 500)
        for key in ('model', 'run_id', 'account_scope', 'conversation_id'):
            self.assertLessEqual(len(record[key]), 256)
        self.assertLessEqual(len(record['status']), 100)
        self.assertEqual(len(steering(record).splitlines()), 3)
        self.assertIn('?', record['status'])

    def test_result_allowlist_does_not_disclose_private_fields(self):
        secret = 'super-secret prompt/response/step data'
        record = self.run_events({'event': 'result', 'result': {
            'status': 'SUCCESS', 'response': secret, 'step': secret, 'usage': {'total_tokens': 2}}})
        serialized = json.dumps(record)
        self.assertNotIn(secret, serialized)
        self.assertEqual(set(record['usage']), {'input_tokens', 'output_tokens', 'thinking_tokens', 'cache_read_tokens', 'total_tokens'})

    def test_malformed_quota_inputs_never_raise_or_join(self):
        now = dt.datetime.now(dt.timezone.utc)
        for raw in (None, [], 'bad', {'source': 'manual:/usage', 'model': 'm',
                                       'observed_at': [], 'remaining': 1, 'unit': 'tokens'}):
            self.assertEqual(quota_snapshot(raw, 'm', now)['status'], 'unknown')
            self.assertEqual(normalize([], 'm', raw)['quota']['status'], 'unknown')


if __name__ == '__main__':
    unittest.main()
