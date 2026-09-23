"""Import Action Effectiveness events into replay history (#742)."""
from __future__ import annotations
from typing import Any, Iterable, Mapping

def import_events(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for event in events:
        kind = str(event.get("kind") or event.get("type") or "action_effect")
        out.append(
            {
                "kind": kind,
                "sha": event.get("sha"),
                "outcome": event.get("outcome") or "UNKNOWN",
                "notes": event.get("notes") or "",
            }
        )
    return out
