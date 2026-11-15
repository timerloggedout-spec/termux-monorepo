#!/usr/bin/env python3
"""Bounded, append-only Integration Intelligence event/measurement ingestion.

Uses the existing Neon lane-events project/database. It never creates a
project, never logs connection strings, and never mutates source records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import subprocess
import tempfile
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

import lane_event

SQL_DIR = lane_event.SQL_DIR
ADAPTER_VERSION = "integration-event-batch/1.0.0"
DEFAULT_MAX_RECORDS = 250
DEFAULT_MAX_BYTES = 512 * 1024
HARD_MAX_RECORDS = 500
HARD_MAX_BYTES = 1024 * 1024

EVENT_REQUIRED = {
    "schema_version", "event_id", "integration_id", "event_type", "source",
    "execution", "outcome", "evidence", "provenance", "idempotency_key",
}
EVENT_ALLOWED = EVENT_REQUIRED | {
    "privacy", "event_at", "observed_at", "supersedes",
}
MEASUREMENT_REQUIRED = {
    "schema_version", "measurement_id", "event_id", "integration_id",
    "metric_name", "metric_type", "value", "unit", "temporality",
    "measurement_status", "observed_at", "dimensions", "provenance",
    "idempotency_key",
}
MEASUREMENT_ALLOWED = MEASUREMENT_REQUIRED | {
    "event_at", "evidence_ref", "confidence", "supersedes",
}
SECRET_KEY_NAMES = {
    "prompt", "completion", "api_key", "authorization", "cookie",
    "password", "secret", "access_token", "refresh_token", "credential",
    "raw_request_body", "raw_response_body", "session_transcript",
    "private_context", "token", "provider_token", "api_token", "auth_token",
    "id_token", "bearer_token", "personal_access_token", "github_token",
}
SECRET_VALUE_RE = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{16,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)"
)
INTEGRATION_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
ADAPTER_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,99}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$")
EVENT_EXECUTION = {"queued", "running", "succeeded", "failed", "cancelled", "blocked", "unknown"}
EVENT_OUTCOMES = {"observed", "executed", "validated", "promoted", "failed", "unknown"}
ATTRIBUTION = {"direct", "provider_reported", "derived", "unknown"}
VALIDATION_STATUS = {"not_run", "pending", "passed", "failed", "not_applicable"}
CONFIDENCE = {"confirmed", "high", "medium", "low", "unknown"}
METRIC_TYPES = {"counter", "gauge", "rate", "duration", "percentage"}
TEMPORALITY = {"instant", "delta", "cumulative"}
MEASUREMENT_STATUS = {"measured", "estimated", "activity_only", "not_established"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_timestamp(value: object, field: str, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")


def _reject_sensitive(value: object, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            credential_name = re.search(r"(?:^|_)(?:secret|password|private_key|access_key|api_key|auth_token|access_token|refresh_token|credential)(?:_|$)", normalized)
            if normalized in SECRET_KEY_NAMES or credential_name:
                raise ValueError(f"sensitive field rejected at {path}.{key}")
            _reject_sensitive(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]")
    elif isinstance(value, str):
        if "\x00" in value:
            raise ValueError(f"NUL character rejected at {path}")
        if SECRET_VALUE_RE.search(value):
            raise ValueError(f"secret-shaped value rejected at {path}")


def _keys(value: object, allowed: set[str], field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{field} has unknown fields: {','.join(sorted(unknown))}")


def _required(value: dict, fields: set[str], field: str) -> None:
    missing = fields - set(value)
    if missing:
        raise ValueError(f"{field} missing fields: {','.join(sorted(missing))}")


def _nonempty(value: object, field: str, maximum: int = 1000) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"{field} must be a non-empty string <= {maximum} characters")


def validate_event(event: dict) -> dict:
    _keys(event, EVENT_ALLOWED, "event")
    _required(event, EVENT_REQUIRED, "event")
    if event["schema_version"] not in {"1.0.0", "1.1.0"}:
        raise ValueError("event.schema_version must be 1.0.0 or 1.1.0")
    _nonempty(event["event_id"], "event.event_id", 200)
    _nonempty(event["event_type"], "event.event_type", 120)
    _nonempty(event["idempotency_key"], "event.idempotency_key", 256)
    if not isinstance(event["integration_id"], str) or not INTEGRATION_RE.fullmatch(event["integration_id"]):
        raise ValueError("event.integration_id is invalid")

    source = event["source"]
    _keys(source, {"repository", "commit_sha", "pull_request", "workflow_run_id", "provider_request_id"}, "event.source")
    _required(source, {"repository"}, "event.source")
    if not isinstance(source["repository"], str) or not REPOSITORY_RE.fullmatch(source["repository"]):
        raise ValueError("event.source.repository is invalid")
    sha = source.get("commit_sha")
    if sha is not None and (not isinstance(sha, str) or not SHA_RE.fullmatch(sha)):
        raise ValueError("event.source.commit_sha is invalid")
    for field in ("pull_request", "workflow_run_id"):
        n = source.get(field)
        if n is not None and (not isinstance(n, int) or isinstance(n, bool) or n < 1):
            raise ValueError(f"event.source.{field} must be a positive integer or null")
    if source.get("provider_request_id") is not None:
        _nonempty(source["provider_request_id"], "event.source.provider_request_id", 256)

    execution = event["execution"]
    _keys(execution, {"status", "started_at", "completed_at", "duration_ms"}, "event.execution")
    _required(execution, {"status", "started_at", "completed_at"}, "event.execution")
    if execution["status"] not in EVENT_EXECUTION:
        raise ValueError("event.execution.status is invalid")
    parse_timestamp(execution["started_at"], "event.execution.started_at", nullable=True)
    parse_timestamp(execution["completed_at"], "event.execution.completed_at", nullable=True)
    duration = execution.get("duration_ms")
    if duration is not None and (not isinstance(duration, int) or isinstance(duration, bool) or duration < 0):
        raise ValueError("event.execution.duration_ms must be a non-negative integer or null")

    outcome = event["outcome"]
    _keys(outcome, {"state", "summary", "confidence"}, "event.outcome")
    _required(outcome, {"state", "summary"}, "event.outcome")
    if outcome["state"] not in EVENT_OUTCOMES:
        raise ValueError("event.outcome.state is invalid")
    if not isinstance(outcome["summary"], str) or len(outcome["summary"]) > 1000:
        raise ValueError("event.outcome.summary must be a string <= 1000 characters")
    if outcome.get("confidence") is not None and outcome["confidence"] not in CONFIDENCE:
        raise ValueError("event.outcome.confidence is invalid")

    evidence = event["evidence"]
    _keys(evidence, {"artifact_refs", "validation_status", "validator"}, "event.evidence")
    _required(evidence, {"artifact_refs", "validation_status"}, "event.evidence")
    if not isinstance(evidence["artifact_refs"], list) or len(evidence["artifact_refs"]) > 50:
        raise ValueError("event.evidence.artifact_refs must be an array of at most 50 refs")
    if any(not isinstance(x, str) or len(x) > 1000 for x in evidence["artifact_refs"]):
        raise ValueError("event.evidence.artifact_refs contains an invalid ref")
    if evidence["validation_status"] not in VALIDATION_STATUS:
        raise ValueError("event.evidence.validation_status is invalid")
    if evidence.get("validator") is not None:
        _nonempty(evidence["validator"], "event.evidence.validator", 200)

    provenance = event["provenance"]
    _keys(provenance, {"provider", "capture_method", "attribution", "model_id", "adapter_version"}, "event.provenance")
    _required(provenance, {"provider", "capture_method", "attribution"}, "event.provenance")
    _nonempty(provenance["provider"], "event.provenance.provider", 200)
    _nonempty(provenance["capture_method"], "event.provenance.capture_method", 200)
    if provenance["attribution"] not in ATTRIBUTION:
        raise ValueError("event.provenance.attribution is invalid")
    if provenance.get("model_id") is not None:
        _nonempty(provenance["model_id"], "event.provenance.model_id", 200)
    if provenance.get("adapter_version") is not None:
        _nonempty(provenance["adapter_version"], "event.provenance.adapter_version", 100)

    if event["schema_version"] == "1.1.0":
        _required(event, {"observed_at", "privacy"}, "event v1.1.0")
        parse_timestamp(event["observed_at"], "event.observed_at")
        privacy = event["privacy"]
        _keys(privacy, {"classification", "contains_raw_prompt", "contains_secret", "redaction_applied"}, "event.privacy")
        _required(privacy, {"classification"}, "event.privacy")
    elif any(field in event for field in ("event_at", "observed_at", "supersedes")):
        raise ValueError("event_at, observed_at and supersedes require schema_version 1.1.0")

    if "event_at" in event:
        parse_timestamp(event["event_at"], "event.event_at", nullable=True)
    if event.get("supersedes") is not None:
        _nonempty(event["supersedes"], "event.supersedes", 200)
    if "privacy" in event:
        privacy = event["privacy"]
        _keys(privacy, {"classification", "contains_raw_prompt", "contains_secret", "redaction_applied"}, "event.privacy")
        if "classification" in privacy and privacy["classification"] not in {"public", "internal", "confidential", "restricted"}:
            raise ValueError("event.privacy.classification is invalid")
        for flag in ("contains_raw_prompt", "contains_secret", "redaction_applied"):
            if flag in privacy and not isinstance(privacy[flag], bool):
                raise ValueError(f"event.privacy.{flag} must be boolean")
        if privacy.get("contains_raw_prompt") is True or privacy.get("contains_secret") is True:
            raise ValueError("privacy policy rejects raw prompts or secrets")
    _reject_sensitive(event)
    return event


def validate_measurement(record: dict) -> dict:
    _keys(record, MEASUREMENT_ALLOWED, "measurement")
    _required(record, MEASUREMENT_REQUIRED, "measurement")
    if record["schema_version"] != "1.0.0":
        raise ValueError("measurement.schema_version must be 1.0.0")
    _nonempty(record["measurement_id"], "measurement.measurement_id", 200)
    _nonempty(record["event_id"], "measurement.event_id", 200)
    _nonempty(record["idempotency_key"], "measurement.idempotency_key", 256)
    if not isinstance(record["integration_id"], str) or not INTEGRATION_RE.fullmatch(record["integration_id"]):
        raise ValueError("measurement.integration_id is invalid")
    if not isinstance(record["metric_name"], str) or not re.fullmatch(r"^[a-z][a-z0-9_.-]{0,127}$", record["metric_name"]):
        raise ValueError("measurement.metric_name is invalid")
    if record["metric_type"] not in METRIC_TYPES:
        raise ValueError("measurement.metric_type is invalid")
    if record["temporality"] not in TEMPORALITY:
        raise ValueError("measurement.temporality is invalid")
    if record["measurement_status"] not in MEASUREMENT_STATUS:
        raise ValueError("measurement.measurement_status is invalid")
    value = record["value"]
    if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value)):
        raise ValueError("measurement.value must be a finite number or null")
    if record["measurement_status"] in {"measured", "estimated"} and value is None:
        raise ValueError("measured/estimated measurements require a numeric value")
    if record["measurement_status"] in {"activity_only", "not_established"} and value is not None:
        raise ValueError("activity_only/not_established measurements must have null value")
    if record["unit"] is not None and (not isinstance(record["unit"], str) or not record["unit"] or len(record["unit"]) > 64):
        raise ValueError("measurement.unit must be a non-empty string <= 64 characters or null")
    parse_timestamp(record["observed_at"], "measurement.observed_at")
    if "event_at" in record:
        parse_timestamp(record["event_at"], "measurement.event_at", nullable=True)
    dimensions = record["dimensions"]
    if not isinstance(dimensions, dict) or len(dimensions) > 32:
        raise ValueError("measurement.dimensions must be an object with at most 32 keys")
    for key, dimension in dimensions.items():
        if not isinstance(key, str) or not isinstance(dimension, (str, int, float, bool)) and dimension is not None:
            raise ValueError("measurement.dimensions values must be scalar")
        if isinstance(dimension, float) and not math.isfinite(dimension):
            raise ValueError("measurement.dimensions values must be finite")
    provenance = record["provenance"]
    _keys(provenance, {"provider", "capture_method", "attribution", "adapter_version"}, "measurement.provenance")
    _required(provenance, {"provider", "capture_method", "attribution"}, "measurement.provenance")
    _nonempty(provenance["provider"], "measurement.provenance.provider", 200)
    _nonempty(provenance["capture_method"], "measurement.provenance.capture_method", 200)
    if provenance["attribution"] not in ATTRIBUTION:
        raise ValueError("measurement.provenance.attribution is invalid")
    if record.get("evidence_ref") is not None:
        ref = record["evidence_ref"]
        if not isinstance(ref, str) or len(ref) > 1000 or not urlsplit(ref).scheme:
            raise ValueError("measurement.evidence_ref must be a URI or null")
    if record.get("confidence") is not None and record["confidence"] not in CONFIDENCE:
        raise ValueError("measurement.confidence is invalid")
    if record.get("supersedes") is not None:
        _nonempty(record["supersedes"], "measurement.supersedes", 200)
    if provenance.get("adapter_version") is not None:
        _nonempty(provenance["adapter_version"], "measurement.provenance.adapter_version", 100)
    _reject_sensitive(record)
    return record


def canonical_json(record: dict) -> str:
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def load_jsonl(path: str, validator) -> list[dict]:
    if not path:
        return []
    records = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                validator(record)
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            records.append(record)
    return records


def load_batch_metadata(path: str) -> dict:
    if not path:
        return {"event": {}, "measurement": {}}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: invalid batch metadata JSON: {exc}") from exc
    _keys(data, {"event", "measurement"}, "batch_metadata")
    result = {"event": {}, "measurement": {}}
    for record_type, integrations in data.items():
        if not isinstance(integrations, dict):
            raise ValueError(f"batch_metadata.{record_type} must be an object")
        for integration_id, cursors in integrations.items():
            if not INTEGRATION_RE.fullmatch(integration_id):
                raise ValueError(f"batch_metadata integration_id is invalid: {integration_id!r}")
            _keys(cursors, {"cursor_before", "cursor_after"}, f"batch_metadata.{record_type}.{integration_id}")
            result[record_type][integration_id] = {
                "cursor_before": validate_cursor(cursors.get("cursor_before"), "cursor_before"),
                "cursor_after": validate_cursor(cursors.get("cursor_after"), "cursor_after"),
            }
    _reject_sensitive(result)
    return result


def group_by_integration(records: list[dict]) -> OrderedDict[str, list[dict]]:
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for record in records:
        groups.setdefault(record["integration_id"], []).append(record)
    return groups


def chunk_records(records: list[dict], max_records: int = DEFAULT_MAX_RECORDS,
                  max_bytes: int = DEFAULT_MAX_BYTES) -> list[list[dict]]:
    if not 1 <= max_records <= HARD_MAX_RECORDS:
        raise ValueError(f"max_records must be between 1 and {HARD_MAX_RECORDS}")
    if not 1 <= max_bytes <= HARD_MAX_BYTES:
        raise ValueError(f"max_bytes must be between 1 and {HARD_MAX_BYTES}")
    chunks, current, current_bytes = [], [], 0
    for record in records:
        size = len(canonical_json(record).encode("utf-8")) + 1
        if size > max_bytes:
            raise ValueError(f"single record exceeds max batch bytes ({size} > {max_bytes})")
        if current and (len(current) >= max_records or current_bytes + size > max_bytes):
            chunks.append(current)
            current, current_bytes = [], 0
        current.append(record)
        current_bytes += size
    if current:
        chunks.append(current)
    return chunks


def sql_literal(value: str | None) -> str:
    if value is None:
        return "NULL"
    if not isinstance(value, str):
        raise TypeError("SQL literal must be a string or None")
    return "'" + value.replace("'", "''") + "'"


def build_batch_sql(records: list[dict], record_type: str, batch_id: str,
                    adapter_version: str = ADAPTER_VERSION,
                    cursor_before: str | None = None,
                    cursor_after: str | None = None) -> tuple[str, dict]:
    if record_type not in {"event", "measurement"} or not records:
        raise ValueError("record_type must be event/measurement and records must be non-empty")
    if not isinstance(adapter_version, str) or not ADAPTER_VERSION_RE.fullmatch(adapter_version):
        raise ValueError("adapter_version must match the safe 1..100 character identifier pattern")
    cursor_before = validate_cursor(cursor_before, "cursor_before")
    cursor_after = validate_cursor(cursor_after, "cursor_after")
    integration_id = records[0]["integration_id"]
    if any(r["integration_id"] != integration_id for r in records):
        raise ValueError("a batch must contain exactly one integration_id")
    lines = [canonical_json(r) for r in records]
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    payload_sha = hashlib.sha256(payload).hexdigest()
    payload_bytes = len(payload)
    started_at = now_iso()
    batch_id = str(uuid.UUID(batch_id))
    values = ",\n".join(f"({sql_literal(line)}::jsonb)" for line in lines)

    if record_type == "event":
        insert = f"""
