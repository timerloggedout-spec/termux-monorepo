"""validate: Minimal required-key schema checks."""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .errors import SchemaError


def require_keys(payload: Mapping[str, Any], keys: Iterable[str], *, label: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise SchemaError(f"{label} missing keys: {missing}")


def require_lane(value: str) -> str:
    allowed = {"promote", "wait", "hold", "extract", "observe"}
    if value not in allowed:
        raise SchemaError(f"unknown lane: {value}")
    return value
