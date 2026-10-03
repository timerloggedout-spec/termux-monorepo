"""_v1_recap -- Hindsight recapitulation package.

Self-contained helpers that recapitulate the shape of prior hindsight work
(scaffold in ``_v1_hindsight`` and sync writer in ``agent_hindsight``) so
callers can introspect and normalise the two without importing either.

Invariant: ``normalize_bank(default_bank_id)`` always returns a non-empty
bank id string; a blank or ``None`` input falls back to the documented
DEFAULT_BANK_ID. No network access happens at import time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

__all__ = [
    "DEFAULT_BANK_ID",
    "RECAP_VERSION",
    "RecapEntry",
    "normalize_bank",
    "recap",
    "shim_specs",
]

RECAP_VERSION = "1.0.0"
DEFAULT_BANK_ID = "termux-monorepo::primary"


@dataclass(slots=True, frozen=True)
class RecapEntry:
    """A single recapitulated tool surface entry."""

    name: str
    description: str
    schema: Mapping[str, Any] = field(default_factory=dict)


def normalize_bank(bank_id: str | None) -> str:
    """Return a guaranteed non-empty bank id.

    Blank / ``None`` inputs fall back to ``DEFAULT_BANK_ID``. This is the
    package invariant: every downstream URL builder can rely on a non-empty
    bank id.
    """
    if bank_id is None:
        return DEFAULT_BANK_ID
    cleaned = str(bank_id).strip()
    return cleaned or DEFAULT_BANK_ID


def _entry(
    name: str, description: str, props: Mapping[str, Any], required: list[str]
) -> RecapEntry:
    return RecapEntry(
        name=name,
        description=description,
        schema={
            "type": "object",
            "properties": dict(props),
            "required": list(required),
        },
    )


def shim_specs() -> tuple[RecapEntry, ...]:
    """Return the canonical three-entry hindsight tool surface.

    These mirror ``_v1_hindsight.build_hindsight_tools`` names exactly so a
    caller can diff the live surface against the recapitulated one.
    """
    return (
        _entry(
            "hindsight_retain",
            "Persist a fact, observation or experience to long-term Hindsight memory.",
            {
                "content": {"type": "string"},
                "bank_id": {"type": "string"},
                "metadata": {"type": "object"},
            },
            ["content"],
        ),
        _entry(
            "hindsight_recall",
            "Retrieve memories relevant to a query from Hindsight long-term memory.",
            {
                "query": {"type": "string"},
                "bank_id": {"type": "string"},
                "limit": {"type": "integer"},
            },
            ["query"],
        ),
        _entry(
            "hindsight_reflect",
            "Ask Hindsight to synthesize an answer from everything stored about a topic.",
            {
                "query": {"type": "string"},
                "bank_id": {"type": "string"},
            },
            ["query"],
        ),
    )


def recap() -> dict[str, Any]:
    """Return a JSON-serialisable recapitulation summary."""
    specs = shim_specs()
    return {
        "version": RECAP_VERSION,
        "default_bank_id": DEFAULT_BANK_ID,
        "tool_count": len(specs),
        "tools": [s.name for s in specs],
    }
