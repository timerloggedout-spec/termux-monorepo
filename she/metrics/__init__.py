"""SHE metrics helpers — durable aggregation from Actions job timestamps.

No network. No dependency on the deprecated /timing endpoint.
Duration/queue derived from job started_at / completed_at / queued_at.
"""

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
    "WorkflowWindowStats",
    "aggregate_run_job_stats",
    "aggregate_workflow_window",
    "duration_ms_from_job",
    "duration_ms_from_jobs",
    "parse_iso_ms",
    "queue_ms_from_job",
]

from she.metrics.agent_throughput import ThroughputMetrics, reduce_events
from she.metrics.tdqs import TDQS_SPEC_VERSION, context_signals, overall_server_score, weighted_score
