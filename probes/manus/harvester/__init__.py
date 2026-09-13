"""Self-session Manus computer-replay harvester. Observe-mode scaffold."""
from .schema import EVENT_FIELDS, EVENT_TYPES, validate_event
from .normalize import normalize_event, dedup_events

__all__ = [
    "EVENT_FIELDS",
    "EVENT_TYPES",
    "validate_event",
    "normalize_event",
    "dedup_events",
]
