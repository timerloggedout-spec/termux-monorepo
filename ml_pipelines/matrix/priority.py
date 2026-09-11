"""Priority ordering for the operator matrix."""
from __future__ import annotations

from typing import Any

ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def sort_items(items: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    return sorted(
        items.items(),
        key=lambda pair: (ORDER.get(str(pair[1].get("priority")), 9), pair[0]),
    )
