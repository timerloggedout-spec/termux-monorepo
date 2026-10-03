#!/usr/bin/env python3
"""Deterministic Delphic Bayesian workflow over canonical evidence.

This is a research projection layer. It does not admit providers, emit telemetry,
approve changes, or replace the repository evidence ledger.
"""

from __future__ import annotations
import json, math, sys
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class Belief:
    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def sd(self) -> float:
        n = self.alpha + self.beta
        return math.sqrt(self.alpha * self.beta / (n*n*(n+1.0)))

    @property
    def interval95_approx(self) -> list[float]:
        # A conservative normal approximation is explicitly labeled approximate.
        half = 1.96 * self.sd
        return [max(0.0, self.mean-half), min(1.0, self.mean+half)]

def posterior(observations: list[dict[str, Any]], prior: Belief=Belief()) -> tuple[Belief, dict[str, int]]:
    seen: set[str] = set()
    successes = failures = 0
    belief = prior
    for row in observations:
        if row.get("executed") is not True or row.get("attributed") is not True:
            continue
        exp_id = row.get("experiment_id")
        if exp_id and exp_id in seen:
            continue
        if exp_id:
            seen.add(exp_id)
        outcome = row.get("outcome")
        if outcome is True:
            belief = Belief(belief.alpha + 1.0, belief.beta); successes += 1
        elif outcome is False:
            belief = Belief(belief.alpha, belief.beta + 1.0); failures += 1
    return belief, {"successes": successes, "failures": failures, "ignored": len(observations)-successes-failures}

def evi(current_expected_utility: float, expected_post_experiment_utility: float, experiment_cost: float) -> float:
    return expected_post_experiment_utility - current_expected_utility - experiment_cost

def adversarial_admission(*, interval_width: float, benchmark_regression: bool=False,
                          anomaly_density: float=0.0, provenance_gap: float=0.0,
                          change_point: bool=False, decision_impact: float=0.0) -> str:
    # Explicitly an admission heuristic, not a reviewer score.
    triggers = sum([
        interval_width >= 0.30,
        benchmark_regression,
        anomaly_density >= 0.20,
        provenance_gap >= 0.25,
        change_point,
        decision_impact >= 0.70,
    ])
    if triggers >= 2 or decision_impact >= 0.90:
        return "required"
    if triggers == 1:
        return "advisory"
    return "not_admitted"

def workflow(payload: dict[str, Any]) -> dict[str, Any]:
    observations = payload.get("observations", [])
    belief, counts = posterior(observations)
    interval = belief.interval95_approx
    review = adversarial_admission(
        interval_width=interval[1]-interval[0],
        benchmark_regression=bool(payload.get("benchmark_regression", False)),
        anomaly_density=float(payload.get("anomaly_density", 0.0)),
        provenance_gap=float(payload.get("provenance_gap", 0.0)),
        change_point=bool(payload.get("change_point", False)),
        decision_impact=float(payload.get("decision_impact", 0.0)),
    )
    left = {
        "tensor": {"axes": ["time", "task_family", "provider", "metric"], "observations": len(observations)},
        "graph": {"nodes": len({x.get("event_id") for x in observations if x.get("event_id")}), "edges": "derived"},
        "matrix": {"rows": "state/cohort", "columns": "outcome/metric"},
        "constellation": {"entities": sorted({x.get("provider") for x in observations if x.get("provider")})},
    }
    right = {
        "dag": {"edges": ["hypothesis→treatment", "treatment→observation", "observation→outcome"]},
        "trellis": {"states": ["unknown", "candidate", "observed", "validated", "decision"]},
        "markov": {"transition_semantics": "explicit transition probabilities only"},
    }
    return {
        "schema_version": "1.0",
        "posterior": {"belief": asdict(belief), "mean": belief.mean, "sd": belief.sd,
                      "credible_interval_95_approx": interval, "counts": counts},
        "adversarial_review": {"admission": review},
        "left_now": left,
        "right_interthreading": right,
        "authority": {
            "canonical_evidence": True,
            "observatory_read_only": True,
            "promotion_authority": False,
            "routing_admission_authority": False,
        },
    }

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: delphic_oracle.py INPUT.json", file=sys.stderr); return 2
    with open(sys.argv[1], encoding="utf-8") as fh:
        payload=json.load(fh)
    json.dump(workflow(payload), sys.stdout, indent=2); sys.stdout.write("\n"); return 0

if __name__ == "__main__":
    raise SystemExit(main())
