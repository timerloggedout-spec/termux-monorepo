import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ops" / "admin_graph_runtime_event.py"
SPEC = importlib.util.spec_from_file_location("admin_graph_runtime_event", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_producer_claim_becomes_task_route_event():
    payload = {
        "repository": {"full_name": MODULE.REPO},
        "sender": {"login": "producer-bot"},
        "issue": {"number": 4095, "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/issues/4095"},
        "comment": {"id": 9001, "created_at": "2026-11-19T12:00:00Z",
                    "body": ("[MUSEai]@{role:{optimizations-assurance}} PRODUCER CLAIM — dispatch pickup.\n\n"
                             "- resolved provider: command-dispatch\n"
                             "- producer: internal seat label\n"
                             "- session: private-session-value\n")}
    }
    event = MODULE.build_event(payload, "issue_comment", {
        "run_id": "12345", "run_attempt": "1", "head_sha": "a" * 40
    })
    assert event["kind"] == "route"
    assert event["event"] == "task_routed"
    assert event["status"] == "routed"
    assert event["id"] == "route:4095:9001"
    assert event["payload"]["route_role"] == "optimizations-assurance"
    assert event["payload"]["provider"] == "command-dispatch"
    assert "session" not in event["payload"]
    assert "producer" not in event["payload"]


def test_dispatch_executor_claim_preserves_arm_and_dispatch_identity():
    payload = {
        "repository": {"full_name": MODULE.REPO},
        "sender": {"login": "dispatch-bot"},
        "issue": {"number": 5176, "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/issues/5176"},
        "comment": {"id": 9002, "created_at": "2026-11-19T12:01:00Z",
                    "body": ("[MUSEai]@{role:{dispatch-executor}} DISPATCH EXECUTOR CLAIM\n\n"
                             "- arm: gemini-cli (gemini-2.5-pro) — selected by policy\n"
                             "- dispatch_id: dispatch-abc-123\n")}
    }
    event = MODULE.build_event(payload, "issue_comment", {
        "run_id": "12346", "run_attempt": "2", "head_sha": "b" * 40
    })
    assert event["kind"] == "route"
    assert event["payload"]["route_role"] == "dispatch-executor"
    assert event["payload"]["arm_id"] == "gemini-cli"
    assert event["payload"]["model"] == "gemini-2.5-pro"
    assert event["payload"]["dispatch_id"] == "dispatch-abc-123"


def test_unrelated_issue_comment_emits_no_route_event():
    payload = {"repository": {"full_name": MODULE.REPO},
               "issue": {"number": 99},
               "comment": {"id": 10, "body": "ordinary discussion"}}
    assert MODULE.build_events(payload, "issue_comment", {
        "run_id": "123", "run_attempt": "1"
    }) == []


def test_workflow_job_event_is_normalized():
    payload = {
        "repository": {"full_name": MODULE.REPO},
        "workflow": {"name": "dispatch-executor"},
        "sender": {"login": "automation"},
        "workflow_job": {"id": 456, "run_id": 123, "run_attempt": 1,
                         "name": "execute task", "status": "in_progress",
                         "started_at": "2026-11-16T12:01:00Z",
                         "head_sha": "b" * 40,
                         "html_url": "https://github.com/example/job/456"}
    }
    event = MODULE.build_event(payload, "workflow_job")
    assert event["event"] == "job_in_progress"
    assert event["kind"] == "job"
    assert event["job_id"] == 456


def test_workflow_snapshot_builds_run_events():
    payload = {"workflow_runs": [
        {"id": 123, "run_attempt": 1, "name": "dispatch-executor",
         "status": "in_progress", "created_at": "2026-11-16T12:00:00Z"},
        {"id": 124, "run_attempt": 2, "name": "n8n SHE bridge",
         "status": "completed", "conclusion": "failure",
         "updated_at": "2026-11-16T12:01:00Z"}
    ]}
    events = MODULE.build_events(payload, "workflow_snapshot")
    assert len(events) == 2
    assert events[0]["event"] == "workflow_in_progress"
    assert events[1]["event"] == "workflow_failure"


def test_repository_identity_is_preserved_for_worker_validation():
    payload = {"repository": {"full_name": "attacker/other"},
               "workflow_run": {"id": 1, "status": "in_progress"}}
    event = MODULE.build_event(payload, "workflow_run")
    assert event["repo"] == "attacker/other"
