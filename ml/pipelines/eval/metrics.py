"""metrics: Offline ranking metrics on labeled lanes."""
from __future__ import annotations

from typing import Iterable, Sequence

LANE_ORDER = ("extract", "hold", "observe", "wait", "promote")


def accuracy(pred: Sequence[str], gold: Sequence[str]) -> float:
    if len(pred) != len(gold) or not pred:
        raise ValueError("pred/gold length mismatch or empty")
    hits = sum(1 for left, right in zip(pred, gold) if left == right)
    return hits / len(gold)


def promote_precision(pred: Iterable[str], gold: Iterable[str]) -> float:
    pairs = list(zip(pred, gold))
    predicted = [1 for p, _ in pairs if p == "promote"]
    if not predicted:
        return 0.0
    correct = sum(1 for p, g in pairs if p == "promote" and g == "promote")
    return correct / len(predicted)
