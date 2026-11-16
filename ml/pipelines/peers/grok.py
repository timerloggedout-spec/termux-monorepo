"""This agent. Product work on master extracts, never force-push."""
from __future__ import annotations

OPERATOR = "timerloggedout-spec"
IDENTITY = "Grok (Administrator)"


def is_operator_extract(title: str) -> bool:
    t = (title or "").lower()
    return t.startswith("feat(ml):") or t.startswith("ops:") or "command-center" in t
