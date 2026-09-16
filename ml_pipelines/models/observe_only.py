"""Fail-closed write fence for observe-mode pipelines."""
from __future__ import annotations

WRITE_ACTIONS = frozenset(
    {
        "merge",
        "force_push",
        "force-push",
        "close",
        "dispatch_shell",
        "issue_to_shell",
        "delete",
        "protect",
        "unprotect",
    }
)
SAFE_ACTIONS = frozenset({"hold", "observe", "classify", "score", "export", "comment"})


def allow_write(action: str) -> bool:
    token = str(action or "").strip().lower().replace(" ", "_")
    if token in WRITE_ACTIONS:
        return False
    return token in SAFE_ACTIONS or token.startswith("observe")
