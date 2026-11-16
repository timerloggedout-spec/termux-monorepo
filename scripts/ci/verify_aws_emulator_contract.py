#!/usr/bin/env python3
"""Fail-closed validator for the optional AWS Emulator integration contract.

This validates repository policy metadata only. It does not start an emulator,
contact AWS, inspect credentials, or claim runtime compatibility.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONTRACT = (
    Path(__file__).resolve().parents[2]
    / "integrations"
    / "aws-emulator"
    / "contract.json"
)
ALLOWED_ENDPOINTS = {
    "https://127.0.0.1:9297",
    "https://localhost:9297",
}
REQUIRED_GATES = {
    "contract_validation",
    "unit_tests",
    "fidelity_replay",
    "security_review",
    "exact_sha_ci",
}


def validate_contract(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "integration_id",
        "status",
        "runtime_enabled",
        "execution_authority",
        "target",
        "endpoint",
        "cloud_fallback",
        "credentials",
        "production_allowed",
        "security_testing_allowed",
        "selected_emulator_release",
        "selected_evaluation_suite_revision",
        "candidate_services",
        "allowed_environments",
        "forbidden_environments",
        "required_gates",
        "upstream",
    }
    missing = sorted(required - data.keys())
    if missing:
        errors.append(f"missing required keys: {', '.join(missing)}")
        return errors

    if data["schema_version"] != "aws-emulator-integration.v1":
        errors.append("unsupported schema_version")
    if data["status"] != "research_only":
        errors.append("status must remain research_only until separately reviewed")
    if data["runtime_enabled"] is not False:
        errors.append("runtime_enabled must be false")
    if data["execution_authority"] != "none":
        errors.append("execution_authority must be none")
    if data["target"] != "local_only":
        errors.append("target must be local_only")
    if data["endpoint"] not in ALLOWED_ENDPOINTS:
        errors.append("endpoint must be an approved loopback HTTPS endpoint")
    if data["cloud_fallback"] != "deny":
        errors.append("cloud_fallback must be deny")
    if data["credentials"] != "synthetic_only":
        errors.append("credentials must be synthetic_only")
    if data["production_allowed"] is not False:
        errors.append("production_allowed must be false")
    if data["security_testing_allowed"] is not False:
        errors.append("security_testing_allowed must be false")

    if data["selected_emulator_release"] is not None:
        if not isinstance(data["selected_emulator_release"], str) or not data["selected_emulator_release"].strip():
            errors.append("selected_emulator_release must be null or a non-empty pinned version")
    if data["selected_evaluation_suite_revision"] is not None:
        if not isinstance(data["selected_evaluation_suite_revision"], str) or not data["selected_evaluation_suite_revision"].strip():
            errors.append("selected_evaluation_suite_revision must be null or a non-empty immutable revision")

    services = data["candidate_services"]
    if not isinstance(services, list) or not services or any(
        not isinstance(item, str) or not item for item in services
    ):
        errors.append("candidate_services must be a non-empty list of service identifiers")

    allowed = data["allowed_environments"]
    if not isinstance(allowed, list) or not set(allowed) <= {"developer_local", "hosted_ci"}:
        errors.append("allowed_environments contains an unsupported environment")
    forbidden = data["forbidden_environments"]
    if not isinstance(forbidden, list) or "production" not in forbidden:
        errors.append("forbidden_environments must explicitly include production")

    gates = data["required_gates"]
    if not isinstance(gates, list) or not REQUIRED_GATES <= set(gates):
        errors.append("required_gates is missing one or more mandatory gates")

    upstream = data["upstream"]
    expected_upstream = {
        "emulator": "https://github.com/aws/aws-emulator",
        "evaluation_suite": "https://github.com/aws/aws-emulator-evaluation-suite",
        "api_models": "https://github.com/aws/api-models-aws",
    }
    if upstream != expected_upstream:
        errors.append("upstream references must match the reviewed official repositories")

    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CONTRACT
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read contract: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR: contract root must be a JSON object", file=sys.stderr)
        return 2

    errors = validate_contract(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: AWS Emulator contract is valid (research-only; runtime disabled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
