"""Job timestamp aggregation — preferred duration source after Timing API deprecation.

GitHub Actions job objects expose:
  started_at, completed_at  (ISO-8601)
  optional queued_at
  conclusion, name, steps[] (each with own timestamps)

This module is pure: accepts already-fetched mappings (from
GET .../actions/runs/{id}/jobs or webhook payloads). No network.

Policy defaults match ops/github-telemetry/config/metric-policy.yaml
(actions-perf-v1): failure set = failure, timed_out.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import median
from typing import Any, Mapping, Sequence

# Default failure set (metric-policy actions-perf-v1)
DEFAULT_FAILURE_CONCLUSIONS: frozenset[str] = frozenset({"failure", "timed_out"})
DEFAULT_SOFT_FAILURES: frozenset[str] = frozenset({"cancelled", "action_required"})
DEFAULT_EXCLUDED: frozenset[str] = frozenset({"skipped", "neutral"})


def parse_iso_ms(value: Any) -> int | None:
    """Parse ISO-8601 timestamp to epoch milliseconds. Returns None if missing/invalid."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def duration_ms_from_job(job: Mapping[str, Any]) -> int | None:
    """Runtime: completed_at - started_at (ms). None if incomplete/invalid."""
    if not isinstance(job, Mapping):
        return None
    start = parse_iso_ms(job.get("started_at"))
    end = parse_iso_ms(job.get("completed_at"))
    if start is None or end is None:
        return None
    if end < start:
        return None
    return end - start


def queue_ms_from_job(job: Mapping[str, Any]) -> int | None:
    """Queue time: started_at - queued_at (ms). None if queued_at absent."""
    if not isinstance(job, Mapping):
        return None
    queued = parse_iso_ms(job.get("queued_at"))
    started = parse_iso_ms(job.get("started_at"))
    if queued is None or started is None:
        return None
    if started < queued:
        return None
    return started - queued


def duration_ms_from_jobs(jobs: Sequence[Mapping[str, Any]]) -> int | None:
    """Wall-clock span: min(started_at) → max(completed_at)."""
    starts: list[int] = []
    ends: list[int] = []
    for j in jobs:
        if not isinstance(j, Mapping):
            continue
        s = parse_iso_ms(j.get("started_at"))
        e = parse_iso_ms(j.get("completed_at"))
        if s is not None:
            starts.append(s)
        if e is not None:
            ends.append(e)
    if not starts or not ends:
        return None
    span = max(ends) - min(starts)
    return span if span >= 0 else None


@dataclass(frozen=True)
class JobDuration:
    job_id: int | None
    name: str
    conclusion: str
    duration_ms: int | None
    queue_ms: int | None = None


@dataclass(frozen=True)
class RunJobStats:
    """Stats for one workflow run's jobs payload."""

    run_id: int | None
    job_count: int
    failed_jobs: int
    durations_ms: tuple[int, ...]
    avg_job_duration_ms: float | None
    median_job_duration_ms: float | None
    wall_duration_ms: int | None
    avg_queue_ms: float | None = None
    jobs: tuple[JobDuration, ...] = field(default_factory=tuple)
    metric_version: str = "actions-perf-v1"

    def to_mapping(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "job_count": self.job_count,
            "failed_jobs": self.failed_jobs,
            "durations_ms": list(self.durations_ms),
            "avg_job_duration_ms": self.avg_job_duration_ms,
            "median_job_duration_ms": self.median_job_duration_ms,
            "wall_duration_ms": self.wall_duration_ms,
            "avg_queue_ms": self.avg_queue_ms,
            "metric_version": self.metric_version,
            "label": "locally_reconstructed",
            "jobs": [
                {
                    "job_id": j.job_id,
                    "name": j.name,
                    "conclusion": j.conclusion,
                    "duration_ms": j.duration_ms,
                    "queue_ms": j.queue_ms,
                }
                for j in self.jobs
            ],
        }


