"""Conductor placement and cue-sheet contract regressions."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deepcli.observatory.conductor import ConductorPlacement, build_cue_sheet

class ConductorTests(unittest.TestCase):
    def setUp(self):
        self.plan = {"waves": [["spec"], ["tests", "docs"]]}
        self.assignments = {
            task: {
                "nominal_at": "2026-11-27T12:00:00Z",
                "opens_at": "2026-11-27T11:59:30Z",
                "closes_at": "2026-11-27T12:05:00Z",
                "expected_duration_ms": 120000,
                "wake_conditions": ["event", "window_close"],
            }
            for task in ("spec", "tests", "docs")
        }
    def test_all_three_placements_emit_same_work_coverage(self):
        sheets = [build_cue_sheet(self.plan, self.assignments, placement) for placement in ConductorPlacement]
        self.assertEqual({sheet["task_count"] for sheet in sheets}, {3})
        self.assertEqual({sheet["placement"] for sheet in sheets}, {placement.value for placement in ConductorPlacement})
        self.assertTrue(all(sheet["dispatch_intent"] for sheet in sheets))
        self.assertTrue(all(sheet["authority"] == "dispatch_intent_only" for sheet in sheets))
    def test_missing_assignment_rejected(self):
        with self.assertRaises(ValueError):
            build_cue_sheet(self.plan, {"spec": {}}, "manager_policy")
    def test_duplicate_task_identity_rejected(self):
        with self.assertRaises(ValueError):
            build_cue_sheet({"waves": [["spec"], ["spec"]]}, self.assignments, "manager_policy")

if __name__ == "__main__":
    unittest.main()
