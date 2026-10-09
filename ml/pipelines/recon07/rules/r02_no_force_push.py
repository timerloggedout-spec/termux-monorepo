"""No force-push to master."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R02"


def evaluate(ctx: dict[str, object]) -> Finding:
    ok = ctx.get("force_push") is not True
    return Finding(RULE_ID, ok, "force-push to master is forbidden")
