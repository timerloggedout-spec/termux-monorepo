"""MLP-05: report harvester scaffold readiness. No network."""
from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = (
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


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    sample = list(snapshot.get("harvester_events") or [])
    return {
        "issue": 503,
        "schema_fields": list(REQUIRED_FIELDS),
        "sample_events": len(sample),
        "observe_only": True,
        "class_3_4_forbidden": True,
    }
