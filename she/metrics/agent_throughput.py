#!/usr/bin/env python3
"""Pure reducers for agent throughput telemetry.

The module is intentionally network-free and treats throughput as observational
telemetry. It never turns speed into a merge-quality gate.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping


def _ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp while accepting the common trailing ``Z``."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _positive(value: Any, default: float = 0.0) -> float:
    """Return a finite non-negative number, or the supplied safe default."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) and number >= 0 else default


@dataclass(frozen=True)
class ThroughputMetrics:
    """Immutable output record for one bounded agent-event reduction."""

    completed_tasks: int
    weighted_completion: float
    workflow_minutes: float
    active_seconds: float
    tool_actions: int
    failed_actions: int
    retries: int
    agents: int
    tcv_tasks_per_min: float
    wtcv_per_min: float | None
    retry_penalty_ratio: float
    action_density_per_active_sec: float
    parallel_yield: float | None
    ates: float | None
    token_processing_velocity: float | None
    context_ingestion_efficiency: float | None
    mean_tool_delay_ms: float | None
    mean_handoff_latency_ms: float | None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the immutable metric record for JSON/JSONL transport."""
        return asdict(self)


def _complexity(entry: Mapping[str, Any]) -> float | None:
    """Resolve explicit complexity, then the documented structural fallback.

    Returning ``None`` is deliberate: missing complexity is evidence absence, not
    zero work. A caller must not silently manufacture a complexity value.
    """
    explicit = entry.get("complexity_score")
    if explicit is not None:
        return _positive(explicit)

    metrics = entry.get("metrics")
    if isinstance(metrics, Mapping):
        explicit = metrics.get("complexity_score")
        if explicit is not None:
            return _positive(explicit)

        # Structural fallback: logarithmic churn dampens verbosity while file
        # count prevents a single giant file from looking like trivial work.
        additions = metrics.get("additions")
        deletions = metrics.get("deletions")
        files_changed = metrics.get("files_changed")
        if additions is not None and deletions is not None and files_changed is not None:
            churn = _positive(additions) + _positive(deletions)
            files = _positive(files_changed)
            return math.log1p(churn) * math.sqrt(files)

    return None


def _duration(events: list[Mapping[str, Any]]) -> float:
    """Return the wall-clock span covered by timestamped events."""
    stamps = [_ts(str(e["timestamp"])) for e in events if e.get("timestamp")]
    if len(stamps) < 2:
        return 0.0
    return max(0.0, (max(stamps) - min(stamps)).total_seconds())


def reduce_events(
    events: Iterable[Mapping[str, Any]],
    *,
    sequential_baseline_sec: float | None = None,
) -> ThroughputMetrics:
    """Reduce sanitized agent events into throughput and quality-adjacent metrics.

    ``parallel_yield`` and ATES require a declared sequential baseline. Missing
    baselines remain ``None`` so the reducer never invents a comparison cohort.
    """
    rows = [dict(e) for e in events]
    workflow_sec = _duration(rows)
    active_sec = sum(
        _positive(e.get("active_seconds"))
        for e in rows
        if e.get("event") == "active_window"
    )
    if active_sec <= 0:
        active_sec = sum(
            _positive(e.get("duration_ms")) / 1000
            for e in rows
            if e.get("event") == "tool_call"
        )
    if active_sec <= 0:
        active_sec = workflow_sec

    completed = [e for e in rows if e.get("event") == "task_completed"]
    tool_calls = [e for e in rows if e.get("event") == "tool_call"]
    retries = [e for e in rows if e.get("event") == "tool_retry"]
    failed = [
        e
        for e in tool_calls
        if str(e.get("status", "")).lower() in {"failed", "error"}
    ]
    agents = {str(e.get("agent_id")) for e in rows if e.get("agent_id")}

    complexities = [_complexity(e) for e in completed]
    known_complexities = [value for value in complexities if value is not None]
    weighted = sum(known_complexities)
    minutes = workflow_sec / 60 if workflow_sec else 0.0
    tcv = len(completed) / minutes if minutes else 0.0
    # Keep throughput observational: WTCV is unavailable if even one completed
    # task lacks complexity evidence, rather than pretending that task was 1.0.
    wtcv = weighted / minutes if minutes and len(known_complexities) == len(completed) else None

    action_count = len(tool_calls) + len(retries)
    rpi = (len(failed) + len(retries)) / action_count if action_count else 0.0
    density = action_count / active_sec if active_sec else 0.0

    eta = None
    if sequential_baseline_sec is not None and agents and workflow_sec > 0:
        # Sequential baseline is only valid when explicitly supplied; never infer
        # one from the observed parallel run because that would bias the metric.
        eta = _positive(sequential_baseline_sec) / (len(agents) * workflow_sec)
    ates = wtcv * max(0.0, 1.0 - rpi) * eta if wtcv is not None and eta is not None else None

    input_tokens = sum(_positive(e.get("tokens_in")) for e in rows)
    output_tokens = sum(_positive(e.get("tokens_out")) for e in rows)
    inference_sec = sum(_positive(e.get("inference_seconds")) for e in rows)
    tpv = (input_tokens + output_tokens) / inference_sec if inference_sec else None
    cie = output_tokens / input_tokens if input_tokens else None

    delays = [_positive(e.get("duration_ms")) for e in tool_calls if e.get("duration_ms") is not None]
    tool_delay = sum(delays) / len(delays) if delays else None
    handoffs = [
        _positive(e.get("latency_ms"))
        for e in rows
        if e.get("event") == "handoff"
    ]
    handoff = sum(handoffs) / len(handoffs) if handoffs else None

    return ThroughputMetrics(
        completed_tasks=len(completed),
        weighted_completion=round(weighted, 6),
        workflow_minutes=round(minutes, 6),
        active_seconds=round(active_sec, 6),
        tool_actions=action_count,
        failed_actions=len(failed),
        retries=len(retries),
        agents=len(agents) or 1,
        tcv_tasks_per_min=round(tcv, 6),
        wtcv_per_min=round(wtcv, 6) if wtcv is not None else None,
        retry_penalty_ratio=round(rpi, 6),
        action_density_per_active_sec=round(density, 6),
        parallel_yield=round(eta, 6) if eta is not None else None,
        ates=round(ates, 6) if ates is not None else None,
        token_processing_velocity=round(tpv, 6) if tpv is not None else None,
        context_ingestion_efficiency=round(cie, 6) if cie is not None else None,
        mean_tool_delay_ms=round(tool_delay, 6) if tool_delay is not None else None,
        mean_handoff_latency_ms=round(handoff, 6) if handoff is not None else None,
    )
