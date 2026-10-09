"""HOLD / WAIT / OBSERVE are invalid parking."""
from __future__ import annotations

from ml.pipelines.lanes.vocab import INVALID_PARKING, VALID_LANES
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Finding

RULE_ID = "R03"


def evaluate(ctx: dict[str, object]) -> Finding:
    del ctx
    bad = [obs.number for obs in load_observations() if obs.lane not in VALID_LANES or obs.lane in INVALID_PARKING]
    return Finding(RULE_ID, not bad, "catalog lanes stay inside vocab v2")
