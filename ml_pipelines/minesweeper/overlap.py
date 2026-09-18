"""Lane overlap summary for operator comments."""
from __future__ import annotations

from collections import Counter
from typing import Any


def overlap_summary(classified: list[dict[str, Any]]) -> dict[str, Any]:
    lanes = Counter(row["lane"] for row in classified)
    dispositions = Counter(row["disposition"] for row in classified)
    return {
        "lanes": dict(lanes),
        "dispositions": dict(dispositions),
        "duplicate_lanes": sorted(
            name for name, count in lanes.items() if name != "unclassified" and count >= 3
        ),
    }
