import json
from pathlib import Path

import pytest

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


def write_stream(tmp_path: Path, *events):
    path = tmp_path / "sim-memory.jsonl"
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )
    return path


def test_valid_problem_and_attempt_stream(tmp_path):
    path = write_stream(tmp_path, problem_event(), attempt_event())
    assert validate_records(path) == {"events": 2, "problems": 1, "attempts": 1}


def test_attempt_requires_prior_problem_open(tmp_path):
    path = write_stream(tmp_path, attempt_event())
    with pytest.raises(SimMemoryValidationError, match="unopened problem_id"):
        validate_records(path)


def test_attempt_ordinals_are_contiguous(tmp_path):
    path = write_stream(tmp_path, problem_event(), attempt_event(ordinal=2))
    with pytest.raises(SimMemoryValidationError, match="expected attempt ordinal 1"):
        validate_records(path)


def test_held_out_feedback_is_rejected(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["context"]["held_out_feedback_exposed"] = True
    path = write_stream(tmp_path, problem_event(), attempt)
    with pytest.raises(SimMemoryValidationError, match="schema violation"):
        validate_records(path)


def test_prediction_precedes_observation_and_record(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["observed_at"] = "2026-11-27T12:01:00Z"
    path = write_stream(tmp_path, problem_event(), attempt)
    with pytest.raises(SimMemoryValidationError, match="predicted_at < observed_at"):
        validate_records(path)


def test_observed_task_ids_are_a_subset_of_predictions(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["observation"]["fixed_task_ids"] = ["unpredicted-task"]
    path = write_stream(tmp_path, problem_event(), attempt)
    with pytest.raises(SimMemoryValidationError, match="exceed the predicted task set"):
        validate_records(path)


def test_passed_count_cannot_exceed_total(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["observation"]["passed"] = 2
    path = write_stream(tmp_path, problem_event(), attempt)
    with pytest.raises(SimMemoryValidationError, match="passed count exceeds"):
        validate_records(path)


def test_regressions_are_valid_observations(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["observation"]["outcome"] = "regressed"
    attempt["attempt"]["observation"]["fixed_task_ids"] = []
    attempt["attempt"]["observation"]["missed_task_ids"] = ["completion-evidence-contract"]
    attempt["attempt"]["observation"]["passed"] = 0
    path = write_stream(tmp_path, problem_event(), attempt)
    assert validate_records(path)["attempts"] == 1


def test_duplicate_record_ids_are_rejected(tmp_path):
    opened = problem_event()
    attempt = attempt_event(record_id=opened["record_id"])
    path = write_stream(tmp_path, opened, attempt)
    with pytest.raises(SimMemoryValidationError, match="duplicate record_id"):
        validate_records(path)
