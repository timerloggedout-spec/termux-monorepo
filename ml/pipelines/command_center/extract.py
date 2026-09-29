"""Plan EXTRACT slices. Size ≠ quality. Mega-PRs stay EXTRACT."""
from __future__ import annotations

from typing import Any

from ml.pipelines.command_center.constants import MEGA_NO_GO, STAGING_ONLY


def plan_for(pr: dict[str, Any]) -> dict[str, Any]:
    n = int(pr.get("number") or 0)
    files = int(pr.get("changed_files") or 0)
    if n in STAGING_ONLY:
        return {"number": n, "action": "LEAVE", "note": "wrong-base master-staging; never retarget"}
    if n in MEGA_NO_GO or pr.get("wholesale") or files > 200:
        return {"number": n, "action": "EXTRACT", "note": "slim green slice onto live master"}
    if files > 100:
        return {"number": n, "action": "EXTRACT", "note": "CodeRabbit ~100-file advisory — split if noisy"}
    return {"number": n, "action": "REBASE", "note": "small slice; dual-gate this SHA"}


def plan_many(prs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [plan_for(pr) for pr in prs]
