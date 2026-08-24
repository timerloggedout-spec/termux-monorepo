"""Job timestamp aggregation — preferred duration source after Timing API deprecation.

GitHub Actions job objects expose:
  started_at, completed_at  (ISO-8601)
  conclusion, name, steps[] (each with own timestamps)

This module is pure: accepts already-fetched mappings (from
GET .../actions/runs/{id}/jobs or webhook payloads). No network.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import median
from typing import Any, Mapping, Sequence


def parse_iso_ms(value: Any) -> int | None:
    """Parse ISO-8601 timestamp to epoch milliseconds. Returns None if missing/invalid."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    # Normalize Z and fractional seconds for fromisoformat
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
    """Duration of a single job from started_at → completed_at (ms).

    Returns None if either timestamp is missing or completed_at < started_at.
    """
    if not isinstance(job, Mapping):
        return None
    start = parse_iso_ms(job.get("started_at"))
    end = parse_iso_ms(job.get("completed_at"))
    if start is None or end is None:
        return None
    if end < start:
        return None
    return end - start


def duration_ms_from_jobs(jobs: Sequence[Mapping[str, Any]]) -> int | None:
    """Wall-clock span across jobs: min(started_at) → max(completed_at).

    Useful when a run has multiple parallel jobs; approximates run duration
    without the deprecated /timing endpoint.
    """
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


@dataclass(frozen=True)
class RunJobStats:
    """Stats for one workflow run's jobs payload."""

    run_id: int | None
    job_count: int
    failed_jobs: int
    durations_ms: tuple[int, ...]
    avg_job_duration_ms: float | None
    median_job_duration_ms: float | None
    wall_duration_ms: int | None  # min start → max complete
    jobs: tuple[JobDuration, ...] = field(default_factory=tuple)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "job_count": self.job_count,
            "failed_jobs": self.failed_jobs,
            "durations_ms": list(self.durations_ms),
            "avg_job_duration_ms": self.avg_job_duration_ms,
            "median_job_duration_ms": self.median_job_duration_ms,
            "wall_duration_ms": self.wall_duration_ms,
            "jobs": [
                {
                    "job_id": j.job_id,
                    "name": j.name,
                    "conclusion": j.conclusion,
                    "duration_ms": j.duration_ms,
                }
                for j in self.jobs
            ],
        }


def aggregate_run_job_stats(
    jobs_payload: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    *,
    run_id: int | None = None,
) -> RunJobStats:
    """Aggregate one run's jobs list (API response or bare list).

    Accepts either ``{"jobs": [...], "total_count": N}`` or a sequence of job dicts.
    """
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
        if d is not None:
            durations.append(d)
        if conclusion in {"failure", "timed_out", "cancelled"}:
            # count hard failures; cancelled optional — include for ops visibility
            if conclusion in {"failure", "timed_out"}:
                failed += 1
        details.append(
            JobDuration(
                job_id=job_id,
                name=name,
                conclusion=conclusion,
                duration_ms=d,
            )
        )

    avg = (sum(durations) / len(durations)) if durations else None
    med = float(median(durations)) if durations else None
    wall = duration_ms_from_jobs(job_list)

    return RunJobStats(
        run_id=run_id,
        job_count=len(job_list),
        failed_jobs=failed,
        durations_ms=tuple(durations),
        avg_job_duration_ms=avg,
        median_job_duration_ms=med,
        wall_duration_ms=wall,
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
        }


def aggregate_workflow_window(
    run_job_payloads: Sequence[Mapping[str, Any] | Sequence[Mapping[str, Any]]],
    *,
    run_ids: Sequence[int | None] | None = None,
) -> WorkflowWindowStats:
    """Aggregate a window of per-run jobs payloads into failure rate + durations.

    Compatible shape with UI CSV columns (failure %, avg run time, runs, jobs).
    """
    stats: list[RunJobStats] = []
    for i, payload in enumerate(run_job_payloads):
        rid = None
        if run_ids is not None and i < len(run_ids):
            rid = run_ids[i]
        stats.append(aggregate_run_job_stats(payload, run_id=rid))

    n = len(stats)
    runs_failed = sum(1 for s in stats if s.failed_jobs > 0)
    total_jobs = sum(s.job_count for s in stats)
    total_failed = sum(s.failed_jobs for s in stats)
    walls = [s.wall_duration_ms for s in stats if s.wall_duration_ms is not None]
    job_durs: list[int] = []
    for s in stats:
        job_durs.extend(s.durations_ms)

    return WorkflowWindowStats(
        run_count=n,
        runs_with_failures=runs_failed,
        failure_rate_pct=(100.0 * runs_failed / n) if n else 0.0,
        total_jobs=total_jobs,
        total_failed_jobs=total_failed,
        avg_wall_duration_ms=(sum(walls) / len(walls)) if walls else None,
        avg_job_duration_ms=(sum(job_durs) / len(job_durs)) if job_durs else None,
        run_stats=tuple(stats),
    )
