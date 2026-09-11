"""Lightweight lag features from timestamps. No network."""
from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_hours(value: Any, now: datetime) -> float | None:
    parsed = parse_ts(value)
    if parsed is None:
        return None
    return round((now - parsed).total_seconds() / 3600.0, 2)
