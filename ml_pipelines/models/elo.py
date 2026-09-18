"""Local Elo for observe-mode ranking. Not a merge authority."""
from __future__ import annotations


def expected(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))


def update(rating: float, expected_score: float, actual: float, k: float = 32.0) -> float:
    return rating + k * (actual - expected_score)
