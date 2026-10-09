"""Actions incidents are evidence, not promote gates."""
from __future__ import annotations

from ml.pipelines.recon07.families import EVIDENCE_INCIDENTS, forbidden_actions
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Finding

RULE_ID = "R11"


def evaluate(ctx: dict[str, object]) -> Finding:
    del ctx
    by_number = {obs.number: obs for obs in load_observations() if obs.kind == "issue"}
    bad = []
    for number in sorted(EVIDENCE_INCIDENTS):
        obs = by_number.get(number)
        if obs is None or obs.lane == "CANDIDATE" or "treat-as-promote-gate" not in forbidden_actions(number):
            bad.append(number)
    return Finding(RULE_ID, not bad, "throughput/ledger incidents stay non-gate")
