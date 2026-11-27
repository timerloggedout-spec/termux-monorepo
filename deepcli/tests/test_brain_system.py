import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory.brain.signals import normalize_signals
from deepcli.observatory.brain.attention import focus_signals
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

    def test_attention_prioritizes_salient_signals_with_a_bounded_focus(self):
        signals = [
            {"signal_id": "s1", "source": "sensor", "kind": "ready", "sequence": 1, "confidence": 0.9, "priority": 1, "salience": 0.9},
            {"signal_id": "s2", "source": "sensor", "kind": "alert", "sequence": 2, "confidence": 0.7, "priority": 3, "salience": 0.2},
            {"signal_id": "s3", "source": "sensor", "kind": "urgent", "sequence": 3, "confidence": 0.8, "priority": 3, "salience": 0.8},
        ]
        result = focus_signals(signals, max_focus=2)
        self.assertEqual(result["focus_signal_ids"], ["s3", "s2"])
        self.assertEqual(result["deferred_signal_ids"], ["s1"])
        self.assertEqual(result["max_focus"], 2)

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
        signals = [
            {"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0, "priority": 4, "salience": 0.9},
            {"signal_id": "s2", "source": "collector", "kind": "heartbeat", "sequence": 2, "confidence": 0.7, "priority": 1, "salience": 0.2},
        ]
        plan = {"waves": [["build"], ["tests"]]}
        assignments = {
            "build": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": [], "evidence_refs": ["ates://build"]},
            "tests": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": ["build-ready"], "evidence_refs": ["ates://tests"], "depends_on": ["build"]},
        }
        candidates = [
            {"id": "build", "priority": 5, "writes": ["src/app.py"]},
            {"id": "tests", "priority": 4, "writes": ["tests/test_app.py"]},
            {"id": "docs", "priority": 2, "writes": ["src/app.py"]},
        ]
        receipt = {"source": "ATES", "run_id": "run-123", "cohort_id": "cohort-1", "evidence_ref": "ates://receipt/123", "sha256": "a" * 64}
        receipt_resolver = lambda evidence_ref: receipt
        timing = [{"task_id": "build", "receipt": receipt, "expected_duration_ms": 100, "actual_duration_ms": 130}]
        wake = {"now_ms": 100, "window_close_ms": 150, "max_wait_ms": 100}
        score = compose_score(intent, signals, plan, assignments, action_candidates=candidates,
                              max_parallel=2, timing_observations=timing, wake_context=wake,
                              receipt_resolver=receipt_resolver, attention_budget=1)
        repeated = compose_score(intent, signals, plan, assignments, action_candidates=candidates,
                                  max_parallel=2, timing_observations=timing, wake_context=wake,
                                  receipt_resolver=receipt_resolver, attention_budget=1)
        policy_variant = compose_score(intent, signals, plan, assignments, action_candidates=candidates,
                                        max_parallel=3, timing_observations=timing, wake_context=wake,
                                        receipt_resolver=receipt_resolver, attention_budget=1)
        attention_variant = compose_score(intent, signals, plan, assignments, action_candidates=candidates,
                                           max_parallel=2, timing_observations=timing, wake_context=wake,
                                           receipt_resolver=receipt_resolver, attention_budget=2)
        self.assertEqual(score["action_shortlist"], ["build", "tests"])
        self.assertEqual(score["timing_feedback"][0]["drift_ms"], 30)
        self.assertEqual(score["timing_feedback"][0]["run_id"], "run-123")
        self.assertEqual(score["timing_feedback"][0]["evidence_ref"], "ates://receipt/123")
        self.assertEqual(score["wake_recommendation"]["wake_at_ms"], 150)
        self.assertEqual(score["schema_version"], "brain.composer.score.v3")
        self.assertEqual(score["authority"]["admission_and_claims"], "QUE")
        self.assertEqual(score["cue_sheet"]["authority"], "dispatch_intent_only")
        self.assertEqual(score["attention"]["focus_signal_ids"], ["s1"])
        self.assertEqual(score["attention"]["max_focus"], 1)
        self.assertEqual(score["cue_sheet"]["waves"][1]["tasks"][0]["depends_on"], ["build"])
        self.assertEqual(score["score_id"], repeated["score_id"])
        self.assertEqual(score["action_shortlist"], policy_variant["action_shortlist"])
        self.assertNotEqual(score["score_id"], policy_variant["score_id"])
        self.assertNotEqual(score["score_id"], attention_variant["score_id"])

    def test_conductor_preserves_required_cue_metadata(self):
        assignments = {"a": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 10, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": ["a-ready"], "evidence_refs": ["ates://a"], "depends_on": ["root"]}}
        cue = build_cue_sheet({"waves": [["a"]]}, assignments, ConductorPlacement.MANAGER_POLICY)["waves"][0]["tasks"][0]
        self.assertEqual(cue["dependency_barriers"], ["a-ready"])
        self.assertEqual(cue["evidence_refs"], ["ates://a"])
        self.assertEqual(cue["depends_on"], ["root"])

    def test_composer_requires_receipt_provenance_for_timing_feedback(self):
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            compose_score(
                {"goal": "validate release"},
                [{"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}],
                {"waves": [["build"]]},
                {"build": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": [], "evidence_refs": ["ates://build"]}},
                timing_observations=[{"task_id": "build", "receipt": {"source": "ATES", "run_id": "run-123", "cohort_id": "cohort-1", "sha256": "a" * 64}, "expected_duration_ms": 100, "actual_duration_ms": 130}],
                receipt_resolver=lambda evidence_ref: {},
            )

    def test_composer_rejects_canonical_receipt_mismatch(self):
        receipt = {"source": "ATES", "run_id": "run-123", "cohort_id": "cohort-1", "evidence_ref": "ates://receipt/123", "sha256": "a" * 64}
        with self.assertRaisesRegex(ValueError, "verification mismatch"):
            compose_score(
                {"goal": "validate release"},
                [{"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}],
                {"waves": [["build"]]},
                {"build": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 100, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": [], "evidence_refs": ["ates://build"]}},
                timing_observations=[{"task_id": "build", "receipt": receipt, "expected_duration_ms": 100, "actual_duration_ms": 130}],
                receipt_resolver=lambda evidence_ref: {**receipt, "sha256": "b" * 64},
            )

    def test_default_score_identity_is_stable_with_empty_optional_modules(self):
        intent = {"goal": "inspect plan"}
        signals = [{"signal_id": "s1", "source": "ci", "kind": "ready", "sequence": 1, "confidence": 1.0}]
        plan = {"waves": [["build"]]}
        assignments = {"build": {"nominal_at": "n", "opens_at": "o", "closes_at": "c", "expected_duration_ms": 10, "phase": "on_beat", "open_length_ms": 10, "dependency_barriers": [], "evidence_refs": ["ates://build"]}}
        first = compose_score(intent, signals, plan, assignments)
        second = compose_score(intent, signals, plan, assignments)
        self.assertEqual(first["schema_version"], "brain.composer.score.v3")
        self.assertEqual(first["score_id"], second["score_id"])
        self.assertEqual(first["action_shortlist"], [])
        self.assertEqual(first["timing_feedback"], [])
        self.assertIsNone(first["wake_recommendation"])

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
