"""Homeostatic observation planning; returns a wake recommendation, never a timer."""
from __future__ import annotations

def plan_wake(now_ms: int, event_deadline_ms: int | None = None,
              window_close_ms: int | None = None, max_wait_ms: int = 60_000) -> dict[str, int | str]:
    if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
        raise ValueError("now_ms must be a non-negative integer")
    if isinstance(max_wait_ms, bool) or not isinstance(max_wait_ms, int) or max_wait_ms < 1:
        raise ValueError("max_wait_ms must be a positive integer")
    candidates: list[tuple[int, str]] = [(now_ms + max_wait_ms, "max_wait")]
    for value, reason in ((event_deadline_ms, "event_deadline"), (window_close_ms, "window_close")):
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{reason} must be an integer timestamp")
            if value > now_ms:
                candidates.append((value, reason))
    wake_at, reason = min(candidates, key=lambda item: (item[0], item[1]))
    return {"schema_version": "brain.homeostasis.wake.v1", "wake_at_ms": wake_at,
            "wake_in_ms": wake_at - now_ms, "wake_reason": reason}
