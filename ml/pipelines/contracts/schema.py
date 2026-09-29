"""Minimal session fixture schema. Stdlib only."""
from __future__ import annotations

from typing import Any

REQUIRED_ROOT = ("master_sha", "session", "prs")
REQUIRED_PR = ("number", "title", "base")


def validate_snapshot(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_ROOT:
        if key not in payload:
            errors.append(f"missing:{key}")
    sha = str(payload.get("master_sha") or "")
    if len(sha) < 7:
        errors.append("master_sha too short")
    prs = payload.get("prs")
    if not isinstance(prs, list):
        errors.append("prs must be a list")
        return errors
    for pr in prs:
        if not isinstance(pr, dict):
            errors.append("pr not object")
            continue
        for key in REQUIRED_PR:
            if key not in pr:
                errors.append(f"pr missing:{key}")
    return errors