WITH inserted AS (
  INSERT INTO integration_events (
    event_id, integration_id, event_type, repository, commit_sha,
    pull_request, workflow_run_id, provider_request_id,
    execution_status, started_at, completed_at, duration_ms,
    outcome_state, outcome_summary, confidence, evidence, provenance,
    privacy, idempotency_key, event_at, observed_at, batch_id, envelope
  )
  SELECT
    doc->>'event_id', doc->>'integration_id', doc->>'event_type',
    doc#>>'{{source,repository}}', doc#>>'{{source,commit_sha}}',
    NULLIF(doc#>>'{{source,pull_request}}','')::bigint,
    NULLIF(doc#>>'{{source,workflow_run_id}}','')::bigint,
    doc#>>'{{source,provider_request_id}}',
    doc#>>'{{execution,status}}',
    NULLIF(doc#>>'{{execution,started_at}}','')::timestamptz,
    NULLIF(doc#>>'{{execution,completed_at}}','')::timestamptz,
    NULLIF(doc#>>'{{execution,duration_ms}}','')::bigint,
    doc#>>'{{outcome,state}}', COALESCE(doc#>>'{{outcome,summary}}',''),
    doc#>>'{{outcome,confidence}}', doc->'evidence', doc->'provenance',
    COALESCE(doc->'privacy','{{}}'::jsonb), doc->>'idempotency_key',
    NULLIF(doc->>'event_at','')::timestamptz,
    COALESCE(NULLIF(doc->>'observed_at','')::timestamptz, clock_timestamp()),
    {sql_literal(batch_id)}::uuid, doc
  FROM _integration_batch_docs
  WHERE true
  ON CONFLICT (integration_id, idempotency_key) DO NOTHING
  RETURNING event_id
)
"""
    else:
        insert = f"""
WITH inserted AS (
  INSERT INTO integration_measurements (
    measurement_id, event_id, integration_id, metric_name, metric_type,
    value, unit, temporality, measurement_status, event_at, observed_at,
    dimensions, provenance, evidence_ref, confidence, idempotency_key,
    supersedes, batch_id, record
  )
  SELECT
    doc->>'measurement_id', doc->>'event_id', doc->>'integration_id',
    doc->>'metric_name', doc->>'metric_type',
    NULLIF(doc->>'value','')::double precision, doc->>'unit',
    doc->>'temporality', doc->>'measurement_status',
    NULLIF(doc->>'event_at','')::timestamptz,
    (doc->>'observed_at')::timestamptz, doc->'dimensions', doc->'provenance',
    doc->>'evidence_ref', doc->>'confidence', doc->>'idempotency_key',
    doc->>'supersedes', {sql_literal(batch_id)}::uuid, doc
  FROM _integration_batch_docs
  WHERE true
  ON CONFLICT (idempotency_key) DO NOTHING
  RETURNING measurement_id
)
"""
    receipt = f"""
, counts AS (SELECT count(*)::integer AS inserted_count FROM inserted)
INSERT INTO integration_ingest_batches (
  batch_id, integration_id, adapter_version, record_type, status,
  records_received, records_inserted, records_duplicates, records_rejected,
  payload_bytes, payload_sha256, cursor_before, cursor_after, started_at, completed_at
)
SELECT
  {sql_literal(batch_id)}::uuid, {sql_literal(integration_id)},
  {sql_literal(adapter_version)}, {sql_literal(record_type)}, 'emitted',
  {len(records)}, counts.inserted_count, {len(records)} - counts.inserted_count,
  0, {payload_bytes}, {sql_literal(payload_sha)}, {sql_literal(cursor_before)},
  {sql_literal(cursor_after)}, {sql_literal(started_at)}::timestamptz, clock_timestamp()
FROM counts
RETURNING records_inserted::text || '|' || records_duplicates::text;
"""
    cursor_guard = ""
    if cursor_after is not None:
        # A random tag prevents untrusted cursor text from terminating the DO body.
        guard_tag = "cursor_guard_" + uuid.uuid4().hex
        cursor_guard = f"""
DO ${guard_tag}$
DECLARE current_cursor text;
BEGIN
  PERFORM pg_advisory_xact_lock(hashtextextended(
    {sql_literal(integration_id + ":" + record_type)}, 0
  ));
  SELECT cursor_after INTO current_cursor
  FROM integration_latest_cursors
  WHERE integration_id = {sql_literal(integration_id)}
    AND record_type = {sql_literal(record_type)};
  IF current_cursor IS DISTINCT FROM {sql_literal(cursor_before)}
     AND current_cursor IS DISTINCT FROM {sql_literal(cursor_after)} THEN
    RAISE EXCEPTION 'integration_cursor_conflict';
  END IF;
END
${guard_tag}$;
"""
    sql = (
        "SET standard_conforming_strings = on;\n"
        "BEGIN;\n"
        + cursor_guard
        + "CREATE TEMP TABLE _integration_batch_docs (doc jsonb NOT NULL) ON COMMIT DROP;\n"
        + "INSERT INTO _integration_batch_docs(doc) VALUES\n" + values + ";\n"
        + insert + receipt + "COMMIT;\n"
    )
    meta = {
        "batch_id": batch_id, "integration_id": integration_id,
        "record_type": record_type, "records_received": len(records),
        "payload_bytes": payload_bytes, "payload_sha256": payload_sha,
        "started_at": started_at, "cursor_before": cursor_before,
        "cursor_after": cursor_after,
    }
    return sql, meta


def record_failed_batch(url: str, meta: dict, adapter_version: str,
                        error_class: str) -> None:
    """Persist a failure receipt after the data transaction has rolled back."""
    sql = f"""
INSERT INTO integration_ingest_batches (
  batch_id, integration_id, adapter_version, record_type, status,
  records_received, records_inserted, records_duplicates, records_rejected,
  payload_bytes, payload_sha256, cursor_before, cursor_after, started_at, completed_at, error_class
) VALUES (
  {sql_literal(meta["batch_id"])}::uuid, {sql_literal(meta["integration_id"])},
  {sql_literal(adapter_version)}, {sql_literal(meta["record_type"])}, 'failed',
  {meta["records_received"]}, 0, 0, 0, {meta["payload_bytes"]},
  {sql_literal(meta["payload_sha256"])}, {sql_literal(meta.get("cursor_before"))}, NULL,
  {sql_literal(meta["started_at"])}::timestamptz, clock_timestamp(), {sql_literal(error_class)}
) ON CONFLICT (batch_id) DO NOTHING;
"""
    lane_event.psql(url, ["-c", sql])


def run_batch(url: str, records: list[dict], record_type: str,
              adapter_version: str = ADAPTER_VERSION,
              cursor_before: str | None = None,
              cursor_after: str | None = None) -> dict:
    batch_id = str(uuid.uuid4())
    sql, meta = build_batch_sql(records, record_type, batch_id, adapter_version, cursor_before, cursor_after)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".sql", delete=False) as handle:
            handle.write(sql)
            temp_path = handle.name
        output = lane_event.psql(url, ["-At", "-f", temp_path]).strip().splitlines()
        if not output:
            raise RuntimeError("database batch returned no receipt counts")
        parts = output[-1].split("|")
        if len(parts) != 2:
            raise RuntimeError("database batch returned malformed receipt counts")
        meta["records_inserted"] = int(parts[0])
        meta["records_duplicates"] = int(parts[1])
        meta["status"] = "emitted"
        return meta
    except Exception as exc:
        try:
            record_failed_batch(url, meta, adapter_version, type(exc).__name__)
        except Exception:
            pass
        raise
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink()
            except OSError:
                pass


class BlockedError(RuntimeError):
    """A missing least-privilege credential or prerequisite requiring operator action."""


def resolve_writer_url() -> str | None:
    """Resolve a dedicated writer URL; never fall back to the legacy owner credential."""
    url = os.environ.get("LANE_EVENTS_WRITER_DATABASE_URL", "").strip()
    if url:
        return url
    key = os.environ.get("NEON_API_KEY", "").strip()
    if not key:
        return None
    project_name = lane_event.NEON_PROJECT
    projects = lane_event._neon("GET", f"/projects?search={quote(project_name)}&limit=50", key).get("projects", [])
    project = next((p for p in projects if p.get("name") == project_name), None)
    if project is None:
        raise BlockedError(f"existing Neon project {project_name!r} was not found; project creation is disabled")
    branches = []
    cursor = None
    while True:
        endpoint = f"/projects/{project['id']}/branches" + (f"?cursor={quote(cursor)}" if cursor else "")
        page = lane_event._neon("GET", endpoint, key)
        branches.extend(page.get("branches", []))
        cursor = (page.get("pagination") or {}).get("next")
        if not cursor:
            break
    branch = next((b for b in branches if b.get("default")), None)
    if branch is None:
        raise BlockedError("existing Neon project has no default branch")
    roles = lane_event._neon("GET", f"/projects/{project['id']}/branches/{branch['id']}/roles", key).get("roles", [])
    role = next((r["name"] for r in roles if r.get("name") in {"integration_ingest", "lane_events_writer"}), None)
    if role is None:
        raise BlockedError("dedicated integration_ingest/lane_events_writer role is absent; operator must provision least-privilege access")
    path = f"/projects/{project['id']}/connection_uri?database_name=neondb&role_name={quote(role)}&branch_id={quote(branch['id'])}"
    return lane_event._neon("GET", path, key)["uri"]


def resolve_read_url() -> str | None:
    """Prefer a read-only URL; otherwise use the dedicated writer role with SELECT grants."""
    url = os.environ.get("LANE_EVENTS_READONLY_DATABASE_URL", "").strip()
    return url or resolve_writer_url()


def resolve_migration_url() -> str | None:
    """Schema DDL requires a separately provisioned operator migration credential."""
    return os.environ.get("LANE_EVENTS_MIGRATION_DATABASE_URL", "").strip() or None


def validate_cursor(value: str | None, field: str) -> str | None:
    if value is None:
        return None
    _nonempty(value, field, 512)
    _reject_sensitive(value)
    return value


def plan(records: list[dict], max_records: int, max_bytes: int,
         cursor_metadata: dict | None = None) -> list[dict]:
    out = []
    cursor_metadata = cursor_metadata or {}
    groups = group_by_integration(records)
    unused = set(cursor_metadata) - set(groups)
    if unused:
        raise ValueError(f"batch cursor metadata references integrations absent from records: {sorted(unused)}")
    for integration_id, group in groups.items():
        chunks = chunk_records(group, max_records, max_bytes)
        cursors = cursor_metadata.get(integration_id, {})
        before = validate_cursor(cursors.get("cursor_before"), "cursor_before")
        after = validate_cursor(cursors.get("cursor_after"), "cursor_after")
        batches = []
        for index, chunk in enumerate(chunks):
            batch = {
                "records": len(chunk),
                "payload_bytes": len(("\n".join(canonical_json(x) for x in chunk) + "\n").encode("utf-8")),
            }
            if (index == 0 or index == len(chunks) - 1) and before is not None:
                batch["cursor_before"] = before
            if index == len(chunks) - 1 and after is not None:
                batch["cursor_after"] = after
            batches.append(batch)
        out.append({"integration_id": integration_id, "records": len(group), "batches": batches})
    return out


def ingest(url: str, records: list[dict], record_type: str,
           max_records: int, max_bytes: int,
           adapter_version: str = ADAPTER_VERSION,
           cursor_metadata: dict | None = None) -> list[dict]:
    results = []
    cursor_metadata = cursor_metadata or {}
    groups = group_by_integration(records)
    unused = set(cursor_metadata) - set(groups)
    if unused:
        raise ValueError(f"batch cursor metadata references integrations absent from records: {sorted(unused)}")
    for integration_id, group in groups.items():
        chunks = chunk_records(group, max_records, max_bytes)
        cursors = cursor_metadata.get(integration_id, {})
        before = validate_cursor(cursors.get("cursor_before"), "cursor_before")
        after = validate_cursor(cursors.get("cursor_after"), "cursor_after")
        for index, chunk in enumerate(chunks):
            results.append(run_batch(
                url, chunk, record_type, adapter_version,
                before if index == 0 or index == len(chunks) - 1 else None,
                after if index == len(chunks) - 1 else None,
            ))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("record", "schema", "count"), default="record")
    parser.add_argument("--events-file", default="")
    parser.add_argument("--measurements-file", default="")
    parser.add_argument("--max-batch-records", type=int, default=DEFAULT_MAX_RECORDS)
    parser.add_argument("--max-batch-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--adapter-version", default=ADAPTER_VERSION)
    parser.add_argument("--batch-metadata-file", default="", help="JSON cursors keyed by record type and integration_id")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    try:
        if not 1 <= args.max_batch_records <= HARD_MAX_RECORDS:
            raise ValueError(f"--max-batch-records must be 1..{HARD_MAX_RECORDS}")
        if not 1 <= args.max_batch_bytes <= HARD_MAX_BYTES:
            raise ValueError(f"--max-batch-bytes must be 1..{HARD_MAX_BYTES}")
        if not ADAPTER_VERSION_RE.fullmatch(args.adapter_version):
            raise ValueError("--adapter-version must match the safe 1..100 character identifier pattern")

        events = load_jsonl(args.events_file, validate_event)
        measurements = load_jsonl(args.measurements_file, validate_measurement)
        batch_metadata = load_batch_metadata(args.batch_metadata_file)
        if args.command == "record" and args.dry_run:
            print(json.dumps({
                "status": "validated_dry_run",
                "events": plan(events, args.max_batch_records, args.max_batch_bytes, batch_metadata["event"]),
                "measurements": plan(measurements, args.max_batch_records, args.max_batch_bytes, batch_metadata["measurement"]),
            }, sort_keys=True))
            return 0
        if args.command == "record" and not events and not measurements:
            if batch_metadata["event"] or batch_metadata["measurement"]:
                raise ValueError("batch cursor metadata cannot advance without corresponding records")
            print(json.dumps({"status": "clean_noop", "events": 0, "measurements": 0}))
            return 0

        if args.command == "schema":
            url = resolve_migration_url()
            if not url:
                print(json.dumps({"status": "blocked", "reason": "LANE_EVENTS_MIGRATION_DATABASE_URL is unavailable"}))
                return 2
            lane_event.psql(url, ["-f", str(SQL_DIR / "integration-events.sql")])
            print(json.dumps({"status": "schema_applied", "database": "existing-lane-events"}))
            return 0

        if args.command == "count":
            url = resolve_read_url()
            if not url:
                print(json.dumps({"status": "blocked", "reason": "LANE_EVENTS_READONLY_DATABASE_URL or dedicated writer role is unavailable"}))
                return 2
            output = lane_event.psql(
                url, ["-At", "-c",
                      "SELECT (SELECT count(*) FROM integration_events),"
                      "(SELECT count(*) FROM integration_measurements),"
                      "(SELECT count(*) FROM integration_ingest_batches)"]
            ).strip()
            print(json.dumps({"status": "observed", "counts": output}))
            return 0

        try:
            url = resolve_writer_url()
        except BlockedError as exc:
            print(json.dumps({"status": "blocked", "reason": str(exc)}))
            return 2
        if not url:
            print(json.dumps({"status": "blocked", "reason": "LANE_EVENTS_WRITER_DATABASE_URL or dedicated integration_ingest role is unavailable"}))
            return 2

        event_receipts = ingest(url, events, "event", args.max_batch_records, args.max_batch_bytes, args.adapter_version, batch_metadata["event"])
        measurement_receipts = ingest(url, measurements, "measurement", args.max_batch_records, args.max_batch_bytes, args.adapter_version, batch_metadata["measurement"])
        print(json.dumps({
            "status": "emitted",
            "events": {"received": len(events), "batches": event_receipts},
            "measurements": {"received": len(measurements), "batches": measurement_receipts},
        }, sort_keys=True))
        return 0
    except BlockedError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:300]}), file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "failed", "error_class": "TimeoutExpired", "message": "database command timed out; connection details suppressed"}), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(json.dumps({"status": "failed", "error_class": type(exc).__name__, "message": str(exc)[:300]}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
