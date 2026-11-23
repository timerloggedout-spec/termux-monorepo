"""Temporal activity: read local Puter Pool counters and emit a correlated EPS event."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from temporalio import activity

from scripts.puter_pool_observation import collect_observation
from .contracts import PuterPoolObservationInput

REPO_ROOT = Path(__file__).resolve().parents[3]


def build_event(observation: dict[str, Any], request: PuterPoolObservationInput, temporal_workflow_id: str, temporal_run_id: str) -> dict[str, Any]:
    counters = observation["pool"]["counters"]
    attributes = {
        "provider_id": observation["provider_id"],
        "provider_family": observation["provider"],
        "task_or_entry_ref": request.task_or_entry_ref or None,
        "doe_run_id": request.doe_run_id or None,
        "workflow_run_id": request.workflow_run_id or None,
        "run_attempt": request.run_attempt,
        "temporal_workflow_id": temporal_workflow_id,
        "temporal_run_id": temporal_run_id,
        "model_count": observation["pool"]["model_count"],
        "model_ids": observation["pool"]["model_ids"],
        "total_requests": counters["totalRequests"],
        "successful_requests": counters["successfulRequests"],
        "failed_requests": counters["failedRequests"],
        "queued_requests": counters["queuedRequests"],
        "active_requests": counters["activeRequests"],
        "average_latency_ms": counters["averageLatency"],
        "active_accounts": counters["activeAccounts"],
        "quota_status": "unknown",
    }
    event = {
        "schema_version": "eps.v1",
        "event_type": "provider.pool.observed",
        "occurred_at": observation["observed_at"],
        "provider": "g4f/Puter",
        "model_provider": "g4f/Puter",
        "source": "puter-pool-temporal-observer",
        "repo": "timerloggedout-spec/termux-monorepo",
        "entity_type": "provider",
        "entity_id": "g4f.puter",
        "status": observation["pool"]["readiness"],
        "run_id": request.workflow_run_id or temporal_workflow_id,
        "run_attempt": request.run_attempt,
        "provenance": {
            "source_repository": observation["source_repository"],
            "observation_schema": observation["schema"],
        },
        "attributes": attributes,
    }
    stable = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    event["event_id"] = "eps-" + hashlib.sha256(stable).hexdigest()[:32]
    return event


@activity.defn
def collect_puter_pool_observation(request: PuterPoolObservationInput) -> dict[str, Any]:
    observation = collect_observation(
        base_url=os.environ.get("PUTER_POOL_BASE_URL", "http://127.0.0.1:3000"),
        timeout=8.0,
        api_key=os.environ.get("PUTER_POOL_API_KEY"),
    )
    info = activity.info()
    observation["correlation"] = {
        "task_or_entry_ref": request.task_or_entry_ref or None,
        "doe_run_id": request.doe_run_id or None,
        "workflow_run_id": request.workflow_run_id or None,
        "run_attempt": request.run_attempt,
        "temporal_workflow_id": info.workflow_id,
        "temporal_run_id": info.workflow_run_id,
    }
    event = build_event(observation, request, info.workflow_id, info.workflow_run_id)
    output = Path(os.environ.get("PUTER_POOL_EVENT_OUT", str(REPO_ROOT / "agent_telemetry_stream.json")))
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise RuntimeError("puter_pool_event_output_symlink_refused")
    with output.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    runtime_output = Path(os.environ.get(
        "PUTER_POOL_RUNTIME_OUT",
        str(REPO_ROOT / "apps" / "tribute-dashboard" / "data" / "puter-pool-runtime.json"),
    ))
    runtime_output.parent.mkdir(parents=True, exist_ok=True)
    if runtime_output.is_symlink():
        raise RuntimeError("puter_pool_runtime_output_symlink_refused")
    temporary = runtime_output.with_name(runtime_output.name + ".tmp")
    temporary.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, runtime_output)
    return {
        "observation": observation,
        "event_id": event["event_id"],
        "event_path": str(output),
        "runtime_feed_path": str(runtime_output),
    }
