"""Temporal assignment and collector primitives.

These functions classify timing and plan observation wakeups. The dependency
phase engine owns readiness; QUE owns admission and claims; adapters own
execution. This module adds temporal evidence without creating a scheduler.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Iterable

class TemporalError(ValueError):
    """Raised when temporal inputs are incomplete or inconsistent."""

class Phase(str, Enum):
    EARLY = "off_beat_early"
    ON_BEAT = "on_beat"
    LATE = "off_beat_late"
    WINDOW_EXPIRED = "window_expired"

class QueObservation(str, Enum):
    QUEUED = "queued"
    STARTED = "started"
    COMPLETED_OBSERVED = "completed_observed"
    CANCELLED = "cancelled"
    RECONCILE_MISSING = "reconcile_missing"

@dataclass(frozen=True)
class AssignmentWindow:
    nominal_at: datetime
    opens_at: datetime
    closes_at: datetime
    expected_duration: timedelta

    def __post_init__(self):
        for name, value in (("nominal_at", self.nominal_at), ("opens_at", self.opens_at), ("closes_at", self.closes_at)):
            _aware(value, name)
        if not (_utc(self.opens_at) <= _utc(self.nominal_at) <= _utc(self.closes_at)):
            raise TemporalError("nominal_at must fall inside the assignment window")
        if self.expected_duration <= timedelta(0):
            raise TemporalError("expected_duration must be positive")

    @property
    def open_length(self):
        return _utc(self.closes_at) - _utc(self.opens_at)

@dataclass(frozen=True)
class TimingObservation:
    phase: Phase
    phase_offset: timedelta
    duration_overrun: bool
    window_expired: bool

@dataclass(frozen=True)
class WakePlan:
    wake_at: datetime
    reason: str

@dataclass(frozen=True)
class CollectorCycle:
    epoch: datetime
    period: timedelta
    phase: timedelta = timedelta(0)

    def __post_init__(self):
        _aware(self.epoch, "epoch")
        if self.period <= timedelta(0):
            raise TemporalError("collector period must be positive")
        if not (timedelta(0) <= self.phase < self.period):
            raise TemporalError("collector phase must be in [0, period)")

    def next_tick_after(self, instant):
        _aware(instant, "instant")
        epoch_utc = _utc(self.epoch)
        instant_utc = _utc(instant)
        elapsed = instant_utc - epoch_utc - self.phase
        ticks = elapsed // self.period + 1
        tick_utc = epoch_utc + self.phase + ticks * self.period
        return tick_utc.astimezone(self.epoch.tzinfo)

def _aware(value, name):
    if value.tzinfo is None or value.utcoffset() is None:
        raise TemporalError(f"{name} must be timezone-aware")

def classify_assignment(window, observed_start, observed_finish=None):
    """Classify phase displacement separately from duration and expiry."""
    _aware(observed_start, "observed_start")
    if observed_finish is not None:
        _aware(observed_finish, "observed_finish")
        if observed_finish < observed_start:
            raise TemporalError("observed_finish must follow observed_start")
    offset = observed_start - window.nominal_at
    if observed_start < window.opens_at or observed_start > window.closes_at:
        phase = Phase.WINDOW_EXPIRED
    elif offset < timedelta(0):
        phase = Phase.EARLY
    elif offset > timedelta(0):
        phase = Phase.LATE
    else:
        phase = Phase.ON_BEAT
    overrun = finish_utc is not None and finish_utc - start_utc > window.expected_duration
    return TimingObservation(phase, offset, bool(overrun), phase is Phase.WINDOW_EXPIRED)

def plan_wait(now, *, expected_completion=None, window_close=None, max_wait_until=None, event_ready=False):
    """Choose the earliest deterministic wake boundary for a WAIT to WATCH loop."""
    _aware(now, "now")
    now_utc = _utc(now)
    candidates = []
    for value, reason, name in (
        (expected_completion, "expected_completion", "expected_completion"),
        (window_close, "window_close", "window_close"),
        (max_wait_until, "max_wait", "max_wait_until"),
    ):
        if value is not None:
            _aware(value, name)
            candidates.append((max(_utc(value), now_utc), reason))
    if event_ready:
        candidates.append((now_utc, "event"))
    if not candidates:
        raise TemporalError("WAIT requires an event or at least one time boundary")
    wake_at, reason = min(candidates, key=lambda item: (item[0], item[1]))
    return WakePlan(wake_at, reason)

def classify_que_event(state):
    """Map QUE lifecycle facts to observations; completion remains a lifecycle fact."""
    mapping = {
        "queued": QueObservation.QUEUED,
        "started": QueObservation.STARTED,
        "completed": QueObservation.COMPLETED_OBSERVED,
        "cancelled": QueObservation.CANCELLED,
        "vanished": QueObservation.RECONCILE_MISSING,
    }
    normalized = state.strip().lower()
    try:
        return mapping[normalized]
    except KeyError as exc:
        raise TemporalError(f"unsupported QUE lifecycle state: {state}") from exc

def next_collector_ticks(cycles: Iterable[CollectorCycle], after: datetime):
    """Return independent collector wake times in stable chronological order."""
    _aware(after, "after")
    return tuple(sorted((cycle.next_tick_after(after) for cycle in cycles), key=_utc))
