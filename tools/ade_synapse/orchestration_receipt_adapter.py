"""Project native orchestration receipts into metadata-only Synaptic Bus v1 envelopes.

The adapter is deliberately a pure projection: callers provide the task correlation
and envelope emission time; the canonical receipt remains the source of truth.
"""

from __future__ import annotations

import re
from typing import Any

_EVENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,199}$")
_SUPPORTED_STATES = {
    "RUNNING": ("action.started", "running"),
    "COMPLETED": ("action.completed", "succeeded"),
    "FAILED": ("action.failed", "failed"),
}


def project_orchestration_receipt(
    receipt: dict[str, Any],
    *,
    task_id: str,
    emitted_at: str,
) -> dict[str, Any]:
    """Return a Synaptic Bus envelope for a terminal/invocation receipt state.

    DISPATCHED, QUEUED, WAITING, STEERED, RETRYING and CANCELLED are
    intentionally outside this adapter's projection until their source
    lifecycle semantics have a dedicated, evidence-backed mapping.
    """
    required = {
        "orchestration_id", "cycle_id", "attempt_id", "action_id",
        "event_id", "actor", "state", "observed_at", "repo", "ref",
        "sha", "evidence_ids",
    }
    missing = sorted(required.difference(receipt))
    if missing:
        raise ValueError(f"receipt missing required fields: {', '.join(missing)}")

    state = receipt["state"]
    if state not in _SUPPORTED_STATES:
        raise ValueError(f"unsupported orchestration receipt state: {state!r}")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty caller-supplied correlation ID")
    if not isinstance(emitted_at, str) or not emitted_at.strip():
        raise ValueError("emitted_at must be a non-empty caller-supplied timestamp")

    source_event_id = receipt["event_id"]
    if not isinstance(source_event_id, str) or not _EVENT_ID.fullmatch(source_event_id):
        raise ValueError("receipt event_id must be a stable 8-200 character bus-safe ID")

    event_type, status = _SUPPORTED_STATES[state]
    event_id = f"orchestration-receipt:{source_event_id}"
    if len(event_id) > 200:
        raise ValueError("projected event_id exceeds Synaptic Bus v1 limit")

    repo = receipt["repo"]
    sha = receipt["sha"]
    if not isinstance(repo, str) or not re.fullmatch(r"[^/\\s]+/[^/\\s]+", repo):
        raise ValueError("receipt repo must use owner/name form")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("receipt sha must be a lowercase 40-character commit SHA")

    evidence_ids = receipt["evidence_ids"]
    if not isinstance(evidence_ids, list) or any(
        not isinstance(item, str) or not item for item in evidence_ids
    ):
        raise ValueError("receipt evidence_ids must be a list of non-empty strings")

    return {
        "schema_version": "synapse.bus.v1",
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": receipt["observed_at"],
        "emitted_at": emitted_at,
        "producer": {
            "system": "ADE-SYNAPSE",
            "component": "orchestration-receipt-adapter",
            "version": "1",
        },
        "correlation": {
            "task_id": task_id,
            "orchestration_id": receipt["orchestration_id"],
            "cycle_id": receipt["cycle_id"],
            "attempt_id": receipt["attempt_id"],
        },
        "subject": {
            "kind": "agent_task",
            "id": receipt["action_id"],
            "repository": repo,
            "ref": receipt["ref"],
            "sha": sha,
        },
        "status": status,
        "actor": {
            "kind": "unknown",
            "id": receipt["actor"],
            "provider": receipt.get("provider"),
            "model": receipt.get("model"),
            "attribution_confidence": None,
        },
        "evidence_refs": [{
            "kind": "orchestration_receipt",
            "uri": f"urn:orchestration-receipt:{source_event_id}",
            "schema_ref": "docs/ops/ORCHESTRATION-RECEIPT.schema.json",
        }],
        "summary": f"Orchestration receipt state: {state}",
        "privacy": {
            "classification": "internal",
            "contains_raw_prompt": False,
            "contains_raw_completion": False,
            "contains_secret": False,
        },
    }
