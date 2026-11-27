"""Composer score compilation contract tests."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deepcli.observatory.composer import (
    ComposerIntent,
    ComposerPolicy,
    compose_score,
    serialize_score,
)
from deepcli.observatory.conductor import ConductorPlacement


def assignment():
    return {
        "nominal_at": "2026-11-27T12:00:00Z",
        "opens_at": "2026-11-27T11:59:30Z",
        "closes_at": "2026-11-27T12:05:00Z",
        "expected_duration_ms": 120000,
        "phase": "on_beat",
        "open_length_ms": 330000,
        "dependency_barriers": ["phase-dag:spec-ready"],
        "evidence_refs": ["ates://receipt/spec"],
        "depends_on": [],
        "wake_conditions": ["event", "window_close"],
    }


class ComposerTests(unittest.TestCase):
    def setUp(self):
        self.intent = ComposerIntent(
            intent_id="intent-5939",
            objective="Build a verified release",
            tasks=(
                {"id": "spec", "depends_on": [], "writes": ["spec.md"]},
                {"id": "tests", "depends_on": ["spec"], "writes": ["tests.py"]},
                {"id": "docs", "depends_on": ["spec"], "writes": ["docs.md"]},
            ),
            success_criteria=("all checks pass", "evidence is attributable"),
            context_refs=("pr://5939", "commit://8ad6b73"),
        )
        self.assignments = {task_id: assignment() for task_id in ("spec", "tests", "docs")}

    def test_composes_intent_through_ballet_and_conductor(self):
        score = compose_score(self.intent, self.assignments)
        self.assertEqual(score["schema_version"], "composer.score.v1")
        self.assertEqual(score["intent"], {"id": "intent-5939", "objective": "Build a verified release"})
        self.assertEqual(score["plan"]["task_count"], 3)
        self.assertEqual(score["cue_sheet"]["task_count"], 3)
        self.assertEqual(score["authority"], "dispatch_intent_only")
        self.assertEqual(score["context_refs"], ["pr://5939", "commit://8ad6b73"])
        self.assertEqual(score["success_criteria"], ["all checks pass", "evidence is attributable"])

    def test_preserves_temporal_provenance_and_task_dependencies(self):
        score = compose_score(self.intent, self.assignments)
        cues = {
            cue["task_id"]: cue
            for wave in score["cue_sheet"]["waves"]
            for cue in wave["tasks"]
        }
        cue = cues["spec"]
        self.assertEqual(cue["phase"], "on_beat")
        self.assertEqual(cue["open_length_ms"], 330000)
        self.assertEqual(cue["dependency_barriers"], ["phase-dag:spec-ready"])
        self.assertEqual(cue["evidence_refs"], ["ates://receipt/spec"])
        self.assertEqual(cues["tests"]["depends_on"], ["spec"])
        self.assertEqual(cues["docs"]["depends_on"], ["spec"])

    def test_policy_controls_placement_and_wave_strategy(self):
        policy = ComposerPolicy(version="composer.policy.v2", placement=ConductorPlacement.MANAGER_POLICY, strategy="sequential", max_parallel=1)
        score = compose_score(self.intent, self.assignments, policy)
        self.assertEqual(score["policy"]["version"], "composer.policy.v2")
        self.assertEqual(score["policy"]["placement"], "manager_policy")
        self.assertEqual(score["plan"]["strategy"], "sequential")
        self.assertEqual(score["plan"]["max_parallel"], 1)

    def test_canonical_serialization_is_independent_of_mapping_insertion_order(self):
        first = compose_score(self.intent, self.assignments)
        second = compose_score(self.intent, dict(reversed(list(self.assignments.items()))))
        self.assertEqual(serialize_score(first), serialize_score(second))
        self.assertEqual(serialize_score(first), json.dumps(first, sort_keys=True, separators=(",", ":"), ensure_ascii=False))

    def test_rejects_blank_intent_id(self):
        invalid = ComposerIntent(" ", "objective", self.intent.tasks, ("done",))
        with self.assertRaisesRegex(ValueError, "intent_id"):
            compose_score(invalid, self.assignments)

    def test_rejects_blank_objective(self):
        invalid = ComposerIntent("i", " ", self.intent.tasks, ("done",))
        with self.assertRaisesRegex(ValueError, "objective"):
            compose_score(invalid, self.assignments)

    def test_rejects_empty_success_criteria(self):
        invalid = ComposerIntent("i", "objective", self.intent.tasks, ())
        with self.assertRaisesRegex(ValueError, "success_criteria"):
            compose_score(invalid, self.assignments)

    def test_rejects_blank_context_reference(self):
        invalid = ComposerIntent("i", "objective", self.intent.tasks, ("done",), (" ",))
        with self.assertRaisesRegex(ValueError, "context_refs"):
            compose_score(invalid, self.assignments)

    def test_rejects_invalid_strategy(self):
        with self.assertRaisesRegex(ValueError, "strategy"):
            compose_score(self.intent, self.assignments, ComposerPolicy(strategy="chaotic"))

    def test_rejects_non_positive_parallel_capacity(self):
        with self.assertRaisesRegex(ValueError, "max_parallel"):
            compose_score(self.intent, self.assignments, ComposerPolicy(max_parallel=0))

    def test_rejects_missing_assignment_metadata(self):
        with self.assertRaisesRegex(ValueError, "assignments"):
            compose_score(self.intent, {"spec": assignment()})

    def test_rejects_extra_assignment(self):
        assignments = dict(self.assignments)
        assignments["stale"] = assignment()
        with self.assertRaisesRegex(ValueError, "extra"):
            compose_score(self.intent, assignments)

    def test_rejects_duplicate_task_ids(self):
        invalid = ComposerIntent("i", "objective", ({"id": "same"}, {"id": "same"}), ("done",))
        with self.assertRaisesRegex(ValueError, "unique"):
            compose_score(invalid, {"same": assignment()})

    def test_rejects_non_json_compatible_task_payload(self):
        invalid = ComposerIntent("i", "objective", ({"id": "spec", "custom": object()},), ("done",))
        with self.assertRaisesRegex(ValueError, "JSON"):
            compose_score(invalid, {"spec": assignment()})

    def test_serialization_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            serialize_score({"invalid": float("nan")})

    def test_does_not_mutate_caller_assignments(self):
        original = json.loads(json.dumps(self.assignments))
        compose_score(self.intent, self.assignments)
        self.assertEqual(self.assignments, original)


if __name__ == "__main__":
    unittest.main()
