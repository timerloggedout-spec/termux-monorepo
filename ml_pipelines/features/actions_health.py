"""Aggregate workflow conclusions. Quota skips are not failures."""
from __future__ import annotations

from collections import Counter
from typing import Any


def actions_health(runs: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter((row.get("conclusion") or row.get("status") or "unknown") for row in runs)
    total = sum(counts.values()) or 1
    failures = counts.get("failure", 0)
    return {
        "total": sum(counts.values()),
        "counts": dict(counts),
        "failure_rate": round(failures / total, 4),
        "success_rate": round(counts.get("success", 0) / total, 4),
        "skip_or_cancel_rate": round(
            (counts.get("skipped", 0) + counts.get("cancelled", 0)) / total, 4
        ),
    }
