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


def _complexity_value(value: Any) -> float | None:
    """Return valid non-negative complexity evidence, preserving invalidity."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _complexity(entry: Mapping[str, Any]) -> float | None:
    """Resolve explicit complexity, then the documented structural fallback.

    Returning ``None`` is deliberate: missing or invalid complexity is evidence
    absence, not zero work. A caller must not silently manufacture a value.
    """
    explicit = entry.get("complexity_score")
    if explicit is not None:
        return _complexity_value(explicit)

    metrics = entry.get("metrics")
    if isinstance(metrics, Mapping):
        explicit = metrics.get("complexity_score")
        if explicit is not None:
            return _complexity_value(explicit)

        # Structural fallback: logarithmic churn dampens verbosity while file
        # count prevents a single giant file from looking like trivial work.
        additions = metrics.get("additions")
        deletions = metrics.get("deletions")
        files_changed = metrics.get("files_changed")
        if additions is not None and deletions is not None and files_changed is not None:
            additions_value = _complexity_value(additions)
            deletions_value = _complexity_value(deletions)
            files_value = _complexity_value(files_changed)
            if additions_value is None or deletions_value is None or files_value is None:
                return None
            return math.log1p(additions_value + deletions_value) * math.sqrt(files_value)

    return None


def _duration(events: list[Mapping[str, Any]]) -> float:
    """Return the wall-clock span covered by valid timestamped events.

    A malformed timestamp is isolated to its record. Valid timestamps still
    provide useful workflow duration evidence instead of aborting the reduction.
    """
    stamps: list[datetime] = []
    for event in events:
        value = event.get("timestamp")
        if not value:
            continue
        try:
            stamp = _ts(str(value))
        except ValueError:
            # Ingestion should reject malformed records when possible; the pure
            # reducer remains resilient so one bad event cannot erase valid data.
            continue
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            # The telemetry contract requires an explicit timezone/offset.
            continue
        stamps.append(stamp)
    if len(stamps) < 2:
        return 0.0
    return max(0.0, (max(stamps) - min(stamps)).total_seconds())


def _bounded_ratio(numerator: int | None, denominator: int | None, *, metric_name: str) -> float | None:
    """Calculate a bounded evidence ratio without manufacturing missing data.

    Counts must be non-negative integers and numerator cannot exceed denominator.
    An unknown count or zero denominator returns None; invalid known counts fail
    loudly so corrupt aggregate inputs are not silently normalized.
    """
    if numerator is None or denominator is None:
        return None
    if (
        isinstance(numerator, bool)
        or isinstance(denominator, bool)
        or not isinstance(numerator, int)
        or not isinstance(denominator, int)
    ):
        raise ValueError(f"{metric_name} counts must be integers")
    if numerator < 0 or denominator < 0:
        raise ValueError(f"{metric_name} counts must be non-negative")
    if numerator > denominator:
        raise ValueError(f"{metric_name} numerator cannot exceed denominator")
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def evidence_coverage_ratio(
    valid_required_observations: int | None,
    expected_required_observations: int | None,
) -> float | None:
    """Return valid required observations / expected observations, or None."""
    return _bounded_ratio(
        valid_required_observations,
        expected_required_observations,
        metric_name="evidence coverage ratio",
    )


def validated_outcome_rate(
    explicit_validation_passes: int | None,
    tasks_with_explicit_validation_outcome: int | None,
) -> float | None:
    """Return explicit validation passes / tasks with an explicit outcome."""
    return _bounded_ratio(
        explicit_validation_passes,
        tasks_with_explicit_validation_outcome,
        metric_name="validated outcome rate",
    )


def validation_coverage(
    tasks_with_explicit_validation_outcome: int | None,
    completed_tasks: int | None,
) -> float | None:
    """Return the share of completed tasks with an explicit validation outcome."""
    return _bounded_ratio(
        tasks_with_explicit_validation_outcome,
        completed_tasks,
        metric_name="validation coverage",
    )


def correlation_completeness(
    eligible_records_with_required_provenance: int | None,
    eligible_records: int | None,
) -> float | None:
    """Return the share of eligible records with the required provenance."""
    return _bounded_ratio(
        eligible_records_with_required_provenance,
        eligible_records,
        metric_name="correlation completeness",
    )


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
    if sequential_baseline_sec is not None and len(agents) > 0 and workflow_sec > 0:
        # Sequential baseline is only valid when explicitly supplied; never infer
        # one from the observed parallel run because that would bias the metric.
        eta = _positive(sequential_baseline_sec) / (len(agents) * workflow_sec)
    # ATES is a diagnostic composite. It is never used as a merge-quality gate.
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
        agents=len(agents),
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



def retry_amplification_ratio(
    total_attempts: int | None,
    logical_operations: int | None,
) -> float | None:
    """Return attempts per logical operation, including the initial attempt.

    A value of 1.0 means one attempt per operation on average. Values above 1
    indicate additional attempts. This is not a failure probability.
    """
    if total_attempts is None or logical_operations is None:
        return None
    if (
        isinstance(total_attempts, bool)
        or isinstance(logical_operations, bool)
        or not isinstance(total_attempts, int)
        or not isinstance(logical_operations, int)
    ):
        raise ValueError("retry amplification counts must be integers")
    if total_attempts < 0 or logical_operations < 0:
        raise ValueError("retry amplification counts must be non-negative")
    if logical_operations == 0:
        return None
    if total_attempts < logical_operations:
        raise ValueError("total attempts cannot be less than logical operations")
    return round(total_attempts / logical_operations, 6)


def retry_recovery_rate(
    retried_operations_that_eventually_succeeded: int | None,
    operations_with_at_least_one_retry: int | None,
) -> float | None:
    """Return the share of retried logical operations that eventually succeeded.

    The numerator and denominator count logical operations, not individual
    attempts. Operations still in progress or with unknown final state must not
    be included in the denominator.
    """
    return _bounded_ratio(
        retried_operations_that_eventually_succeeded,
        operations_with_at_least_one_retry,
        metric_name="retry recovery rate",
    )


def wilson_proportion_interval(
    successes: int | None,
    trials: int | None,
    *,
    z_score: float = 1.959963984540054,
) -> tuple[float, float] | None:
    """Return a two-sided Wilson score interval for a binomial proportion.

    Defaults to approximately 95% confidence. This interval is appropriate for
    a count of independent Bernoulli trials; clustered/repeated workflow events
    violate that assumption and need a cluster-aware analysis instead.
    """
    if successes is None or trials is None:
        return None
    if (
        isinstance(successes, bool)
        or isinstance(trials, bool)
        or not isinstance(successes, int)
        or not isinstance(trials, int)
    ):
        raise ValueError("Wilson interval counts must be integers")
    if successes < 0 or trials < 0:
        raise ValueError("Wilson interval counts must be non-negative")
    if successes > trials:
        raise ValueError("Wilson interval successes cannot exceed trials")
    if trials == 0:
        return None
    try:
        z = float(z_score)
    except (TypeError, ValueError) as exc:
        raise ValueError("z_score must be a finite positive number") from exc
    if not math.isfinite(z) or z <= 0:
        raise ValueError("z_score must be a finite positive number")

    proportion = successes / trials
    z_squared = z * z
    denominator = 1 + z_squared / trials
    center = (proportion + z_squared / (2 * trials)) / denominator
    margin = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / trials
            + z_squared / (4 * trials * trials)
        )
        / denominator
    )
    return (round(max(0.0, center - margin), 6), round(min(1.0, center + margin), 6))
