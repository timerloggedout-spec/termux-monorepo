"""Observe-mode 'train' is a transparent histogram, not a model fit."""
from __future__ import annotations

from collections import Counter
from typing import Any


def stage_train(context: dict[str, Any]) -> None:
    counts = Counter(row["lane"] for row in context.get("lanes") or [])
    context["lane_counts"] = dict(counts)
