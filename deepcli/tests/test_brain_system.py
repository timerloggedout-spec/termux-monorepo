"""Brain/CNS-inspired pure coordination contract tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deepcli.observatory.brain.signals import normalize_signals
from deepcli.observatory.brain.context import build_context
from deepcli.observatory.brain.executive import normalize_intent
from deepcli.observatory.brain.action_selection import select_actions
from deepcli.observatory.brain.prediction import timing_error
from deepcli.observatory.brain.homeostasis import plan_wake
from deepcli.observatory.brain.composer import compose_score

class BrainSystemTests(unittest.TestCase):
    def test_signal_normalization_deduplicates_and_orders_by_sequence(self):
        signals=[{"signal_id":"s2","source":"collector","kind":"completed","sequence":2,"confidence":0.9},
                 {"signal_id":"s1","source":"sensor","kind":"ready","sequence":1,"confidence":0.8},
                 {"signal_id":"s1","source":"sensor","kind":"ready","sequence":1,"confidence":0.8}]
        self.assertEqual([item["signal_id"] for item in normalize_signals(signals)],["s1","s2"])
    def test_conflicting_signal_identity_is_rejected(self):
        signal={"signal_id":"s1","source":"sensor","kind":"ready","sequence":1,"confidence":0.8}
        with self.assertRaisesRegex(ValueError,"conflicting duplicate"): normalize_signals([signal,{**signal,"kind":"failed"}])
    def test_invalid_signal_confidence_and_sequence_are_rejected(self):
        signal={"signal_id":"s1","source":"sensor","kind":"ready","sequence":1,"confidence":1.2}
        with self.assertRaisesRegex(ValueError,"confidence"): normalize_signals([signal])
        with self.assertRaisesRegex(ValueError,"sequence"): normalize_signals([{**signal,"confidence":0.5,"sequence":1.5}])
    def test_context_preserves_evidence_references_and_is_bounded(self):
        result=build_context([{"signal_id":"s1","source":"sensor","kind":"ready","sequence":1,"confidence":1.0}],
          episodes=[{"episode_id":"e1","evidence_refs":["ates://r1"]}],max_items=1)
        self.assertEqual(result["evidence_refs"],["ates://r1"]); self.assertEqual(len(result["signals"]),1)
    def test_context_reports_truncation_and_keeps_evidence(self):
        signals=[{"signal_id":f"s{i}","source":"sensor","kind":"ready","sequence":i,"confidence":1.0} for i in range(3)]
        result=build_context(signals,episodes=[{"episode_id":"e1","evidence_refs":["ates://keep"]}],max_items=2)
        self.assertEqual([x["signal_id"] for x in result["signals"]],["s1","s2"])
        self.assertEqual(result["truncated_signal_count"],1); self.assertEqual(result["evidence_refs"],["ates://keep"])
    def test_intent_requires_goal_and_normalizes_constraints(self):
        result=normalize_intent({"goal":"ship validated change","priority":4,"constraints":["tests-green"]})
        self.assertEqual(result["goal"],"ship validated change"); self.assertEqual(result["priority"],4)
        with self.assertRaises(ValueError): normalize_intent({"goal":" "})
        with self.assertRaises(ValueError): normalize_intent({"goal":"ship","priority":6})
    def test_action_selection_is_deterministic_and_respects_write_conflicts(self):
        candidates=[{"id":"docs","priority":2,"writes":["docs/README.md"]},{"id":"tests","priority":5,"writes":["tests/test_x.py"]},{"id":"docs2","priority":3,"writes":["docs/README.md"]}]
        self.assertEqual(select_actions(candidates,max_parallel=2),["tests","docs2"])
        with self.assertRaisesRegex(ValueError,"unique"): select_actions([{"id":"x"},{"id":"x"}])
    def test_timing_error_reports_signed_drift_without_mutating_policy(self):
        result=timing_error(100,130)
        self.assertEqual(result["drift_ms"],30); self.assertEqual(result["status"],"overrun")
        self.assertEqual(result["policy_action"],"observe_only")
        self.assertEqual(timing_error(100,70)["status"],"underrun"); self.assertEqual(timing_error(100,100)["status"],"on_time")
        with self.assertRaises(ValueError): timing_error(100,float("nan"))
    def test_homeostasis_selects_earliest_wake_boundary(self):
        result=plan_wake(100,event_deadline_ms=180,window_close_ms=160,max_wait_ms=100)
        self.assertEqual(result["wake_at_ms"],160); self.assertEqual(result["wake_reason"],"window_close")
        future=plan_wake(100,event_deadline_ms=90,window_close_ms=100,max_wait_ms=50)
        self.assertEqual(future["wake_at_ms"],150); self.assertEqual(future["wake_reason"],"max_wait")
    def test_composer_emits_deterministic_score_and_keeps_dispatch_intent_only(self):
        intent={"goal":"validate release","priority":3,"constraints":["evidence-required"]}
        signals=[{"signal_id":"s1","source":"ci","kind":"ready","sequence":1,"confidence":1.0}]
        plan={"waves":[["spec"],["tests"]]}
        assignments={
          "spec":{"nominal_at":"2026-11-27T12:00:00Z","opens_at":"2026-11-27T11:59:00Z","closes_at":"2026-11-27T12:05:00Z","expected_duration_ms":1000,"phase":"on_beat","open_length_ms":360000,"dependency_barriers":[],"evidence_refs":["ates://spec"]},
          "tests":{"nominal_at":"2026-11-27T12:01:00Z","opens_at":"2026-11-27T12:00:00Z","closes_at":"2026-11-27T12:06:00Z","expected_duration_ms":2000,"phase":"on_beat","open_length_ms":360000,"dependency_barriers":["spec-ready"],"evidence_refs":["ates://tests"],"depends_on":["spec"]}}
        first=compose_score(intent,signals,plan,assignments); second=compose_score(intent,signals,plan,assignments)
        self.assertEqual(first,second); self.assertEqual(first["schema_version"],"brain.composer.score.v1")
        self.assertEqual(first["cue_sheet"]["authority"],"dispatch_intent_only")
        self.assertEqual(first["cue_sheet"]["waves"][0]["tasks"][0]["phase"],"on_beat")
        self.assertEqual(first["score_id"],second["score_id"]); self.assertEqual(first["authority"]["admission_and_claims"],"QUE")
        self.assertEqual(first["cue_sheet"]["waves"][1]["tasks"][0]["depends_on"],["spec"])
if __name__ == "__main__": unittest.main()
