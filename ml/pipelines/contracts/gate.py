"""Gate helpers. Dual-gate SUCCESS on THIS SHA is required to promote."""
from __future__ import annotations

from typing import Any

from ml.pipelines.lib.errors import GateBlocked


REQUIRED_GATES = ("repo-gate", "termux-smoke")
NON_GATES = frozenset({"vercel", "copilot", "coderabbit", "qodo", "devin", "gitlab"})


def assert_promotable(pr: dict[str, Any]) -> None:
    reasons = block_reasons(pr)
    if reasons:
        raise GateBlocked(pr.get("number"), reasons)


def block_reasons(pr: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if pr.get("draft"):
        reasons.append("draft")
    if pr.get("mergeable_state") == "dirty":
        reasons.append("mergeable_state=dirty")
    base = (pr.get("base") or {}).get("ref") if isinstance(pr.get("base"), dict) else pr.get("base")
    if base and base != "master":
        reasons.append(f"wrong-base:{base}")
    gates = pr.get("gates") or {}
    for name in REQUIRED_GATES:
        if gates.get(name) != "success":
            reasons.append(f"missing-gate:{name}")
    if pr.get("wholesale"):
        reasons.append("ml-wholesale-no-go")
    return reasons


def is_non_gate(context: str) -> bool:
    key = context.split("–")[0].split("-")[0].strip().lower()
    return any(token in context.lower() for token in NON_GATES) or key in NON_GATES
