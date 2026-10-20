"""Shared evidence contract. Adapters do not retain secret values or page bodies."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceContract:
    name: str
    scope: str
    is_promote_gate: bool
    retains_secret_values: bool = False
    retains_private_bodies: bool = False
    manual_only: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "scope": self.scope,
            "is_promote_gate": self.is_promote_gate,
            "retains_secret_values": self.retains_secret_values,
            "retains_private_bodies": self.retains_private_bodies,
            "manual_only": self.manual_only,
        }
