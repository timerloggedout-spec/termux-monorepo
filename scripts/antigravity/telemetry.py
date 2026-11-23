#!/usr/bin/env python3
"""Normalize Antigravity stream-json without retaining prompt or tool payloads."""
import argparse
import datetime as dt
import json
import math
import re
import sys
import uuid

MAX_EVENT_BYTES = 1048576
FIELDS = ('input_tokens', 'output_tokens', 'thinking_tokens', 'cache_read_tokens', 'total_tokens')
RECORD_SCHEMA_VERSION = 1
EVENT_SCHEMA_VERSION = 1
EVENT_RECORD_TYPE = 'telemetry_event'
EVENT_NAME_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/+\-]{0,127}\Z')
EVENT_TYPES = {'init', 'step_update', 'result'}
STEP_TYPES = {'user_input', 'agent_response', 'tool', 'checkpoint'}
STEP_STATES = {'ACTIVE', 'DONE'}


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def count(value):
    return value if type(value) is int and 0 <= value <= (2**63 - 1) else None


def _safe_string(value, limit=256):
    if not isinstance(value, str):
        return None
    text = ''.join(ch if ch.isprintable() else '?' for ch in value)
    return text[:limit] or None


def _safe_identifier(value, limit=128):
    if not isinstance(value, str) or len(value) > limit or not EVENT_NAME_RE.fullmatch(value):
        return None
    return value


def _finite_number(value):
    return (type(value) in (int, float) and 0 <= value <= (2**63 - 1)
            and math.isfinite(value))


def _usage(value):
    if not isinstance(value, dict):
        return None
    return {key: count(value.get(key)) for key in FIELDS}


def _usage_status(value):
    return 'SUCCESS' if value == 'SUCCESS' else ('INCOMPLETE' if value == 'INCOMPLETE' else 'FAILED')


def malformed_event(run_id, sequence, reason):
    return {'schema_version': EVENT_SCHEMA_VERSION, 'record_type': EVENT_RECORD_TYPE,
            'run_id': run_id, 'sequence': sequence, 'observed_at': stamp(),
            'event_type': 'malformed', 'reason': reason}


def project_event(event, run_id, sequence):
    """Project one source envelope to a strict allowlist; never copy source subtrees."""
    event_type = event.get('event')
    kind = event_type if isinstance(event_type, str) and event_type in EVENT_TYPES else 'other'
    projected = {'schema_version': EVENT_SCHEMA_VERSION,
                 'record_type': EVENT_RECORD_TYPE,
                 'run_id': run_id,
                 'sequence': sequence,
                 'observed_at': stamp(),
                 'event_type': kind}
    if kind == 'init':
        init = event.get('init')
        if isinstance(init, dict):
            model = _safe_identifier(init.get('model'))
            if model:
                projected['model'] = model
    elif kind == 'step_update':
        step = event.get('step_update')
        if not isinstance(step, dict):
            return projected
        index = count(step.get('step_index'))
        if index is not None:
            projected['step_index'] = index
        step_type = step.get('step_type')
        projected['step_type'] = step_type if isinstance(step_type, str) and step_type in STEP_TYPES else 'other'
        state = step.get('state')
        projected['state'] = state if isinstance(state, str) and state in STEP_STATES else 'other'
        duration = step.get('duration_seconds')
        if _finite_number(duration):
            projected['duration_seconds'] = duration
        if projected['step_type'] == 'tool':
            name = _safe_identifier(step.get('tool_name'))
            tool_info = step.get('tool_info')
            if name is None and isinstance(tool_info, dict):
                name = _safe_identifier(tool_info.get('name'))
            if name:
                projected['tool_name'] = name
        snapshot = _usage(step.get('usage'))
        if snapshot is not None:
            projected['usage_snapshot'] = snapshot
            projected['usage_role'] = 'non_authoritative_step_snapshot'
    elif kind == 'result':
        result = event.get('result')
        if not isinstance(result, dict):
            return projected
        projected['run_status'] = _usage_status(result.get('status'))
        duration = result.get('duration_seconds')
        if _finite_number(duration):
            projected['duration_seconds'] = duration
        turns = count(result.get('num_turns'))
        if turns is not None:
            projected['num_turns'] = turns
        final = _usage(result.get('usage'))
        if final is not None:
            projected['final_usage'] = final
            projected['usage_role'] = 'authoritative_result_usage'
    return projected