def aggregate_run_job_stats(
    jobs_payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    *,
    run_id: int | None = None,
    failure_conclusions: frozenset[str] | None = None,
) -> RunJobStats:
    """Aggregate one run's jobs list (API response or bare list).

    Accepts either ``{"jobs": [...], "total_count": N}`` or a sequence of job dicts.
    """
    fail_set = failure_conclusions or DEFAULT_FAILURE_CONCLUSIONS
    if isinstance(jobs_payload, Mapping):
        raw = jobs_payload.get("jobs") or []
        if run_id is None and jobs_payload.get("run_id") is not None:
            try:
                run_id = int(jobs_payload["run_id"])  # type: ignore[index]
            except (TypeError, ValueError):
                pass
    else:
        raw = jobs_payload

    job_list: list[Mapping[str, Any]] = [
        j for j in raw if isinstance(j, Mapping)
    ]

    details: list[JobDuration] = []
    durations: list[int] = []
    queues: list[int] = []
    failed = 0
    for j in job_list:
        jid = j.get("id")
        try:
            job_id = int(jid) if jid is not None else None
        except (TypeError, ValueError):
            job_id = None
        name = str(j.get("name") or "")
        conclusion = str(j.get("conclusion") or j.get("status") or "").lower()
        d = duration_ms_from_job(j)
        q = queue_ms_from_job(j)
        if d is not None:
            durations.append(d)
        if q is not None:
            queues.append(q)
        if conclusion in fail_set:
            failed += 1
        details.append(
            JobDuration(
                job_id=job_id,
                name=name,
                conclusion=conclusion,
                duration_ms=d,
                queue_ms=q,
            )
        )

    avg = (sum(durations) / len(durations)) if durations else None
    med = float(median(durations)) if durations else None
    avg_q = (sum(queues) / len(queues)) if queues else None
    wall = duration_ms_from_jobs(job_list)

    return RunJobStats(
        run_id=run_id,
        job_count=len(job_list),
        failed_jobs=failed,
        durations_ms=tuple(durations),
        avg_job_duration_ms=avg,
        median_job_duration_ms=med,
        wall_duration_ms=wall,
        avg_queue_ms=avg_q,
        jobs=tuple(details),
    )


@dataclass(frozen=True)
class WorkflowWindowStats:
    """Aggregated stats across multiple runs for one workflow window."""

    run_count: int
    runs_with_failures: int
    failure_rate_pct: float  # 0–100
    total_jobs: int
    total_failed_jobs: int
    avg_wall_duration_ms: float | None
    avg_job_duration_ms: float | None
    avg_queue_ms: float | None = None
    window_label: str = ""  # e.g. 7d, 30d, all
    metric_version: str = "actions-perf-v1"
    run_stats: tuple[RunJobStats, ...] = field(default_factory=tuple)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "run_count": self.run_count,
            "runs_with_failures": self.runs_with_failures,
            "failure_rate_pct": self.failure_rate_pct,
            "total_jobs": self.total_jobs,
            "total_failed_jobs": self.total_failed_jobs,
            "avg_wall_duration_ms": self.avg_wall_duration_ms,
            "avg_job_duration_ms": self.avg_job_duration_ms,
            "avg_queue_ms": self.avg_queue_ms,
            "window_label": self.window_label,
            "metric_version": self.metric_version,
            "label": "locally_reconstructed",
        }


def aggregate_workflow_window(
    run_job_payloads: Sequence[Mapping[str, Any] | Sequence[Mapping[str, Any]]],
    *,
    run_ids: Sequence[int | None] | None = None,
    failure_conclusions: frozenset[str] | None = None,
    window_label: str = "",
) -> WorkflowWindowStats:
    """Aggregate a window of per-run jobs payloads into failure rate + durations.

    Compatible shape with UI CSV columns (failure %, avg run time, runs, jobs).
    Results are locally reconstructed — not claimed as GitHub UI metrics.
    """
    stats: list[RunJobStats] = []
    for i, payload in enumerate(run_job_payloads):
        rid = None
        if run_ids is not None and i < len(run_ids):
            rid = run_ids[i]
        stats.append(
            aggregate_run_job_stats(
                payload,
                run_id=rid,
                failure_conclusions=failure_conclusions,
            )
        )

    n = len(stats)
    runs_failed = sum(1 for s in stats if s.failed_jobs > 0)
    total_jobs = sum(s.job_count for s in stats)
    total_failed = sum(s.failed_jobs for s in stats)
    walls = [s.wall_duration_ms for s in stats if s.wall_duration_ms is not None]
    job_durs: list[int] = []
    queues: list[float] = []
    for s in stats:
        job_durs.extend(s.durations_ms)
        if s.avg_queue_ms is not None:
            queues.append(s.avg_queue_ms)

    return WorkflowWindowStats(
        run_count=n,
        runs_with_failures=runs_failed,
        failure_rate_pct=(100.0 * runs_failed / n) if n else 0.0,
        total_jobs=total_jobs,
        total_failed_jobs=total_failed,
        avg_wall_duration_ms=(sum(walls) / len(walls)) if walls else None,
        avg_job_duration_ms=(sum(job_durs) / len(job_durs)) if job_durs else None,
        avg_queue_ms=(sum(queues) / len(queues)) if queues else None,
        window_label=window_label,
        run_stats=tuple(stats),
    )
