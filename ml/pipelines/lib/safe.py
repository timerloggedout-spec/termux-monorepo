"""Reject Class 3/4 artifacts. Names-only for #184."""
from __future__ import annotations

FORBIDDEN_KEYS = frozenset(
    {"token", "password", "secret", "authorization", "cookie", "private_key"}
)


def redact(payload: dict) -> dict:
    out = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(token in lowered for token in FORBIDDEN_KEYS):
            out[key] = "[redacted]"
        elif isinstance(value, dict):
            out[key] = redact(value)
        else:
            out[key] = value
    return out
