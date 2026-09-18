"""Classify automation chatter vs real execution failure.

Taxonomy (Issue #175 / #390 / #546):
  actionable_finding, provider_state, reviewer_noise,
  execution_failure, not_executed, self_trigger_candidate
"""
from __future__ import annotations

from typing import Any

PROVIDER_STATE_TOKENS = (
    "rate limit",
    "rate-limit",
    "quota",
    "billing",
    "trial expired",
    "no credits",
    "permission",
    "resource not accessible",
    "unavailable",
    "deployment rate limited",
)
NOISE_TOKENS = (
    "review rate limited",
    "full review skipped",
    "coderabbit",
    "devin review",
    "i will re-review",
)
NOT_EXECUTED_CONCLUSIONS = {"skipped", "cancelled", "startup_failure", "neutral"}


def classify_activity(item: dict[str, Any]) -> str:
    conclusion = str(item.get("conclusion") or item.get("status") or "").lower()
    hay = " ".join(
        str(item.get(k) or "")
        for k in ("name", "display_title", "title", "description", "context", "conclusion")
    ).lower()
    if any(tok in hay for tok in PROVIDER_STATE_TOKENS):
        return "provider_state"
    if any(tok in hay for tok in NOISE_TOKENS):
        return "reviewer_noise"
    if "self-trigger" in hay or "comment-loop" in hay:
        return "self_trigger_candidate"
    if conclusion in NOT_EXECUTED_CONCLUSIONS or conclusion in {"queued", "in_progress", "waiting"}:
        return "not_executed"
    if conclusion == "failure":
        return "execution_failure"
    if conclusion == "success":
        return "actionable_finding" if "finding" in hay else "ok"
    return "unknown"
