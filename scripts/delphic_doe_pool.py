"""Read-only DoE/MoneyBall task candidate packet builder.

No provider calls, dispatch, wallet writes, quota mutation or scheduling.
Selection is deterministic and operates only on caller-supplied evidence.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


REQUIRED_INSTANCE = (
    "provider", "model", "endpoint", "protocol", "account_scope",
    "system_prompt_sha256", "tools_sha256", "role", "moniker",
    "context", "instance_key",
)


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _string_set(value: Any) -> set[str] | None:
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item for item in value
    ):
        return None
    return set(value)


def _eligible(candidate: dict[str, Any], task: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    identity = candidate.get("instance")
    if not isinstance(identity, dict) or any(not identity.get(k) for k in REQUIRED_INSTANCE):
        reasons.append("incomplete_configured_instance_identity")
    participant_id = candidate.get("participant_id")
    if not isinstance(participant_id, str) or not participant_id.strip():
        reasons.append("participant_identity_not_issued")
    if candidate.get("route_verified") is not True:
        reasons.append("route_not_verified")
    if candidate.get("health") != "healthy":
        reasons.append("health_not_healthy")
    if candidate.get("capacity") != "available":
        reasons.append("capacity_unavailable")
    if candidate.get("quota_state") != "available" or candidate.get("quota_class") != "free":
        reasons.append("free_quota_not_available")
    action_classes = _string_set(candidate.get("action_classes"))
    action_class = task.get("action_class")
    if not isinstance(action_class, str) or not action_class.strip():
        reasons.append("action_class_evidence_invalid")
    elif action_classes is None or action_class not in action_classes:
        reasons.append("action_class_not_authorized")

    required_tools = _string_set(task.get("required_tools", []))
    available_tools = _string_set(candidate.get("available_tools"))
    if required_tools is None:
        reasons.append("required_tools_evidence_invalid")
    if available_tools is None:
        reasons.append("available_tools_evidence_invalid")
    if required_tools is not None and available_tools is not None and not required_tools.issubset(available_tools):
        reasons.append("required_tools_unavailable")

    task_context = task.get("context_class")
    candidate_context = candidate.get("context_class")
    if not isinstance(task_context, str) or not task_context or not isinstance(candidate_context, str) or not candidate_context:
        reasons.append("context_class_evidence_missing")
    elif candidate_context != task_context:
        reasons.append("context_class_mismatch")
    return not reasons, reasons


def build_candidate_packet(task: dict[str, Any], candidates: list[dict[str, Any]],
                           *, previous_provider: str | None = None) -> dict[str, Any]:
    """Build a deterministic, read-only eligibility/ranking packet."""
    if not isinstance(task, dict) or not isinstance(task.get("task_id"), str) or not task["task_id"].strip():
        raise ValueError("task_id is required")
    if not isinstance(task.get("action_class"), str) or not task["action_class"].strip():
        raise ValueError("action_class must be a non-empty string")
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
        fit = candidate.get("task_fit_score")
        reliability = candidate.get("verified_reliability")
        if (type(fit) not in (int, float) or not math.isfinite(fit)
                or not 0.0 <= fit <= 1.0):
            excluded.append({**record, "reasons": ["task_fit_score_missing_or_invalid"]})
            continue
        if (type(reliability) not in (int, float) or not math.isfinite(reliability)
                or not 0.0 <= reliability <= 1.0):
            excluded.append({**record, "reasons": ["verified_reliability_missing_or_invalid"]})
            continue
        eligible.append({**record, "task_fit_score": fit, "verified_reliability": reliability,
                         "score": fit * 0.7 + reliability * 0.3})

    # Deterministic task-fit ordering; previous provider is deprioritized only
    # when another eligible provider has the same evidence score.
    eligible.sort(key=lambda x: (-x["score"], x["provider"] == previous_provider,
                                 x["provider"], x["model"], x["instance_key"]))
    selection = eligible[0] if eligible else None
    previous_candidate = next(
        (item for item in eligible if item["provider"] == previous_provider),
        None,
    )
    rotation_applied = bool(
        selection and previous_candidate
        and selection["provider"] != previous_provider
        and selection["score"] == previous_candidate["score"]
    )
    packet = {
        "schema": "delphic-doe-task-candidate/v1",
        "task_id": task["task_id"],
        "status": "CANDIDATES_AVAILABLE" if selection else "HELD_NO_ELIGIBLE_INSTANCE",
        "selection_policy": "task_fit_then_verified_reliability_no_hard_select_v1",
        "selected": selection,
        "eligible": eligible,
        "excluded": sorted(excluded, key=lambda x: (str(x.get("participant_id")), str(x.get("instance_key")))),
        "selection_provenance": {
            "previous_provider": previous_provider,
            "rotation_applied": rotation_applied,
        },
        "dispatch_authorized": False,
        "wallet_mutation_authorized": False,
        "input_digest": _digest({
            "task": task, "candidates": candidates,
            "previous_provider": previous_provider,
        }),
    }
    return packet
