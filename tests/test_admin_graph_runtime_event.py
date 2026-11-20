import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ops" / "admin_graph_runtime_event.py"
SPEC = importlib.util.spec_from_file_location("admin_graph_runtime_event", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RuntimeEventTests(unittest.TestCase):
    def test_producer_claim_becomes_task_route_event(self):
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
        self.assertEqual(event["kind"], "route")
        self.assertEqual(event["event"], "task_routed")
        self.assertEqual(event["status"], "routed")
        self.assertEqual(event["id"], "route:4095:9001")
        self.assertEqual(event["payload"]["route_role"], "optimizations-assurance")
        self.assertEqual(event["payload"]["provider"], "command-dispatch")
        self.assertNotIn("session", event["payload"])
        self.assertNotIn("producer", event["payload"])

    def test_dispatch_executor_claim_preserves_arm_and_dispatch_identity(self):
        payload = {
            "repository": {"full_name": MODULE.REPO},
            "sender": {"login": "dispatch-bot"},
            "issue": {"number": 5176, "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/issues/5176"},
            "comment": {"id": 9002, "created_at": "2026-11-19T12:01:00Z",
                        "body": ("[MUSEai]@{role:{dispatch-executor}} PRODUCER CLAIM — dispatch executor claim on #5176\n\n"
                                 "- arm: gemini-cli (gemini-2.5-pro) — selected by policy\n"
                                 "- dispatch_id: dispatch-abc-123\n")}
        }
        event = MODULE.build_event(payload, "issue_comment", {
            "run_id": "12346", "run_attempt": "2", "head_sha": "b" * 40
        })
        self.assertEqual(event["kind"], "route")
        self.assertEqual(event["payload"]["route_role"], "dispatch-executor")
        self.assertEqual(event["payload"]["arm_id"], "gemini-cli")
        self.assertEqual(event["payload"]["model"], "gemini-2.5-pro")
        self.assertEqual(event["payload"]["dispatch_id"], "dispatch-abc-123")
        self.assertEqual(event["payload"]["source"], "dispatch_executor_claim")

    def test_unrelated_issue_comment_emits_no_route_event(self):
        payload = {"repository": {"full_name": MODULE.REPO},
                   "issue": {"number": 99},
                   "comment": {"id": 10, "body": "ordinary discussion"}}
        events = MODULE.build_events(payload, "issue_comment", {
            "run_id": "123", "run_attempt": "1"
        })
        self.assertEqual(events, [])

    def test_route_delivery_identity_is_stable(self):
        payload = {
            "repository": {"full_name": MODULE.REPO},
            "sender": {"login": "producer-bot"},
            "issue": {"number": 4095},
            "comment": {"id": 9001, "created_at": "2026-11-19T12:00:00Z",
                        "body": "[MUSEai]@{role:{worker}} PRODUCER CLAIM\n- resolved provider: provider-x"}
        }
        context = {"run_id": "12345", "run_attempt": "1"}
        first = MODULE.build_event(payload, "issue_comment", context)
        second = MODULE.build_event(payload, "issue_comment", context)
        self.assertEqual(first["id"], second["id"])

    def test_runtime_snapshot_recovers_github_token_claims(self):
        payload = {
            "workflow_runs": [],
            "issue_comments": [{
                "id": 9010,
                "issue_url": "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/issues/6001",
                "created_at": "2026-11-19T12:05:00Z",
                "user": {"login": "github-actions[bot]"},
                "body": ("[MUSEai]@{role:{dispatch-executor}} PRODUCER CLAIM — dispatch executor claim on #6001\n"
                         "- arm: gemini-cli (gemini-2.5-pro)\n"
                         "- dispatch_id: dispatch-6001\n")
            }]
        }
        events = MODULE.build_events(payload, "runtime_snapshot", {
            "run_id": "12347", "run_attempt": "1", "head_sha": "c" * 40
        })
        route_events = [event for event in events if event["kind"] == "route"]
        self.assertEqual(len(route_events), 1)
        self.assertEqual(route_events[0]["id"], "route:6001:9010")
        self.assertEqual(route_events[0]["payload"]["dispatch_id"], "dispatch-6001")

    def test_runtime_snapshot_orders_route_before_later_run_event(self):
        payload = {
            "workflow_runs": [{
                "id": 124, "run_attempt": 1, "name": "dispatch-executor",
                "status": "in_progress", "created_at": "2026-11-19T12:10:00Z"
            }],
            "issue_comments": [{
                "id": 9012,
                "issue_url": "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/issues/6003",
                "created_at": "2026-11-19T12:05:00Z",
                "user": {"login": "producer-bot"},
                "body": ("[MUSEai]@{role:{worker}} PRODUCER CLAIM\n"
                         "- resolved provider: provider-x\n")
            }]
        }
        events = MODULE.build_events(payload, "runtime_snapshot", {
            "run_id": "12349", "run_attempt": "1"
        })
        self.assertEqual(events[0]["kind"], "route")
        self.assertEqual(events[1]["kind"], "workflow")

    def test_dispatch_watchdog_auto_claim_emits_route_pulse(self):
        payload = {
            "workflow_runs": [],
            "issue_comments": [{
                "id": 9011,
                "issue_url": "https://api.github.com/repos/timerloggedout-spec/termux-monorepo/issues/6002",
                "created_at": "2026-11-19T12:06:00Z",
                "user": {"login": "termux-fleet-swarm[bot]"},
                "body": ("[MUSEai]@{role:{dispatch-watchdog}} PRODUCER CLAIM — auto-claim by rank.\n\n"
                         "- resolved provider: repo-machinery\n"
                         "- producer: dispatch-watchdog auto-claim\n"
                         "- auto-claim: class=executor claimant=dispatch-executor lease_expires=2026-11-19T14:06:00Z\n")
            }]
        }
        events = MODULE.build_events(payload, "runtime_snapshot", {
            "run_id": "12348", "run_attempt": "1", "head_sha": "d" * 40
        })
        route_events = [event for event in events if event["kind"] == "route"]
        self.assertEqual(len(route_events), 1)
        self.assertEqual(route_events[0]["payload"]["route_role"], "dispatch-watchdog")
        self.assertEqual(route_events[0]["payload"]["provider"], "repo-machinery")

    def test_claim_marker_without_route_stamp_is_filtered(self):
        payload = {"repository": {"full_name": MODULE.REPO},
                   "issue": {"number": 77},
                   "comment": {"id": 78, "body": "PRODUCER CLAIM mentioned in discussion"}}
        self.assertEqual(MODULE.build_events(payload, "issue_comment", {
            "run_id": "123", "run_attempt": "1"
        }), [])

    def test_workflow_job_event_is_normalized(self):
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
        self.assertEqual(event["event"], "job_in_progress")
        self.assertEqual(event["kind"], "job")
        self.assertEqual(event["job_id"], 456)

    def test_workflow_snapshot_builds_run_events(self):
        payload = {"workflow_runs": [
            {"id": 123, "run_attempt": 1, "name": "dispatch-executor",
             "status": "in_progress", "created_at": "2026-11-16T12:00:00Z"},
            {"id": 124, "run_attempt": 2, "name": "n8n SHE bridge",
             "status": "completed", "conclusion": "failure",
             "updated_at": "2026-11-16T12:01:00Z"}
        ]}
        events = MODULE.build_events(payload, "workflow_snapshot")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "workflow_in_progress")
        self.assertEqual(events[1]["event"], "workflow_failure")

    def test_repository_identity_is_preserved_for_worker_validation(self):
        payload = {"repository": {"full_name": "attacker/other"},
                   "workflow_run": {"id": 1, "status": "in_progress"}}
        event = MODULE.build_event(payload, "workflow_run")
        self.assertEqual(event["repo"], "attacker/other")


if __name__ == "__main__":
    unittest.main()
