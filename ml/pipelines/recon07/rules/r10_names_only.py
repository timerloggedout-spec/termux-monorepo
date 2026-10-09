"""Issue #184 inventory is names-only. Never commit secret values."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R10"


def evaluate(ctx: dict[str, object]) -> Finding:
    ok = ctx.get("secret_values") is not True
    return Finding(RULE_ID, ok, "Issue #184 records names, never values")
