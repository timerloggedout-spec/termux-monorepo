"""Tests for she.metrics.job_timestamps — pure duration + queue aggregation."""
from __future__ import annotations

from she.metrics.job_timestamps import (
    DEFAULT_FAILURE_CONCLUSIONS,
    aggregate_run_job_stats,
    aggregate_workflow_window,
    duration_ms_from_job,
    duration_ms_from_jobs,
    parse_iso_ms,
    queue_ms_from_job,
)


def test_parse_iso_ms_zulu():
    ms = parse_iso_ms("2020-01-20T17:42:40Z")
    assert ms is not None
    assert ms > 0


def test_parse_iso_ms_none():
    assert parse_iso_ms(None) is None
    assert parse_iso_ms("") is None
    assert parse_iso_ms("not-a-date") is None


def test_duration_ms_from_job():
    job = {
        "id": 1,
        "name": "build",
        "conclusion": "success",
        "started_at": "2020-01-20T17:42:40Z",
        "completed_at": "2020-01-20T17:44:39Z",
    }
    d = duration_ms_from_job(job)
    assert d == 119_000  # 1m 59s


def test_queue_ms_from_job():
    job = {
        "queued_at": "2020-01-20T17:42:00Z",
        "started_at": "2020-01-20T17:42:40Z",
        "completed_at": "2020-01-20T17:44:39Z",
    }
    assert queue_ms_from_job(job) == 40_000


def test_queue_ms_absent():
    assert queue_ms_from_job({"started_at": "2020-01-20T17:42:40Z"}) is None


def test_duration_ms_missing_completed():
    assert duration_ms_from_job({"started_at": "2020-01-20T17:42:40Z"}) is None


def test_duration_ms_from_jobs_wall():
    jobs = [
        {
            "started_at": "2020-01-20T17:42:40Z",
            "completed_at": "2020-01-20T17:43:00Z",
        },
        {
            "started_at": "2020-01-20T17:42:50Z",
            "completed_at": "2020-01-20T17:44:40Z",
        },
    ]
    assert duration_ms_from_jobs(jobs) == 120_000


def test_aggregate_run_job_stats_failure():
    payload = {
        "total_count": 2,
        "jobs": [
            {
                "id": 10,
                "name": "lint",
                "conclusion": "success",
                "started_at": "2020-01-20T17:42:40Z",
                "completed_at": "2020-01-20T17:43:00Z",
            },
            {
                "id": 11,
                "name": "copilot-cli",
                "conclusion": "failure",
                "started_at": "2020-01-20T17:42:40Z",
                "completed_at": "2020-01-20T17:45:40Z",
            },
        ],
    }
    stats = aggregate_run_job_stats(payload, run_id=99)
    assert stats.run_id == 99
    assert stats.job_count == 2
    assert stats.failed_jobs == 1
    assert stats.wall_duration_ms == 180_000
    assert stats.avg_job_duration_ms is not None
    assert len(stats.durations_ms) == 2
    assert stats.metric_version == "actions-perf-v1"
    m = stats.to_mapping()
    assert m["label"] == "locally_reconstructed"


def test_cancelled_not_hard_failure_by_default():
    payload = {
        "jobs": [
            {
                "name": "x",
                "conclusion": "cancelled",
                "started_at": "2020-01-20T17:00:00Z",
                "completed_at": "2020-01-20T17:01:00Z",
            }
        ]
    }
    stats = aggregate_run_job_stats(payload)
    assert stats.failed_jobs == 0  # policy default: failure, timed_out only


def test_policy_override_includes_cancelled():
    payload = {
        "jobs": [
            {
                "name": "x",
                "conclusion": "cancelled",
                "started_at": "2020-01-20T17:00:00Z",
                "completed_at": "2020-01-20T17:01:00Z",
            }
        ]
    }
    soft = DEFAULT_FAILURE_CONCLUSIONS | frozenset({"cancelled"})
    stats = aggregate_run_job_stats(payload, failure_conclusions=soft)
    assert stats.failed_jobs == 1


def test_aggregate_workflow_window_failure_rate():
    run_a = {
        "jobs": [
            {
                "name": "a",
                "conclusion": "failure",
                "started_at": "2020-01-20T17:00:00Z",
                "completed_at": "2020-01-20T17:03:00Z",
            }
        ]
    }
    run_b = {
        "jobs": [
            {
                "name": "b",
                "conclusion": "success",
                "started_at": "2020-01-20T18:00:00Z",
                "completed_at": "2020-01-20T18:02:00Z",
            }
        ]
    }
    win = aggregate_workflow_window([run_a, run_b], window_label="30d")
    assert win.run_count == 2
    assert win.runs_with_failures == 1
    assert win.failure_rate_pct == 50.0
    assert win.total_jobs == 2
    assert win.total_failed_jobs == 1
    assert win.avg_wall_duration_ms is not None
    assert win.window_label == "30d"
    assert win.to_mapping()["label"] == "locally_reconstructed"
