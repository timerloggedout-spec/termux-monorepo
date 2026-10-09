"""Frozen recon observations. Stdlib only. Not a merge authority."""
from __future__ import annotations

from dataclasses import dataclass

from ml.pipelines.lanes.vocab import VALID_LANES

KINDS = frozenset({"pr", "issue"})


@dataclass(frozen=True)
class Observation:
    kind: str
    number: int
    lane: str
    title: str
    reasons: tuple[str, ...]
    action: str
    base: str = "master"

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"kind:{self.kind}")
        if self.number <= 0:
            raise ValueError("number")
        if self.lane not in VALID_LANES:
            raise ValueError(f"lane:{self.lane}")
        if not self.title or not self.action:
            raise ValueError("title/action required")
        object.__setattr__(self, "reasons", tuple(self.reasons))


@dataclass(frozen=True)
class Finding:
    rule_id: str
    ok: bool
    detail: str
