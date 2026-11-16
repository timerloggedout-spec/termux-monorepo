#!/usr/bin/env python3
"""Evidence-envelope validator — PYTHON generation (V4 contract-first).

Generated-style validator for envelope_schema.json (schema_id
evidence-envelope/v1): validate(payload) returns the AGGREGATED list
of violations (never first-fail), mirroring validate_envelope.js
field-for-field so the fixture can cross-check the two languages
against one payload set.
"""

from __future__ import annotations

import re

REQUIRED = ["workflow_id", "unit_id", "receipt_sha256", "receipt_count",
            "history_sha256", "unknown_outcomes"]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate(payload) -> list[str]:
    violations: list[str] = []
    if not isinstance(payload, dict):
        return ["payload: not an object"]
    for field in REQUIRED:
        if field not in payload:
            violations.append(f"{field}: missing required field")
    for field in ("workflow_id", "unit_id"):
        if field in payload and (not isinstance(payload[field], str) or not payload[field]):
            violations.append(f"{field}: must be a non-empty string")
    for field in ("receipt_sha256", "history_sha256"):
        if field in payload and (not isinstance(payload[field], str)
                                 or not SHA256.match(payload[field])):
            violations.append(f"{field}: must be a 64-char lowercase hex sha256")
    if "receipt_count" in payload:
        v = payload["receipt_count"]
        if not isinstance(v, int) or isinstance(v, bool) or v < 0:
            violations.append("receipt_count: must be an integer >= 0")
    if "unknown_outcomes" in payload and not isinstance(payload["unknown_outcomes"], list):
        violations.append("unknown_outcomes: must be an array")
    for key in payload:
        if key not in REQUIRED:
            violations.append(f"{key}: additional property not allowed")
    return violations
