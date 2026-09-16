"""Actions health stage wrapping feature aggregation."""
from __future__ import annotations

from collections import Counter
from typing import Any

from ml_pipelines.features.actions_health import actions_health
from ml_pipelines.features.quota import classify_run
from ml_pipelines.features.reviewer_noise import classify_activity


def run(snapshot: dict[str, Any]) -> dict[str, Any]:
    runs = list(snapshot.get("runs") or [])
    health = actions_health(runs)
    classes = [classify_run(run) for run in runs]
    taxonomy = [classify_activity(run) for run in runs]
    return {
        **health,
        "classes": dict(Counter(classes)),
        "activity_taxonomy": dict(Counter(taxonomy)),
        "note": "not_executed is not execution_failure; Vercel/CodeRabbit/Devin quota is provider_state.",
    }
