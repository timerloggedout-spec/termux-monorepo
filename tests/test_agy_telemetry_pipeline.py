"""Synthetic-only contracts for event streaming, encrypted archives, and Hindsight outbox."""
import io
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / 'scripts' / 'antigravity'
sys.path.insert(0, str(SCRIPT_DIR))
from archive import (ArchiveError, _read_archive_header, compare_archive_headers,
                     decrypt_archive, encrypt_archive)
from capture import capture
from hindsight_outbox import (DeliveryUncertain, Outbox, OutboxError,
                              endpoint_url, sanitized_summary)
from telemetry import (MAX_EVENT_BYTES, migrate_source_event, normalize)


class ImmediateEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agy-pipeline-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_events_flush_before_source_is_read_again(self):
        first = {'event': 'init', 'conversation_id': 'PRIVATE-CONVERSATION',
                 'init': {'model': 'gemini-2.5-pro', 'cwd': '/private/path', 'tools': ['secret-tool']}}
        second = {'event': 'result', 'result': {'status': 'SUCCESS', 'response': 'PRIVATE RESPONSE',
                  'usage': {'input_tokens': 11, 'total_tokens': 11}}}
        chunks = [json.dumps(first).encode() + b'\n', json.dumps(second).encode() + b'\n']
        destination = self.root / 'capture'

        class ObserveBetweenReads:
            def __init__(self):
                self.index = 0

            def read1(self, size):
                if self.index == 1:
                    rows = (destination / 'events.ndjson').read_text().splitlines()
                    self_outer.assertEqual(len(rows), 1)
                    self_outer.assertEqual(json.loads(rows[0])['event_type'], 'init')
                if self.index >= len(chunks):
                    return b''
                chunk = chunks[self.index]
                self.index += 1
                return chunk

        self_outer = self
        raw_bytes = b''.join(chunks)
        record, summary = capture(ObserveBetweenReads(), destination, run_id='fixture-run')
        events = [json.loads(line) for line in (destination / 'events.ndjson').read_text().splitlines()]
        self.assertEqual((destination / 'stream.ndjson').read_bytes(), raw_bytes)
        self.assertEqual(record['usage']['total_tokens'], 11)
        self.assertEqual(len(summary.splitlines()), 3)
        self.assertEqual([row['event_type'] for row in events], ['init', 'result', 'run_summary'])
        serialized = json.dumps(events)
        for private in ('PRIVATE-CONVERSATION', 'PRIVATE RESPONSE', '/private/path', 'secret-tool'):
            self.assertNotIn(private, serialized)
        self.assertEqual(events[-1]['usage_role'], 'authoritative_run_total')
        for path in destination.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_step_snapshots_and_repeated_results_are_never_summed(self):
        source = [
            {'event': 'step_update', 'step_update': {'step_index': 3, 'step_type': 'tool',
             'state': 'DONE', 'tool_name': 'run_command', 'usage': {'total_tokens': 900},
             'text_delta': 'PRIVATE TEXT', 'tool_info': {'parameters': {'secret': 'PRIVATE ARG'},
                                                         'output': 'PRIVATE TOOL OUTPUT'}}},
            {'event': 'result', 'result': {'status': 'SUCCESS', 'usage': {'total_tokens': 8},
                                           'response': 'PRIVATE RESPONSE'}},
            {'event': 'result', 'result': {'status': 'SUCCESS', 'usage': {'total_tokens': 15},
                                           'response': 'PRIVATE RESPONSE 2'}}]
        records = []
        result = normalize(map(json.dumps, source), run_id='repeat-run', event_sink=records.append)
        self.assertEqual(result['usage']['total_tokens'], 15)
        self.assertEqual(result['event_count'], 3)
        self.assertEqual(result['tool_step_count'], 1)
        self.assertEqual(records[0]['usage_snapshot']['total_tokens'], 900)
        self.assertEqual(records[0]['usage_role'], 'non_authoritative_step_snapshot')
        self.assertEqual(records[1]['final_usage']['total_tokens'], 8)
        self.assertEqual(records[2]['final_usage']['total_tokens'], 15)
        serialized = json.dumps(records)
        for private in ('PRIVATE TEXT', 'PRIVATE ARG', 'PRIVATE TOOL OUTPUT', 'PRIVATE RESPONSE'):
            self.assertNotIn(private, serialized)
        self.assertNotIn('parameters', serialized)
        self.assertNotIn('conversation_id', serialized)

    def test_malformed_oversized_and_unrecognized_events_are_bounded(self):
        destination = self.root / 'capture'
        data = (b'\xff\n' + b'x' * (MAX_EVENT_BYTES + 1) + b'\n' +
                b'{"event": []}\n' +
                b'{"event":"result","result":{"status":"SUCCESS","usage":{"total_tokens":7}}}\n' * 2)
        record, _ = capture(io.BytesIO(data), destination, run_id='malformed-run')
        events = [json.loads(line) for line in (destination / 'events.ndjson').read_text().splitlines()]
        self.assertEqual((destination / 'stream.ndjson').read_bytes(), data)
        self.assertEqual(record['malformed_events'], 2)
        self.assertEqual(record['event_count'], 3)
        self.assertEqual(record['usage']['total_tokens'], 7)
        self.assertEqual([e['reason'] for e in events[:2]], ['invalid_utf8', 'oversized'])
        self.assertEqual(events[2]['event_type'], 'other')
        self.assertEqual(events[-1]['final_usage']['total_tokens'], 7)

    def test_legacy_stream_event_migration_is_privacy_projected(self):
        migrated = migrate_source_event(
            {'event': 'step_update', 'conversation_id': 'PRIVATE',
             'step_update': {'step_type': 'agent_response', 'text_delta': 'PRIVATE TEXT',
                             'usage': {'total_tokens': 4}}}, 'legacy-run', 2)
        self.assertEqual(migrated['schema_version'], 1)
        self.assertEqual(migrated['usage_role'], 'non_authoritative_step_snapshot')
        self.assertNotIn('PRIVATE', json.dumps(migrated))
        with self.assertRaises(ValueError):
            migrate_source_event({'event': 'init'}, 'legacy-run', 0, source_schema_version=1)

    def test_public_schemas_are_versioned_and_exclude_raw_payload_fields(self):
        event_schema = json.loads((ROOT / 'schemas/antigravity/telemetry-event-v1.schema.json').read_text())
        archive_schema = json.loads((ROOT / 'schemas/antigravity/encrypted-archive-v1.schema.json').read_text())
        hindsight_schema = json.loads((ROOT / 'schemas/antigravity/hindsight-summary-v1.schema.json').read_text())
        self.assertEqual(event_schema['properties']['schema_version']['const'], 1)
        self.assertEqual(archive_schema['properties']['archive_schema_version']['const'], 1)
        self.assertEqual(hindsight_schema['properties']['summary_schema_version']['const'], 1)
        for forbidden in ('response', 'text_delta', 'tool_info', 'conversation_id', 'cwd'):
            self.assertNotIn(forbidden, event_schema['properties'])
        for forbidden in ('model', 'run_id', 'account_scope', 'response'):
            self.assertNotIn(forbidden, hindsight_schema['properties'])


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agy-age-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.age = self.root / 'age-fixture'
        self.recipient = 'age1' + secrets.token_hex(24)
        os.environ['AGY_TEST_AGE_RECIPIENT'] = self.recipient
        self.addCleanup(os.environ.pop, 'AGY_TEST_AGE_RECIPIENT', None)
        self.age.write_text('#!' + sys.executable + '\n' + '''import os, pathlib, sys
args = sys.argv[1:]
if len(args) >= 2 and args[0] == '-r':
    if args[1] != os.environ.get('AGY_TEST_AGE_RECIPIENT'): sys.exit(10)
    value = sys.stdin.buffer.read()
    sys.stdout.buffer.write(b'FAKE-AGE-V1\\x00' + value[::-1])
elif len(args) >= 4 and args[0] == '-d' and args[1] == '-i':
    key = pathlib.Path(args[2]).read_bytes()
    if not key.startswith(b'FAKE-AGE-IDENTITY-'): sys.exit(11)
    value = pathlib.Path(args[3]).read_bytes()
    prefix = b'FAKE-AGE-V1\\x00'
    if not value.startswith(prefix): sys.exit(12)
    sys.stdout.buffer.write(value[len(prefix):][::-1])
else:
    sys.exit(13)
''')
        self.age.chmod(0o700)
        self.identity = self.root / 'identity.key'
        self.identity.write_bytes(b'FAKE-AGE-IDENTITY-' + secrets.token_bytes(32) + b'\n')
        self.identity.chmod(0o600)
        self.source = self.root / 'synthetic-private.ndjson'
        self.payload = b'{"schema_version":1,"synthetic":"fixture only"}\n'
        self.source.write_bytes(self.payload)
        self.ciphertext = self.root / 'fixture.age'

    def test_encrypt_and_jit_decrypt_without_plaintext_file(self):
        header = encrypt_archive(self.source, self.ciphertext, recipient=self.recipient,
                                 age_binary=str(self.age))
        self.assertEqual(header['archive_schema_version'], 1)
        self.assertEqual(header['telemetry_schema_version'], 1)
        before = set(self.root.iterdir())
        output = io.BytesIO()
        decrypted = decrypt_archive(self.ciphertext, self.identity, output.write,
                                    age_binary=str(self.age))
        self.assertEqual(decrypted, header)
        self.assertEqual(output.getvalue(), self.payload)
        self.assertEqual(set(self.root.iterdir()), before)
        self.assertEqual(stat.S_IMODE(self.ciphertext.stat().st_mode), 0o600)
        self.assertNotIn(self.payload, self.ciphertext.read_bytes())

    def test_missing_recipient_creates_no_archive(self):
        with self.assertRaises(ArchiveError):
            encrypt_archive(self.source, self.ciphertext, recipient=None, age_binary=str(self.age))
        self.assertFalse(self.ciphertext.exists())

    def test_archive_output_inside_git_is_rejected_before_creation(self):
        repo = self.root / 'repo'
        repo.mkdir()
        (repo / '.git').mkdir()
        target = repo / 'private.age'
        with self.assertRaises(ArchiveError):
            encrypt_archive(self.source, target, recipient=self.recipient, age_binary=str(self.age))
        self.assertFalse(target.exists())

    def test_unknown_archive_schema_is_rejected(self):
        header = {'archive_schema_version': 99, 'telemetry_schema_version': 1,
                  'payload_sha256': '0' * 64, 'payload_bytes': 0}
        with self.assertRaises(ArchiveError):
            _read_archive_header(io.BytesIO((json.dumps(header) + '\n').encode()))

    def test_archive_metadata_comparison_tracks_schema_and_payload_changes(self):
        left = {'archive_schema_version': 1, 'telemetry_schema_version': 1,
                'payload_sha256': 'a' * 64, 'payload_bytes': 17}
        right = {'archive_schema_version': 1, 'telemetry_schema_version': 2,
                 'payload_sha256': 'b' * 64, 'payload_bytes': 18}
        comparison = compare_archive_headers(left, right)
        self.assertTrue(comparison['telemetry_schema_changed'])
        self.assertFalse(comparison['payload_equal'])
        self.assertFalse(comparison['payload_sha256_equal'])

    def test_identity_inside_git_and_permissive_identity_are_rejected(self):
        encrypt_archive(self.source, self.ciphertext, recipient=self.recipient,
                        age_binary=str(self.age))
        fake_repo = self.root / 'repo'
        fake_repo.mkdir()
        (fake_repo / '.git').mkdir()
        nested_identity = fake_repo / 'identity.key'
        nested_identity.write_bytes(b'fake')
        nested_identity.chmod(0o600)
        with self.assertRaises(ArchiveError):
            decrypt_archive(self.ciphertext, nested_identity, io.BytesIO().write,
                            age_binary=str(self.age))
        self.identity.chmod(0o644)
        with self.assertRaises(ArchiveError):
            decrypt_archive(self.ciphertext, self.identity, io.BytesIO().write,
                            age_binary=str(self.age))


class HindsightOutboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agy-outbox-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db_path = self.root / 'private-outbox.sqlite3'
        self.record = {'schema_version': 1, 'telemetry_schema_version': 1,
                       'run_id': 'fixture-stable-run', 'conversation_id': 'PRIVATE-CONVERSATION',
                       'account_scope': 'PRIVATE-ACCOUNT', 'model': 'PRIVATE-MODEL',
                       'status': 'SUCCESS', 'usage_source': 'stream-json:result.usage',
                       'usage': {'input_tokens': 12, 'output_tokens': 3, 'total_tokens': 15},
                       'duration_seconds': 2.5, 'event_count': 7, 'tool_step_count': 2,
                       'malformed_events': 1, 'response': 'PRIVATE RESPONSE'}

    def open_outbox(self):
        box = Outbox(self.db_path)
        self.addCleanup(box.close)
        return box

    def test_reviewed_aggregate_is_allowlisted_and_local_enqueue_makes_no_network_call(self):
        summary = sanitized_summary(self.record)
        rendered = json.dumps(summary)
        for private in ('PRIVATE-CONVERSATION', 'PRIVATE-ACCOUNT', 'PRIVATE-MODEL', 'PRIVATE RESPONSE', 'fixture-stable-run'):
            self.assertNotIn(private, rendered)
        with mock.patch('hindsight_outbox.http_post', side_effect=AssertionError('network must not run')):
            box = self.open_outbox()
            with self.assertRaises(OutboxError):
                box.enqueue(self.record, reviewed=False)
            first = box.enqueue(self.record, reviewed=True)
            duplicate = box.enqueue(self.record, reviewed=True)
        self.assertTrue(first['inserted'])
        self.assertFalse(duplicate['inserted'])
        self.assertEqual(first['document_id'], duplicate['document_id'])
        self.assertEqual(stat.S_IMODE(self.db_path.stat().st_mode), 0o600)

    def test_outbox_inside_git_is_rejected_before_creation(self):
        repo = self.root / 'repo'
        repo.mkdir()
        (repo / '.git').mkdir()
        path = repo / 'outbox.sqlite3'
        with self.assertRaises(OutboxError):
            Outbox(path)
        self.assertFalse(path.exists())

    def test_same_document_appends_revised_payload_without_duplicate_retain(self):
        box = self.open_outbox()
        sent = []

        def acknowledge(url, body, *, api_key=None):
            sent.append((url, body, api_key))
            return {'success': True, 'async': True, 'operation_id': body['operation_id']}

        original = box.enqueue(self.record, reviewed=True)
        first = box.deliver_next(base_url='https://hindsight.example', bank_id='private-bank',
                                 reviewed=True, post=acknowledge)
        updated_record = dict(self.record)
        updated_record['usage'] = dict(self.record['usage'], total_tokens=18)
        revised = box.enqueue(updated_record, reviewed=True)
        second = box.deliver_next(base_url='https://hindsight.example', bank_id='private-bank',
                                  reviewed=True, post=acknowledge)
        duplicate = box.enqueue(updated_record, reviewed=True)
        self.assertTrue(original['inserted'])
        self.assertTrue(revised['inserted'])
        self.assertFalse(duplicate['inserted'])
        self.assertEqual(first['state'], 'accepted')
        self.assertEqual(second['state'], 'accepted')
        self.assertEqual(sent[0][1]['items'][0]['document_id'], sent[1][1]['items'][0]['document_id'])
        self.assertEqual(sent[0][1]['items'][0]['update_mode'], 'append')
        self.assertNotEqual(sent[0][1]['operation_id'], sent[1][1]['operation_id'])
        self.assertEqual(sent[1][1]['operation_id'], revised['operation_id'])
        self.assertEqual(sent[0][0], 'https://hindsight.example/v1/default/banks/private-bank/memories')

    def test_ambiguous_ack_requires_explicit_retry_with_identical_operation_id(self):
        box = self.open_outbox()
        queued = box.enqueue(self.record, reviewed=True)
        sent_ids = []

        def timeout(url, body, *, api_key=None):
            sent_ids.append(body['operation_id'])
            raise TimeoutError('fixture ambiguous ack')

        with self.assertRaises(DeliveryUncertain):
            box.deliver_next(base_url='https://hindsight.example', bank_id='fixture',
                             reviewed=True, post=timeout)
        self.assertIsNone(box.deliver_next(base_url='https://hindsight.example', bank_id='fixture',
                                           reviewed=True, post=lambda *a, **k: self.fail('must not auto-retry')))

        def ack(url, body, *, api_key=None):
            sent_ids.append(body['operation_id'])
            return {'success': True, 'async': True, 'operation_id': body['operation_id']}

        result = box.deliver_next(base_url='https://hindsight.example', bank_id='fixture',
                                  reviewed=True, retry_ambiguous=True, post=ack)
        self.assertEqual(result['state'], 'accepted')
        self.assertEqual(sent_ids, [queued['operation_id'], queued['operation_id']])
        self.assertEqual(result['attempt'], 2)

    def test_interrupted_sending_row_recovers_as_uncertain_without_auto_retry(self):
        box = self.open_outbox()
        queued = box.enqueue(self.record, reviewed=True)
        box.db.execute("UPDATE entries SET state='sending' WHERE document_id=?", (queued['document_id'],))
        box.db.commit()
        box.close()
        recovered = Outbox(self.db_path)
        try:
            row = recovered.db.execute('SELECT state,last_error,operation_id FROM entries').fetchone()
            self.assertEqual(row, ('uncertain', 'interrupted_during_send', queued['operation_id']))
            self.assertIsNone(recovered.deliver_next(base_url='https://hindsight.example', bank_id='fixture',
                                                     reviewed=True, post=lambda *a, **k: self.fail('must not auto-retry')))
        finally:
            recovered.close()

    def test_send_requires_explicit_review_and_nonloopback_http_is_rejected(self):
        box = self.open_outbox()
        box.enqueue(self.record, reviewed=True)
        with self.assertRaises(OutboxError):
            box.deliver_next(base_url='https://hindsight.example', bank_id='fixture', reviewed=False,
                             post=lambda *a, **k: self.fail('must not send'))
        with self.assertRaises(OutboxError):
            endpoint_url('http://not-local.example', 'fixture')
        self.assertEqual(endpoint_url('http://127.0.0.1:8888', 'fixture'),
                         'http://127.0.0.1:8888/v1/default/banks/fixture/memories')


if __name__ == '__main__':
    unittest.main()
