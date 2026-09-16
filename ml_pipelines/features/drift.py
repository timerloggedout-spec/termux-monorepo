"""Jules lane drift: many MERGEABLE/UNSTABLE PRs on the same theme."""
from __future__ import annotations

from typing import Any


def drift_flags(clusters: dict[str, list[int]]) -> list[dict[str, Any]]:
    flags = []
    for lane, numbers in clusters.items():
        if lane == "unclassified":
            continue
        if len(numbers) >= 3:
            flags.append(
                {
                    "lane": lane,
                    "count": len(numbers),
                    "numbers": numbers,
                    "disposition": "minesweep-keep-newest-extract",
                }
            )
    return flags
