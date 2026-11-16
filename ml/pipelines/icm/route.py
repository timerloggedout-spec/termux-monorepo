"""Pick one ICM card for a task before loading deeper source."""
from __future__ import annotations

import re

# Longer / more specific tokens first.
KEYWORDS = (
    ("repo-tracking", "tracking"),
    ("lane-project", "tracking"),
    ("lane×project", "tracking"),
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
    blob = re.sub(r"[\s_]+", "-", (task or "").lower())
    for token, card in KEYWORDS:
        if token in blob:
            return card
    return "entry"
