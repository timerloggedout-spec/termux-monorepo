"""Provider-neutral adapter contracts for System One engines.

This module deliberately avoids importing LangChain or an external Jev SDK. The
repository contract is stable first; optional integrations implement the protocol
at the edge and return the normalized decision envelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class DecisionRequest:
    state: dict[str, Any]
    questions: dict[str, Any]
    experiment_id: str
    lane_id: str


@dataclass(frozen=True)
class DecisionResponse:
    engine: str
    status: str
    answers: dict[str, Any]
    confidence: float | None
    metadata: dict[str, Any]


class SystemOneAdapter(Protocol):
    engine: str

    def evaluate(self, request: DecisionRequest) -> DecisionResponse:
        """Evaluate a bounded decision request without execution authority."""


class UnavailableAdapter:
    """Explicit adapter used when optional credentials/dependencies are absent."""

    engine = "jev"

    def evaluate(self, request: DecisionRequest) -> DecisionResponse:
        return DecisionResponse(
            engine=self.engine,
            status="UNAVAILABLE",
            answers={},
            confidence=None,
            metadata={"failure_class": "ENGINE_UNAVAILABLE"},
        )


def langchain_boundary() -> dict[str, str]:
    """Describe the optional LangChain integration boundary without importing it."""
    return {
        "contract": "DecisionRequest -> DecisionResponse",
        "execution": "adapter only",
        "authority": "no provider command, branch write, merge, or secret access",
        "installation": "optional integration dependency",
    }
