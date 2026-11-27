"""Composer: deterministic intent-to-score assembly over existing control-plane plans."""
from __future__ import annotations
import hashlib
import json
from typing import Any, Iterable, Mapping
from .context import build_context
from .executive import normalize_intent
from .signals import normalize_signals
from ..conductor import ConductorPlacement, build_cue_sheet

def compose_score(intent: Mapping[str, Any], signals: Iterable[Mapping[str, Any]],
                  plan: Mapping[str, Any], assignments: Mapping[str, Mapping[str, Any]],
                  placement: ConductorPlacement | str = ConductorPlacement.MANAGER_POLICY,
                  episodes: Iterable[Mapping[str, Any]] = ()) -> dict[str, Any]:
    """Compile a stable, auditable score from intent, observations, and a Ballet plan."""
    normalized_intent = normalize_intent(intent)
    normalized_signals = normalize_signals(signals)
    context = build_context(normalized_signals, episodes=episodes)
    cue_sheet = build_cue_sheet(plan, assignments, placement)
    score = {
        "schema_version": "brain.composer.score.v1",
        "intent": normalized_intent,
        "context": context,
        "signal_ids": [item["signal_id"] for item in normalized_signals],
        "plan": {"waves": [list(wave) for wave in plan["waves"]],
                 "task_count": sum(len(wave) for wave in plan["waves"])},
        "cue_sheet": cue_sheet,
        "authority": {
            "composer": "intent_and_score_composition_only",
            "readiness": "dependency_phase_engine",
            "wave_planning": "ballet_coordinator",
            "admission_and_claims": "QUE",
            "execution": "specialist_adapters",
            "evidence": "ATES",
        },
        "adaptation": "candidate_only; validated_observations_and_explicit_policy_version_required",
    }
    canonical = json.dumps(score, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    score["score_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return score
