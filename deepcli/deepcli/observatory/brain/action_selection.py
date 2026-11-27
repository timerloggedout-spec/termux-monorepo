"""Action-selection proposal helper; QUE remains the canonical admission authority."""
from __future__ import annotations
from typing import Any, Iterable, Mapping

def select_actions(candidates: Iterable[Mapping[str, Any]], max_parallel: int = 1) -> list[str]:
    """Select a deterministic, write-disjoint shortlist by priority then task identity."""
    if isinstance(max_parallel, bool) or not isinstance(max_parallel, int) or max_parallel < 1:
        raise ValueError("max_parallel must be a positive integer")
    normalized = []
    seen: set[str] = set()
    for raw in candidates:
        task_id = str(raw.get("id", "")).strip()
        if not task_id or task_id in seen:
            raise ValueError("candidate tasks require unique non-empty ids")
        seen.add(task_id)
        priority = raw.get("priority", 0)
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise ValueError(f"candidate {task_id} priority must be an integer")
        writes = sorted({str(path).strip() for path in raw.get("writes", []) if str(path).strip()})
        normalized.append((task_id, priority, writes))
    normalized.sort(key=lambda item: (-item[1], item[0]))
    selected: list[str] = []
    claimed: set[str] = set()
    for task_id, _, writes in normalized:
        if claimed.isdisjoint(writes):
            selected.append(task_id)
            claimed.update(writes)
            if len(selected) == max_parallel:
                break
    return selected
