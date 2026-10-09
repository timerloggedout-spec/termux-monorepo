"""Product SHA stays put until a new dual-gate."""
from __future__ import annotations

from ml.pipelines.recon07.stamp import PRODUCT_SHA, is_product_sha, promotable_tip
from ml.pipelines.recon07.types import Finding

RULE_ID = "R01"


def evaluate(ctx: dict[str, object]) -> Finding:
    ok = is_product_sha(PRODUCT_SHA) and not promotable_tip(str(ctx.get("observer_tip") or ""))
    return Finding(RULE_ID, ok, "observer tip is not a product promote SHA")
