"""Actions health stage wrapping feature aggregation."""
from __future__ import annotations

from typing import Any

from ml_pipelines.features.actions_health import actions_health
from ml_pipelines.features.quota import classify_run


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    runs = list(snapshot.get("runs") or [])
    health = actions_health(runs)
    classes = [classify_run(run) for run in runs]
    from collections import Counter

    return {**health, "classes": dict(Counter(classes))}
