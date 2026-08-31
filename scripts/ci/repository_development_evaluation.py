#!/usr/bin/env python3
"""Build and audit redacted repository-development evaluation manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
EXPECTED = {
    "schema_version",
    "subject_type",
    "subject_key",
    "source_revision",
    "adapter",
    "collected_at",
    "lifecycle",
    "metrics",
    "result_digest",
}
RAW_EXPECTED = EXPECTED - {"schema_version", "result_digest"}
ADAPTER = "repository-pr-lifecycle"
SUBJECT_KEY = re.compile(r"^pr-[1-9][0-9]{0,9}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
SECRET = re.compile(
    r"(?i)(?:ghp|github_pat|sk|tskey|AIza|client_secret|api[_-]?key)"
    r"[-_a-z0-9]{6,}"
)
LIFECYCLE_FIELDS = {"state", "opened_at", "updated_at", "closed_at", "merged_at"}
METRIC_FIELDS = {
    "commit_count",
    "changed_file_count",
    "additions",
    "deletions",
    "review_count",
    "unresolved_thread_count",
    "check_success_count",
    "check_failure_count",
    "check_cancelled_count",
    "check_pending_count",
    "automation_marker_count",
    "first_automation_response_at",
}


class ContractError(ValueError):
    """Raised when a repository-development evaluation manifest is invalid."""


def canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "result_digest"}


def digest(payload: dict[str, Any]) -> str:
    serialized = json.dumps(canonical_payload(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be an RFC 3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} is not a valid timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def required_string(payload: dict[str, Any], field: str, pattern: re.Pattern[str] | None = None) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be a non-empty string")
    if pattern and not pattern.fullmatch(value):
        raise ContractError(f"{field} has an invalid format")
    return value


def nullable_timestamp(payload: dict[str, Any], key: str, label: str | None = None) -> datetime | None:
    value = payload.get(key)
    if value is None:
        return None
    return timestamp(value, label or key)


def nonnegative(value: Any, field: str, *, nullable: bool = False) -> int | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{field} must be a non-negative integer")
    return value


def exact_fields(payload: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(payload)
    unknown = set(payload) - expected
    if missing or unknown:
        raise ContractError(f"{label} missing={sorted(missing)} unknown={sorted(unknown)}")


def validate(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ContractError("manifest root must be an object")
    exact_fields(payload, EXPECTED, "manifest")
    if SECRET.search(json.dumps(payload, sort_keys=True)):
        raise ContractError("manifest contains a credential-shaped value")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unsupported schema_version")
    if payload["subject_type"] != "pull-request":
        raise ContractError("subject_type must be pull-request")
    required_string(payload, "subject_key", SUBJECT_KEY)
    required_string(payload, "source_revision", REVISION)
    if payload["adapter"] != ADAPTER:
        raise ContractError("adapter is not allowlisted")
    collected_at = timestamp(payload["collected_at"], "collected_at")

    lifecycle = payload["lifecycle"]
    if not isinstance(lifecycle, dict):
        raise ContractError("lifecycle must be an object")
    exact_fields(lifecycle, LIFECYCLE_FIELDS, "lifecycle")
    state = required_string(lifecycle, "state")
    if state not in {"open", "closed", "merged"}:
        raise ContractError("lifecycle.state is not allowlisted")
    opened_at = timestamp(lifecycle["opened_at"], "lifecycle.opened_at")
    updated_at = timestamp(lifecycle["updated_at"], "lifecycle.updated_at")
    closed_at = nullable_timestamp(lifecycle, "closed_at", "lifecycle.closed_at")
    merged_at = nullable_timestamp(lifecycle, "merged_at", "lifecycle.merged_at")
    if updated_at < opened_at or collected_at < opened_at:
        raise ContractError("lifecycle timestamps are not monotonic")
    if state == "open" and (closed_at is not None or merged_at is not None):
        raise ContractError("open lifecycle cannot include close or merge timestamp")
    if state == "closed" and (closed_at is None or merged_at is not None):
        raise ContractError("closed lifecycle requires closed_at and forbids merged_at")
    if state == "merged" and (closed_at is None or merged_at is None):
        raise ContractError("merged lifecycle requires closed_at and merged_at")

    metrics = payload["metrics"]
    if not isinstance(metrics, dict):
        raise ContractError("metrics must be an object")
    exact_fields(metrics, METRIC_FIELDS, "metrics")
    for field in METRIC_FIELDS - {"unresolved_thread_count", "first_automation_response_at"}:
        nonnegative(metrics[field], f"metrics.{field}")
    nonnegative(metrics["unresolved_thread_count"], "metrics.unresolved_thread_count", nullable=True)
    first_response = nullable_timestamp(metrics, "first_automation_response_at", "metrics.first_automation_response_at")
    if first_response is not None and first_response < opened_at:
        raise ContractError("first automation response precedes pull-request opening")
    if metrics["check_success_count"] + metrics["check_failure_count"] + metrics["check_cancelled_count"] + metrics["check_pending_count"] == 0:
        raise ContractError("metrics must describe at least one check state")
    required_string(payload, "result_digest", DIGEST)
    if payload["result_digest"] != digest(payload):
        raise ContractError("result_digest does not match canonical manifest")


def build(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ContractError("raw evidence root must be an object")
    exact_fields(raw, RAW_EXPECTED, "raw evidence")
    payload = {"schema_version": SCHEMA_VERSION, **raw}
    payload["result_digest"] = digest(payload)
    validate(payload)
    return payload


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot load JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError("JSON root must be an object")
    return payload


def command_manifest(arguments: argparse.Namespace) -> int:
    try:
        payload = build(load_json(Path(arguments.input)))
        output = Path(arguments.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote repository-development manifest {output}")
    return 0


def command_audit(arguments: argparse.Namespace) -> int:
    try:
        payload = load_json(Path(arguments.manifest))
        validate(payload)
    except ContractError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: repository-development manifest {payload['subject_key']} ({payload['lifecycle']['state']})")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    manifest = commands.add_parser("manifest", help="Build a canonical result manifest from raw evidence")
    manifest.add_argument("--input", required=True)
    manifest.add_argument("--output", required=True)
    manifest.set_defaults(handler=command_manifest)
    audit = commands.add_parser("audit", help="Audit a canonical repository-development manifest")
    audit.add_argument("manifest")
    audit.set_defaults(handler=command_audit)
    return root


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    return arguments.handler(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
