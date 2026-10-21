"""DoE — Design of Experiments helpers for MVT campaigns."""
from __future__ import annotations
import itertools, random
from typing import Any


def full_factorial(factors: dict[str, list[Any]]) -> list[dict]:
    """All combinations of factor levels. 2^k growth; use only for small k."""
    keys = list(factors.keys())
    combos = list(itertools.product(*(factors[k] for k in keys)))
    return [dict(zip(keys, c)) for c in combos]


def taguchi_l9(factors: dict[str, list[Any]]) -> list[dict]:
    """L9 orthogonal array for up to 4 factors at 3 levels each."""
    if len(factors) > 4 or any(len(v) != 3 for v in factors.values()):
        raise ValueError("L9 requires <=4 factors, each exactly 3 levels")
    idx = [[0,0,0,0],[0,1,1,1],[0,2,2,2],[1,0,1,2],[1,1,2,0],
           [1,2,0,1],[2,0,2,1],[2,1,0,2],[2,2,1,0]]
    keys = list(factors.keys())
    while len(keys) < 4:
        keys.append(f"_pad{len(keys)}")
    return [
        {k: factors[k][row[i]] for i, k in enumerate(keys) if k in factors}
        for row in idx
    ]


def mvt_shuffle(variants: list[Any], n: int, seed: int | None = None) -> list[Any]:
    """Randomized assignment for multi-variate testing. Duplicates allowed."""
    rng = random.Random(seed)
    return [rng.choice(variants) for _ in range(n)]
