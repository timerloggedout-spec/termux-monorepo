"""Do not pulse-comment Issue #175."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R08"


def evaluate(ctx: dict[str, object]) -> Finding:
    ok = ctx.get("pulse_comment") is not True
    return Finding(RULE_ID, ok, "edit the issue body when intent changes; do not pulse-comment")
