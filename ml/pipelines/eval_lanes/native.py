"""Repository-native dual gate. The only promote authority."""
from __future__ import annotations

from ml.pipelines.eval_lanes.contract import EvidenceContract

REPO_GATE = EvidenceContract(
    name="repo-gate",
    scope="hygiene + portability on the candidate SHA",
    is_promote_gate=True,
)
TERMUX_SMOKE = EvidenceContract(
    name="termux-smoke",
    scope="agentic termux runtime surface on the candidate SHA",
    is_promote_gate=True,
)


def native_gates() -> tuple[EvidenceContract, ...]:
    return (REPO_GATE, TERMUX_SMOKE)
