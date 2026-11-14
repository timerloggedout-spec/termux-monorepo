"""Read-only DoE/MoneyBall task candidate packet builder.

No provider calls, dispatch, wallet writes, quota mutation or scheduling.
Selection is deterministic and operates only on caller-supplied evidence.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


REQUIRED_INSTANCE = (
    "provider", "model", "endpoint", "protocol", "account_scope",
    "system_prompt_sha256", "tools_sha256", "role", "moniker",
    "context", "instance_key",
)


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _eligible(candidate: dict[str, Any], task: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    identity = candidate.get("instance")
    if not isinstance(identity, dict) or any(not identity.get(k) for k in REQUIRED_INSTANCE):
        reasons.append("incomplete_configured_instance_identity")
    if candidate.get("participant_id") is None:
        reasons.append("participant_identity_not_issued")
    if candidate.get("route_verified") is not True:
        reasons.append("route_not_verified")
    if candidate.get("health") != "healthy":
        reasons.append("health_not_healthy")
    if candidate.get("capacity") != "available":
        reasons.append("capacity_unavailable")
    if candidate.get("quota_state") != "available" or candidate.get("quota_class") != "free":
        reasons.append("free_quota_not_available")
    if candidate.get("action_classes") is None or task.get("action_class") not in candidate.get("action_classes", []):
        reasons.append("action_class_not_authorized")
    required_tools = set(task.get("required_tools", []))
    available_tools = set(candidate.get("available_tools", []))
    if not required_tools.issubset(available_tools):
        reasons.append("required_tools_unavailable")
    if candidate.get("context_class") != task.get("context_class"):
        reasons.append("context_class_mismatch")
    return not reasons, reasons


def build_candidate_packet(task: dict[str, Any], candidates: list[dict[str, Any]],
                           *, previous_provider: str | None = None) -> dict[str, Any]:
    """Build a deterministic, read-only eligibility/ranking packet."""
    if not isinstance(task, dict) or not task.get("task_id") or not task.get("action_class"):
        raise ValueError("task_id and action_class are required")
    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for candidate in candidates:
        ok, reasons = _eligible(candidate, task)
        instance = candidate.get("instance") if isinstance(candidate.get("instance"), dict) else {}
        record = {
            "participant_id": candidate.get("participant_id"),
            "instance_key": instance.get("instance_key"),
            "provider": instance.get("provider"),
            "model": instance.get("model"),
            "endpoint": instance.get("endpoint"),
        }
        if not ok:
            excluded.append({**record, "reasons": sorted(reasons)})
            continue
        fit = candidate.get("task_fit_score", 0)
        reliability = candidate.get("verified_reliability", 0)
        if not isinstance(fit, (int, float)) or not isinstance(reliability, (int, float)):
            excluded.append({**record, "reasons": ["non_numeric_ranking_evidence"]})
            continue
        eligible.append({**record, "task_fit_score": fit, "verified_reliability": reliability,
                         "score": fit * 0.7 + reliability * 0.3})

    # Deterministic task-fit ordering; previous provider is deprioritized only
    # when another eligible provider has the same evidence score.
    eligible.sort(key=lambda x: (-x["score"], x["provider"] == previous_provider,
                                 x["provider"], x["model"], x["instance_key"]))
    selection = eligible[0] if eligible else None
    packet = {
        "schema": "delphic-doe-task-candidate/v1",
        "task_id": task["task_id"],
        "status": "CANDIDATES_AVAILABLE" if selection else "HELD_NO_ELIGIBLE_INSTANCE",
        "selection_policy": "task_fit_then_verified_reliability_no_hard_select_v1",
        "selected": selection,
        "eligible": eligible,
        "excluded": sorted(excluded, key=lambda x: (str(x.get("participant_id")), str(x.get("instance_key")))),
        "dispatch_authorized": False,
        "wallet_mutation_authorized": False,
        "input_digest": _digest({"task": task, "candidates": candidates}),
    }
    return packet
