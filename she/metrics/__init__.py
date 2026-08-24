"""SHE metrics helpers — durable aggregation from Actions job timestamps.

No network. No dependency on the deprecated /timing endpoint.
Duration is derived from job (and optional step) started_at / completed_at.
"""

from she.metrics.job_timestamps import (
    JobDuration,
    RunJobStats,
    WorkflowWindowStats,
    aggregate_run_job_stats,
    aggregate_workflow_window,
    duration_ms_from_job,
    duration_ms_from_jobs,
    parse_iso_ms,
)

__all__ = [
    "JobDuration",
    "RunJobStats",
    "WorkflowWindowStats",
    "aggregate_run_job_stats",
    "aggregate_workflow_window",
    "duration_ms_from_job",
    "duration_ms_from_jobs",
    "parse_iso_ms",
]
