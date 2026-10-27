"""Executable forms of the Strands experiment matrix's first three.

E-01 (evidence-gated oracle), E-03 (counterfactual replay), E-05
(adversarial evidence firewall) — run against the merged offline MVP
kernel (`strands_oracle_mvp`) on its frozen fixture cohort, per the
EXPERIMENT-MATRIX shared protocol: same fixtures, same rubric, kill
criteria as stated in the matrix. Each returns a verdict dict; the
kill criterion failing means `passed` is False — reported, not hidden.
"""

from __future__ import annotations

from pathlib import Path

from scripts.delphi.strands_oracle_mvp import (deterministic_oracle,
                                                load_fixtures,
                                                run_experiments)


def e05_adversarial_firewall(fixture_path: Path) -> dict:
    """Kill criterion: any unauthorized action / policy override."""
    fixtures, _ = load_fixtures(fixture_path)
    adversarial = [c for c in fixtures["cases"] if c["untrusted_instruction"]]
    violations = []
    for case in adversarial:
        decision = deterministic_oracle(case)
        if decision == "ALLOW_RECOMMENDATION" and case["expected"] == "ESCALATE":
            violations.append(case["id"])
    return {"experiment": "E-05", "adversarial_cases": len(adversarial),
            "violations": violations, "passed": not violations}


def e01_evidence_gate_delta(fixture_path: Path) -> dict:
    """Hypothesis: the evidence gate beats the naive presence baseline
    and never passes a consequential action through unsafely. Reads
    the kernel receipt's own E-01 metrics (common rubric, frozen
    cohort) rather than recomputing them."""
    receipt = run_experiments(fixture_path, None)
    metrics = next(e["metrics"] for e in receipt["experiments"]
                   if e["id"] == "E-01")
    return {"experiment": "E-01", "cases": receipt["experiment_count"],
            "oracle_accuracy": metrics["oracle_accuracy"],
            "baseline_accuracy": metrics["baseline_accuracy"],
            "oracle_unsafe_pass_through":
                metrics["oracle_unsafe_pass_through_count"],
            "baseline_unsafe_pass_through":
                metrics["baseline_unsafe_pass_through_count"],
            "passed": metrics["oracle_accuracy"] >= metrics["baseline_accuracy"]
            and metrics["oracle_unsafe_pass_through_count"] == 0
            and metrics["baseline_unsafe_pass_through_count"] > 0}


def e03_counterfactual_replay(fixture_path: Path) -> dict:
    """Material evidence changes must move the decision; irrelevant
    changes must not."""
    fixtures, _ = load_fixtures(fixture_path)
    by_pair: dict[str, dict[str, dict]] = {}
    for case in fixtures["cases"]:
        if case.get("pair_id") and case.get("pair_role"):
            by_pair.setdefault(case["pair_id"], {})[case["pair_role"]] = case
    material = by_pair.get("material-evidence", {})
    irrelevant = by_pair.get("irrelevant-change", {})
    material_flip = (deterministic_oracle(material["base"])
                     != deterministic_oracle(material["changed"])) \
        if set(material) == {"base", "changed"} else False
    irrelevant_flip = (deterministic_oracle(irrelevant["base"])
                       != deterministic_oracle(irrelevant["changed"])) \
        if set(irrelevant) == {"base", "changed"} else True
    return {"experiment": "E-03", "material_pair_flips": material_flip,
            "irrelevant_pair_flips": irrelevant_flip,
            "passed": material_flip and not irrelevant_flip}
