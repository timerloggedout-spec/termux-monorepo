#!/usr/bin/env python3
"""Build provenance-only ATES receipts when metric collection is unavailable."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


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
    """Return an outcome receipt without manufacturing throughput metrics."""
    source_conclusion = source_conclusion or "unknown"
    if source_conclusion != "success":
        status = "source_non_success"
        effective_reason = f"source_conclusion_{source_conclusion}"
    elif collection_outcome in {"failure", "skipped"} or checkout_outcome == "failure":
        status = "failed"
        effective_reason = "collection_failed"
    elif skip_reason == "rate_limited":
        status = "deferred"
        effective_reason = skip_reason
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
        "source_run_id": int(source_run_id),
        "source_run_attempt": int(source_run_attempt),
        "source_head_sha": source_head_sha or None,
        "source_workflow_name": source_workflow_name or None,
        "source_conclusion": source_conclusion,
        "observed_at": observed_at or datetime.now(timezone.utc).isoformat(),
        "task_boundary_artifact_outcome": task_boundary_outcome,
        "metrics_emitted": False,
        "missing_evidence_policy": "unknown remains unknown; no metrics inferred",
    }
