"""Compare git SHAs without treating a short prefix as a different commit."""
from __future__ import annotations

MIN_PREFIX = 7

def normalize(sha: str) -> str:
    return str(sha or "").strip().lower()

def same_commit(left: str, right: str) -> bool:
    a = normalize(left)
    b = normalize(right)
    if len(a) < MIN_PREFIX or len(b) < MIN_PREFIX:
        return False
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return long.startswith(short)

def tip_relation(recorded: str, live: str) -> str:
    if same_commit(recorded, live):
        return "aligned"
    return "drift"