def run_summary_event(record, sequence):
    """Append a sanitized terminal aggregate, distinct from source step snapshots."""
    producer_code = record.get('producer_exit_code')
    if producer_code is None:
        producer_state = 'not_observed'
    elif type(producer_code) is int and producer_code == 0:
        producer_state = 'success'
    elif type(producer_code) is int and producer_code < 0:
        producer_state = 'signaled'
    else:
        producer_state = 'failed'
    usage = record.get('usage')
    safe_usage = {key: count(usage.get(key)) for key in FIELDS} if isinstance(usage, dict) else dict.fromkeys(FIELDS)
    duration = record.get('duration_seconds')
    summary = {'schema_version': EVENT_SCHEMA_VERSION,
               'record_type': 'run_summary',
               'run_id': _safe_string(record.get('run_id')) or str(uuid.uuid4()),
               'sequence': sequence,
               'observed_at': stamp(),
               'event_type': 'run_summary',
               'run_status': _usage_status(record.get('status')),
               'producer_state': producer_state,
               'usage_source': 'stream-json:result.usage' if record.get('usage_source') == 'stream-json:result.usage' else 'unavailable',
               'final_usage': safe_usage,
               'usage_role': 'authoritative_run_total',
               'event_count': count(record.get('event_count')) or 0,
               'tool_step_count': count(record.get('tool_step_count')) or 0,
               'malformed_event_count': count(record.get('malformed_events')) or 0}
    if _finite_number(duration):
        summary['duration_seconds'] = duration
    return summary


def migrate_source_event(source_event, run_id, sequence, source_schema_version=0):
    """Migrate a legacy unversioned CLI envelope to the current sanitized event shape."""
    if source_schema_version != 0:
        raise ValueError('unsupported source event schema version')
    if not isinstance(source_event, dict):
        raise ValueError('source event must be an object')
    return project_event(source_event, _safe_string(run_id) or str(uuid.uuid4()), sequence)


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


def normalize(lines, model=None, quota=None, run_id=None, account_scope=None, *, event_sink=None):
    initial_model = _safe_string(model)
    safe_run_id = _safe_string(run_id) or str(uuid.uuid4())
    safe_scope = _safe_string(account_scope)
    record = {'schema_version': RECORD_SCHEMA_VERSION, 'telemetry_schema_version': EVENT_SCHEMA_VERSION,
              'provider': 'antigravity', 'run_id': safe_run_id, 'conversation_id': None,
              'account_scope': safe_scope, 'model': initial_model,
              'observed_at': stamp(), 'status': 'INCOMPLETE',
              'usage_source': 'unavailable', 'usage_scope': 'run',
              'usage': dict.fromkeys(FIELDS), 'duration_seconds': None,
              'cost_usd': None, 'malformed_events': 0, 'event_count': 0,
              'source_event_count': 0, 'tool_step_count': 0}
    result = None
    sequence = 0
    for line in lines:
        reason = None
        if line == 'INVALID_OVERSIZED_EVENT':
            reason = 'oversized'
        elif line == 'INVALID_UTF8_EVENT':
            reason = 'invalid_utf8'
        if reason:
            record['malformed_events'] += 1
            record['source_event_count'] += 1
            if event_sink is not None:
                event_sink(malformed_event(safe_run_id, sequence, reason))
            sequence += 1
            continue
        if isinstance(line, bytes):
            if len(line) > MAX_EVENT_BYTES:
                record['malformed_events'] += 1
                record['source_event_count'] += 1
                if event_sink is not None:
                    event_sink(malformed_event(safe_run_id, sequence, 'oversized'))
                sequence += 1
                continue
            try:
                line = line.decode('utf-8', errors='strict')
            except UnicodeDecodeError:
                record['malformed_events'] += 1
                record['source_event_count'] += 1
                if event_sink is not None:
                    event_sink(malformed_event(safe_run_id, sequence, 'invalid_utf8'))
                sequence += 1
                continue
        if not isinstance(line, str):
            record['malformed_events'] += 1
            record['source_event_count'] += 1
            if event_sink is not None:
                event_sink(malformed_event(safe_run_id, sequence, 'invalid_type'))
            sequence += 1
            continue
        try:
            if len(line.encode('utf-8')) > MAX_EVENT_BYTES:
                record['malformed_events'] += 1
                record['source_event_count'] += 1
                if event_sink is not None:
                    event_sink(malformed_event(safe_run_id, sequence, 'oversized'))
                sequence += 1
                continue
        except UnicodeError:
            record['malformed_events'] += 1
            record['source_event_count'] += 1
            if event_sink is not None:
                event_sink(malformed_event(safe_run_id, sequence, 'invalid_unicode'))
            sequence += 1
            continue
        if not line.strip():
            continue
        record['source_event_count'] += 1
        try:
            event = _json_object(line)
        except (ValueError, TypeError, UnicodeError, RecursionError):
            record['malformed_events'] += 1
            if event_sink is not None:
                event_sink(malformed_event(safe_run_id, sequence, 'invalid_json'))
            sequence += 1
            continue
        projected = project_event(event, safe_run_id, sequence)
        if event_sink is not None:
            event_sink(projected)
        sequence += 1
        record['event_count'] += 1
        if projected['event_type'] == 'step_update' and projected.get('step_type') == 'tool':
            record['tool_step_count'] += 1
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
        if _finite_number(duration):
            record['duration_seconds'] = duration
        usage = result.get('usage')
        if isinstance(usage, dict):
            record['usage'] = {key: count(usage.get(key)) for key in FIELDS}
            record['usage_source'] = 'stream-json:result.usage'
    scoped_quota = quota if safe_scope and isinstance(quota, dict) and quota.get('account_scope') == safe_scope else None
    record['quota'] = quota_snapshot(scoped_quota, record['model'])
    return record


