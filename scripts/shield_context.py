"""SHIELD: bounded, provenance-preserving task-context admission.

Pure policy helpers only. This module does not persist context, access files,
or perform network operations. Callers decide where admitted context is used.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any

SCHEMA = "shield-context/v1"
MAX_ITEMS = 128
MAX_CHARS = 50_000
MAX_TASK_CHARS = 2_000
MAX_SOURCE_REF_CHARS = 512

_SECRET_KEY_PARTS = (
    "api_key", "apikey", "access_token", "refresh_token", "authorization",
    "cookie", "password", "secret", "private_key", "session_id",
    "credential", "bearer",
)
_INSTRUCTION_OVERRIDE = re.compile(
    r"(?:ignore|disregard|override)\s+(?:all\s+)?(?:previous|prior|system|developer)\s+instructions"
    r"|reveal\s+(?:the\s+)?secrets?"
    r"|send\s+(?:the\s+)?credentials?",
    re.IGNORECASE,
)


def _has_secret_key(value: Any, depth: int = 0) -> bool:
    if depth > 6:
        return True
    if isinstance(value, dict):
        for key, child in value.items():
            name = str(key).lower().replace("-", "_")
            if any(part in name for part in _SECRET_KEY_PARTS):
                return True
            if _has_secret_key(child, depth + 1):
                return True
    elif isinstance(value, (list, tuple)):
        return any(_has_secret_key(child, depth + 1) for child in value[:128])
    return False


def _safe_ref(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > MAX_SOURCE_REF_CHARS or any(ord(c) < 32 for c in value):
        return None
    return value


def _safe_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.replace("\x00", "").strip()


def classify_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Classify a signal without returning its text or payload."""
    if not isinstance(signal, dict):
        return {"disposition": "quarantine", "reason": "invalid_signal", "source_ref": None}

    source_ref = _safe_ref(signal.get("source_ref"))
    text = _safe_text(signal.get("text"))
    urgency = signal.get("urgency") if signal.get("urgency") in {"low", "normal", "high", "critical"} else "unknown"
    relevance = signal.get("relevance")
    if isinstance(relevance, bool) or not isinstance(relevance, (int, float)) or not math.isfinite(relevance):
        relevance = None
    elif not 0 <= relevance <= 1:
        relevance = None

    base = {
        "source_ref": source_ref,
        "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else None,
        "content_chars": len(text),
        "relevance": relevance,
        "urgency": urgency,
    }

    if _has_secret_key(signal):
        return {**base, "disposition": "quarantine", "reason": "secret_bearing_signal"}
    if signal.get("security_critical") is True or urgency == "critical":
        return {**base, "disposition": "escalate", "reason": "critical_security_or_operational_signal"}
    if _INSTRUCTION_OVERRIDE.search(text):
        return {**base, "disposition": "quarantine", "reason": "instruction_override_detected"}
    if signal.get("trusted") is not True:
        return {**base, "disposition": "quarantine", "reason": "source_trust_not_established"}
    if source_ref is None:
        return {**base, "disposition": "quarantine", "reason": "source_provenance_missing"}
    if relevance is None:
        return {**base, "disposition": "defer", "reason": "relevance_evidence_unknown"}
    if relevance < 0.35:
        return {**base, "disposition": "defer", "reason": "below_relevance_threshold"}
    if not text:
        return {**base, "disposition": "defer", "reason": "content_missing"}
    return {**base, "disposition": "admit", "reason": "trusted_relevant_source"}


def _bounded_strings(value: Any, *, limit: int, item_chars: int) -> list[str]:
    if not isinstance(value, list):
        return []
    output = []
    for item in value[:limit]:
        if isinstance(item, str):
            cleaned = _safe_text(item)
            if cleaned:
                output.append(cleaned[:item_chars])
    return output


def build_capsule(
    task: dict[str, Any],
    signals: list[dict[str, Any]],
    max_items: int = 24,
    max_chars: int = 12_000,
) -> dict[str, Any]:
    """Build an in-memory task capsule with bounded, admitted signal content.

    The result is suitable for local context assembly. Callers must emit only
    the summary/metadata fields to telemetry, never the capsule content.
    """
    if not isinstance(task, dict):
        raise ValueError("task_must_be_object")
    if not isinstance(signals, list):
        raise ValueError("signals_must_be_list")

    item_limit = max(0, min(int(max_items), MAX_ITEMS))
    char_limit = max(0, min(int(max_chars), MAX_CHARS))
    task_id = _safe_text(task.get("task_id"))[:128]
    objective = _safe_text(task.get("objective"))[:MAX_TASK_CHARS]
    if not task_id or not objective:
        raise ValueError("task_id_and_objective_required")

    current_sha = task.get("current_sha")
    if not isinstance(current_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", current_sha):
        current_sha = None

    source_refs = []
    for ref in _bounded_strings(task.get("source_refs"), limit=32, item_chars=MAX_SOURCE_REF_CHARS):
        safe = _safe_ref(ref)
        if safe and safe not in source_refs:
            source_refs.append(safe)

    constraints = _bounded_strings(task.get("constraints"), limit=16, item_chars=500)
    allowed_effects = _bounded_strings(task.get("allowed_effects"), limit=16, item_chars=128)

    admitted = []
    counts = {"admit": 0, "quarantine": 0, "defer": 0, "escalate": 0}
    used_chars = 0
    omitted = max(0, len(signals) - item_limit)

    for signal in signals[:item_limit]:
        classified = classify_signal(signal)
        disposition = classified["disposition"]
        counts[disposition] += 1
        entry = dict(classified)
        if disposition == "admit":
            text = _safe_text(signal.get("text"))
            remaining = char_limit - used_chars
            if remaining <= 0:
                entry["disposition"] = "defer"
                entry["reason"] = "context_budget_exhausted"
                counts["admit"] -= 1
                counts["defer"] += 1
            else:
                content = text[:remaining]
                entry["content"] = content
                entry["truncated"] = len(content) < len(text)
                used_chars += len(content)
        admitted.append(entry)

    return {
        "schema": SCHEMA,
        "task": {
            "task_id": task_id,
            "objective": objective,
            "constraints": constraints,
            "source_refs": source_refs,
            "current_sha": current_sha,
            "allowed_effects": allowed_effects,
        },
        "signals": admitted,
        "counts": counts,
        "budget": {
            "max_items": item_limit,
            "max_chars": char_limit,
            "used_chars": used_chars,
            "omitted_signals": omitted,
        },
    }
