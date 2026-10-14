"""Reject secret-shaped text before a names-only probe can be stamped."""
from __future__ import annotations

import re

MARKERS = (
    "ghp_",
    "github_pat_",
    "BEGIN PRIVATE",
    "BEGIN RSA",
    "Bearer ",
    "sk-",
    "AKIA",
    "ya29.",
    "xoxb-",
    "xoxp-",
)
EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def secret_hits(blob: str) -> tuple[str, ...]:
    hits = [marker for marker in MARKERS if marker in blob]
    if EMAIL.search(blob):
        hits.append("email")
    return tuple(hits)


def assert_names_only(blob: str) -> None:
    hits = secret_hits(blob)
    if hits:
        raise ValueError("names-only probe rejected: " + ",".join(hits))
