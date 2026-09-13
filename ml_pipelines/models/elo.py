"""Tiny Elo helper for local ranking. Decision-support only."""
from __future__ import annotations

import math


def expected(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))


def update(rating: float, expected_score: float, actual: float, k: float = 16.0) -> float:
    return rating + k * (actual - expected_score)
