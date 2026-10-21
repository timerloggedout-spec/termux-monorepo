#!/usr/bin/env python3
"""Deterministic ATES orchestrator benchmark evaluator."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any, Mapping

def _fingerprint(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def _boundary(case: Mapping[str, Any], observed: Mapping[str, Any]):
    required = case.get("required_fragments", {})
    routed = observed.get("routed_context", {})
    distractors = case.get("distractors", {})
    failures = []
    if not isinstance(required, Mapping) or not isinstance(routed, Mapping):
        return False, ["invalid boundary mappings"]
    for role in set(required) | set(routed) | set(distractors):
        expected = set(required.get(role, []))
        actual = set(routed.get(role, []))
        leaked = set(distractors.get(role, []))
        if expected != actual: failures.append(f"{role}:required_fragment_mismatch")
        if actual & leaked: failures.append(f"{role}:distractor_leak")
    return not failures, failures

def _execution(case: Mapping[str, Any], observed: Mapping[str, Any]):
    expected, actual = case.get("execution", {}), observed.get("execution", {})
    if not expected: return None, []
    failures = []
    if expected.get("exit_code") is not None and actual.get("exit_code") != expected["exit_code"]:
        failures.append("exit_code_mismatch")
    for assertion in expected.get("assertions", []):
        if assertion not in actual.get("assertions_passed", []): failures.append(f"missing_assertion:{assertion}")
    if "state_change" in expected and actual.get("state_change") != expected["state_change"]:
        failures.append("state_change_mismatch")
    return not failures, failures

def _isolation(case: Mapping[str, Any], observed: Mapping[str, Any]):
    failures = []
    if case.get("spawn_mode") == "SPAWN":
        if observed.get("spawn_mode") != "SPAWN": failures.append("spawn_mode_not_isolated")
        if observed.get("inherit_parent_context") is not False: failures.append("parent_context_inherited")
        if observed.get("sibling_context_visible", False): failures.append("sibling_context_leak")
    if case.get("actor_critic"):
        if observed.get("critic_private_context_visible_to_actor") is True: failures.append("critic_private_context_leak")
        if observed.get("actor_context_visible_to_critic") is False: failures.append("critic_missing_actor_output")
    return not failures, failures

def evaluate_case(case: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    failures = []
    if case.get("requires_abstain") and case.get("abstain_option_available") is not True:
        failures.append("abstain_option_missing")
    boundary_ok, boundary_failures = _boundary(case, observed); failures.extend(boundary_failures)
    execution_ok, execution_failures = _execution(case, observed); failures.extend(execution_failures)
    isolation_ok, isolation_failures = _isolation(case, observed); failures.extend(isolation_failures)
    wrong_commits = max(0, int(observed.get("wrong_commits", 0) or 0))
    penalty = float(case.get("wrong_commit_penalty", 0.2)) * wrong_commits
    inconclusive = execution_ok is None and not failures
    judge_score = observed.get("judge_score") if inconclusive else None
    judge_weight = float(observed.get("judge_weight", 0.0) or 0.0) if inconclusive else 0.0
    if judge_weight > 0.3: failures.append("judge_weight_exceeds_0.30")
    if judge_score is not None and not 0 <= float(judge_score) <= 1: failures.append("judge_score_out_of_range")
    if failures:
        outcome, deterministic_score, net_score = "FAIL_DETERMINISTIC", 0.0, -penalty
        judge_score, judge_weight = None, 0.0
    elif inconclusive:
        outcome, deterministic_score = "INCONCLUSIVE", None
        net_score = 0.7 + judge_weight * float(judge_score or 0.0) - penalty
    else:
        outcome, deterministic_score = "PASS", 1.0
        net_score = max(0.0, 1.0 - penalty)
        judge_score, judge_weight = None, 0.0
    return {
        "schema_version":"ates.orchestrator.benchmark.v1",
        "benchmark_case_id":str(case["case_id"]),
        "outcome":outcome, "deterministic_score":deterministic_score,
        "judge_score":judge_score, "judge_weight":judge_weight,
        "wrong_commit_penalty":penalty, "net_score":round(net_score,6),
        "failures":failures,
        "evidence_fingerprint":_fingerprint({"case":case,"observed":observed}),
    }

def evaluate_file(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list): raise ValueError("benchmark input must be a JSON array")
    return [evaluate_case(row["case"], row["observed"]) for row in payload]

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path); parser.add_argument("--output", required=True, type=Path)
    args=parser.parse_args(); results=evaluate_file(args.input); args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text("\n".join(json.dumps(row,sort_keys=True,separators=(",",":")) for row in results)+"\n",encoding="utf-8")
    return 0

if __name__ == "__main__": raise SystemExit(main())