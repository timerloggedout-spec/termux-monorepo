"""Fail-closed write policy. Scores never become merge commands."""
from __future__ import annotations

ALLOWED = frozenset({"hold", "observe", "extract", "comment", "classify"})
FORBIDDEN = frozenset({"merge", "force_push", "close", "delete", "dispatch_shell"})


def allow_write(action: str) -> bool:
    name = str(action or "").strip().lower()
    if name in FORBIDDEN:
        return False
    return name in ALLOWED
