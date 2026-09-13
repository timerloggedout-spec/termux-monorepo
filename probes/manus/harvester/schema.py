"""JSONL event schema for self-session computer-replay."""
from __future__ import annotations

from typing import Any

EVENT_FIELDS = (
    "event_id",
    "session_id",
    "turn_id",
    "ts",
    "type",
    "actor",
    "payload",
    "stream_seq",
    "raw_ref",
)
EVENT_TYPES = frozenset(
    {"prompt", "thinking", "action", "response", "workspace_event"}
)
ACTORS = frozenset({"user", "agent", "system"})


class HarvesterError(ValueError):
    """Raised when an event violates the capture schema."""


def validate_event(event: dict[str, Any]) -> None:
    missing = [key for key in EVENT_FIELDS if key not in event]
    if missing:
        raise HarvesterError(f"missing fields: {missing}")
    if event.get("type") not in EVENT_TYPES:
        raise HarvesterError(f"bad type: {event.get('type')}")
    if event.get("actor") not in ACTORS:
        raise HarvesterError(f"bad actor: {event.get('actor')}")
    if not isinstance(event.get("payload"), dict):
        raise HarvesterError("payload must be a map")
    if not isinstance(event.get("stream_seq"), int):
        raise HarvesterError("stream_seq must be int")
