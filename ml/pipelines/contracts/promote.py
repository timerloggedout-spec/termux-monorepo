"""Promote decision: ALLOW | BLOCK | NEED_EVIDENCE."""
from __future__ import annotations

from typing import Any

from ml.pipelines.contracts.gate import block_reasons
from ml.pipelines.lanes.vocab import Lane


def promote_decision(pr: dict[str, Any]) -> str:
    reasons = block_reasons(pr)
    if "mergeable_state=dirty" in reasons or any(r.startswith("wrong-base:") for r in reasons):
        return "NEED_EVIDENCE"
    if reasons:
        return "BLOCK"
    if pr.get("lane") == Lane.EXTRACT.value:
        return "BLOCK"
    return "ALLOW"
