"""Typed pipeline outcomes. UNKNOWN is a first-class result."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Verdict = Literal["PASS", "FAIL", "HOLD", "UNKNOWN"]


@dataclass(frozen=True)
class Outcome:
    verdict: Verdict
    reason: str
    evidence: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict,
            "reason": self.reason,
            "evidence": list(self.evidence),
        }
