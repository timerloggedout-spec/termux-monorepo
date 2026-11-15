"""Shared action-first rules for Git collaboration metadata."""
from __future__ import annotations

import re

NEGATIVE_FIRST = re.compile(
    r"^\s*(?:(?:[-*]\s*)|(?:#+\s*))?(?:do not|don't|never|no|not|avoid)\b",
    re.IGNORECASE,
)


def is_negative_first_line(line: str) -> bool:
    """Detect negative-first prose across plain, list, and heading forms."""
    return bool(NEGATIVE_FIRST.match(line))

IMPERATIVE = frozenset({
    "accept", "add", "align", "apply", "audit", "build", "bound", "bump", "centralize", "check", "close", "consolidate",
    "collect", "compare", "cover", "create", "define", "deploy", "distinguish", "document", "enforce", "expand",
    "export", "fix", "gate", "generate", "guard", "include", "inspect", "keep", "measure",
    "migrate", "move", "open", "preserve", "publish", "recognize", "record", "reject", "reconcile", "refresh",
    "refine", "register", "regenerate", "rebuild", "remove", "rename", "repair", "replace",
    "require", "restore", "retain", "route", "run", "set", "snapshot", "split", "sync", "test",
    "update", "use", "validate", "verify", "wire",
})


def is_imperative_subject(subject: str) -> bool:
    """Validate the action verb after an optional conventional scope."""
    words = subject.rsplit(": ", 1)[-1].split()
    return bool(words) and words[0].lower() in IMPERATIVE
