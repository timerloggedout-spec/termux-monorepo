"""Observation record. Stdlib only."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Observation:
    kind: str
    number: int
    lane: str
    title: str
    reasons: tuple[str, ...]
    action: str
    base: str = ""
    login: str = ""
    head_ref: str = ""

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        return payload
