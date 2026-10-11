"""Provider-neutral evaluation registry."""
from __future__ import annotations

from ml.pipelines.eval_lanes.app_probe import APP_PROBE
from ml.pipelines.eval_lanes.contract import EvidenceContract
from ml.pipelines.eval_lanes.gamut import GAMUT
from ml.pipelines.eval_lanes.native import native_gates

NON_GATES = (
    EvidenceContract("vercel", "hobby deploy surface", False),
    EvidenceContract("coderabbit", "advisory review", False),
    EvidenceContract("qodo", "advisory review", False),
    EvidenceContract("devin", "advisory review", False),
    EvidenceContract("copilot", "advisory review", False),
    EvidenceContract("gitlab", "non-blocking mirror", False),
    GAMUT,
    APP_PROBE,
)


def all_contracts() -> tuple[EvidenceContract, ...]:
    return native_gates() + NON_GATES


def promote_gates() -> tuple[str, ...]:
    return tuple(item.name for item in all_contracts() if item.is_promote_gate)
