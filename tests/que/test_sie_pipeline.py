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
        changed["item_key"] = "changed-key"
        changed["source"]["id"] = "999"
        self.assertTrue(any(
            "advance exactly one stage" in error
            for error in validate_transition(before, skipped)
        ))
        errors = validate_transition(before, changed)
        self.assertTrue(any("item_key" in error for error in errors))
        self.assertTrue(any("source" in error for error in errors))

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
