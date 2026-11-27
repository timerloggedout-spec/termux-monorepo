"""Composer: deterministic intent-to-score assembly over existing control-plane plans."""
from __future__ import annotations
import hashlib
import json
from typing import Any, Callable, Iterable, Mapping
from .action_selection import select_actions
from .attention import focus_signals
from .context import build_context
from .executive import normalize_intent
from .homeostasis import plan_wake
from .prediction import timing_error
from .signals import normalize_signals
from ..conductor import ConductorPlacement, build_cue_sheet
from ..ballet import validate_ates_receipt


def compose_score(
    intent: Mapping[str, Any],
    signals: Iterable[Mapping[str, Any]],
    plan: Mapping[str, Any],
    assignments: Mapping[str, Mapping[str, Any]],
    placement: ConductorPlacement | str = ConductorPlacement.MANAGER_POLICY,
    episodes: Iterable[Mapping[str, Any]] = (),
    action_candidates: Iterable[Mapping[str, Any]] = (),
    max_parallel: int = 1,
    timing_observations: Iterable[Mapping[str, Any]] = (),
    wake_context: Mapping[str, Any] | None = None,
    receipt_resolver: Callable[[str], Mapping[str, Any]] | None = None,
    attention_budget: int = 8,
) -> dict[str, Any]:
    """Compile a stable, auditable score from intent, signals, plans, and feedback."""
    normalized_intent = normalize_intent(intent)
    normalized_signals = normalize_signals(signals)
    context = build_context(normalized_signals, episodes=episodes)
    attention = focus_signals(normalized_signals, max_focus=attention_budget)
    cue_sheet = build_cue_sheet(plan, assignments, placement)
    action_shortlist = select_actions(action_candidates, max_parallel=max_parallel)
    timing_feedback = []
    for observation in timing_observations:
        task_id = str(observation.get("task_id", "")).strip()
        if not task_id:
            raise ValueError("timing observation requires a task_id")
        if receipt_resolver is None:
            raise ValueError("timing feedback requires a canonical ATES receipt resolver")
        receipt = validate_ates_receipt({"receipt": observation.get("receipt")})
        canonical_receipt = validate_ates_receipt({"receipt": receipt_resolver(receipt["evidence_ref"])})
        if canonical_receipt != receipt:
            raise ValueError(f"ATES receipt verification mismatch for timing task {task_id}")
        timing_feedback.append({
            "task_id": task_id,
            **receipt,
            **timing_error(observation["expected_duration_ms"], observation["actual_duration_ms"]),
        })
    wake_recommendation = plan_wake(**dict(wake_context)) if wake_context is not None else None
    score = {
        "schema_version": "brain.composer.score.v3",
        "intent": normalized_intent,
        "context": context,
        "attention": attention,
        "signal_ids": [item["signal_id"] for item in normalized_signals],
        "plan": {"waves": [list(wave) for wave in plan["waves"]],
                 "task_count": sum(len(wave) for wave in plan["waves"])},
        "action_shortlist": action_shortlist,
        "action_selection_policy": {
            "policy_version": "brain.action-selection.write-disjoint.v1",
            "max_parallel": max_parallel,
        },
        "timing_feedback": timing_feedback,
        "wake_recommendation": wake_recommendation,
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
