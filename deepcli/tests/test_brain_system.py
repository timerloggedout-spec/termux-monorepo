import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory.brain.signals import normalize_signals
from deepcli.observatory.brain.context import build_context
from deepcli.observatory.brain.executive import normalize_intent
from deepcli.observatory.brain.action_selection import select_actions
from deepcli.observatory.brain.prediction import timing_error
from deepcli.observatory.brain.homeostasis import plan_wake
from deepcli.observatory.brain.composer import compose_score
from deepcli.observatory.conductor import build_cue_sheet, ConductorPlacement


class BrainSystemTests(unittest.TestCase):
    def test_signal_normalization_deduplicates_and_orders_by_sequence(self):
        signals = [
            {"signal_id": "s2", "source": "collector", "kind": "completed", "sequence": 2, "confidence": 0.9},
            {"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 0.8},
            {"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 0.8},
        ]
        result = normalize_signals(signals)
        self.assertEqual([item["signal_id"] for item in result], ["s1", "s2"])

    def test_conflicting_signal_identity_is_rejected(self):
        signal = {"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 0.8}
        conflicting = {**signal, "kind": "failed"}
        with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
            normalize_signals([signal, conflicting])

    def test_invalid_signal_confidence_and_sequence_are_rejected(self):
        signal = {"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 1.2}
        with self.assertRaisesRegex(ValueError, "confidence"):
            normalize_signals([signal])
        with self.assertRaisesRegex(ValueError, "sequence"):
            normalize_signals([{**signal, "confidence": 0.5, "sequence": 1.5}])

    def test_context_preserves_evidence_references_and_is_bounded(self):
        result = build_context(
            [{"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 1.0}],
            episodes=[{"episode_id": "e1", "evidence_refs": ["ates://r1"]}],
            max_items=1,
        )
        self.assertEqual(result["evidence_refs"], ["ates://r1"])
        self.assertEqual(len(result["signals"]), 1)
        self.assertEqual(result["truncated_signal_count"], 0)

    def test_context_reports_truncation_and_keeps_evidence(self):
        signals = [{"signal_id": f"s{i}", "source": "sensor", "kind": "ready", "sequence": i, "confidence": 1.0} for i in range(3)]
        result = build_context(signals, episodes=[{"episode_id": "e1", "evidence_refs": ["ates://keep"]}], max_items=2)
        self.assertEqual([item["signal_id"] for item in result["signals"]], ["s1", "s2"])
        self.assertEqual(result["truncated_signal_count"], 1)
        self.assertEqual(result["evidence_refs"], ["ates://keep"])

    def test_intent_requires_goal_and_normalizes_constraints(self):
        result = normalize_intent({"goal": "ship validated change", "priority": 4, "constraints": ["tests-green"]})
        self.assertEqual(result["goal"], "ship validated change")
        self.assertEqual(result["priority"], 4)
        with self.assertRaises(ValueError):
            normalize_intent({"goal": " "})
        with self.assertRaises(ValueError):
            normalize_intent({"goal": "ship", "priority": 6})

    def test_action_selection_is_deterministic_and_respects_write_conflicts(self):
        candidates = [
            {"id": "docs", "priority": 2, "writes": ["docs/README.md"]},
            {"id": "tests", "priority": 5, "writes": ["tests/test_x.py"]},
            {"id": "docs2", "priority": 3, "writes": ["docs/README.md"]},
        ]
        self.assertEqual(select_actions(candidates, max_parallel=2), ["tests", "docs2"])
        with self.assertRaisesRegex(ValueError, "unique"):
            select_actions([{"id": "x"}, {"id": "x"}])

    def test_timing_error_reports_signed_drift_without_mutating_policy(self):
        result = timing_error(expected_duration_ms=100, actual_duration_ms=130)
        self.assertEqual(result["drift_ms"], 30)
        self.assertEqual(result["status"], "overrun")
        self.assertEqual(result["policy_action"], "observe_only")
        self.assertEqual(timing_error(100, 70)["status"], "underrun")
        self.assertEqual(timing_error(100, 100)["status"], "on_time")
        with self.assertRaises(ValueError):
            timing_error(100, float("nan"))

    def test_homeostasis_selects_earliest_wake_boundary(self):
        result = plan_wake(now_ms=100, event_deadline_ms=180, window_close_ms=160, max_wait_ms=100)
        self.assertEqual(result["wake_at_ms"], 160)
        self.assertEqual(result["wake_reason"], "window_close")
        future = plan_wake(now_ms=100, event_deadline_ms=90, window_close_ms=100, max_wait_ms=50)
        self.assertEqual(future["wake_at_ms"], 150)
        self.assertEqual(future["wake_reason"], "max_wait")

    def test_composer_wires_action_prediction_and_homeostasis_modules(self):
        intent = {"goal": "validate release", "priority": 3}
        signals = [{"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}]
        plan = {"waves": [["build"], ["tests"]]}
        assignments = {
            "build": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": [], "evidence_refs": ["ates://build"]},
            "tests": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": ["build-ready"], "evidence_refs": ["ates://tests"], "depends_on": ["spec"]},
        }
        score = compose_score(
            intent, signals, plan, assignments,
            action_candidates=[
                {"id": "build", "priority": 5, "writes": ["src/app.py"]},
                {"id": "tests", "priority": 4, "writes": ["tests/test_app.py"]},
                {"id": "docs", "priority": 2, "writes": ["src/app.py"]},
            ],
            max_parallel=2,
            timing_observations=[{"task_id": "build", "expected_duration_ms": 100, "actual_duration_ms": 130}],
            wake_context={"now_ms": 100, "window_close_ms": 150, "max_wait_ms": 100},
        )
        self.assertEqual(score["action_shortlist"], ["build", "tests"])
        self.assertEqual(score["timing_feedback"][0]["drift_ms"], 30)
        self.assertEqual(score["wake_recommendation"]["wake_at_ms"], 150)

    def test_conductor_preserves_required_cue_metadata(self):
        assignments = {"a": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 10, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": ["a-ready"], "evidence_refs": ["ates://a"], "depends_on": ["root"]}}
        cue = build_cue_sheet({"waves": [["a"]]}, assignments, ConductorPlacement.MANAGER_POLICY)["waves"][0]["tasks"][0]
        self.assertEqual(cue["dependency_barriers"], ["a-ready"])
        self.assertEqual(cue["evidence_refs"], ["ates://a"])
        self.assertEqual(cue["depends_on"], ["root"])

    def test_score_id_tracks_evidence_changes(self):
        intent = {"goal": "validate release", "priority": 3}
        signals = [{"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}]
        plan = {"waves": [["spec"]]}
        assignment = {
            "spec": {
                "nominal_at": "2026-11-27T12:00:00Z", "opens_at": "2026-11-27T11:59:00Z",
                "closes_at": "2026-11-27T12:05:00Z", "expected_duration_ms": 1000,
                "phase": "on_beat", "open_length_ms": 360000, "dependency_barriers": [],
                "evidence_refs": ["ates://spec-v1"],
            }
        }
        original = compose_score(intent, signals, plan, assignment)
        revised = compose_score(intent, signals, plan, {"spec": {**assignment["spec"], "evidence_refs": ["ates://spec-v2"]}})
        self.assertNotEqual(original["score_id"], revised["score_id"])


if __name__ == "__main__":
    unittest.main()
