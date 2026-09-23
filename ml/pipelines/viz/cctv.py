"""ICM-CCTV projection for ops dashboards (Stepie 2087 step 10023)."""
from __future__ import annotations
from collections import Counter
from typing import Any, Iterable, Mapping

def cctv(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = list(rows)
    counts = Counter(str(row.get("lane") or "observe") for row in items)
    return {
        "surface": "icm-cctv",
        "n": len(items),
        "lanes": dict(counts),
        "operator": "ACTIVE",
        "primary_goal": 2149,
        "adjacent_goal": 2087,
        "step": 10023,
    }
