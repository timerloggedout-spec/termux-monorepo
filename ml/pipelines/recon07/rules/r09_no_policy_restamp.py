"""Do not restamp docs/ops/LANE-MATRIX.md from a session."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R09"


def evaluate(ctx: dict[str, object]) -> Finding:
    ok = ctx.get("restamp_lane_matrix") is not True
    return Finding(RULE_ID, ok, "lane-matrix policy file is not a session stamp")
