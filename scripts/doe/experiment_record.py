#!/usr/bin/env python3
"""Build and validate canonical DoE/MVT experiment evidence records.

This module intentionally keeps missing execution evidence explicit. It never
turns an absent SHA, test result, or measurement into a successful observation.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_record(*, experiment_id: str, observed_at: str,
                 baseline_sha: str, candidate_sha: str,
                 merge_base_sha: str | None, suite: str,
                 baseline_exit_code: int | None,
                 candidate_exit_code: int | None,
                 compare_only: bool, repository: str,
                 run_id: str, run_attempt: str,
                 manager_policy_id: str | None = None) -> dict[str, Any]:
    """Return a schema-v1 record with explicit terminal status and provenance."""
    if not SHA40.fullmatch(baseline_sha) or not SHA40.fullmatch(candidate_sha):
        raise ValueError("baseline_sha and candidate_sha must be resolved 40-hex commit SHAs")
    if merge_base_sha is not None and not SHA40.fullmatch(merge_base_sha):
        raise ValueError("merge_base_sha must be null or a resolved 40-hex commit SHA")
    if compare_only:
        status, outcome = "observed", "Reference metadata captured; validation intentionally not run."
    elif baseline_exit_code is None or candidate_exit_code is None:
        status, outcome = "failed", "Validation did not produce a terminal exit code for both immutable refs."
    elif baseline_exit_code == 0 and candidate_exit_code == 0:
        status, outcome = "passed", "Baseline and candidate completed the same validation suite successfully."
    else:
        status, outcome = "failed", "At least one immutable ref failed the validation suite."
    now = observed_at or utc_now()
    return {
        "schema_version": "1.0",
        "experiment_id": experiment_id,
        "observed_at": now,
        "baseline_sha": baseline_sha,
        "candidate_sha": candidate_sha,
        "merge_base_sha": merge_base_sha,
        "suite": suite,
        "cohort": run_id or None,
        "treatment": {
            "manager_policy_id": manager_policy_id or f"agent-mvt/{suite}",
            "provider": None,
            "model": None,
            "arm": "candidate-vs-baseline",
            "instance": None
        },
        "status": status,
        "outcome": outcome,
        "metrics": {
            "baseline_exit_code": baseline_exit_code,
            "candidate_exit_code": candidate_exit_code,
            "run_attempt": int(run_attempt) if str(run_attempt).isdigit() else None
        },
        "provenance": "github",
        "confidence": "low",
        "evidence_refs": [
            f"https://github.com/{repository}/actions/runs/{run_id}"
        ] if repository and run_id else [],
        "session_id": None,
        "window": {"start": now, "end": utc_now()}
    }


def validate_record(record: dict[str, Any], schema_path: str | Path) -> None:
    """Validate against the repository's canonical JSON Schema (Draft 2020-12)."""
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover - exercised by workflow dependency
        raise RuntimeError("jsonschema is required to validate canonical experiment records") from exc
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(record)


def write_failure_envelope(path: str | Path, *, experiment_id: str,
                           stage: str, reason: str, candidate_ref: str,
                           baseline_ref: str, run_id: str) -> None:
    """Preserve pre-resolution failures without inventing canonical commit SHAs."""
    payload = {
        "evidence_type": "mvt-precanonical-failure/v1",
        "experiment_id": experiment_id,
        "status": "blocked",
        "failed_stage": stage,
        "reason": reason[:2000],
        "candidate_ref": candidate_ref,
        "baseline_ref": baseline_ref,
        "run_id": run_id,
        "observed_at": utc_now(),
        "canonical_record_emitted": False,
        "canonical_record_reason": "Immutable baseline/candidate SHAs were not both resolved."
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output", default="mvt-experiment.json")
    parser.add_argument("--failure-output", default="mvt-failure.json")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--baseline-sha", default="")
    parser.add_argument("--candidate-sha", default="")
    parser.add_argument("--merge-base-sha", default="")
    parser.add_argument("--suite", default="smoke")
    parser.add_argument("--baseline-exit", type=int)
    parser.add_argument("--candidate-exit", type=int)
    parser.add_argument("--compare-only", action="store_true")
    parser.add_argument("--repository", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-attempt", default="1")
    parser.add_argument("--failed-stage", default="validation")
    parser.add_argument("--failure-reason", default="")
    parser.add_argument("--candidate-ref", default="")
    parser.add_argument("--baseline-ref", default="")
    args = parser.parse_args()

    if not SHA40.fullmatch(args.baseline_sha) or not SHA40.fullmatch(args.candidate_sha):
        write_failure_envelope(
            args.failure_output, experiment_id=args.experiment_id,
            stage=args.failed_stage,
            reason=args.failure_reason or "Commit resolution or an earlier workflow stage failed.",
            candidate_ref=args.candidate_ref, baseline_ref=args.baseline_ref,
            run_id=args.run_id
        )
        return 0

    record = build_record(
        experiment_id=args.experiment_id, observed_at=utc_now(),
        baseline_sha=args.baseline_sha, candidate_sha=args.candidate_sha,
        merge_base_sha=args.merge_base_sha or None, suite=args.suite,
        baseline_exit_code=args.baseline_exit,
        candidate_exit_code=args.candidate_exit,
        compare_only=args.compare_only, repository=args.repository,
        run_id=args.run_id, run_attempt=args.run_attempt
    )
    validate_record(record, args.schema)
    Path(args.output).write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"schema_version": record["schema_version"],
                      "status": record["status"],
                      "experiment_id": record["experiment_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
