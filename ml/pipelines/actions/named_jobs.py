"""Named dual-gate jobs. Combined status is not authority."""
from __future__ import annotations

REPO = ("hygiene + portability gate", "repo gate", "repo-gate", "hygiene + portability")
SMOKE = ("agentic termux smoke", "termux smoke", "termux-smoke")


def _norm(name: str) -> str:
    return " ".join(str(name or "").lower().replace("_", " ").replace("-", " ").split())


def match_repo_gate(name: str) -> bool:
    n = _norm(name)
    return n in {_norm(x) for x in REPO} or n.endswith("repo gate")


def match_smoke(name: str) -> bool:
    n = _norm(name)
    return n in {_norm(x) for x in SMOKE} or n.endswith("termux smoke")
