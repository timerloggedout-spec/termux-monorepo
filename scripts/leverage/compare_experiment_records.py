#!/usr/bin/env python3
"""Compare two explicit arms from canonical DoE experiment JSONL records.

This is a read-only projection. It never writes experiment records or changes
mechanism lifecycle state. Configured-instance identity is always explicit.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

TERMINAL = {"passed", "failed", "observed", "skipped", "blocked", "superseded"}
GUARDRAIL_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_.-]*)>=(\-?\d+(?:\.\d+)?)$")


class ComparisonError(ValueError):
    pass


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ComparisonError(f"line {line_no}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ComparisonError(f"line {line_no}: record must be an object")
        records.append(value)
    return records


def _number(record: dict[str, Any], key: str, label: str) -> float:
    metrics = record.get("metrics")
    if not isinstance(metrics, dict) or key not in metrics:
        raise ComparisonError(f"{label}: missing metrics.{key}")
    value = metrics[key]
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ComparisonError(f"{label}: metrics.{key} must be a finite number")
    return float(value)


def _selected(
    records: list[dict[str, Any]], experiment_id: str, cohort: str,
    arm: str, instance_key: str,
) -> list[dict[str, Any]]:
    selected = []
    for index, record in enumerate(records):
        if record.get("experiment_id") != experiment_id or record.get("cohort") != cohort:
            continue
        treatment = record.get("treatment")
        if not isinstance(treatment, dict) or treatment.get("arm") != arm:
            continue
        instance = treatment.get("instance")
        if not isinstance(instance, dict) or instance.get("instance_key") != instance_key:
            continue
        if record.get("status") not in TERMINAL:
            raise ComparisonError(f"record {index}: non-terminal status cannot be scored")
        repetition = record.get("metrics", {}).get("repetition") if isinstance(record.get("metrics"), dict) else None
        if not isinstance(repetition, int) or isinstance(repetition, bool) or repetition < 1:
            raise ComparisonError(f"record {index}: metrics.repetition must be a positive integer")
        selected.append(record)
    if not selected:
        raise ComparisonError(f"no records found for arm={arm!r}, instance_key={instance_key!r}")
    return selected


def compare_records(
    records: list[dict[str, Any]], *, experiment_id: str, cohort: str,
    control_arm: str, treatment_arm: str, control_instance_key: str,
    treatment_instance_key: str, outcome_key: str, outcome_direction: str,
    cost_key: str, cost_unit: str, min_pairs: int,
    guardrails: list[tuple[str, float]],
) -> dict[str, Any]:
    if control_arm == treatment_arm:
        raise ComparisonError("control and treatment arms must differ")
    if control_instance_key == treatment_instance_key:
        raise ComparisonError("control and treatment configured-instance keys must differ")
    control = _selected(records, experiment_id, cohort, control_arm, control_instance_key)
    treatment = _selected(records, experiment_id, cohort, treatment_arm, treatment_instance_key)

    def metadata(rows: list[dict[str, Any]], label: str) -> tuple[str, str, str]:
        first = rows[0]
        values = (first.get("suite"), first.get("baseline_sha"), first.get("candidate_sha"))
        if any(not isinstance(value, str) or not value for value in values):
            raise ComparisonError(f"{label}: suite, baseline_sha and candidate_sha are required")
        for row in rows[1:]:
            if (row.get("suite"), row.get("baseline_sha"), row.get("candidate_sha")) != values:
                raise ComparisonError(f"{label}: suite or source SHA changed within selected arm")
        return values

    control_meta = metadata(control, "control")
    treatment_meta = metadata(treatment, "treatment")
    if control_meta != treatment_meta:
        raise ComparisonError("arms do not share the same suite, baseline SHA and candidate SHA")

    def by_repetition(rows: list[dict[str, Any]], label: str) -> dict[int, dict[str, Any]]:
        indexed: dict[int, dict[str, Any]] = {}
        for row in rows:
            repetition = row["metrics"]["repetition"]
            if repetition in indexed:
                raise ComparisonError(f"{label}: duplicate repetition {repetition}")
            indexed[repetition] = row
        return indexed

    c = by_repetition(control, "control")
    t = by_repetition(treatment, "treatment")
    if set(c) != set(t):
        raise ComparisonError("control and treatment must have identical repetition sets")
    repetitions = sorted(c)
    if len(repetitions) < min_pairs:
        raise ComparisonError(f"insufficient matched repetitions: {len(repetitions)} < preregistered minimum {min_pairs}")

    outcome_sign = 1.0 if outcome_direction == "higher" else -1.0
    outcome_control: list[float] = []
    outcome_treatment: list[float] = []
    cost_control: list[float] = []
    cost_treatment: list[float] = []
    guardrail_results: list[dict[str, Any]] = []
    for repetition in repetitions:
        label = f"repetition {repetition}"
        co = _number(c[repetition], outcome_key, f"control {label}")
        to = _number(t[repetition], outcome_key, f"treatment {label}")
        cc = _number(c[repetition], cost_key, f"control {label}")
        tc = _number(t[repetition], cost_key, f"treatment {label}")
        if cc < 0 or tc < 0:
            raise ComparisonError(f"{label}: resource cost cannot be negative")
        outcome_control.append(co)
        outcome_treatment.append(to)
        cost_control.append(cc)
        cost_treatment.append(tc)
        for key, minimum in guardrails:
            observed = _number(t[repetition], key, f"treatment {label}")
            guardrail_results.append({
                "repetition": repetition, "metric": key, "minimum": minimum,
                "observed": observed, "satisfied": observed >= minimum,
            })

    mean = lambda values: sum(values) / len(values)
    outcome_delta = outcome_sign * (mean(outcome_treatment) - mean(outcome_control))
    incremental_cost = mean(cost_treatment) - mean(cost_control)
    guardrails_pass = all(item["satisfied"] for item in guardrail_results)
    ratio = None
    ratio_reason = None
    if not guardrails_pass:
        ratio_reason = "one or more treatment guardrails failed"
    elif incremental_cost <= 0:
        ratio_reason = "incremental resource cost is zero or negative; ratio is not computable"
    else:
        ratio = outcome_delta / incremental_cost

    return {
        "schema": "l3verage-comparison/v1",
        "experiment_id": experiment_id,
        "cohort": cohort,
        "suite": control_meta[0],
        "baseline_sha": control_meta[1],
        "candidate_sha": control_meta[2],
        "arms": {
            "control": {"arm": control_arm, "instance_key": control_instance_key, "n": len(control)},
            "treatment": {"arm": treatment_arm, "instance_key": treatment_instance_key, "n": len(treatment)},
        },
        "matched_repetitions": repetitions,
        "outcome": {
            "metric": outcome_key, "direction": outcome_direction,
            "control_mean": mean(outcome_control), "treatment_mean": mean(outcome_treatment),
            "oriented_incremental_mean": outcome_delta,
        },
        "resource_cost": {
            "metric": cost_key, "unit": cost_unit,
            "control_mean": mean(cost_control), "treatment_mean": mean(cost_treatment),
            "incremental_mean": incremental_cost,
        },
        "guardrails": {"satisfied": guardrails_pass, "checks": guardrail_results},
        "leverage_ratio": ratio,
        "leverage_ratio_reason": ratio_reason,
        "interpretation": "descriptive comparison only; this report does not validate, promote, or change mechanism state",
        "promotion_authorized": False,
    }


def parse_guardrail(value: str) -> tuple[str, float]:
    match = GUARDRAIL_RE.fullmatch(value)
    if not match:
        raise argparse.ArgumentTypeError("guardrail must be METRIC>=MINIMUM")
    return match.group(1), float(match.group(2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path, help="canonical DoE EXPERIMENT JSONL file")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--control-arm", required=True)
    parser.add_argument("--treatment-arm", required=True)
    parser.add_argument("--control-instance-key", required=True)
    parser.add_argument("--treatment-instance-key", required=True)
    parser.add_argument("--outcome-key", required=True, help="numeric key in EXPERIMENT metrics")
    parser.add_argument("--outcome-direction", choices=("higher", "lower"), required=True)
    parser.add_argument("--cost-key", required=True, help="numeric resource-cost key in EXPERIMENT metrics")
    parser.add_argument("--cost-unit", required=True)
    parser.add_argument("--min-pairs", type=int, required=True, help="pre-registered minimum matched repetitions")
    parser.add_argument("--guardrail", action="append", type=parse_guardrail, default=[], metavar="METRIC>=MIN")
    args = parser.parse_args()
    if args.min_pairs < 1:
        parser.error("--min-pairs must be at least 1")
    try:
        report = compare_records(
            load_jsonl(args.records), experiment_id=args.experiment_id, cohort=args.cohort,
            control_arm=args.control_arm, treatment_arm=args.treatment_arm,
            control_instance_key=args.control_instance_key,
            treatment_instance_key=args.treatment_instance_key,
            outcome_key=args.outcome_key, outcome_direction=args.outcome_direction,
            cost_key=args.cost_key, cost_unit=args.cost_unit, min_pairs=args.min_pairs,
            guardrails=args.guardrail,
        )
    except (OSError, ComparisonError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
