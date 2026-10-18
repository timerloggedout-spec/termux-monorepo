#!/usr/bin/env python3
"""Validate FOSS procurement decisions and edge/manager evidence contracts offline.

This checks structure and decision guardrails; it does not run workloads, verify
vendor claims, or label a target portable without real target-specific evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

HORIZONS = {"H0", "H1", "H2", "H3"}
CONFIDENCE = {"high", "medium", "low", "unknown"}
DECISIONS = {"WATCH", "INVESTIGATE", "PROTOTYPE", "ADOPT", "REJECT", "HOLD"}
PORTABILITY_TARGETS = {"arm64_linux", "x86_64_linux", "android", "termux", "offline_airgapped"}
PROCUREMENT_REQUIRED = {
    "resource_id", "project", "canonical_source", "license", "maintenance", "portability",
    "offline_capability", "interoperability", "reproducibility", "provenance",
    "dependency_risk", "lock_in_risk", "security_surface", "resource_cost",
    "operational_fit", "horizon", "confidence", "decision_status", "version_or_commit",
    "observed_at", "unresolved_questions",
}
EDGE_REQUIRED = {
    "schema_version", "experiment_id", "device_abi", "model_hash", "runtime",
    "backend", "observed_at", "provenance",
}
EDGE_FIELDS = EDGE_REQUIRED | {
    "device_model", "os_version", "model_family", "quantization", "runtime_version",
    "tokens_per_second", "latency_p50_ms", "latency_p95_ms", "peak_memory_mb",
    "thermal_state", "energy_proxy", "offline", "fallback_path",
}
EDGE_PROVENANCE_REQUIRED = {"repository_sha", "environment_fingerprint"}
EDGE_PROVENANCE_FIELDS = EDGE_PROVENANCE_REQUIRED | {"runtime_source", "model_source"}
TOURNAMENT_REQUIRED = {
    "schema_version", "tournament_id", "cohort_id", "policy_version", "task_contract_hash",
    "environment_fingerprint", "managers", "evaluation_contract", "provenance",
}
TOURNAMENT_FIELDS = TOURNAMENT_REQUIRED
TOURNAMENT_PROVENANCE_REQUIRED = {"created_at", "repository_sha"}
TOURNAMENT_PROVENANCE_FIELDS = TOURNAMENT_PROVENANCE_REQUIRED | {"benchmark_source"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
GIT_SHA_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except ValueError:
        return False


def utc_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not UTC_RE.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def unverified(value: Any) -> bool:
    if not isinstance(value, str):
        return True
    normalized = value.strip().upper()
    return normalized in {"", "VERIFY", "UNKNOWN", "TBD", "PENDING", "UNVERIFIED", "NOT TESTED"} or normalized.startswith(
        ("VERIFY ", "UNKNOWN ", "TBD ", "PENDING ", "UNVERIFIED ", "NOT TESTED ")
    )


def validate_procurement_record(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record: expected JSON object"]
    for key in sorted(PROCUREMENT_REQUIRED - set(record)):
        errors.append(f"{key}: required field missing")
    for key in ("resource_id", "project", "license", "maintenance", "offline_capability",
                "interoperability", "reproducibility", "provenance", "dependency_risk",
                "lock_in_risk", "security_surface", "resource_cost", "operational_fit",
                "version_or_commit"):
        if key in record and not nonempty(record[key]):
            errors.append(f"{key}: expected non-empty string")
    lock_in = record.get("lock_in_risk")
    if not isinstance(lock_in, dict):
        errors.append("lock_in_risk: expected object with runtime and evidence dimensions")
    else:
        for field in ("runtime", "evidence"):
            if not nonempty(lock_in.get(field)):
                errors.append(f"lock_in_risk.{field}: expected non-empty string")
    if not http_url(record.get("canonical_source")):
        errors.append("canonical_source: expected absolute HTTP(S) URL")
    if record.get("horizon") not in HORIZONS:
        errors.append(f"horizon: expected one of {sorted(HORIZONS)}")
    if record.get("confidence") not in CONFIDENCE:
        errors.append(f"confidence: expected one of {sorted(CONFIDENCE)}")
    if record.get("decision_status") not in DECISIONS:
        errors.append(f"decision_status: expected one of {sorted(DECISIONS)}")
    if not utc_timestamp(record.get("observed_at")):
        errors.append("observed_at: expected UTC ISO-8601 timestamp ending in Z")
    questions = record.get("unresolved_questions")
    if not isinstance(questions, list) or any(not nonempty(q) for q in questions):
        errors.append("unresolved_questions: expected list of non-empty strings")
    portability = record.get("portability")
    if not isinstance(portability, dict):
        errors.append("portability: expected object with explicit target entries")
    else:
        for target in sorted(PORTABILITY_TARGETS):
            if not nonempty(portability.get(target)):
                errors.append(f"portability.{target}: required target status missing")
    if record.get("decision_status") == "ADOPT":
        for field in ("license", "maintenance", "version_or_commit", "offline_capability"):
            if unverified(record.get(field)):
                errors.append(f"ADOPT requires verified {field}; found {record.get(field)!r}")
        if isinstance(portability, dict):
            for target in sorted(PORTABILITY_TARGETS):
                value = portability.get(target)
                if not isinstance(value, str) or not value.strip().upper().startswith(
                    ("TESTED: PASS", "TESTED: FAIL", "VERIFIED: PASS", "VERIFIED: FAIL", "NOT_APPLICABLE:")
                ):
                    errors.append(f"ADOPT requires explicit tested/verified status for portability.{target}")
    return errors


def validate_edge_evidence(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["edge evidence: expected JSON object"]
    unknown = set(record) - EDGE_FIELDS
    if unknown:
        errors.append(f"edge evidence: unknown fields {sorted(unknown)}")
    for field in sorted(EDGE_REQUIRED - set(record)):
        errors.append(f"edge evidence.{field}: required field missing")
    if record.get("schema_version") != "edge.inference.v1":
        errors.append("edge evidence.schema_version: expected edge.inference.v1")
    for field in ("experiment_id", "device_abi", "runtime", "backend"):
        if field in record and not nonempty(record[field]):
            errors.append(f"edge evidence.{field}: expected non-empty string")
    if not SHA256_RE.fullmatch(str(record.get("model_hash", ""))):
        errors.append("edge evidence.model_hash: expected 64-character SHA-256 hex")
    if not utc_timestamp(record.get("observed_at")):
        errors.append("edge evidence.observed_at: expected UTC ISO-8601 timestamp ending in Z")
    if "offline" not in record or not isinstance(record.get("offline"), bool):
        errors.append("edge evidence.offline: expected boolean")
    for field in ("device_model", "os_version", "model_family", "quantization", "runtime_version", "thermal_state", "fallback_path"):
        if field in record and record[field] is not None and not isinstance(record[field], str):
            errors.append(f"edge evidence.{field}: expected string or null")
    for field in ("tokens_per_second", "latency_p50_ms", "latency_p95_ms", "peak_memory_mb", "energy_proxy"):
        value = record.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0):
            errors.append(f"edge evidence.{field}: expected non-negative number or null")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("edge evidence.provenance: expected object")
    else:
        if set(provenance) - EDGE_PROVENANCE_FIELDS:
            errors.append(f"edge evidence.provenance: unknown fields {sorted(set(provenance) - EDGE_PROVENANCE_FIELDS)}")
        for field in sorted(EDGE_PROVENANCE_REQUIRED - set(provenance)):
            errors.append(f"edge evidence.provenance.{field}: required field missing")
        if not GIT_SHA_RE.fullmatch(str(provenance.get("repository_sha", ""))):
            errors.append("edge evidence.provenance.repository_sha: expected 40- or 64-character Git SHA")
        if not SHA256_RE.fullmatch(str(provenance.get("environment_fingerprint", ""))):
            errors.append("edge evidence.provenance.environment_fingerprint: expected SHA-256 hex")
        for field in ("runtime_source", "model_source"):
            value = provenance.get(field)
            if value is not None and not http_url(value):
                errors.append(f"edge evidence.provenance.{field}: expected HTTP(S) URL or null")
    return errors


def validate_manager_tournament(record: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["manager tournament: expected JSON object"]
    if set(record) - TOURNAMENT_FIELDS:
        errors.append(f"manager tournament: unknown fields {sorted(set(record) - TOURNAMENT_FIELDS)}")
    for field in sorted(TOURNAMENT_REQUIRED - set(record)):
        errors.append(f"manager tournament.{field}: required field missing")
    if record.get("schema_version") != "manager.tournament.v1":
        errors.append("manager tournament.schema_version: expected manager.tournament.v1")
    for field in ("tournament_id", "cohort_id", "policy_version"):
        if field in record and not nonempty(record[field]):
            errors.append(f"manager tournament.{field}: expected non-empty string")
    for field in ("task_contract_hash", "environment_fingerprint"):
        if not SHA256_RE.fullmatch(str(record.get(field, ""))):
            errors.append(f"manager tournament.{field}: expected SHA-256 hex")
    managers = record.get("managers")
    if not isinstance(managers, list) or not managers:
        errors.append("manager tournament.managers: expected non-empty list")
    else:
        seen: set[str] = set()
        for index, manager in enumerate(managers):
            prefix = f"manager tournament.managers[{index}]"
            if not isinstance(manager, dict):
                errors.append(f"{prefix}: expected object")
                continue
            if set(manager) - {"manager_id", "policy_hash", "routing_policy"}:
                errors.append(f"{prefix}: unknown fields {sorted(set(manager) - {'manager_id', 'policy_hash', 'routing_policy'})}")
            if not nonempty(manager.get("manager_id")):
                errors.append(f"{prefix}.manager_id: expected non-empty string")
            elif manager["manager_id"] in seen:
                errors.append(f"{prefix}.manager_id: duplicate manager ID")
            else:
                seen.add(manager["manager_id"])
            if not SHA256_RE.fullmatch(str(manager.get("policy_hash", ""))):
                errors.append(f"{prefix}.policy_hash: expected SHA-256 hex")
            if manager.get("routing_policy") is not None and not isinstance(manager.get("routing_policy"), str):
                errors.append(f"{prefix}.routing_policy: expected string or null")
    contract = record.get("evaluation_contract")
    if not isinstance(contract, dict):
        errors.append("manager tournament.evaluation_contract: expected object")
    else:
        if set(contract) - {"acceptance", "evidence_schema", "repetitions"}:
            errors.append("manager tournament.evaluation_contract: unknown fields")
        for field in ("acceptance", "evidence_schema"):
            if not nonempty(contract.get(field)):
                errors.append(f"manager tournament.evaluation_contract.{field}: expected non-empty string")
        if not isinstance(contract.get("repetitions"), int) or isinstance(contract.get("repetitions"), bool) or contract["repetitions"] < 1:
            errors.append("manager tournament.evaluation_contract.repetitions: expected integer >= 1")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("manager tournament.provenance: expected object")
    else:
        if set(provenance) - TOURNAMENT_PROVENANCE_FIELDS:
            errors.append("manager tournament.provenance: unknown fields")
        if not utc_timestamp(provenance.get("created_at")):
            errors.append("manager tournament.provenance.created_at: expected UTC ISO-8601 timestamp ending in Z")
        if not GIT_SHA_RE.fullmatch(str(provenance.get("repository_sha", ""))):
            errors.append("manager tournament.provenance.repository_sha: expected 40- or 64-character Git SHA")
        source = provenance.get("benchmark_source")
        if source is not None and not http_url(source):
            errors.append("manager tournament.provenance.benchmark_source: expected HTTP(S) URL or null")
    return errors


def load_jsonl(path: Path) -> list[tuple[int, Any]]:
    records: list[tuple[int, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append((line_number, json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:L{line_number}: invalid JSONL: {exc}") from exc
    return records


def validate_schema_contract(path: Path, expected_version: str, required: set[str], fields: set[str]) -> list[str]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: cannot read valid schema JSON: {exc}"]
    errors: list[str] = []
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        errors.append(f"{path}: expected a closed object schema")
    properties = schema.get("properties", {})
    if properties.get("schema_version", {}).get("const") != expected_version:
        errors.append(f"{path}: unexpected schema_version const")
    if set(schema.get("required", [])) != required:
        errors.append(f"{path}: required fields drifted from validator contract")
    if set(properties) != fields:
        errors.append(f"{path}: properties drifted from validator contract")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--procurement", type=Path, default=Path("data/briefing/procurement.jsonl"))
    parser.add_argument("--edge-schema", type=Path, default=Path("docs/ops/EDGE-INFERENCE-EVIDENCE.schema.json"))
    parser.add_argument("--manager-schema", type=Path, default=Path("docs/ops/MANAGER-TOURNAMENT.schema.json"))
    parser.add_argument("--edge-evidence", type=Path, action="append", default=[],
                        help="optional JSONL edge evidence to validate (repeatable)")
    parser.add_argument("--manager-tournament", type=Path, action="append", default=[],
                        help="optional JSON manager tournament record to validate (repeatable)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    procurement = args.procurement if args.procurement.is_absolute() else root / args.procurement
    edge_schema = args.edge_schema if args.edge_schema.is_absolute() else root / args.edge_schema
    manager_schema = args.manager_schema if args.manager_schema.is_absolute() else root / args.manager_schema
    errors: list[str] = []
    errors.extend(validate_schema_contract(edge_schema, "edge.inference.v1", EDGE_REQUIRED, EDGE_FIELDS))
    errors.extend(validate_schema_contract(manager_schema, "manager.tournament.v1", TOURNAMENT_REQUIRED, TOURNAMENT_FIELDS))
    try:
        records = load_jsonl(procurement)
        if not records:
            errors.append(f"{procurement}: expected at least one procurement record")
        for line_number, record in records:
            errors.extend(f"{procurement}:L{line_number}: {error}" for error in validate_procurement_record(record))
        for raw_path in args.edge_evidence:
            path = raw_path if raw_path.is_absolute() else root / raw_path
            for line_number, record in load_jsonl(path):
                errors.extend(f"{path}:L{line_number}: {error}" for error in validate_edge_evidence(record))
        for raw_path in args.manager_tournament:
            path = raw_path if raw_path.is_absolute() else root / raw_path
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{path}: cannot read valid JSON: {exc}")
                continue
            errors.extend(f"{path}: {error}" for error in validate_manager_tournament(record))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Procurement/schema validation passed for {len(records)} procurement records.")
    if args.edge_evidence:
        print(f"Validated {len(args.edge_evidence)} edge evidence file(s).")
    if args.manager_tournament:
        print(f"Validated {len(args.manager_tournament)} manager tournament record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
