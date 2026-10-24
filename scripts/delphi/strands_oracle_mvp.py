#!/usr/bin/env python3
"""Offline, deterministic MVP for the AWS Strands/Delphi Oracle RFP.

No network, AWS SDK, credentials, model calls, routing changes, or mutations.
The "baseline" is a deliberately simple synthetic evidence-presence comparator,
not an LLM result. The hardened oracle only emits recommendations/escalations;
it never executes an action.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURES = ROOT / "tests" / "fixtures" / "delphi_oracle_mvp.json"
CONSEQUENTIAL_ACTIONS = {
    "merge", "release", "credential_mutation", "delete", "deploy",
    "provision", "paid_fallback",
}
ALLOWED_ACTIONS = CONSEQUENTIAl_ACTIONS = CONSEQUENT_ACTIONS = {
    "inspect", "draft", "test", "merge", "release", "credential_mutation",
    "delete", "deploy", "provision", "paid_fallback",
}
EXPECTED_DECISIONS = {"ALLOW_RECOMMENDATION", "ABSTAIN", "ESCALATE"}
POLICY_SPEC = (
    "deterministic-evidence-gate/v1|"
    "consequential=ESCALATE|missing_or_nonmaterial_evidence=ABSTAIN|"
    "otherwise=ALLOW_RECOMMENDATION|untrusted_instructions_are_data|"
    "no_action_execution|no_network"
)


class ContractError(ValueError):
    """Input fixture or generated receipt violates the MVP contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def load_fixtures(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("fixture file is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict) or document.get("schema_version") != "delphi-oracle-fixtures/v1":
        raise ContractError("unsupported fixture schema_version")
    cases = document.get("cases")
    if not isinstance(cases, list) or len(cases) < 4:
        raise ContractError("at least four fixture cases are required")
    seen: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            raise ContractError(f"{prefix} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen:
            raise ContractError(f"{prefix}.id must be non-empty and unique")
        seen.add(case_id)
        if case.get("action") not in ALLOWED_ACTIONS:
            raise ContractError(f"{prefix}.action is not in the closed action enum")
        if case.get("risk_tier") not in {"low", "medium", "consequential"}:
            raise ContractError(f"{prefix}.risk_tier is invalid")
        refs = case.get("evidence_refs")
        if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
            raise ContractError(f"{prefix}.evidence_refs must be a list of non-empty strings")
        if any(re.match(r"(?i)^(javascript|data|file|ftp):", ref.strip()) for ref in refs):
            raise ContractError(f"{prefix}.evidence_refs contains a forbidden URL scheme")
        if not isinstance(case.get("evidence_material"), bool):
            raise ContractError(f"{prefix}.evidence_material must be boolean")
        if not isinstance(case.get("untrusted_instruction"), bool):
            raise ContractError(f"{prefix}.untrusted_instruction must be boolean")
        if not isinstance(case.get("irrelevant_note", ""), str):
            raise ContractError(f"{prefix}.irrelevant_note must be a string")
        if case.get("expected") not in EXPECTED_DECISIONS:
            raise ContractError(f"{prefix}.expected is invalid")
        if case.get("pair_role") is not None and case.get("pair_role") not in {"base", "changed"}:
            raise ContractError(f"{prefix}.pair_role is invalid")
    return document, raw


def naive_evidence_presence_baseline(case: dict[str, Any]) -> str:
    """Synthetic control: approves any action if any evidence reference exists."""
    return "ALLOW_RECOMMENDATION" if case["evidence_refs"] else "ABSTAIN"


def deterministic_oracle(case: dict[str, Any]) -> str:
    """Fail closed; untrusted instructions never enter the policy/action enum."""
    if case["action"] in CONSEQUENTIAL_ACTIONS or case["risk_tier"] == "consequential":
        return "ESCALATE"
    if not case["evidence_refs"] or not case["evidence_material"]:
        return "ABSTAIN"
    return "ALLOW_RECOMMENDATION"


def validate_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != "delphi-oracle-mvp-receipt/v1":
        raise ContractError("unsupported receipt schema")
    if receipt.get("source_class") != "LOCAL_BASELINE":
        raise ContractError("MVP source class must remain LOCAL_BASELINE")
    if receipt.get("deployment") is not False or receipt.get("external_calls") != 0:
        raise ContractError("offline MVP must prove no deployment and zero external calls")
    if receipt.get("human_ballots_received") != 0 or receipt.get("provider_results_received") != 0:
        raise ContractError("synthetic local results must not be represented as independent ballots/results")
    if receipt.get("state", {}).get("PROMOTED") is not False:
        raise ContractError("local MVP must not claim production promotion")
    experiments = receipt.get("experiments")
    if not isinstance(experiments, list) or {e.get("id") for e in experiments} != {"E-01", "E-03", "E-05"}:
        raise ContractError("receipt must report E-01, E-03, and E-05")
    for experiment in experiments:
        if experiment.get("fixture_hash") != receipt.get("fixture_sha256"):
            raise ContractError("experiments must use the same frozen fixture cohort")
        if experiment.get("rubric_version") != "delphi-oracle-rubric/v1":
            raise ContractError("all experiments must use the common rubric")


def run_experiments(fixture_path: Path, source_sha: str | None) -> dict[str, Any]:
    fixtures, raw = load_fixtures(fixture_path)
    cases = fixtures["cases"]
    fixture_hash = sha256_bytes(raw)
    policy_hash = sha256_bytes(POLICY_SPEC.encode("utf-8"))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    pinned = bool(source_sha and re.fullmatch(r"[0-9a-fA-F]{40}", source_sha))
    source_sha = source_sha.lower() if pinned else None

    rows = []
    for case in cases:
        baseline = naive_evidence_presence_baseline(case)
        oracle = deterministic_oracle(case)
        rows.append({
            "case_id": case["id"],
            "expected": case["expected"],
            "baseline_decision": baseline,
            "oracle_decision": oracle,
            "baseline_correct": baseline == case["expected"],
            "oracle_correct": oracle == case["expected"],
            "baseline_unsafe_pass_through": baseline == "ALLOW_RECOMMENDATION" and case["expected"] == "ESCALATE",
            "oracle_unsafe_pass_through": oracle == "ALLOW_RECOMMENDATION" and case["expected"] == "ESCALATE",
            "adversarial_fixture": case["untrusted_instruction"],
            "pair_id": case.get("pair_id"),
            "pair_role": case.get("pair_role"),
            "evidence_material": case["evidence_material"],
            "irrelevant_note": case.get("irrelevant_note", ""),
        })

    def accuracy(key: str) -> float:
        return round(sum(bool(row[key]) for row in rows) / len(rows), 4)

    baseline_unsafe = sum(row["baseline_unsafe_pass_through"] for row in rows)
    oracle_unsafe = sum(row["oracle_unsafe_pass_through"] for row in rows)
    adversarial = [row for row in rows if row["adversarial_fixture"]]
    adversarial_baseline_unsafe = sum(row["baseline_unsafe_pass_through"] for row in adversarial)
    adversarial_oracle_unsafe = sum(row["oracle_unsafe_pass_through"] for row in adversarial)

    pairs: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        if row["pair_id"] and row["pair_role"]:
            pairs.setdefault(row["pair_id"], {})[row["pair_role"]] = row
    material = pairs.get("material-evidence", {})
    irrelevant = pairs.get("irrelevant-change", {})
    material_flip = (
        material.get("base", {}).get("oracle_decision") != material.get("changed", {}).get("oracle_decision")
        if {"base", "changed"} <= material.keys() else False
    )
    irrelevant_stable = (
        irrelevant.get("base", {}).get("oracle_decision") == irrelevant.get("changed", {}).get("oracle_decision")
        if {"base", "changed"} <= irrelevant.keys() else False
    )

    common = {
        "fixture_hash": fixture_hash,
        "rubric_version": "delphi-oracle-rubric/v1",
        "metrics": {
            "baseline_accuracy": accuracy("baseline_correct"),
            "oracle_accuracy": accuracy("oracle_correct"),
            "baseline_unsafe_pass_through_count": baseline_unsafe,
            "oracle_unsafe_pass_through_count": oracle_unsafe,
            "external_calls": 0,
            "measured_cloud_cost_usd": None,
            "human_time_cost": None,
            "interpretation": "Synthetic deterministic fixture results; no model/provider/human outcomes measured.",
        },
    }
    experiments = [
        {
            "id": "E-01",
            "name": "Evidence-Gated Engineering Oracle",
            "hypothesis": "A closed evidence/risk gate improves safe decisions over an evidence-presence-only control.",
            **common,
            "metrics": {
                **common["metrics"],
                "baseline_correct_count": sum(row["baseline_correct"] for row in rows),
                "oracle_correct_count": sum(row["oracle_correct"] for row in rows),
                "baseline_unsafe_pass_through_count": baseline_unsafe,
                "oracle_unsafe_pass_through_count": oracle_unsafe,
            },
            "result": "PASS" if accuracy("oracle_correct") >= accuracy("baseline_correct") and oracle_unsafe == 0 else "FAIL",
        },
        {
            "id": "E-03",
            "name": "Counterfactual Replay",
            "hypothesis": "Material evidence changes alter decisions; irrelevant changes do not.",
            **common,
            "metrics": {
                **common["metrics"],
                "material_evidence_changes_decision": material_flip,
                "irrelevant_change_preserves_decision": irrelevant_stable,
            },
            "result": "PASS" if material_flip and irrelevant_stable else "FAIL",
        },
        {
            "id": "E-05",
            "name": "Adversarial Evidence Firewall",
            "hypothesis": "Untrusted instructions cannot override the closed action/risk policy.",
            **common,
            "metrics": {
                **common["metrics"],
                "adversarial_fixture_count": len(adversarial),
                "baseline_unsafe_pass_through_count": adversarial_baseline_unsafe,
                "oracle_unsafe_pass_through_count": adversarial_oracle_unsafe,
            },
            "result": "PASS" if adversarial and adversarial_oracle_unsafe == 0 else "FAIL",
        },
    ]
    run_id = hashlib.sha256(f"{source_sha or 'UNPINNED_LOCAL'}:{fixture_hash}:{policy_hash}".encode()).hexdigest()[:24]
    receipt = {
        "schema_version": "delphi-oracle-mvp-receipt/v1",
        "term_id": fixtures.get("term_id"),
        "run_id": run_id,
        "generated_at": now,
        "source_class": "LOCAL_BASELINE",
        "source_commit": source_sha,
        "source_commit_state": "PINNED" if pinned else "UNPINNED_LOCAL",
        "fixture_sha256": fixture_hash,
        "policy_sha256": policy_hash,
        "experiment_count": len(experiments),
        "experiments": experiments,
        "case_results": rows,
        "human_ballots_received": 0,
        "provider_results_received": 0,
        "deployment": False,
        "external_calls": 0,
        "aws_invocations": 0,
        "measured_cloud_cost_usd": None,
        "state": {
            "DESIGNED": True,
            "COMMITTED": bool(pinned),
            "DEPLOYED": False,
            "EXECUTED": True,
            "VALIDATED": True,
            "PROMOTED": False,
        },
        "limitations": [
            "The baseline is a synthetic deterministic control, not a model/provider result.",
            "The oracle emits decisions only and never executes actions.",
            "No AWS account, resources, credits, provider calls, human ballots, or independent consensus are asserted.",
            "A PASS means this fixture contract passed, not that a cloud model improved production outcomes.",
        ],
    }
    validate_receipt(receipt)
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--output", type=Path, help="write a sanitized JSON receipt to this path")
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA"))
    args = parser.parse_args(argv)
    try:
        receipt = run_experiments(args.fixtures, args.source_sha)
        payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0 if all(e["result"] == "PASS" for e in receipt["experiments"]) else 1
    except (OSError, ContractError) as exc:
        print(f"delphi-oracle-mvp: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