def bounded_lines(source):
    """Read bounded chunks and yield one bounded candidate per input line."""
    pending = bytearray()
    oversized = False
    too_large = b'\x00' * (MAX_EVENT_BYTES + 1)
    while True:
        chunk = source.read(65536)
        if not chunk:
            break
        parts = chunk.split(b'\n')
        for index, part in enumerate(parts):
            if not oversized:
                if len(pending) + len(part) > MAX_EVENT_BYTES:
                    pending.clear()
                    oversized = True
                else:
                    pending.extend(part)
            if index < len(parts) - 1:
                yield too_large if oversized else bytes(pending)
                pending.clear()
                oversized = False
    if pending or oversized:
        yield too_large if oversized else bytes(pending)


def steering(record):
    usage, quota = record['usage'], record['quota']
    def val(value):
        return '?' if value is None else str(value)
    qtext = 'UNKNOWN; inspect /usage' if quota['status'] == 'unknown' else (
        f"{quota['remaining']} {quota['unit']} remaining [{quota['status']}; manual]")
    process = ''
    next_action = 'refresh /usage' if quota['status'] != 'observed' else 'owner decides; no auto-switch'
    if 'producer_exit_code' in record:
        process = f" | EXIT {val(record['producer_exit_code'])}"
        if record.get('producer_launch_error'):
            process += ' | LAUNCH FAILED'
        if record['producer_exit_code'] != 0 or record['status'] != 'SUCCESS':
            next_action = 'inspect private diagnostics; no automatic retry'
    return '\n'.join((
        f"MODEL {record['model'] or 'UNKNOWN'} | RUN {record['status']}{process}",
        f"TOKENS in={val(usage['input_tokens'])} out={val(usage['output_tokens'])} total={val(usage['total_tokens'])} | USD unknown",
        f"QUOTA {qtext} | NEXT {next_action}"))


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
    record = normalize(bounded_lines(sys.stdin.buffer), args.model, quota, args.run_id, args.account_scope)
    print(json.dumps(record, allow_nan=False))
    if args.steering:
        print(steering(record), file=sys.stderr)
    return 2 if record['status'] == 'INCOMPLETE' else 0


if __name__ == '__main__':
    sys.exit(main())
