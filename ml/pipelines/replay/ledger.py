from __future__ import annotations

from typing import Any

from ml.pipelines.lib.clock import utc_now


def ledger_row(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "at": utc_now(),
        "master_sha": context.get("master_sha"),
        "issue": 175,
        "lanes": context.get("lane_counts"),
        "mode": "observe",
    }
