from __future__ import annotations

from typing import Any


def observe(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "spine": "ates-phase-b",
        "master_sha": snapshot.get("master_sha"),
        "mode": "observe",
        "issue": 175,
    }
