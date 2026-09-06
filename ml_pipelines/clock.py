"""UTC clock seam so tests can freeze collection time."""
from __future__ import annotations

from datetime import UTC, datetime


def now_utc() -> datetime:
    return datetime.now(tz=UTC)


def rfc3339(value: datetime | None = None) -> str:
    stamp = value or now_utc()
    return stamp.astimezone(UTC).isoformat().replace("+00:00", "Z")
