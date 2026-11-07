#!/usr/bin/env python3
"""Build provenance-only ATES receipts when metric collection is unavailable."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

VALID_CONCLUSIONS = frozenset({
    "success", "failure", "neutral", "cancelled", "skipped", "timed_out",
    "action_required", "stale", "startup_failure",
})


def build_outcome_receipt(
    *,
    source_run_id: int,
    source_run_attempt: int,
    source_head_sha: str | None,
    source_workflow_name: str | None,
    source_conclusion: str | None,
    skip_reason: str,
    collection_outcome: str,
    checkout_outcome: str,
    task_boundary_outcome: str,
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Return a provenance receipt without manufacturing throughput metrics."""
    if isinstance(source_run_id, bool) or not isinstance(source_run_id, int) or source_run_id < 0:
        raise ValueError("source_run_id must be a non-negative integer")
    if isinstance(source_run_attempt, bool) or not isinstance(source_run_attempt, int) or source_run_attempt < 1:
        raise ValueError("source_run_attempt must be a positive integer")

    conclusion = source_conclusion if source_conclusion in VALID_CONCLUSIONS else "unknown"
    if conclusion != "success":
        status = "source_non_success"
        effective_reason = f"source_conclusion_{conclusion}"
    elif collection_outcome in {"failure", "skipped"} or checkout_outcome == "failure":
        status = "failed"
        effective_reason = "collection_failed"
    elif skip_reason == "rate_limited":
        status = "deferred"
        effective_reason = "rate_limited"
    else:
        status = "skipped"
        effective_reason = skip_reason or "metadata_unavailable"

    return {
        "schema_version": "ates.observation.v1",
        "producer": "agent-throughput-evidence",
        "status": status,
        "skip_reason": effective_reason,
        "collection_outcome": collection_outcome,
        "checkout_outcome": checkout_outcome,
        "source_run_id": source_run_id,
        "source_run_attempt": source_run_attempt,
        "source_head_sha": source_head_sha or None,
        "source_workflow_name": source_workflow_name or None,
        "source_conclusion": conclusion,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "task_boundary_artifact_outcome": task_boundary_outcome,
        "metrics_emitted": False,
        "missing_evidence_policy": "unknown remains unknown; no metrics inferred",
    }
