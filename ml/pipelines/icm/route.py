"""Pick one ICM card for a task before loading deeper source."""
from __future__ import annotations

# Longer / more specific tokens first.
KEYWORDS = (
    ("175", "hub"),
    ("issue #", "hub"),
    ("keepalive", "center"),
    ("command", "center"),
    ("cctv", "cctv-skill"),
    ("pipeline", "ml"),
    ("dual", "gate"),
    ("gate", "gate"),
    ("skill", "skills"),
    ("ml", "ml"),
    ("lane", "lane"),
    ("matrix", "lane"),
)


def route(task: str) -> str:
    blob = (task or "").lower()
    for token, card in KEYWORDS:
        if token in blob:
            return card
    return "entry"
