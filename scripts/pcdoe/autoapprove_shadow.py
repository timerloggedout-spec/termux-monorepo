"""Evaluate bounded AutoApprove eligibility without performing the requested action."""
from __future__ import annotations

from datetime import datetime
from typing import Any

FORMAL_APPROVAL_CLASSES = {
    "github_review", "merge", "release", "production_promotion",
    "credential", "permission", "security_policy", "destructive_data",
    "external_commitment",
}


def evaluate_autoapprove(
    policy: dict[str, Any],
    action: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, Any]:
    reasons: list[str] = []
    approval_class = action.get("approval_class")
    if approval_class in FORMAL_APPROVAL_CLASSES:
        reasons.append("formal_approval_required")
    if policy.get("status") != "authorized":
        reasons.append("policy_not_authorized")
    if approval_class != "preauthorized_low_risk":
        reasons.append("approval_class_out_of_scope")

    entry = next((
        candidate for candidate in policy.get("allowlist", [])
        if candidate.get("action_id") == action.get("action_id")
        and candidate.get("resource_pattern") == action.get("resource")
    ), None)
    if entry is None:
        reasons.append("allowlist_mismatch")
    else:
        if entry.get("actor_class") != action.get("actor_class"):
            reasons.append("actor_class_mismatch")
        if entry.get("max_scope") != action.get("scope"):
            reasons.append("scope_mismatch")
        if float(action.get("cost", float("inf"))) > float(entry.get("max_cost", -1)):
            reasons.append("budget_exceeded")
        if int(action.get("timeout_seconds", 0)) > int(entry.get("timeout_seconds", 0)):
            reasons.append("timeout_exceeded")
        expiry = datetime.fromisoformat(entry["expires_at"].replace("Z", "+00:00"))
        if now.tzinfo is None or expiry.tzinfo is None or now >= expiry:
            reasons.append("allowlist_expired")

    checks = {
        "identity_verified": "identity_unverified",
        "existing_permission": "permission_unverified",
        "risk_within_limit": "risk_out_of_bounds",
        "inputs_fresh": "inputs_stale_or_unknown",
        "idempotency_proven": "idempotency_unproven",
        "compensation_tested": "compensation_unproven",
        "evidence_present": "required_evidence_missing",
    }
    for field, reason in checks.items():
        if action.get(field) is not True:
            reasons.append(reason)

    return {
        "decision": "eligible" if not reasons else "ineligible",
        "reasons": reasons,
        "recommendation_only": True,
        "execution_performed": False,
        "action_id": action.get("action_id"),
        "resource": action.get("resource"),
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("version"),
    }
