"""Attention focus: rank typed signals by explicit priority, salience, and confidence."""
from __future__ import annotations
import math
from typing import Any, Iterable, Mapping


def focus_signals(signals: Iterable[Mapping[str, Any]], max_focus: int = 8) -> dict[str, Any]:
    """Return a deterministic bounded focus set and an ordered deferred set."""
    if isinstance(max_focus, bool) or not isinstance(max_focus, int) or max_focus < 1:
        raise ValueError("max_focus must be a positive integer")
    ranked = []
    for raw in signals:
        signal_id = str(raw.get("signal_id", "")).strip()
        if not signal_id:
            raise ValueError("attention signals require a signal_id")
        priority = raw.get("priority", 0)
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 5:
            raise ValueError(f"signal {signal_id} priority must be an integer from 0 through 5")
        salience = float(raw.get("salience", 0.5))
        confidence = float(raw.get("confidence", 0.5))
        if not math.isfinite(salience) or not 0.0 <= salience <= 1.0:
            raise ValueError(f"signal {signal_id} salience must be between 0 and 1")
        if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
            raise ValueError(f"signal {signal_id} confidence must be between 0 and 1")
        sequence = raw.get("sequence", 0)
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError(f"signal {signal_id} sequence must be a non-negative integer")
        ranked.append({"signal_id": signal_id, "priority": priority, "salience": salience,
                       "confidence": confidence, "sequence": sequence})
    ranked.sort(key=lambda item: (-item["priority"], -item["salience"], -item["confidence"], item["sequence"], item["signal_id"]))
    focused, deferred = ranked[:max_focus], ranked[max_focus:]
    return {
        "schema_version": "brain.attention.focus.v1",
        "policy_version": "brain.attention.lexicographic.v1",
        "max_focus": max_focus,
        "focus_signal_ids": [item["signal_id"] for item in focused],
        "deferred_signal_ids": [item["signal_id"] for item in deferred],
        "ranking": ranked,
    }
