"""attribution: Record who acted; never store PATs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


ALLOWED_ROLES = {"operator", "administrator", "jules", "bolt", "sentinel", "reviewer", "collaborator"}


@dataclass(frozen=True)
class Attribution:
    actor: str
    role: str
    issue: int
    note: str


def make_attribution(payload: Mapping[str, str | int]) -> Attribution:
    role = str(payload.get("role") or "")
    if role not in ALLOWED_ROLES:
        raise ValueError(f"unknown role: {role}")
    actor = str(payload.get("actor") or "")
    if not actor or "token" in actor.lower() or "pat" == actor.lower():
        raise ValueError("refusing credential-shaped actor")
    return Attribution(actor=actor, role=role, issue=int(payload.get("issue") or 175), note=str(payload.get("note") or ""))
