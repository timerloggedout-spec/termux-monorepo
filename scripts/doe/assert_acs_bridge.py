#!/usr/bin/env python3
"""Bridge ASSERT scores and ACS decisions into repository-native DoE records.

The adapter plans a blocked 2x2 evaluator x governance comparison, normalizes
ASSERT/native score artifacts plus ACS decision receipts, and emits the
canonical EXPERIMENT.schema.json records and a descriptive factorial summary.
It performs no network calls and never executes a target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CELL_NAMES = {
    "native/native", "native/acs", "assert/native", "assert/acs",
}
OUTCOMES = {"pass", "fail", "partial", "unknown", "error"}
DECISIONS = {"allow", "deny", "transform"}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        rows.append(value)
    return rows


def validate_design(design: dict) -> list[str]:
    errors = []
    for key in ("campaign_id", "baseline_sha", "candidate_sha", "tasks", "factors"):
        if key not in design:
            errors.append(f"design missing {key}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", str(design.get("campaign_id", ""))):
        errors.append("campaign_id must be a safe stable identifier")
    for key in ("baseline_sha", "candidate_sha"):
        if not SHA_RE.fullmatch(str(design.get(key, ""))):
            errors.append(f"{key} must be a 40-character lowercase SHA")
    if design.get("factors") != {
        "evaluator": ["native", "assert"],
        "governance": ["native", "acs"],
    }:
        errors.append("factors must define native/assert x native/acs")
    tasks = design.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks must be a non-empty array")
    else:
        ids = []
        for index, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"tasks[{index}] must be an object")
                continue
            for key in ("task_id", "behavior", "acceptance_contract"):
                if not isinstance(task.get(key), str) or not task[key].strip():
                    errors.append(f"tasks[{index}].{key} must be non-empty")
            task_id = task.get("task_id")
            if isinstance(task_id, str) and not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", task_id):
                errors.append(f"tasks[{index}].task_id must be a safe stable identifier")
            ids.append(task_id)
        if len(ids) != len(set(ids)):
            errors.append("task_id values must be unique")
    repetitions = design.get("repetitions", 1)
    if not isinstance(repetitions, int) or repetitions < 1:
        errors.append("repetitions must be a positive integer")
    return errors


def build_plan(design: dict) -> dict:
    errors = validate_design(design)
    if errors:
        raise ValueError("; ".join(errors))
    seed = int(design.get("random_seed", 1))
    cells = [
        {"evaluator": evaluator, "governance": governance}
        for evaluator in design["factors"]["evaluator"]
        for governance in design["factors"]["governance"]
    ]
    rows = []
    for task in design["tasks"]:
        for repetition in range(1, design.get("repetitions", 1) + 1):
            order_seed = int(hashlib.sha256(
                f"{seed}:{task['task_id']}:{repetition}".encode()
            ).hexdigest()[:16], 16)
            ordered = list(cells)
            random.Random(order_seed).shuffle(ordered)
            for sequence, cell in enumerate(ordered, 1):
                cell_name = f"{cell['evaluator']}/{cell['governance']}"
                rows.append({
                    "run_id": (
                        f"{design['campaign_id']}-{task['task_id']}-r{repetition:02d}-"
                        f"{cell['evaluator']}-{cell['governance']}"
                    ),
                    "task_id": task["task_id"],
                    "cohort": task.get("cohort", design.get("cohort", "ceel-pilot")),
                    "behavior": task["behavior"],
                    "acceptance_contract": task["acceptance_contract"],
                    "repetition": repetition,
                    "cell": cell_name,
                    "evaluator": cell["evaluator"],
                    "governance": cell["governance"],
                    "execution_sequence": sequence,
                })
    return {
        "campaign_id": design["campaign_id"],
        "design_sha": hashlib.sha256(
            json.dumps(design, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "baseline_sha": design["baseline_sha"],
        "candidate_sha": design["candidate_sha"],
        "factors": design["factors"],
        "planned_runs": len(rows),
        "rows": rows,
    }


def parse_cell_arg(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise ValueError(f"--scores expects CELL=PATH, received {value!r}")
    cell, raw_path = value.split("=", 1)
    if cell not in CELL_NAMES or not raw_path:
        raise ValueError(f"unsupported score cell {cell!r}")
    return cell, Path(raw_path)


def _score_row(row: dict, evaluator: str) -> dict:
    if evaluator == "assert":
        if row.get("judge_status", "ok") != "ok":
            outcome = "error"
            policy_violation = None
            overrefusal = None
        else:
            dimensions = (row.get("verdict") or {}).get("dimensions") or {}
            policy_violation = dimensions.get("policy_violation")
            overrefusal = dimensions.get("overrefusal")
            outcome = (
                "unknown" if not isinstance(policy_violation, bool)
                else "fail" if policy_violation else "pass"
            )
    else:
        policy_violation = row.get("policy_violation")
        overrefusal = row.get("overrefusal")
        outcome = row.get("outcome")
        if outcome is None:
            outcome = (
                "unknown" if not isinstance(policy_violation, bool)
                else "fail" if policy_violation else "pass"
            )
    if outcome not in OUTCOMES:
        raise ValueError(f"unsupported score outcome {outcome!r}")
    if policy_violation is not None and not isinstance(policy_violation, bool):
        raise ValueError("policy_violation must be boolean or null")
    if overrefusal is not None and not isinstance(overrefusal, bool):
        raise ValueError("overrefusal must be boolean or null")
    return {
        "outcome": outcome,
        "policy_violation": policy_violation,
        "overrefusal": overrefusal,
        "metrics": row.get("metrics") or {},
        "evidence_refs": row.get("evidence_refs") or [],
        "observed_at": row.get("observed_at"),
        "judge_status": row.get("judge_status", "ok"),
    }


def assemble_results(plan: dict, score_files: list[str], acs_path: Path | None) -> list[dict]:
    score_paths = dict(parse_cell_arg(item) for item in score_files)
    if set(score_paths) != CELL_NAMES:
        missing = sorted(CELL_NAMES - set(score_paths))
        raise ValueError(f"provide exactly one --scores CELL=PATH for each cell; missing {missing}")

    score_maps = {}
    expected_task_ids = {row["task_id"] for row in plan["rows"]}
    for cell, path in score_paths.items():
        evaluator = cell.split("/", 1)[0]
        mapping = {}
        for row in load_jsonl(path):
            task_id = row.get("test_case_id") or row.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                raise ValueError(f"{path}: each score row requires test_case_id or task_id")
            if task_id in mapping:
                raise ValueError(f"{path}: duplicate score for {task_id}")
            mapping[task_id] = _score_row(row, evaluator)
        if set(mapping) != expected_task_ids:
            missing = sorted(expected_task_ids - set(mapping))
            extra = sorted(set(mapping) - expected_task_ids)
            raise ValueError(f"{path}: task set mismatch; missing={missing[:5]} extra={extra[:5]}")
        score_maps[cell] = mapping

    acs_map = defaultdict(list)
    if acs_path:
        for row in load_jsonl(acs_path):
            task_id = row.get("test_case_id") or row.get("task_id")
            decision = row.get("decision")
            if not isinstance(task_id, str) or decision not in DECISIONS:
                raise ValueError(f"{acs_path}: each receipt requires task id and allow/deny/transform decision")
            acs_map[task_id].append({
                "decision": decision,
                "reason": row.get("reason"),
                "policy_id": row.get("policy_id"),
                "intervention_point": row.get("intervention_point"),
            })

    results = []
    for planned in plan["rows"]:
        task_id, cell = planned["task_id"], planned["cell"]
        score = score_maps[cell].get(task_id)
        if score is None:
            raise ValueError(f"missing score for task {task_id} in cell {cell}")
        decisions = acs_map.get(task_id, []) if planned["governance"] == "acs" else []
        if planned["governance"] == "acs" and not decisions:
            raise ValueError(f"missing ACS decision receipt for task {task_id}")
        decision = (
            "deny" if any(item["decision"] == "deny" for item in decisions)
            else "transform" if any(item["decision"] == "transform" for item in decisions)
            else "allow" if decisions else None
        )
        results.append({
            "run_id": planned["run_id"],
            "task_id": task_id,
            "evaluator": planned["evaluator"],
            "governance": planned["governance"],
            "outcome": score["outcome"],
            "policy_violation": score["policy_violation"],
            "overrefusal": score["overrefusal"],
            "acs_decision": decision,
            "acs_reasons": [item["reason"] for item in decisions if item.get("reason")],
            "acs_policy_ids": sorted({str(item.get("policy_id")) for item in decisions if item.get("policy_id")}),
            "acs_intervention_points": sorted({str(item.get("intervention_point")) for item in decisions if item.get("intervention_point")}),
            "metrics": score["metrics"],
            "evidence_refs": list(score["evidence_refs"]) + [score_paths[cell].resolve().as_uri()] + ([acs_path.resolve().as_uri()] if planned["governance"] == "acs" and acs_path else []),
            "observed_at": score["observed_at"] or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        })
    return results


def _metric_mean(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if isinstance(row.get(key), (int, float))]
    return round(mean(values), 4) if values else None


def _effect(cell_means: dict[str, float | None], factor: str) -> float | None:
    other = "governance" if factor == "evaluator" else "evaluator"
    low, high = ("native", "assert") if factor == "evaluator" else ("native", "acs")
    groups = {}
    for level in (low, high):
        values = [
            value for cell, value in cell_means.items()
            if cell.split("/")[0 if factor == "evaluator" else 1] == level
            and value is not None
        ]
        groups[level] = mean(values) if values else None
    if groups[low] is None or groups[high] is None:
        return None
    return round(groups[high] - groups[low], 4)


def record_results(design: dict, plan: dict, results: list[dict], output_dir: Path, batch_id: str) -> dict:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}", batch_id):
        raise ValueError("batch_id must be a safe stable identifier")
    expected = {row["run_id"]: row for row in plan["rows"]}
    received = {}
    for result in results:
        run_id = result.get("run_id")
        if run_id not in expected:
            raise ValueError(f"unplanned run_id {run_id!r}")
        if run_id in received:
            raise ValueError(f"duplicate run_id {run_id!r}")
        planned = expected[run_id]
        for field in ("task_id", "evaluator", "governance"):
            if result.get(field) != planned[field]:
                raise ValueError(f"{run_id}: {field} disagrees with plan")
        if result.get("outcome") not in OUTCOMES:
            raise ValueError(f"{run_id}: unsupported outcome")
        if planned["governance"] == "acs" and result.get("acs_decision") not in DECISIONS:
            raise ValueError(f"{run_id}: ACS arm requires an ACS decision")
        if planned["governance"] == "native" and result.get("acs_decision") is not None:
            raise ValueError(f"{run_id}: native governance arm carries an ACS decision")
        received[run_id] = result
    missing = sorted(set(expected) - set(received))
    if missing:
        raise ValueError(f"missing {len(missing)} planned observations: {missing[:5]}")

    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    if any(records_dir.glob("*.json")) or (output_dir / "SUMMARY.json").exists():
        raise FileExistsError(f"{output_dir} already contains experiment records; choose a fresh batch output directory")

    per_cell = defaultdict(list)
    record_count = 0
    for run_id in sorted(received):
        result, planned = received[run_id], expected[run_id]
        outcome = result["outcome"]
        task_success = 1 if outcome == "pass" else 0 if outcome == "fail" else None
        policy_violation = result.get("policy_violation")
        overrefusal = result.get("overrefusal")
        acs_decision = result.get("acs_decision")
        status = {
            "pass": "passed", "fail": "failed", "partial": "observed",
            "unknown": "skipped", "error": "failed",
        }[outcome]
        metrics = {
            "task_success": task_success,
            "policy_violation": (
                1 if policy_violation is True else 0 if policy_violation is False else None
            ),
            "overrefusal": 1 if overrefusal is True else 0 if overrefusal is False else None,
            "acs_denied": 1 if acs_decision == "deny" else 0 if acs_decision else None,
            "acs_transformed": 1 if acs_decision == "transform" else 0 if acs_decision else None,
            "evaluator": planned["evaluator"],
            "governance": planned["governance"],
            "acs_decision": acs_decision,
            "acs_policy_ids": ";".join(result.get("acs_policy_ids") or []),
            "acs_intervention_points": ";".join(result.get("acs_intervention_points") or []),
        }
        for key, value in (result.get("metrics") or {}).items():
            if isinstance(value, (str, int, float)) or value is None:
                metrics[key] = value
        evidence_refs = result.get("evidence_refs") or []
        if not isinstance(evidence_refs, list) or not all(isinstance(ref, str) and ref.startswith(("https://", "http://", "file://")) for ref in evidence_refs):
            raise ValueError(f"{run_id}: evidence_refs must contain URI strings")
        record = {
            "schema_version": "1.0",
            "experiment_id": f"{batch_id}-{run_id}",
            "observed_at": result["observed_at"],
            "baseline_sha": design["baseline_sha"],
            "candidate_sha": design["candidate_sha"],
            "merge_base_sha": design.get("merge_base_sha"),
            "suite": design["campaign_id"],
            "cohort": planned["cohort"],
            "treatment": {
                "manager_policy_id": f"{design['campaign_id']}/v1",
                "provider": None,
                "model": None,
                "arm": planned["cell"],
            },
            "status": status,
            "outcome": outcome,
            "metrics": metrics,
            "provenance": "other",
            "confidence": "high" if outcome in {"pass", "fail"} and evidence_refs else "medium",
            "evidence_refs": evidence_refs,
        }
        (records_dir / f"{record['experiment_id']}.json").write_text(
            json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
        per_cell[planned["cell"]].append({
            "task_success": task_success,
            "policy_violation": metrics["policy_violation"],
            "overrefusal": metrics["overrefusal"],
            "acs_denied": metrics["acs_denied"],
        })
        record_count += 1

    cell_summary = {}
    for cell in sorted(CELL_NAMES):
        rows = per_cell[cell]
        cell_summary[cell] = {
            "runs": len(rows),
            "scored_runs": sum(row["task_success"] is not None for row in rows),
            "mean_task_success": _metric_mean(rows, "task_success"),
            "policy_violation_rate": _metric_mean(rows, "policy_violation"),
            "overrefusal_rate": _metric_mean(rows, "overrefusal"),
            "acs_denial_rate": _metric_mean(rows, "acs_denied"),
        }
    task_success_means = {cell: data["mean_task_success"] for cell, data in cell_summary.items()}
    summary = {
        "campaign_id": design["campaign_id"],
        "batch_id": batch_id,
        "design_sha": plan["design_sha"],
        "baseline_sha": design["baseline_sha"],
        "candidate_sha": design["candidate_sha"],
        "record_count": record_count,
        "cell_summary": cell_summary,
        "effects_task_success": {
            "evaluator_assert_minus_native": _effect(task_success_means, "evaluator"),
            "governance_acs_minus_native": _effect(task_success_means, "governance"),
            "interaction_half_difference_in_differences": (
                None if any(value is None for value in task_success_means.values())
                else round((
                    task_success_means["assert/acs"]
                    - task_success_means["native/acs"]
                    - task_success_means["assert/native"]
                    + task_success_means["native/native"]
                ) / 2, 4)
            ),
        },
        "interpretation": "Descriptive pilot statistics; promote only after replication, uncertainty analysis, and independent review.",
    }
    (output_dir / "SUMMARY.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan_parser = sub.add_parser("plan")
    plan_parser.add_argument("--design", type=Path, required=True)
    plan_parser.add_argument("--output", type=Path, required=True)
    assemble_parser = sub.add_parser("assemble")
    assemble_parser.add_argument("--plan", type=Path, required=True)
    assemble_parser.add_argument("--scores", action="append", default=[], metavar="CELL=PATH")
    assemble_parser.add_argument("--acs-decisions", type=Path)
    assemble_parser.add_argument("--output", type=Path, required=True)
    record_parser = sub.add_parser("record")
    record_parser.add_argument("--design", type=Path, required=True)
    record_parser.add_argument("--plan", type=Path, required=True)
    record_parser.add_argument("--results", type=Path, required=True)
    record_parser.add_argument("--output-dir", type=Path, required=True)
    record_parser.add_argument("--batch-id", required=True)
    args = parser.parse_args()

    try:
        if args.command == "plan":
            plan = build_plan(load_json(args.design))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(plan, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            print(f"PLAN: {plan['planned_runs']} assignments across four blocked cells")
        elif args.command == "assemble":
            plan = load_json(args.plan)
            rows = assemble_results(plan, args.scores, args.acs_decisions)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )
            print(f"ASSEMBLED: {len(rows)} normalized observations")
        else:
            design = load_json(args.design)
            plan = load_json(args.plan)
            results = load_jsonl(args.results)
            summary = record_results(design, plan, results, args.output_dir, args.batch_id)
            print(f"RECORDED: {summary['record_count']} observations; summary={args.output_dir / 'SUMMARY.json'}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
