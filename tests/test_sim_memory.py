import json
import tempfile
import unittest
from pathlib import Path

from scripts.agent_evolution.sim_memory import RetrievalQuery, retrieve_sim_memory

from scripts.ci.validate_sim_memory import (
    SimMemoryValidationError,
    validate_records,
)

SHA_A = "a" * 40
SHA_B = "b" * 40
DIGEST = "c" * 64


def problem_event(record_id="record-open", problem_id="premature-completion"):
    return {
        "schema_version": "sim.memory.v1",
        "record_id": record_id,
        "recorded_at": "2026-11-27T12:00:00Z",
        "record_type": "problem_opened",
        "problem_id": problem_id,
        "problem": {
            "summary": "Completion is inferred from command exit status",
            "root_cause": "The harness checks process success rather than deliverable acceptance",
            "domain": "repository-engineering",
            "component": "completion-gate",
            "opened_round": 0,
        },
    }


def attempt_event(ordinal=1, record_id="record-attempt-1", attempt_id="attempt-1"):
    event = problem_event()
    event.update({
        "record_id": record_id,
        "record_type": "attempt_recorded",
        "attempt": {
            "attempt_id": attempt_id,
            "ordinal": ordinal,
            "sample_id": "candidate-s1",
            "accepted": True,
            "change": {
                "summary": "Bind completion to the requested artifact",
                "files": ["scripts/ci/validate_sim_memory.py"],
                "artifact_ref": "docs/ops/SELF-IMPROVEMENT-MEMORY.md",
                "diff_sha256": DIGEST,
            },
            "rationale": "A successful process exit does not prove the requested deliverable exists",
            "predicted_at": "2026-11-27T11:58:00Z",
            "prediction": {
                "expected_effect": "Reduce false-positive task completion",
                "predicted_task_ids": ["completion-evidence-contract"],
                "target_signals": ["acceptance-evidence", "false-completion-rate"],
            },
            "observed_at": "2026-11-27T11:59:00Z",
            "observation": {
                "outcome": "improved",
                "summary": "Focused contract fixture confirms artifact evidence is required",
                "fixed_task_ids": ["completion-evidence-contract"],
                "missed_task_ids": [],
                "unresolved_task_ids": [],
                "passed": 1,
                "total": 1,
                "measured_signals": [
                    {"name": "fixture-pass", "baseline": 0, "observed": 1, "unit": "boolean"}
                ],
                "evidence_refs": ["https://github.com/timerloggedout-spec/termux-monorepo/commit/" + SHA_B],
            },
            "context": {
                "repository": "timerloggedout-spec/termux-monorepo",
                "source_run_id": "source-run-1",
                "target_run_id": "target-run-1",
                "source_sha": SHA_A,
                "target_sha": SHA_B,
                "source_harness_version": "seed-v0",
                "target_harness_version": "candidate-v1",
                "source_policy": {"attribution": "unknown"},
                "target_policy": {"attribution": "unknown"},
                "source_benchmark": {
                    "id": "source-bench",
                    "version": "1",
                    "cohort_id": "source-cohort-1",
                },
                "target_benchmark": {
                    "id": "target-bench",
                    "version": "1",
                    "cohort_id": "target-cohort-1",
                },
                "source_environment_fingerprint": "source-python-ci-linux",
                "target_environment_fingerprint": "target-python-ci-linux",
                "evaluator": "contract-tests-v1",
                "domain": "repository-engineering",
                "round": 1,
                "candidate_budget": 2,
                "evaluation_budget": 1,
                "evaluation_split": "evolve",
                "held_out_feedback_exposed": False,
            },
            "selection": {
                "status": "selected",
                "rationale": "Selected for the bounded contract fixture evaluation",
            },
        },
    })
    return event


class SimMemoryValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.path = Path(self.tempdir.name) / "sim-memory.jsonl"

    def write_stream(self, *events):
        self.path.write_text(
            "".join(json.dumps(event) + "\n" for event in events),
            encoding="utf-8",
        )
        return self.path

    def test_valid_problem_and_attempt_stream(self):
        path = self.write_stream(problem_event(), attempt_event())
        self.assertEqual(
            validate_records(path),
            {"events": 2, "problems": 1, "attempts": 1},
        )

    def test_attempt_requires_prior_problem_open(self):
        path = self.write_stream(attempt_event())
        with self.assertRaisesRegex(SimMemoryValidationError, "unopened problem_id"):
            validate_records(path)

    def test_attempt_ordinals_are_contiguous(self):
        path = self.write_stream(problem_event(), attempt_event(ordinal=2))
        with self.assertRaisesRegex(SimMemoryValidationError, "expected attempt ordinal 1"):
            validate_records(path)

    def test_held_out_feedback_is_rejected(self):
        attempt = attempt_event()
        attempt["attempt"]["context"]["held_out_feedback_exposed"] = True
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "schema violation"):
            validate_records(path)

    def test_selector_acceptance_is_required(self):
        attempt = attempt_event()
        attempt["attempt"]["accepted"] = False
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "expected constant"):
            validate_records(path)

    def test_prediction_precedes_observation_and_record(self):
        attempt = attempt_event()
        attempt["attempt"]["observed_at"] = "2026-11-27T12:01:00Z"
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "predicted_at < observed_at"):
            validate_records(path)

    def test_observed_task_ids_are_a_subset_of_predictions(self):
        attempt = attempt_event()
        attempt["attempt"]["observation"]["fixed_task_ids"] = ["unpredicted-task"]
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "exceed the predicted task set"):
            validate_records(path)

    def test_predicted_tasks_require_observed_outcomes(self):
        attempt = attempt_event()
        attempt["attempt"]["observation"]["fixed_task_ids"] = []
        attempt["attempt"]["observation"]["missed_task_ids"] = []
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "missing observed outcomes"):
            validate_records(path)

    def test_json_nan_is_rejected(self):
        path = self.write_stream(problem_event(), attempt_event())
        raw = path.read_text(encoding="utf-8").replace('"observed": 1', '"observed": NaN')
        path.write_text(raw, encoding="utf-8")
        with self.assertRaisesRegex(SimMemoryValidationError, "invalid JSON numeric constant NaN"):
            validate_records(path)

    def test_integral_decimal_json_number_is_an_integer(self):
        path = self.write_stream(problem_event(), attempt_event())
        raw = path.read_text(encoding="utf-8").replace('"passed": 1', '"passed": 1.0')
        path.write_text(raw, encoding="utf-8")
        self.assertEqual(validate_records(path)["attempts"], 1)

    def test_timestamp_rejects_out_of_range_offset(self):
        attempt = attempt_event()
        attempt["attempt"]["predicted_at"] = "2026-11-27T11:59:00+00:60"
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "invalid RFC 3339"):
            validate_records(path)

    def test_timestamp_comparison_preserves_nanosecond_precision(self):
        attempt = attempt_event()
        attempt["recorded_at"] = "2026-11-27T12:00:00.000000003Z"
        attempt["attempt"]["predicted_at"] = "2026-11-27T12:00:00.000000001Z"
        attempt["attempt"]["observed_at"] = "2026-11-27T12:00:00.000000002Z"
        path = self.write_stream(problem_event(), attempt)
        self.assertEqual(validate_records(path)["attempts"], 1)

    def test_passed_count_cannot_exceed_total(self):
        attempt = attempt_event()
        attempt["attempt"]["observation"]["passed"] = 2
        path = self.write_stream(problem_event(), attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "passed count exceeds"):
            validate_records(path)

    def test_regressions_are_valid_observations(self):
        attempt = attempt_event()
        attempt["attempt"]["observation"]["outcome"] = "regressed"
        attempt["attempt"]["observation"]["fixed_task_ids"] = []
        attempt["attempt"]["observation"]["missed_task_ids"] = ["completion-evidence-contract"]
        attempt["attempt"]["observation"]["passed"] = 0
        path = self.write_stream(problem_event(), attempt)
        self.assertEqual(validate_records(path)["attempts"], 1)

    def test_duplicate_record_ids_are_rejected(self):
        opened = problem_event()
        attempt = attempt_event(record_id=opened["record_id"])
        path = self.write_stream(opened, attempt)
        with self.assertRaisesRegex(SimMemoryValidationError, "duplicate record_id"):
            validate_records(path)



    def test_retrieval_ranks_exact_policy_benchmark_and_environment(self):
        attempt = attempt_event()
        context = attempt["attempt"]["context"]
        context["target_policy"] = {
            "provider": "provider-x",
            "model": "model-y",
            "attribution": "invocation_verified",
        }
        context["target_environment_fingerprint"] = "target-python-ci-linux"
        path = self.write_stream(problem_event(), attempt)
        query = RetrievalQuery(
            domain="repository-engineering",
            component="completion-gate",
            target_provider="provider-x",
            target_model="model-y",
            target_benchmark_id="target-bench",
            target_benchmark_version="1",
            target_environment_fingerprint="target-python-ci-linux",
            task_ids=("completion-evidence-contract",),
        )
        lessons = retrieve_sim_memory(path, query)
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].compatibility["policy"], "target-exact")
        self.assertEqual(lessons[0].compatibility["benchmark"], "target-exact")
        self.assertEqual(lessons[0].compatibility["environment"], "target-exact")

    def test_retrieval_preserves_regressed_attempts(self):
        attempt = attempt_event()
        context = attempt["attempt"]["context"]
        context["source_policy"] = {
            "provider": "provider-x",
            "model": "source-model",
            "attribution": "invocation_verified",
        }
        context["target_policy"] = {
            "provider": "provider-x",
            "model": "target-model",
            "attribution": "invocation_verified",
        }
        observation = attempt["attempt"]["observation"]
        observation["outcome"] = "regressed"
        observation["fixed_task_ids"] = []
        observation["missed_task_ids"] = ["completion-evidence-contract"]
        observation["passed"] = 0
        path = self.write_stream(problem_event(), attempt)
        query = RetrievalQuery(
            domain="repository-engineering",
            target_provider="provider-x",
            target_model="different-model",
        )
        lessons = retrieve_sim_memory(path, query)
        self.assertEqual(len(lessons), 1)
        self.assertEqual(lessons[0].outcome, "regressed")
        self.assertEqual(lessons[0].compatibility["policy"], "cross-model")
        self.assertEqual(lessons[0].missed_task_ids, ("completion-evidence-contract",))

    def test_retrieval_filters_domain_and_component(self):
        path = self.write_stream(problem_event(), attempt_event())
        self.assertEqual(
            retrieve_sim_memory(path, RetrievalQuery(domain="networking")),
            [],
        )
        self.assertEqual(
            retrieve_sim_memory(
                path,
                RetrievalQuery(domain="repository-engineering", component="networking"),
            ),
            [],
        )

    def test_retrieval_limit_bounds_context(self):
        path = self.write_stream(
            problem_event(),
            attempt_event(),
            attempt_event(ordinal=2, record_id="record-attempt-2", attempt_id="attempt-2"),
        )
        lessons = retrieve_sim_memory(
            path,
            RetrievalQuery(domain="repository-engineering", limit=1),
        )
        self.assertEqual(len(lessons), 1)

    def test_retrieval_rejects_unbounded_limits(self):
        with self.assertRaisesRegex(ValueError, "limit must be between 1 and 32"):
            RetrievalQuery(domain="repository-engineering", limit=33)

if __name__ == "__main__":
    unittest.main()
