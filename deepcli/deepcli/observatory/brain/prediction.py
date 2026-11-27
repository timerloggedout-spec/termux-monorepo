"""Prediction/error observation; measured drift is advisory and policy-neutral."""
from __future__ import annotations
import math

def timing_error(expected_duration_ms: float, actual_duration_ms: float) -> dict[str, object]:
    expected, actual = float(expected_duration_ms), float(actual_duration_ms)
    if not math.isfinite(expected) or not math.isfinite(actual) or expected < 0 or actual < 0:
        raise ValueError("expected and actual durations must be finite and non-negative")
    drift = actual - expected
    status = "overrun" if drift > 0 else "underrun" if drift < 0 else "on_time"
    return {"schema_version": "brain.prediction-error.v1", "expected_ms": expected,
            "actual_ms": actual, "drift_ms": drift, "status": status, "policy_action": "observe_only"}
