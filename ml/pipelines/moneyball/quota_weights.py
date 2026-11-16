"""3L0 / MoneyBall quota multipliers. Transparent, optional, neutral by default.

Reads routing-weights.json produced by scripts/quota_poll.py (workflow artifact
"quota-readings"). Missing file or provider -> 1.0, so routing is unchanged
until live evidence exists. Multiply a candidate's 3L0/ELO x role score by it.
"""
from __future__ import annotations

import json, os

DEFAULT_PATH = os.environ.get("QUOTA_WEIGHTS_PATH", "quota-out/routing-weights.json")


def load(path: str = DEFAULT_PATH) -> dict:
    try:
        with open(path) as f:
            return json.load(f).get("multipliers", {})
    except (OSError, ValueError):
        return {}


def quota_multiplier(provider: str, weights: dict | None = None) -> float:
    w = load() if weights is None else weights
    v = w.get(provider, 1.0)
    return max(0.0, min(float(v), 2.0))
