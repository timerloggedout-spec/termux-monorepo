"""Project replay evidence (#741/#742) into pipeline context. Isolated adapter."""
from __future__ import annotations
from typing import Any, Mapping

def lineage_fields(event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "experiment_id": event.get("experiment_id") or event.get("id"),
        "parent_sha": event.get("parent_sha"),
        "child_sha": event.get("child_sha") or event.get("sha"),
        "gain": float(event.get("gain") or 0.0),
        "promoted": bool(event.get("promoted")),
    }

def sufficient_gain(event: Mapping[str, Any], floor: float = 0.0) -> bool:
    return lineage_fields(event)["gain"] > floor
