from __future__ import annotations

import importlib.util

import pytest

temporalio = pytest.importorskip("temporalio")
from scripts.temporal.puter_pool_observation.activities import build_event
from scripts.temporal.puter_pool_observation.contracts import PuterPoolObservationInput
from scripts.temporal.puter_pool_observation.workflow import TASK_QUEUE, PuterPoolObservationWorkflow


def test_temporal_contract_projects_provider_task_and_doe_correlation():
    observation = {
        "schema": "provider-runtime-observation/v1",
        "provider_id": "g4f.puter",
        "provider": "g4f/Puter",
        "source_repository": "timerloggedout-spec/puter-pool_fork",
        "observed_at": "2026-11-23T12:00:00Z",
        "pool": {
            "readiness": "ready", "model_count": 2, "model_ids": ["model-a", "model-b"],
            "counters": {
                "totalRequests": 12, "successfulRequests": 10, "failedRequests": 2,
                "queuedRequests": 1, "activeRequests": 1, "averageLatency": 210,
                "activeAccounts": 3,
            },
        },
    }
    request = PuterPoolObservationInput(
        task_or_entry_ref="QUE-42", doe_run_id="doe-17",
        workflow_run_id="45123", run_attempt=2, interval_seconds=300,
    )
    event = build_event(observation, request, "wf-puter-1", "run-abc")
    assert event["entity_id"] == "g4f.puter"
    assert event["attributes"]["task_or_entry_ref"] == "QUE-42"
    assert event["attributes"]["doe_run_id"] == "doe-17"
    assert event["attributes"]["temporal_workflow_id"] == "wf-puter-1"
    assert event["attributes"]["total_requests"] == 12
    assert event["attributes"]["quota_status"] == "unknown"
    assert TASK_QUEUE == "puter-pool-observability"
    assert "prompt" not in event["attributes"]
    assert "completion" not in event["attributes"]


def test_temporal_workflow_is_registered():
    assert PuterPoolObservationWorkflow is not None
