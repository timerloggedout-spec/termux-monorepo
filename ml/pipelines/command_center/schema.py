"""Snapshot schema v2 for command-center fixtures."""
from __future__ import annotations

from typing import Any

REQUIRED_KEYS = ("master_sha", "observed_at", "prs", "session")


def validate_snapshot(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_KEYS:
        if key not in payload:
            errors.append(f"missing:{key}")
    prs = payload.get("prs")
    if not isinstance(prs, list):
        errors.append("prs-not-list")
        return errors
    for pr in prs:
        if "number" not in pr:
            errors.append("pr-missing-number")
            break
        lane = pr.get("lane")
        if lane in {"HOLD", "WAIT", "OBSERVE"}:
            errors.append(f"invalid-parking:{pr.get('number')}:{lane}")
    return errors


def is_valid(payload: dict[str, Any]) -> bool:
    return not validate_snapshot(payload)
