"""ORBIT: deterministic, provider-neutral dual-accumulator arbitration.

Pure policy code. It does not invoke providers, inspect credentials, perform
network requests, or authorize side effects. Evidence is supplied by callers.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

SCHEMA = "orbit-decision/v1"
POLICY_VERSION = "orbit-dual-accumulator/v1"
HARD_GATES = (
    "capability", "effect", "provenance", "policy", "endpoint",
    "credential", "authentication", "catalog_freshness", "health",
    "quota", "data_classification", "current_sha", "execution_authority",
)
MAX_CANDIDATES = 128
BENEFIT_FIELDS = (
    "capability_fit", "repository_outcome", "task_suitability", "integration_value",
)
RISK_COST_FIELDS = (
    "uncertainty", "failure_risk", "latency_cost", "quota_cost",
    "context_cost", "retry_cost", "conflict_cost", "human_intervention_cost",
)


def _identity(candidate: dict[str, Any]) -> dict[str, str] | None:
    raw = candidate.get("identity")
    if not isinstance(raw, dict):
        return None
    allowed = ("kind", "provider", "model", "endpoint_id", "agent_id", "adapter")
    identity = {}
    for key in allowed:
        value = raw.get(key)
        if isinstance(value, str) and value.strip() and len(value) <= 256:
            identity[key] = value.strip()
    kind = identity.get("kind")
    if kind in {"provider_endpoint", "provider_route"}:
        if not identity.get("provider") or not (identity.get("model") or identity.get("endpoint_id")):
            return None
    elif kind == "agent":
        if not identity.get("agent_id"):
            return None
    else:
        return None
    return identity


def _identity_key(identity: dict[str, str]) -> str:
    return json.dumps(identity, sort_keys=True, separators=(",", ":"))


def _score(factors: Any, required: tuple[str, ...]) -> float | None:
    if not isinstance(factors, dict):
        return None
    values = []
    for name in required:
        value = factors.get(name)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if not math.isfinite(value) or not 0 <= value <= 1:
            return None
        values.append(float(value))
    return sum(values) / len(values) if values else None


def _refs(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({item.strip()[:512] for item in value
                   if isinstance(item, str) and item.strip() and len(item) <= 512})[:20]


def _evaluate(candidate: dict[str, Any], identity: dict[str, str], duplicate: bool) -> dict[str, Any]:
    base = {
        "identity": identity,
        "evidence_refs": _refs(candidate.get("evidence_refs")),
        "benefit_accumulator": None,
        "risk_cost_accumulator": None,
        "margin": None,
        "failed_gates": [],
        "unknown_gates": [],
    }
    if duplicate:
        return {**base, "decision": "VETO", "reason": "duplicate_endpoint_identity"}
    gates = candidate.get("hard_gates")
    if not isinstance(gates, dict):
        gates = {}
    failed = [name for name in HARD_GATES if gates.get(name) is False]
    unknown = [name for name in HARD_GATES if gates.get(name) is not True and gates.get(name) is not False]
    if failed:
        return {**base, "decision": "VETO", "reason": "hard_gate_failed",
                "failed_gates": failed, "unknown_gates": unknown}
    if unknown:
        return {**base, "decision": "DEFER", "reason": "hard_gate_evidence_unknown",
                "unknown_gates": unknown}

    benefit = _score(candidate.get("benefit"), BENEFIT_FIELDS)
    risk_cost = _score(candidate.get("risk_cost"), RISK_COST_FIELDS)
    if benefit is None or risk_cost is None:
        return {**base, "decision": "DEFER", "reason": "benefit_or_risk_evidence_unknown"}
    margin = benefit - risk_cost
    return {
        **base,
        "decision": "SCORE",
        "reason": "hard_gates_passed",
        "benefit_accumulator": round(benefit, 6),
        "risk_cost_accumulator": round(risk_cost, 6),
        "margin": round(margin, 6),
    }


def arbitrate(
    candidates: list[dict[str, Any]],
    threshold: float = 0.10,
    max_candidates: int = MAX_CANDIDATES,
) -> dict[str, Any]:
    """Return SELECT, DEFER, or VETO without invoking any candidate."""
    if not isinstance(candidates, list):
        raise ValueError("candidates_must_be_list")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold_must_be_between_zero_and_one")
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or max_candidates < 1:
        raise ValueError("max_candidates_must_be_positive_integer")

    limit = min(max_candidates, MAX_CANDIDATES)
    truncated = len(candidates) > limit
    considered = candidates[:limit]
    identities = [_identity(item) if isinstance(item, dict) else None for item in considered]
    keys = [_identity_key(item) if item is not None else None for item in identities]
    counts = Counter(key for key in keys if key is not None)

    evaluated = []
    for candidate, identity, key in zip(considered, identities, keys):
        if identity is None:
            evaluated.append({
                "identity": None, "decision": "VETO", "reason": "invalid_candidate_identity",
                "evidence_refs": [], "benefit_accumulator": None,
                "risk_cost_accumulator": None, "margin": None,
                "failed_gates": ["identity"], "unknown_gates": [],
            })
            continue
        evaluated.append(_evaluate(candidate, identity, counts[key] > 1))

    scored = []
    for item in evaluated:
        if item["decision"] != "SCORE":
            continue
        if item["margin"] < threshold:
            item["decision"] = "DEFER"
            item["reason"] = "benefit_margin_below_threshold"
        else:
            scored.append(item)

    scored.sort(key=lambda item: (-item["margin"], _identity_key(item["identity"])))
    selected = None
    decision = "DEFER"
    reason = "insufficient_candidate_evidence"

    if truncated:
        reason = "candidate_population_truncated"
    elif scored:
        if len(scored) > 1 and abs(scored[0]["margin"] - scored[1]["margin"]) <= 1e-9:
            reason = "top candidates have indistinguishable benefit-risk margins"
        else:
            decision = "SELECT"
            reason = "highest_verified_benefit_risk_margin"
            selected = scored[0]["identity"]
            scored[0]["decision"] = "SELECT"
            scored[0]["reason"] = reason
    elif evaluated and all(item["decision"] == "VETO" for item in evaluated):
        decision = "VETO"
        reason = "all_candidates_vetoed"

    evaluated.sort(key=lambda item: _identity_key(item["identity"]) if item["identity"] else "~invalid")
    return {
        "schema": SCHEMA,
        "policy_version": POLICY_VERSION,
        "decision": decision,
        "reason": reason,
        "threshold": float(threshold),
        "selected": selected,
        "candidate_count": len(candidates),
        "considered_count": len(considered),
        "candidate_population_truncated": truncated,
        "eligible_count": sum(1 for item in evaluated if item["decision"] == "SELECT"),
        "deferred_count": sum(1 for item in evaluated if item["decision"] == "DEFER"),
        "vetoed_count": sum(1 for item in evaluated if item["decision"] == "VETO"),
        "candidates": evaluated,
    }
