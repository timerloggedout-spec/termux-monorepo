#!/usr/bin/env python3
"""Queue reviewed, allowlisted AGY run summaries for an explicitly opted-in Hindsight send."""
import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

from telemetry import EVENT_SCHEMA_VERSION, FIELDS, count

SUMMARY_SCHEMA_VERSION = 1
OUTBOX_SCHEMA_VERSION = 1
NAMESPACE = uuid.UUID('7a7da7bc-1ec1-46b4-b6eb-4c7ba8a6d5cf')


class OutboxError(Exception):
    pass


class DeliveryUncertain(OutboxError):
    pass


def _outside_git(path):
    resolved = Path(path).resolve()
    for parent in (resolved.parent, *resolved.parents):
        marker = parent / '.git'
        if marker.exists() or marker.is_symlink():
            raise OutboxError('outbox must be outside Git worktrees')
    return resolved


def _status(value):
    if value == 'SUCCESS':
        return 'SUCCESS'
    if value == 'INCOMPLETE':
        return 'INCOMPLETE'
    return 'FAILED'


def _producer_state(value):
    if 'producer_exit_code' not in value:
        return 'not_observed'
    code = value.get('producer_exit_code')
    if type(code) is not int:
        return 'launch_failed'
    if code == 0:
        return 'success'
    if code < 0:
        return 'signaled'
    return 'failed'


def sanitized_summary(record):
    """Keep only reviewed-safe aggregate counters; drop model, IDs and all payloads."""
    if not isinstance(record, dict):
        raise OutboxError('run record must be an object')
    raw_usage = record.get('usage')
    usage = {key: count(raw_usage.get(key)) for key in FIELDS} if isinstance(raw_usage, dict) else dict.fromkeys(FIELDS)
    duration = record.get('duration_seconds')
    if not (type(duration) in (int, float) and math.isfinite(duration) and 0 <= duration <= 2**63 - 1):
        duration = None
    schema = record.get('telemetry_schema_version', EVENT_SCHEMA_VERSION)
    if type(schema) is not int or schema < 1 or schema > 2**31 - 1:
        schema = EVENT_SCHEMA_VERSION
    return {'summary_schema_version': SUMMARY_SCHEMA_VERSION,
            'telemetry_schema_version': schema,
            'source': 'antigravity_cli_stream_json',
            'run_status': _status(record.get('status')),
            'producer_state': _producer_state(record),
            'usage_source': 'stream-json:result.usage' if record.get('usage_source') == 'stream-json:result.usage' else 'unavailable',
            'usage_scope': 'run',
            'final_usage': usage,
            'duration_seconds': duration,
            'event_count': count(record.get('event_count')) or 0,
            'tool_step_count': count(record.get('tool_step_count')) or 0,
            'malformed_event_count': count(record.get('malformed_events')) or 0}


def stable_document_id(run_id):
    if not isinstance(run_id, str) or not run_id:
        raise OutboxError('run_id is required for stable idempotency')
    return str(uuid.uuid5(NAMESPACE, 'cue:agy:run:' + run_id))


def operation_id_for(document_id, payload_hash):
    return str(uuid.uuid5(NAMESPACE, 'cue:agy:retain:' + document_id + ':' + payload_hash))


