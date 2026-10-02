from __future__ import annotations


def short_sha(sha: str, n: int = 8) -> str:
    return sha[:n]


def same_sha(left: str, right: str) -> bool:
    n = min(len(left), len(right), 7)
    return bool(n) and left[:n] == right[:n]
