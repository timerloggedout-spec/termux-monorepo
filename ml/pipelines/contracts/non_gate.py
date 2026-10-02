"""Advisory / non-gate providers. Never block promote on these."""
from __future__ import annotations

ADVISORY = (
    "Vercel",
    "CodeRabbit",
    "Copilot",
    "Qodo",
    "Devin",
    "GitLab",
    "Mintlify",
)


def is_advisory(name: str) -> bool:
    lowered = name.lower()
    return any(token.lower() in lowered for token in ADVISORY)
