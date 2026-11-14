"""Shared action-first rules for Git collaboration metadata."""
from __future__ import annotations

IMPERATIVE = frozenset({
    "accept", "add", "align", "apply", "audit", "build", "bump", "check", "close",
    "collect", "compare", "create", "define", "deploy", "document", "enforce", "expand",
    "export", "fix", "gate", "generate", "guard", "include", "inspect", "keep", "measure",
    "migrate", "move", "open", "preserve", "publish", "record", "reconcile", "refresh",
    "refine", "register", "regenerate", "rebuild", "remove", "rename", "repair", "replace",
    "require", "restore", "route", "run", "set", "snapshot", "split", "sync", "test",
    "update", "use", "validate", "verify", "wire",
})


def is_imperative_subject(subject: str) -> bool:
    """Validate the action verb after an optional conventional scope."""
    words = subject.rsplit(": ", 1)[-1].split()
    return bool(words) and words[0].lower() in IMPERATIVE
