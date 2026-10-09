"""Wholesale ML family stays EXTRACT."""
from __future__ import annotations

from ml.pipelines.recon07.families import WHOLESALE_ML
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Finding

RULE_ID = "R04"


def evaluate(ctx: dict[str, object]) -> Finding:
    del ctx
    by_number = {obs.number: obs for obs in load_observations() if obs.kind == "pr"}
    bad = [n for n in sorted(WHOLESALE_ML) if by_number.get(n) is None or by_number[n].lane != "EXTRACT"]
    return Finding(RULE_ID, not bad, "wholesale ML numbers are EXTRACT")
