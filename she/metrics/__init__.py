"""SHE metrics helpers — durable Actions timing and agent throughput reducers.

No network. No dependency on the deprecated /timing endpoint.
"""

from she.metrics.agent_throughput import ThroughputMetrics, reduce_events
from she.metrics.job_timestamps import (
    DEFAULT_FAILURE_CONCLUSIONS,
    JobDuration,
    RunJobStats,
    WorkflowWindowStats,
    aggregate_run_job_stats,
    aggregate_workflow_window,
    duration_ms_from_job,
    duration_ms_from_jobs,
    parse_iso_ms,
    queue_ms_from_job,
)

__all__ = [
    "DEFAULT_FAILURE_CONCLUSIONS",
    "JobDuration",
    "RunJobStats",
    "ThroughputMetrics",
    "WorkflowWindowStats",
    "aggregate_run_job_stats",
    "aggregate_workflow_window",
    "duration_ms_from_job",
    "duration_ms_from_jobs",
    "parse_iso_ms",
    "queue_ms_from_job",
    "reduce_events",
]
