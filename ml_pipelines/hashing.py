"""Stable hashing helpers. Never hash secrets; callers redact first."""
from __future__ import annotations

import hashlib
from typing import Iterable


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_join(parts: Iterable[str]) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()
