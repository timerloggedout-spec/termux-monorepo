#!/usr/bin/env python3
"""Create and audit redacted manifests for bounded SWE-reference evaluation runs."""

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
ALLOWED_REFERENCES = {"mini-swe-agent", "swe-agent"}
ALLOWED_BENCHMARKS = {"lite", "verified"}
ALLOWED_SPLITS = {"dev", "test"}
ALLOWED_STATES = {"agent-run-complete", "agent-run-failed"}
EXPECTED_FIELDS = {
    "schema_version",
    "run_id",
    "reference",
    "reference_revision",
    "benchmark",
    "split",
    "slice",
    "model_id",
    "started_at",
    "finished_at",
    "runner_exit_code",
    "agent_completed_instances",
    "benchmark_resolved_instances",
    "evaluation_state",
    "result_digest",
}
RUN_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,96}$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,191}$")
SECRET = re.compile(
    r"(?i)(?:ghp|github_pat|sk|tskey|AIza|client_secret|api[_-]?key)"
    r"[-_a-z0-9]{6,}"
)


class ContractError(ValueError):
    """Raised when a result manifest violates the evaluation contract."""


def canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "result_digest"}


def digest(payload: dict[str, Any]) -> str:
    serialized = json.dumps(canonical_payload(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be an RFC 3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} is not a valid timestamp") from exc
    if parsed.tzinfo is None:
        raise ContractError(f"{field} must include a timezone")
    return parsed.astimezone(UTC)


def require_string(payload: dict[str, Any], field: str, pattern: re.Pattern[str] | None = None) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be a non-empty string")
    if pattern is not None and not pattern.fullmatch(value):
        raise ContractError(f"{field} has an invalid format")
    return value


def require_nonnegative_int(payload: dict[str, Any], field: str) -> int:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractError(f"{field} must be a non-negative integer")
    return value


def validate(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ContractError("manifest root must be an object")
    missing = EXPECTED_FIELDS - set(payload)
    unknown = set(payload) - EXPECTED_FIELDS
    if missing or unknown:
        raise ContractError(f"missing={sorted(missing)} unknown={sorted(unknown)}")
    if SECRET.search(json.dumps(payload, sort_keys=True)):
        raise ContractError("manifest contains a credential-shaped value")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ContractError("unsupported schema_version")

    require_string(payload, "run_id", RUN_ID)
    reference = require_string(payload, "reference")
    if reference not in ALLOWED_REFERENCES:
        raise ContractError("reference is not allowlisted")
    require_string(payload, "reference_revision", REVISION)
    benchmark = require_string(payload, "benchmark")
    if benchmark not in ALLOWED_BENCHMARKS:
        raise ContractError("benchmark is not allowlisted")
    split = require_string(payload, "split")
    if split not in ALLOWED_SPLITS:
        raise ContractError("split is not allowlisted")
    if payload["slice"] != "0:1":
        raise ContractError("slice must remain bounded to 0:1")
    require_string(payload, "model_id", MODEL_ID)

    started_at = parse_timestamp(payload["started_at"], "started_at")
    finished_at = parse_timestamp(payload["finished_at"], "finished_at")
    if finished_at < started_at:
        raise ContractError("finished_at precedes started_at")

    exit_code = require_nonnegative_int(payload, "runner_exit_code")
    if exit_code > 255:
        raise ContractError("runner_exit_code must be between 0 and 255")
    completed = require_nonnegative_int(payload, "agent_completed_instances")
    if completed > 1:
        raise ContractError("agent_completed_instances exceeds the bounded slice")
    resolved = payload["benchmark_resolved_instances"]
    if resolved is not None:
        if isinstance(resolved, bool) or not isinstance(resolved, int) or resolved < 0 or resolved > completed:
            raise ContractError("benchmark_resolved_instances must be null or within completed instances")

    state = require_string(payload, "evaluation_state")
    if state not in ALLOWED_STATES:
        raise ContractError("evaluation_state is not allowlisted")
    if (exit_code == 0) != (state == "agent-run-complete"):
        raise ContractError("evaluation_state must agree with runner_exit_code")
    require_string(payload, "result_digest", DIGEST)
    if payload["result_digest"] != digest(payload):
        raise ContractError("result_digest does not match the canonical manifest")


def now_utc() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_predictions(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"cannot read predictions JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ContractError("predictions JSON must be an object")
    return len(payload)


def build_manifest(arguments: argparse.Namespace) -> dict[str, Any]:
    completed = load_predictions(Path(arguments.predictions))
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": arguments.run_id,
        "reference": arguments.reference,
        "reference_revision": arguments.reference_revision,
        "benchmark": arguments.benchmark,
        "split": arguments.split,
        "slice": "0:1",
        "model_id": arguments.model_id,
        "started_at": arguments.started_at,
        "finished_at": arguments.finished_at or now_utc(),
        "runner_exit_code": arguments.runner_exit_code,
        "agent_completed_instances": completed,
        "benchmark_resolved_instances": None,
        "evaluation_state": "agent-run-complete" if arguments.runner_exit_code == 0 else "agent-run-failed",
    }
    payload["result_digest"] = digest(payload)
    validate(payload)
    return payload


def command_audit(arguments: argparse.Namespace) -> int:
    try:
        payload = json.loads(Path(arguments.manifest).read_text(encoding="utf-8"))
        validate(payload)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: SWE evaluation manifest {payload['run_id']} ({payload['evaluation_state']})")
    return 0


def command_manifest(arguments: argparse.Namespace) -> int:
    try:
        payload = build_manifest(arguments)
        output = Path(arguments.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ContractError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote SWE evaluation manifest {output}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    audit = commands.add_parser("audit", help="Validate a redacted evaluation manifest")
    audit.add_argument("manifest")
    audit.set_defaults(handler=command_audit)

    manifest = commands.add_parser("manifest", help="Create a redacted evaluation manifest")
    manifest.add_argument("--output", required=True)
    manifest.add_argument("--run-id", required=True)
    manifest.add_argument("--reference", required=True)
    manifest.add_argument("--reference-revision", required=True)
    manifest.add_argument("--benchmark", required=True)
    manifest.add_argument("--split", required=True)
    manifest.add_argument("--model-id", required=True)
    manifest.add_argument("--started-at", required=True)
    manifest.add_argument("--finished-at")
    manifest.add_argument("--runner-exit-code", required=True, type=int)
    manifest.add_argument("--predictions", required=True)
    manifest.set_defaults(handler=command_manifest)
    return root


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    return arguments.handler(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
