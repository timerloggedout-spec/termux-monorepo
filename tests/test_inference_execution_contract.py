"""Contract tests for project-scoped, parallel inference events."""
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = json.loads((ROOT / "docs/integrations/schemas/integration-event.schema.json").read_text())
PROJECT_SCHEMA = json.loads((ROOT / "ops/projects/profile.schema.json").read_text())


def base_event():
    return {
        "schema_version": "1.0.0",
        "event_id": "evt-001",
        "integration_id": "codex-otel",
        "event_type": "inference.completed",
        "source": {"repository": "timerloggedout-spec/termux-monorepo"},
        "execution": {"status": "succeeded", "started_at": "2026-11-19T10:00:00Z", "completed_at": "2026-11-19T10:00:02Z", "duration_ms": 2000},
        "outcome": {"state": "executed", "summary": "Inference completed", "confidence": "confirmed"},
        "evidence": {"artifact_refs": [], "validation_status": "not_run", "validator": None},
        "provenance": {"provider": "openai", "capture_method": "otel", "attribution": "provider_reported", "model_id": "gpt-6", "adapter_version": "0.1.0"},
        "idempotency_key": "evt-001",
        "project": {"portfolio_id": "core-platform", "project_id": "termux-monorepo", "profile_ref": "ops/projects/termux-monorepo.json", "profile_sha256": "a" * 64},
        "task": {"task_id": "task-42", "parent_task_id": None, "work_item_ref": "IIS-002", "kind": "implementation"},
        "inference": {
            "inference_id": "inf-42", "attempt_id": "attempt-1", "attempt_number": 1,
            "parent_inference_id": None, "session_id": "session-7", "run_id": "run-9",
            "endpoint_id": "openai/gpt-6", "instance_key": "instance-sha256-abc",
            "provider": "openai", "model": "gpt-6", "concurrency_group_id": "portfolio-core",
            "queue_id": "project-termux", "priority_class": "normal",
            "usage": {"input_tokens": 100, "cached_input_tokens": 20, "output_tokens": 50,
                      "credits": None, "estimated_cost": None, "currency": None,
                      "measurement_status": "measured", "attribution": "provider_reported"}
        }
    }


def test_inference_event_requires_project_task_and_attempt_identity():
    event = base_event()
    jsonschema.validate(event, EVENT_SCHEMA)
    for key in ("project", "task", "inference"):
        candidate = dict(event)
        candidate.pop(key)
        assert list(jsonschema.Draft202012Validator(EVENT_SCHEMA).iter_errors(candidate)), key
    candidate = base_event()
    candidate["inference"].pop("attempt_id")
    assert list(jsonschema.Draft202012Validator(EVENT_SCHEMA).iter_errors(candidate))


def test_inference_usage_preserves_unknown_as_null_and_rejects_negative_counts():
    event = base_event()
    event["inference"]["usage"]["credits"] = None
    event["inference"]["usage"]["estimated_cost"] = None
    jsonschema.validate(event, EVENT_SCHEMA)
    event["inference"]["usage"]["input_tokens"] = -1
    assert list(jsonschema.Draft202012Validator(EVENT_SCHEMA).iter_errors(event))


def test_legacy_integration_event_remains_valid_without_inference_fields():
    event = base_event()
    for key in ("project", "task", "inference"):
        event.pop(key)
    event["event_type"] = "integration.observed"
    jsonschema.validate(event, EVENT_SCHEMA)


def test_project_profile_accepts_stable_project_and_portfolio_ids():
    profile = {
        "name": "Termux Monorepo", "class": "user-project",
        "scope": {"repos": ["timerloggedout-spec/termux-monorepo"], "issue_classes": [], "lanes": [], "artifact_stores": []},
        "surfaces": ["github-repo"], "portfolio_id": "core-platform",
        "project_id": "termux-monorepo"
    }
    jsonschema.validate(profile, PROJECT_SCHEMA)


def test_project_profile_identity_requires_portfolio_pair():
    profile = {
        "name": "Termux Monorepo", "class": "user-project",
        "scope": {"repos": ["timerloggedout-spec/termux-monorepo"], "issue_classes": [], "lanes": [], "artifact_stores": []},
        "surfaces": ["github-repo"], "project_id": "termux-monorepo"
    }
    assert list(jsonschema.Draft202012Validator(PROJECT_SCHEMA).iter_errors(profile))


def test_activity_only_usage_requires_null_numeric_measurements():
    event = base_event()
    usage = event["inference"]["usage"]
    usage["measurement_status"] = "activity_only"
    usage["input_tokens"] = 100
    assert list(jsonschema.Draft202012Validator(EVENT_SCHEMA).iter_errors(event))
    for key in ("input_tokens", "cached_input_tokens", "output_tokens", "credits", "estimated_cost", "currency"):
        usage[key] = None
    jsonschema.validate(event, EVENT_SCHEMA)


def test_parallel_project_events_keep_project_queues_and_portfolio_group_distinct():
    project_a = base_event()
    project_b = base_event()
    project_b["event_id"] = "evt-002"
    project_b["idempotency_key"] = "evt-002"
    project_b["project"]["project_id"] = "research-lab"
    project_b["task"]["task_id"] = "task-84"
    project_b["inference"]["inference_id"] = "inf-84"
    project_b["inference"]["attempt_id"] = "attempt-1"
    project_b["inference"]["queue_id"] = "project-research"
    jsonschema.validate(project_a, EVENT_SCHEMA)
    jsonschema.validate(project_b, EVENT_SCHEMA)
    assert project_a["project"]["project_id"] != project_b["project"]["project_id"]
    assert project_a["inference"]["queue_id"] != project_b["inference"]["queue_id"]
    assert project_a["inference"]["concurrency_group_id"] == project_b["inference"]["concurrency_group_id"]


def test_inference_event_requires_explicit_usage_observation():
    event = base_event()
    event["inference"].pop("usage")
    assert list(jsonschema.Draft202012Validator(EVENT_SCHEMA).iter_errors(event))
