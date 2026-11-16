from __future__ import annotations

from typing import Any


def stage_export(context: dict[str, Any]) -> None:
    context["export"] = {
        "master_sha": context.get("master_sha"),
        "issue": 175,
        "lane_counts": context.get("lane_counts"),
        "operator": "ACTIVE",
    }
