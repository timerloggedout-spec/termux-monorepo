"""Bind named dual-gate jobs. Combined commit status is not dual-gate."""
from __future__ import annotations

from typing import Any

REPO_GATE_NAMES = frozenset({"hygiene + portability gate", "repo gate", "repo-gate"})
SMOKE_NAMES = frozenset({"agentic termux smoke", "termux smoke", "termux-smoke"})


def named_gate_success(checks: list[dict[str, Any]], names: frozenset[str]) -> bool:
    for check in checks:
        name = str(check.get("name") or check.get("context") or "").lower()
        conclusion = str(check.get("conclusion") or check.get("state") or "").lower()
        if name in {n.lower() for n in names} and conclusion in {"success"}:
            return True
    return False


def dual_gate_green(checks: list[dict[str, Any]]) -> bool:
    return named_gate_success(checks, REPO_GATE_NAMES) and named_gate_success(checks, SMOKE_NAMES)
