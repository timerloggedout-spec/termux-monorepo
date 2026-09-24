"""Surfaces that must never block promote: Vercel, GitLab, Copilot, CodeRabbit, Qodo, Devin."""
from __future__ import annotations

NON_GATE_CONTEXTS = (
    "Vercel",
    "GitLab",
    "Copilot",
    "CodeRabbit",
    "Qodo",
    "Devin Review",
    "Mintlify",
)

def is_nongate_context(name: str) -> bool:
    lowered = name.lower()
    return any(token.lower() in lowered for token in NON_GATE_CONTEXTS)
