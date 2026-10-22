#!/usr/bin/env python3
"""Normalize one existing stream-json invocation; this module never launches agy."""
import argparse
import datetime as dt
import json
import math
import sys
import uuid

MAX_EVENT_BYTES = 1048576
FIELDS = ('input_tokens', 'output_tokens', 'thinking_tokens', 'cache_read_tokens', 'total_tokens')


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def count(value):
    return value if type(value) is int and 0 <= value <= (2**63 - 1) else None


def _safe_string(value, limit=256):
    if not isinstance(value, str):
        return None
    text = ''.join(ch if ch.isprintable() else '?' for ch in value)
    return text[:limit] or None


def quota_snapshot(raw, model, now=None):
    """Validate explicit manual quota evidence; never derive it from token counts."""
    unknown = {'source': 'unavailable', 'status': 'unknown', 'remaining': None,
               'limit': None, 'unit': None, 'observed_at': None, 'reset_at': None}
    if not isinstance(raw, dict) or not model:
        return unknown
    if raw.get('source') != 'manual:/usage' or raw.get('model') != model:
        return unknown
    observed_text = raw.get('observed_at')
    if not isinstance(observed_text, str):
        return unknown
    try:
        observed = dt.datetime.fromisoformat(observed_text.replace('Z', '+00:00'))
        current = now or dt.datetime.now(dt.timezone.utc)
        if observed.tzinfo is None or current.tzinfo is None:
            return unknown
        age = (current - observed).total_seconds()
    except (TypeError, ValueError, AttributeError, OverflowError):
        return unknown
    unit = raw.get('unit')
    if age < 0 or unit not in ('requests', 'tokens', 'percent'):
        return unknown

    def number(value):
        return (type(value) in (int, float) and 0 <= value <= (2**63 - 1)
                and math.isfinite(value))

    remaining, limit = raw.get('remaining'), raw.get('limit')
    if not number(remaining) or (limit is not None and (not number(limit) or remaining > limit)):
        return unknown
    if unit == 'percent' and remaining > 100:
        return unknown
    reset_text = raw.get('reset_at')
    reset_dt = None
    if reset_text is not None:
        if not isinstance(reset_text, str):
            return unknown
        try:
            reset_dt = dt.datetime.fromisoformat(reset_text.replace('Z', '+00:00'))
            if reset_dt.tzinfo is None:
                return unknown
        except (TypeError, ValueError, AttributeError, OverflowError):
            return unknown
    stale = age > 900 or (reset_dt is not None and reset_dt <= current)
    return {'source': 'manual:/usage', 'status': 'stale' if stale else 'observed',
            'remaining': remaining, 'limit': limit, 'unit': unit,
            'observed_at': observed_text, 'age_seconds': round(age), 'reset_at': reset_text}


def _json_object(line):
    def reject_constant(value):
        raise ValueError('non-finite JSON constant')
    event = json.loads(line, parse_constant=reject_constant)
    if not isinstance(event, dict):
        raise ValueError('event must be an object')
    return event


def normalize(lines, model=None, quota=None, run_id=None, account_scope=None):
    initial_model = _safe_string(model)
    safe_run_id = _safe_string(run_id) or str(uuid.uuid4())
    safe_scope = _safe_string(account_scope)
    record = {'schema_version': 1, 'provider': 'antigravity',
              'run_id': safe_run_id, 'conversation_id': None,
              'account_scope': safe_scope, 'model': initial_model,
              'observed_at': stamp(), 'status': 'INCOMPLETE',
              'usage_source': 'unavailable', 'usage_scope': 'run',
              'usage': dict.fromkeys(FIELDS), 'duration_seconds': None,
              'cost_usd': None, 'malformed_events': 0}
    result = None
    for line in lines:
        if isinstance(line, bytes):
            if len(line) > MAX_EVENT_BYTES:
                record['malformed_events'] += 1
                continue
            try:
                line = line.decode('utf-8', errors='strict')
            except UnicodeDecodeError:
                record['malformed_events'] += 1
                continue
        if not isinstance(line, str):
            record['malformed_events'] += 1
            continue
        try:
            if len(line.encode('utf-8')) > MAX_EVENT_BYTES:
                record['malformed_events'] += 1
                continue
        except UnicodeError:
            record['malformed_events'] += 1
            continue
        if not line.strip():
            continue
        try:
            event = _json_object(line)
        except (ValueError, TypeError, UnicodeError, RecursionError):
            record['malformed_events'] += 1
            continue
        if event.get('event') == 'init':
            record['conversation_id'] = _safe_string(event.get('conversation_id'))
            init = event.get('init')
            if isinstance(init, dict):
                record['model'] = _safe_string(init.get('model')) or initial_model
        elif event.get('event') == 'result' and isinstance(event.get('result'), dict):
            result = event['result']
    if result is not None:
        record['conversation_id'] = _safe_string(result.get('conversation_id')) or record['conversation_id']
        record['status'] = _safe_string(result.get('status'), 100) or 'UNKNOWN'
        duration = result.get('duration_seconds')
        if (type(duration) in (int, float) and 0 <= duration <= (2**63 - 1)
                and math.isfinite(duration)):
            record['duration_seconds'] = duration
        usage = result.get('usage')
        if isinstance(usage, dict):
            record['usage'] = {key: count(usage.get(key)) for key in FIELDS}
            record['usage_source'] = 'stream-json:result.usage'
    scoped_quota = quota if safe_scope and isinstance(quota, dict) and quota.get('account_scope') == safe_scope else None
    record['quota'] = quota_snapshot(scoped_quota, record['model'])
    return record


def steering(record):
    usage, quota = record['usage'], record['quota']
    def val(value):
        return '?' if value is None else str(value)
    qtext = 'UNKNOWN; inspect /usage' if quota['status'] == 'unknown' else (
        f"{quota['remaining']} {quota['unit']} remaining [{quota['status']}; manual]")
    return '\n'.join((
        f"MODEL {record['model'] or 'UNKNOWN'} | RUN {record['status']}",
        f"TOKENS in={val(usage['input_tokens'])} out={val(usage['output_tokens'])} total={val(usage['total_tokens'])} | USD unknown",
        f"QUOTA {qtext} | NEXT {'refresh /usage' if quota['status'] != 'observed' else 'owner decides; no auto-switch'}"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model')
    parser.add_argument('--run-id')
    parser.add_argument('--account-scope')
    parser.add_argument('--quota', help='Optional manually observed /usage JSON file')
    parser.add_argument('--steering', action='store_true')
    args = parser.parse_args()
    quota = None
    if args.quota:
        try:
            with open(args.quota, encoding='utf-8') as stream:
                quota = json.load(stream, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (OSError, ValueError):
            quota = None
    record = normalize(sys.stdin.buffer, args.model, quota, args.run_id, args.account_scope)
    print(json.dumps(record, allow_nan=False))
    if args.steering:
        print(steering(record), file=sys.stderr)
    return 2 if record['status'] == 'INCOMPLETE' else 0


if __name__ == '__main__':
    sys.exit(main())
