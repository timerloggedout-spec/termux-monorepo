"""Bind named dual-gate jobs to a SHA. Combined status is not dual-gate."""
from __future__ import annotations

from typing import Any

from ml.pipelines.contracts.dual_gate import dual_gate_green

PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"


def bind(sha: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    green = dual_gate_green(checks)
    same = sha == PRODUCT_SHA or sha.startswith(PRODUCT_SHA[:12])
    return {
        "sha": sha,
        "dual_gate": "GREEN" if green else "MISSING",
        "binds_product_sha": same,
        "promotable": bool(green and same),
        "note": "Observer refreshes (help-wanted) are not promote SHAs.",
    }


def require_this_sha(evidence_sha: str, candidate_sha: str) -> bool:
    """Dual-gate SUCCESS on an older head does not authorize a newer SHA."""
    return evidence_sha == candidate_sha
