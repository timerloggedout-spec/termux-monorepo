"""Advisory / non-gate signals. Never block promote on these alone."""
from __future__ import annotations

NON_GATE = frozenset(
    {
        "vercel_rate_limit",
        "gitlab",
        "mintlify",
        "copilot",
        "coderabbit",
        "qodo",
        "devin",
        "age_days",
    }
)


def is_non_gate(signal: str) -> bool:
    return signal in NON_GATE
