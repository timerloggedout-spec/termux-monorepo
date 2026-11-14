import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "que"))

from sie_pipeline import (
    StageValidationError, build_receipt, item_key, next_stage,
    stable_event_id, validate_receipt, validate_transition,
)
from self_repair import item_body
from sie_event_adapter import queue_stall_groups


def receipt(stage="OBSERVE", state="COMPLETED", **kwargs):
    return build_receipt(
        source_kind="workflow_run", source_id="123",
        source_revision="a" * 40, failure_class="ci",
        stage=stage, state=state, sha="a" * 40,
        observed_at="2026-11-13T00:00:00Z", **kwargs,
    )


class TestSIEPipeline(unittest.TestCase):
    def test_event_identity_is_deterministic_and_revision_sensitive(self):
        first = stable_event_id("workflow_run", "123", "a" * 40)
        self.assertEqual(first, stable_event_id("workflow_run", "123", "a" * 40))
        self.assertNotEqual(first, stable_event_id("workflow_run", "123", "b" * 40))

    def test_item_identity_groups_repeated_failure_observations(self):
        first = item_key("workflow_run", "build.yml", "lint")
        self.assertEqual(first, item_key("workflow_run", "build.yml", "lint"))
        self.assertNotEqual(first, item_key("workflow_run", "build.yml", "test"))

    def test_receipt_is_valid_and_evidence_refs_are_canonical(self):
        data = receipt(evidence_refs=["run:2", "sha:a", "run:2"])
        self.assertEqual(validate_receipt(data), [])
        self.assertEqual(data["evidence_refs"], ["run:2", "sha:a"])

    def test_receipt_rejects_invalid_sha_and_source(self):
        data = receipt()
        data["sha"] = "bad"
        data["source"]["kind"] = "mystery"
        errors = validate_receipt(data)
        self.assertTrue(any("sha:" in error for error in errors))
        self.assertTrue(any("source.kind:" in error for error in errors))

    def test_lifecycle_order_is_linear_and_complete(self):
        self.assertEqual(next_stage("OBSERVE"), "TRIAGE")
        self.assertEqual(next_stage("DELPHI"), "DESIGN")
        self.assertIsNone(next_stage("LEARN"))
        with self.assertRaises(StageValidationError):
            next_stage("UNKNOWN")

    def test_transition_preserves_identity_and_advances_one_stage(self):
        before = receipt("OBSERVE", "COMPLETED")
        after = receipt("TRIAGE", "READY")
        self.assertEqual(validate_transition(before, after), [])

    def test_transition_rejects_stage_skip_and_identity_drift(self):
        before = receipt("OBSERVE", "COMPLETED")
        skipped = receipt("RESEARCH", "READY")
        changed = receipt("TRIAGE", "READY")
        changed["item_key"] = "b" * 24
        changed["source"]["id"] = "999"
        self.assertTrue(any(
            "advance exactly one stage" in error
            for error in validate_transition(before, skipped)
        ))
        errors = validate_transition(before, changed)
        self.assertTrue(any("item_key" in error for error in errors))
        self.assertTrue(any("source" in error for error in errors))

    def test_same_stage_execution_reaches_completion_then_advances(self):
        ready = receipt("TRIAGE", "READY")
        active = receipt("TRIAGE", "ACTIVE")
        completed = receipt("TRIAGE", "COMPLETED")
        research = receipt("RESEARCH", "READY")
        self.assertEqual(validate_transition(ready, active), [])
        self.assertEqual(validate_transition(active, completed), [])
        self.assertEqual(validate_transition(completed, research), [])
        self.assertTrue(validate_transition(ready, completed))

    def test_blocked_stage_recovers_and_completes(self):
        blocked = receipt("RESEARCH", "BLOCKED")
        ready = receipt("RESEARCH", "READY")
        active = receipt("RESEARCH", "ACTIVE")
        completed = receipt("RESEARCH", "COMPLETED")
        self.assertEqual(validate_transition(blocked, ready), [])
        self.assertEqual(validate_transition(ready, active), [])
        self.assertEqual(validate_transition(active, completed), [])

    def test_receipt_rejects_schema_unknown_properties_and_optional_type_drift(self):
        data = receipt()
        data["unexpected"] = True
        self.assertTrue(any("unsupported properties" in error
                            for error in validate_receipt(data)))
        data = receipt()
        data["source"]["unexpected"] = True
        self.assertTrue(any("source: unsupported properties" in error
                            for error in validate_receipt(data)))
        data = receipt()
        data["owner_role"] = 17
        self.assertTrue(any("owner_role" in error
                            for error in validate_receipt(data)))

    def test_blocked_stage_resumes_in_place(self):
        before = receipt("RESEARCH", "BLOCKED")
        resumed = receipt("RESEARCH", "READY")
        self.assertEqual(validate_transition(before, resumed), [])

    def test_terminal_lineage_requires_new_item(self):
        before = receipt("LEARN", "REJECTED")
        after = receipt("OBSERVE", "READY")
        self.assertTrue(any(
            "terminal lineage" in error
            for error in validate_transition(before, after)
        ))

    def test_queue_watchdog_escalations_create_stable_sie_intake(self):
        feed = {
            "dispatches": [
                {
                    "issue": 8123, "state": "escalated", "age_min": 91,
                    "claim": None, "tier": {"name": "ESCALATION"},
                    "stall_events": [{"kind": "flag"}, {"kind": "escalation"}],
                },
                {
                    "issue": 8124, "state": "claimed", "age_min": 95,
                    "claim": {"by": "worker"}, "tier": {"name": "BASE"},
                    "stall_events": [],
                },
                {
                    "issue": 8125, "state": "claimed", "age_min": 120,
                    "claim": None, "tier": {"name": "FINAL"},
                    "stall_events": [{"kind": "escalation"}],
                },
            ]
        }
        groups = queue_stall_groups(feed)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["source_kind"], "stall_gap")
        self.assertEqual(groups[0]["source_id"], "8123")
        self.assertEqual(groups[0]["step"], "dispatch-watchdog")
        self.assertEqual(groups[0]["key"], queue_stall_groups(feed)[0]["key"])
        advanced = json.loads(json.dumps(feed))
        advanced["dispatches"][0]["age_min"] = 121
        refreshed = queue_stall_groups(advanced)[0]
        self.assertEqual(groups[0]["source_revision"], refreshed["source_revision"])
        self.assertGreater(refreshed["priority"], groups[0]["priority"])
        advanced["dispatches"][0]["tier"]["name"] = "FINAL"
        advanced["dispatches"][0]["stall_events"].append({"kind": "new-observation"})
        changed_observation = queue_stall_groups(advanced)[0]
        self.assertEqual(groups[0]["key"], changed_observation["key"])
        self.assertNotEqual(groups[0]["source_revision"], changed_observation["source_revision"])
        body = item_body(groups[0])
        match = re.search(r"## SIE stage receipt\n\x60\x60\x60json\n(.*?)\n\x60\x60\x60", body, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(validate_receipt(data), [])
        self.assertEqual(data["source"]["kind"], "stall_gap")
        self.assertEqual(data["source"]["id"], "8123")

    def test_workflow_run_attempts_have_distinct_event_ids_but_shared_item_key(self):
        def make(run_id, attempt):
            item = {
                "key": "build.yml:failure-signature",
                "path": ".github/workflows/build.yml",
                "sig": "failure-signature",
                "priority": 1.0,
                "failures": 1,
                "total": 1,
                "window_h": 6,
                "step": "test",
                "message": "failure",
                "room": None,
                "receipts": [{
                    "url": f"https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/{run_id}",
                    "sha": "a" * 40,
                    "id": run_id,
                    "run_attempt": attempt,
                }],
            }
            body = item_body(item)
            lines = body.split("\n")
            start = lines.index("## SIE stage receipt") + 2
            end = next(i for i in range(start, len(lines)) if lines[i].startswith(chr(96) * 3))
            return json.loads("\n".join(lines[start:end]))

        first = make(100, 1)
        replay = make(100, 1)
        another_run = make(101, 1)
        rerun = make(100, 2)
        self.assertEqual(first["event_id"], replay["event_id"])
        self.assertNotEqual(first["event_id"], another_run["event_id"])
        self.assertNotEqual(first["event_id"], rerun["event_id"])
        self.assertEqual(first["item_key"], another_run["item_key"])
        self.assertEqual(first["item_key"], rerun["item_key"])

    def test_self_repair_intake_embeds_valid_source_receipt(self):
        item = {
            "key": "dispatch-watchdog:abc123",
            "path": ".github/workflows/dispatch-watchdog.yml",
            "sig": "abc123def456",
            "priority": 1.0,
            "failures": 1,
            "total": 1,
            "window_h": 6,
            "step": "test",
            "message": "contract failure",
            "room": None,
            "receipts": [{
                "url": "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/123",
                "sha": "a" * 40,
            }],
        }
        body = item_body(item)
        match = re.search(
            r"## SIE stage receipt\n```json\n(.*?)\n```",
            body, re.S,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(validate_receipt(data), [])
        self.assertEqual(data["source"]["kind"], "workflow_run")
        self.assertEqual(data["sha"], "a" * 40)


if __name__ == "__main__":
    unittest.main()