class Outbox:
    def __init__(self, path):
        self.path = _outside_git(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise OutboxError('outbox path must not be a symlink')
        if not self.path.exists():
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
            fd = os.open(self.path, flags, 0o600)
            os.close(fd)
        info = self.path.lstat()
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) & 0o077:
            raise OutboxError('outbox must be a private regular file')
        self.db = sqlite3.connect(self.path, timeout=10)
        self.db.execute('PRAGMA journal_mode=DELETE')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY, value TEXT NOT NULL)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS entries (
            document_id TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            operation_id TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('pending','sending','uncertain','accepted','failed')),
            attempts INTEGER NOT NULL DEFAULT 0,
            ack_operation_id TEXT,
            last_error TEXT,
            created_at TEXT NOT NULL,
            PRIMARY KEY(document_id, payload_hash))''')
        schema = self.db.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if schema is None:
            self.db.execute("INSERT INTO metadata(key,value) VALUES('schema_version',?)", (str(OUTBOX_SCHEMA_VERSION),))
            self.db.commit()
        elif schema[0] != str(OUTBOX_SCHEMA_VERSION):
            self.db.close()
            raise OutboxError('unsupported outbox schema version')
        self.db.execute('''UPDATE entries SET state='uncertain',
            last_error='interrupted_during_send' WHERE state='sending' ''')
        self.db.commit()

    def close(self):
        self.db.close()

    def enqueue(self, record, *, reviewed=False):
        if not reviewed:
            raise OutboxError('a human must review and explicitly approve the sanitized summary')
        summary = sanitized_summary(record)
        payload = json.dumps(summary, sort_keys=True, separators=(',', ':'), allow_nan=False)
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        document_id = stable_document_id(record.get('run_id'))
        operation_id = operation_id_for(document_id, payload_hash)
        cursor = self.db.execute('''INSERT OR IGNORE INTO entries
            (document_id,payload_hash,payload_json,operation_id,state,created_at)
            VALUES(?,?,?,?,?,?)''', (document_id, payload_hash, payload, operation_id,
                                      'pending', dt.datetime.now(dt.timezone.utc).isoformat()))
        self.db.commit()
        return {'document_id': document_id, 'payload_hash': payload_hash,
                'operation_id': operation_id, 'inserted': cursor.rowcount == 1,
                'summary': summary}

    def _select(self, retry_ambiguous):
        row = self.db.execute('''SELECT document_id,payload_hash,payload_json,operation_id,state,attempts
            FROM entries WHERE state='pending' ORDER BY created_at,rowid LIMIT 1''').fetchone()
        if row is None and retry_ambiguous:
            row = self.db.execute('''SELECT document_id,payload_hash,payload_json,operation_id,state,attempts
                FROM entries WHERE state='uncertain' ORDER BY created_at,rowid LIMIT 1''').fetchone()
        return row

    def deliver_next(self, *, base_url, bank_id, api_key=None, reviewed=False,
                     retry_ambiguous=False, post=None):
        if not reviewed:
            raise OutboxError('a human must explicitly approve this Hindsight send')
        if not isinstance(bank_id, str) or not bank_id.strip():
            raise OutboxError('HINDSIGHT_BANK_ID is required')
        url = endpoint_url(base_url, bank_id)
        row = self._select(retry_ambiguous)
        if row is None:
            return None
        document_id, payload_hash, payload_json, operation_id, old_state, attempts = row
        self.db.execute('UPDATE entries SET state=?,attempts=?,last_error=NULL WHERE document_id=? AND payload_hash=?',
                        ('sending', attempts + 1, document_id, payload_hash))
        self.db.commit()
        body = {'items': [{'content': payload_json, 'document_id': document_id,
                           'update_mode': 'append'}],
                'async': True, 'operation_id': operation_id}
        sender = post or http_post
        try:
            response = sender(url, body, api_key=api_key)
        except Exception as error:
            self.db.execute('UPDATE entries SET state="uncertain",last_error=? WHERE document_id=? AND payload_hash=?',
                            (error.__class__.__name__, document_id, payload_hash))
            self.db.commit()
            raise DeliveryUncertain('send acknowledgment is uncertain; retry only with the same operation ID') from None
        acknowledged = response.get('operation_id') if isinstance(response, dict) else None
        if (not isinstance(response, dict) or response.get('success') is not True
                or response.get('async') is not True or acknowledged != operation_id):
            self.db.execute('UPDATE entries SET state="uncertain",last_error="missing_or_mismatched_ack" WHERE document_id=? AND payload_hash=?',
                            (document_id, payload_hash))
            self.db.commit()
            raise DeliveryUncertain('Hindsight acknowledgment was missing or mismatched')
        self.db.execute('UPDATE entries SET state="accepted",ack_operation_id=?,last_error=NULL WHERE document_id=? AND payload_hash=?',
                        (acknowledged, document_id, payload_hash))
        self.db.commit()
        return {'document_id': document_id, 'operation_id': operation_id,
                'state': 'accepted', 'attempt': attempts + 1}


def endpoint_url(base_url, bank_id):
    if not isinstance(base_url, str):
        raise OutboxError('HINDSIGHT_BASE_URL is required')
    parsed = urllib.parse.urlsplit(base_url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise OutboxError('Hindsight base URL must be an http(s) URL without credentials')
    if parsed.query or parsed.fragment:
        raise OutboxError('Hindsight base URL must not contain query or fragment')
    if parsed.scheme != 'https':
        try:
            local = parsed.hostname == 'localhost' or ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            local = False
        if not local:
            raise OutboxError('non-loopback Hindsight endpoints require HTTPS')
    prefix = parsed.path.rstrip('/')
    path = prefix + '/v1/default/banks/' + urllib.parse.quote(bank_id, safe='') + '/memories'
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, '', ''))


def http_post(url, body, *, api_key=None, timeout=20):
    encoded = json.dumps(body, separators=(',', ':'), allow_nan=False).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if api_key:
        headers['Authorization'] = 'Bearer ' + api_key
    request = urllib.request.Request(url, data=encoded, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status < 200 or response.status >= 300:
                raise OutboxError(f'Hindsight HTTP status {response.status}')
            return json.loads(response.read(65536).decode('utf-8'))
    except urllib.error.HTTPError as error:
        raise OutboxError(f'Hindsight HTTP status {error.code}') from None


def _load_record(path):
    with open(path, encoding='utf-8') as stream:
        value = json.load(stream, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if not isinstance(value, dict):
        raise OutboxError('run record must be a JSON object')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    preview = commands.add_parser('preview', help='Print only the allowlisted summary; never contacts Hindsight')
    preview.add_argument('--record', required=True)
    enqueue = commands.add_parser('enqueue', help='Queue a reviewed summary locally; never contacts Hindsight')
    enqueue.add_argument('--record', required=True)
    enqueue.add_argument('--outbox', required=True)
    enqueue.add_argument('--reviewed', action='store_true', required=True)
    deliver = commands.add_parser('deliver', help='Send one reviewed item only with explicit opt-in')
    deliver.add_argument('--outbox', required=True)
    deliver.add_argument('--enable-hindsight', action='store_true', required=True)
    deliver.add_argument('--reviewed', action='store_true', required=True)
    deliver.add_argument('--retry-ambiguous', action='store_true',
                         help='Retry an uncertain operation using its unchanged operation_id')
    args = parser.parse_args()
    try:
        if args.command == 'preview':
            print(json.dumps(sanitized_summary(_load_record(args.record)), sort_keys=True, indent=2))
            return 0
        outbox = Outbox(args.outbox)
        try:
            if args.command == 'enqueue':
                result = outbox.enqueue(_load_record(args.record), reviewed=args.reviewed)
                print(json.dumps({key: result[key] for key in ('document_id', 'payload_hash', 'operation_id', 'inserted')}, sort_keys=True))
                return 0
            base_url = os.environ.get('HINDSIGHT_BASE_URL')
            bank_id = os.environ.get('HINDSIGHT_BANK_ID')
            result = outbox.deliver_next(base_url=base_url, bank_id=bank_id,
                                         api_key=os.environ.get('HINDSIGHT_API_KEY'),
                                         reviewed=args.reviewed,
                                         retry_ambiguous=args.retry_ambiguous)
            print(json.dumps(result or {'state': 'empty'}, sort_keys=True))
            return 0
        finally:
            outbox.close()
    except (OSError, ValueError, sqlite3.Error, OutboxError) as error:
        print(f'Outbox operation failed: {error.__class__.__name__}', file=sys.stderr)
        return 3


if __name__ == '__main__':
    sys.exit(main())
