#!/usr/bin/env python3
"""Capability, scope, and specialist decision helpers for AR-17 observe mode.

The module is intentionally pure. It consumes declared candidate facts and emits
bounded decision data; callers retain every provider, GitHub, and file mutation
capability. Eligibility is decided before a candidate receives a score.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

SCHEMA_VERSION = 2
OBSERVE_MODE = "observe"
MAX_CANDIDATES = 16
READ_ONLY_EFFECTS = {"read_only_analysis", "review_request"}
BRANCH_WRITE_EFFECTS = {
    "branch_write",
    "stacked_pull_request",
    "provider_configuration",
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Keep a score component within its documented closed interval."""
    return max(low, min(high, value))


def _normalise_elo(elo: float) -> float:
    """Map existing 3L0/ELO-like values to a bounded, explainable prior."""
    return _clamp((float(elo) - 900.0) / 600.0)


def _availability_state(
    provider: str,
    model: str,
    has_provider: bool,
    openrouter_models: set[str] | None,
    openrouter_catalog_state: str,
) -> tuple[str, str | None]:
    """Return the operational availability state and a fail-closed reason."""
    if not has_provider:
        return "blocked", "provider credential or policy gate is unavailable"
    if provider != "openrouter":
        return "configured", None
    if openrouter_models is None:
        return "unavailable", "no live or cached OpenRouter catalog is available"
    if model not in openrouter_models:
        return "blocked", "model is absent from the permitted OpenRouter catalog"
    return openrouter_catalog_state, None


def _hard_gate_reason(
    *,
    capability: str,
    declared_capabilities: set[str],
    effect: str,
    provenance: dict[str, Any],
    policy_enabled: bool,
    requires_current_sha: bool,
    target_sha: str | None,
    current_sha: str | None,
    branch_write_confirmed: bool,
) -> str | None:
    """Return the first failed authorization gate; successful gates return None."""
    if not capability or capability not in declared_capabilities:
        return "requested capability is not declared for this specialist"
    if effect not in READ_ONLY_EFFECTS | BRANCH_WRITE_EFFECTS:
        return "candidate effect is not declared by the capability policy"
    if not provenance.get("trusted") or not provenance.get("declared_source"):
        return "candidate provenance is not trusted and declared"
    if not policy_enabled:
        return "candidate policy gate is disabled"
    if requires_current_sha and (not target_sha or target_sha != current_sha):
        return "current-SHA gate is missing or stale"
    if effect in BRANCH_WRITE_EFFECTS and not branch_write_confirmed:
        return "branch-write effect lacks explicit confirmation"
    return None


