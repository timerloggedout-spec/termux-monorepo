"""MLP-05: summarise vendor gitmodules audit from snapshot extras."""
from __future__ import annotations

from typing import Any


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    extras = snapshot.get("gitmodules") or []
    live = [e for e in extras if e.get("status") == "LIVE"]
    missing = [e for e in extras if e.get("status") != "LIVE"]
    return {
        "issue": 503,
        "live": len(live),
        "missing": len(missing),
        "entries": extras,
        "mutate_gitmodules": False,
    }
