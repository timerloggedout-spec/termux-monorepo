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
            "change": {
                "summary": "Bind completion to the requested artifact",
                "artifact_ref": "docs/ops/SELF-IMPROVEMENT-MEMORY.md",
                "diff_sha256": DIGEST,
            },
            "rationale": "A successful process exit does not prove the requested deliverable exists",
            "prediction": {
                "expected_effect": "Reduce false-positive task completion",
                "target_signals": ["acceptance-evidence", "false-completion-rate"],
            },
            "observation": {
                "outcome": "improved",
                "summary": "Focused contract fixture confirms artifact evidence is required",
                "measured_signals": [
                    {"name": "fixture-pass", "baseline": 0, "observed": 1, "unit": "boolean"}
                ],
                "evidence_refs": ["https://github.com/timerloggedout-spec/termux-monorepo/commit/" + SHA_B],
            },
            "context": {
                "repository": "timerloggedout-spec/termux-monorepo",
                "source_sha": SHA_A,
                "target_sha": SHA_B,
                "harness_version": "completion-gate-v1",
                "policy": {"attribution": "unknown"},
                "benchmark": {
                    "id": "sim-contract-fixtures",
                    "version": "1",
                    "stage": "target",
                    "cohort_id": "sim-fixture-cohort-1",
                },
                "environment_fingerprint": "python-ci-linux",
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


def test_regressions_are_valid_observations(tmp_path):
    attempt = attempt_event()
    attempt["attempt"]["observation"]["outcome"] = "regressed"
    path = write_stream(tmp_path, problem_event(), attempt)
    assert validate_records(path)["attempts"] == 1


def test_duplicate_record_ids_are_rejected(tmp_path):
    opened = problem_event()
    attempt = attempt_event(record_id=opened["record_id"])
    path = write_stream(tmp_path, opened, attempt)
    with pytest.raises(SimMemoryValidationError, match="duplicate record_id"):
        validate_records(path)
