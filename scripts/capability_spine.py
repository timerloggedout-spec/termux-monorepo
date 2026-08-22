#!/usr/bin/env python3
"""Capability–scope–specialist decision helpers for AR-17 observe mode.

This module is intentionally pure: it consumes declared candidates and operational
facts, emits a bounded decision envelope, and has no provider, GitHub, or file
mutation capability. Callers retain all execution authority.
"""

from __future__ import annotations

from typing import Any, Iterable


SCHEMA_VERSION = 1
OBSERVE_MODE = "observe"
MAX_CANDIDATES = 16


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _normalise_elo(elo: float) -> float:
    """Map the existing 3L0/ELO-like values to a bounded, explainable prior."""
    return _clamp((float(elo) - 900.0) / 600.0)


def _availability_state(provider: str, model: str, has_provider: bool,
                        openrouter_models: set[str] | None,
                        openrouter_catalog_state: str) -> tuple[str, str | None]:
    if not has_provider:
        return "blocked", "provider credential or policy gate is unavailable"
    if provider != "openrouter":
        return "configured", None
    if openrouter_models is None:
        return "unavailable", "no live or cached OpenRouter catalog is available"
    if model not in openrouter_models:
        return "blocked", "model is absent from the permitted OpenRouter catalog"
    return openrouter_catalog_state, None


def make_candidate(
    *, provider: str, model: str, capability: str, has_provider: bool,
    openrouter_models: set[str] | None, openrouter_catalog_state: str,
    limits: dict[str, dict[str, int]], usage: int,
    success_entry: dict[str, Any],
) -> dict[str, Any]:
    """Create one candidate and expose all score components for review.

    Existing model-success values are retained as a *historic prior*, not claimed
    as a current measured repository outcome. Their low confidence prevents an
    unobserved value from silently outweighing later recorded evidence.
    """
    availability, exclusion = _availability_state(
        provider, model, has_provider, openrouter_models, openrouter_catalog_state
    )
    limit = int(limits.get(f"{provider}/{model}", limits.get(model, {})).get(capability, 0))
    if limit <= 0:
        availability = "blocked"
        exclusion = "no declared capability quota exists"
    elif usage >= limit:
        availability = "blocked"
        exclusion = f"soft budget exhausted ({usage}/{limit})"

    elo = float(success_entry.get("elo", 1000))
    suitability = float(success_entry.get("role_suitability", {}).get(capability, 1.0))
    historic_prior = _normalise_elo(elo) * _clamp(suitability / 1.3)
    repository_evidence_confidence = 0.20 if success_entry else 0.0
    repository_outcome = (
        historic_prior * repository_evidence_confidence
        + 0.50 * (1.0 - repository_evidence_confidence)
    )
    quota_headroom = _clamp((limit - usage) / limit) if limit else 0.0
    availability_component = quota_headroom if availability not in {"blocked", "unavailable"} else 0.0
    public_board_prior = 0.50
    evidence_confidence = repository_evidence_confidence
    score = (
        0.55 * repository_outcome
        + 0.15 * evidence_confidence
        + 0.15 * public_board_prior
        + 0.15 * availability_component
    )

    return {
        "specialist": {"provider": provider, "model": model},
        "capability": capability,
        "effect": "read_only_analysis",
        "provenance": {
            "declared_source": "llm-peers.yaml/model-success-matrix.yaml",
            "trusted": True,
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
        "eligible": availability not in {"blocked", "unavailable"},
        "exclusion": exclusion,
    }


def decide(
    *, capability: str, candidates: Iterable[dict[str, Any]],
    mode: str = OBSERVE_MODE,
) -> dict[str, Any]:
    """Return a stable bounded recommendation without executing any specialist."""
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
    """Bound workflow output to decision facts; omit free-form source data."""
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
