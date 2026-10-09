"""Minesweeper peers are not auto-promoted."""
from __future__ import annotations

from ml.pipelines.recon07.families import MINESWEEPER, forbidden_actions
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Finding

RULE_ID = "R05"


def evaluate(ctx: dict[str, object]) -> Finding:
    del ctx
    by_number = {obs.number: obs for obs in load_observations() if obs.kind == "pr"}
    bad = []
    for number in sorted(MINESWEEPER):
        obs = by_number.get(number)
        if obs is None or obs.lane == "CANDIDATE" or "overwrite-peer" not in forbidden_actions(number):
            bad.append(number)
    return Finding(RULE_ID, not bad, "minesweeper family forbids overwrite-peer")
