"""Harvester schema constants. Capture implementation lives under probes/manus."""
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
__all__ = ["EVENT_FIELDS", "EVENT_TYPES"]
