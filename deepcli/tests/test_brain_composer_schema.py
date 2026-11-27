"""Brain Composer score schema and deterministic identity regressions."""
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory.brain.composer import compose_score


class BrainComposerSchemaTests(unittest.TestCase):
    def setUp(self):
        self.intent = {
            "goal": "validate release",
            "priority": 3,
            "constraints": ["evidence-required"],
            "success_criteria": ["checks pass"],
        }
        self.signals = [
            {"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}
        ]
        self.plan = {"waves": [["spec"]]}
        self.assignments = {
            "spec": {
                "nominal_at": "2026-11-27T12:00:00Z",
                "opens_at": "2026-11-27T11:59:00Z",
                "closes_at": "2026-11-27T12:05:00Z",
                "expected_duration_ms": 1000,
                "phase": "on_beat",
                "open_length_ms": 360000,
                "dependency_barriers": [],
                "evidence_refs": ["ates://spec"],
            }
        }

    def test_score_identity_is_deterministic_and_content_addressed(self):
        kwargs = {
            "action_candidates": [{"id": "spec", "priority": 5, "writes": ["src/spec.py"]}],
            "timing_observations": [{
                "task_id": "spec",
                "run_id": "run-5939",
                "evidence_ref": "ates://timing/spec",
                "source": "ATES",
                "expected_duration_ms": 1000,
                "actual_duration_ms": 1250,
            }],
            "wake_context": {"now_ms": 100, "window_close_ms": 500, "max_wait_ms": 600},
        }
        first = compose_score(self.intent, self.signals, self.plan, self.assignments, **kwargs)
        second = compose_score(self.intent, self.signals, self.plan, self.assignments, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(len(first["score_id"]), 64)
        self.assertEqual(first["cue_sheet"]["authority"], "dispatch_intent_only")
        self.assertEqual(first["timing_feedback"][0]["evidence_ref"], "ates://timing/spec")

    def test_score_schema_declares_provenance_and_authority_contract(self):
        path = REPO_ROOT / "docs" / "schemas" / "brain.composer.score.v1.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], "brain.composer.score.v1")
        self.assertEqual(schema["properties"]["score_id"]["pattern"], "^[0-9a-f]{64}$")
        self.assertEqual(schema["properties"]["authority"]["properties"]["admission_and_claims"]["const"], "QUE")
        self.assertIn("timing_feedback", schema["required"])
        feedback = schema["properties"]["timing_feedback"]["items"]
        self.assertIn("evidence_ref", feedback["required"])
        self.assertIn("run_id", feedback["required"])

    def test_timing_feedback_changes_content_address(self):
        base = {
            "task_id": "spec", "run_id": "run-1", "evidence_ref": "ates://timing/v1",
            "expected_duration_ms": 100, "actual_duration_ms": 110,
        }
        first = compose_score(self.intent, self.signals, self.plan, self.assignments, timing_observations=[base])
        second = compose_score(self.intent, self.signals, self.plan, self.assignments,
                               timing_observations=[{**base, "evidence_ref": "ates://timing/v2"}])
        self.assertNotEqual(first["score_id"], second["score_id"])


if __name__ == "__main__":
    unittest.main()