def make_candidate(
    *,
    provider: str,
    model: str,
    capability: str,
    declared_capabilities: set[str],
    effect: str,
    provenance: dict[str, Any],
    policy_enabled: bool,
    requires_current_sha: bool,
    target_sha: str | None,
    current_sha: str | None,
    branch_write_confirmed: bool,
    has_provider: bool,
    openrouter_models: set[str] | None,
    openrouter_catalog_state: str,
    limits: dict[str, dict[str, int]],
    usage: int,
    success_entry: dict[str, Any],
) -> dict[str, Any]:
    """Create one candidate and expose hard-gate and score components.

    Existing model-success data remains a low-confidence historic prior. It is
    never represented as a measured current repository outcome.
    """
    gate_reason = _hard_gate_reason(
        capability=capability,
        declared_capabilities=declared_capabilities,
        effect=effect,
        provenance=provenance,
        policy_enabled=policy_enabled,
        requires_current_sha=requires_current_sha,
        target_sha=target_sha,
        current_sha=current_sha,
        branch_write_confirmed=branch_write_confirmed,
    )
    availability, availability_reason = _availability_state(
        provider,
        model,
        has_provider,
        openrouter_models,
        openrouter_catalog_state,
    )
    limit = int(
        limits.get(f"{provider}/{model}", limits.get(model, {})).get(capability, 0)
    )
    quota_reason = None
    if limit <= 0:
        quota_reason = "no declared capability quota exists"
    elif usage >= limit:
        quota_reason = f"soft budget exhausted ({usage}/{limit})"

    exclusion = gate_reason or availability_reason or quota_reason
    if gate_reason or quota_reason:
        availability = "blocked"

    elo = float(success_entry.get("elo", 1000))
    suitability = float(success_entry.get("role_suitability", {}).get(capability, 1.0))
    historic_prior = _normalise_elo(elo) * _clamp(suitability / 1.3)
    repository_evidence_confidence = 0.20 if success_entry else 0.0
    repository_outcome = (
        historic_prior * repository_evidence_confidence
        + 0.50 * (1.0 - repository_evidence_confidence)
    )
    quota_headroom = _clamp((limit - usage) / limit) if limit else 0.0
    availability_component = (
        quota_headroom if availability not in {"blocked", "unavailable"} else 0.0
    )
    public_board_prior = 0.50
    score = (
        0.55 * repository_outcome
        + 0.15 * repository_evidence_confidence
        + 0.15 * public_board_prior
        + 0.15 * availability_component
    )

    return {
        "specialist": {"provider": provider, "model": model},
        "capability": capability,
        "effect": effect,
        "provenance": {
            "declared_source": provenance.get("declared_source"),
            "trusted": bool(provenance.get("trusted")),
        },
        "sha_binding": {
            "required": requires_current_sha,
            "target_sha": target_sha if requires_current_sha else None,
            "current_sha": current_sha if requires_current_sha else None,
        },
        "availability": availability,
        "quota": {"used": usage, "limit": limit, "headroom": round(quota_headroom, 4)},
        "repository_evidence": {
            "kind": "historic_3l0_prior" if success_entry else "missing",
            "sample_count": 0,
            "confidence": round(repository_evidence_confidence, 4),
            "score": round(repository_outcome, 4),
        },
        "external_inference": {
            "kind": "neutral_public_feature_prior",
            "score": public_board_prior,
        },
        "score_components": {
            "repository_outcome_weight": 0.55,
            "evidence_confidence_weight": 0.15,
            "external_inference_weight": 0.15,
            "availability_headroom_weight": 0.15,
            "historic_elo": elo,
            "role_suitability": suitability,
            "score": round(score, 4),
        },
        "eligible": exclusion is None and availability not in {"blocked", "unavailable"},
        "exclusion": exclusion,
    }


def decide(
    *,
    capability: str,
    candidates: Iterable[dict[str, Any]],
    mode: str = OBSERVE_MODE,
) -> dict[str, Any]:
    """Return a stable bounded observation without executing a specialist."""
    if mode != OBSERVE_MODE:
        raise ValueError("AR-17 accepts observe mode only")
    all_candidates = list(candidates)[:MAX_CANDIDATES]
    eligible = [candidate for candidate in all_candidates if candidate["eligible"]]
    eligible.sort(
        key=lambda item: (
            item["score_components"]["score"],
            item["quota"]["headroom"],
            item["specialist"]["provider"],
            item["specialist"]["model"],
        ),
        reverse=True,
    )
    recommendation = eligible[0]["specialist"] if eligible else None
    runner_up = eligible[1]["specialist"] if len(eligible) > 1 else None
    state = "recommended" if recommendation else "no_eligible_specialist"
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": OBSERVE_MODE,
        "capability": capability,
        "state": state,
        "recommendation": recommendation,
        "runner_up": runner_up,
        "candidates": all_candidates,
        "summary": (
            f"observe capability={capability} state={state} "
            f"recommendation={recommendation['provider']}/{recommendation['model']}"
            if recommendation
            else f"observe capability={capability} state={state}"
        ),
    }


def compact_envelope(decision: dict[str, Any]) -> dict[str, Any]:
    """Keep workflow output to structured decision facts without raw source data."""
    return {
        "schema_version": decision["schema_version"],
        "mode": decision["mode"],
        "capability": decision["capability"],
        "state": decision["state"],
        "recommendation": decision["recommendation"],
        "runner_up": decision["runner_up"],
        "summary": decision["summary"],
        "candidates": [
            {
                "specialist": candidate["specialist"],
                "effect": candidate["effect"],
                "provenance": candidate["provenance"],
                "sha_binding": candidate["sha_binding"],
                "availability": candidate["availability"],
                "eligible": candidate["eligible"],
                "exclusion": candidate["exclusion"],
                "quota": candidate["quota"],
                "repository_evidence": candidate["repository_evidence"],
                "score_components": candidate["score_components"],
            }
            for candidate in decision["candidates"]
        ],
    }
