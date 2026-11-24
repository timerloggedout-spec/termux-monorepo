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


def randomized_blocked_assignments(
    variants: list[Any], blocks: list[tuple[Any, ...]], seed: int | None = None
) -> list[dict[str, Any]]:
    """Assign every treatment exactly once in each randomized block."""
    if not variants or len(set(variants)) != len(variants):
        raise ValueError("variants must be non-empty and unique")
    if len(set(blocks)) != len(blocks):
        raise ValueError("block identifiers must be unique")
    rng = random.Random(seed)
    assignments = [
        {"block": list(block), "treatments": rng.sample(variants, k=len(variants))}
        for block in blocks
    ]
    validate_blocked_assignments(assignments, variants, blocks)
    return assignments


def validate_blocked_assignments(
    assignments: list[dict[str, Any]],
    variants: list[Any],
    expected_blocks: list[tuple[Any, ...]],
) -> None:
    """Reject missing, duplicated, extra, or unbalanced treatment blocks."""
    if not variants or len(set(variants)) != len(variants):
        raise ValueError("variants must be non-empty and unique")
    seen_blocks = []
    for assignment in assignments:
        block = tuple(assignment.get("block", []))
        treatments = assignment.get("treatments", [])
        if len(treatments) != len(variants) or set(treatments) != set(variants):
            raise ValueError(f"block {block!r} must contain each treatment exactly once")
        seen_blocks.append(block)
    if len(seen_blocks) != len(set(seen_blocks)) or set(seen_blocks) != set(expected_blocks):
        raise ValueError("assignments must cover every expected block exactly once")
