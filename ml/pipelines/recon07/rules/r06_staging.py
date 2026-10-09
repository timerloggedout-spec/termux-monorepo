"""#48 and #788 stay off master retarget."""
from __future__ import annotations

from ml.pipelines.recon07.families import STAGING_ONLY
from ml.pipelines.recon07.registry import load_observations
from ml.pipelines.recon07.types import Finding

RULE_ID = "R06"


def evaluate(ctx: dict[str, object]) -> Finding:
    del ctx
    by_number = {obs.number: obs for obs in load_observations() if obs.kind == "pr"}
    bad = [
        n
        for n in sorted(STAGING_ONLY)
        if by_number.get(n) is None or by_number[n].base == "master" or by_number[n].lane == "CANDIDATE"
    ]
    return Finding(RULE_ID, not bad, "staging-only PRs keep a non-master base")
