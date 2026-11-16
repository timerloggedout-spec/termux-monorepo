"""Evidence envelope: SHA + named jobs + lane. No secrets."""
from __future__ import annotations

from typing import Any


def envelope(sha: str, jobs: dict[str, str], lane: str) -> dict[str, Any]:
    if lane in {"HOLD", "WAIT", "OBSERVE"}:
        raise ValueError(f"invalid parking {lane}")
    return {"sha": sha, "jobs": dict(jobs), "lane": lane, "secrets": False}
