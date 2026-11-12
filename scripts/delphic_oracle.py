#!/usr/bin/env python3
"""Deterministic Delphic Bayesian workflow over canonical evidence.

Research projection layer only. It does not admit providers, emit telemetry,
approve changes, or replace the repository evidence ledger.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, asdict
from typing import Any

from scripts.delphic_math import (
    beta_entropy,
    one_step_information_gain,
    posterior_predictive_probability,
    posterior_predictive_variance,
    posterior_predictive_mean,
    evsi_binary_decision,
)


_BETA_EPS = 3e-30
_BETA_MAX_ITER = 200
_BETA_TOL = 3e-14
_QUANTILE_ITERS = 100


def _beta_continued_fraction(a: float, b: float, x: float) -> float:
    """Lentz-style continued fraction for the regularized incomplete beta."""
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _BETA_EPS:
        d = _BETA_EPS
    d = 1.0 / d
    h = d
    for iteration in range(1, _BETA_MAX_ITER + 1):
        m2 = 2 * iteration
        aa = iteration * (b - iteration) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _BETA_EPS:
            d = _BETA_EPS
        c = 1.0 + aa / c
        if abs(c) < _BETA_EPS:
            c = _BETA_EPS
        d = 1.0 / d
        h *= d * c

        aa = -(a + iteration) * (qab + iteration) * x / (
            (a + m2) * (qap + m2)
        )
        d = 1.0 + aa * d
        if abs(d) < _BETA_EPS:
            d = _BETA_EPS
        c = 1.0 + aa / c
        if abs(c) < _BETA_EPS:
            c = _BETA_EPS
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _BETA_TOL:
            break
    return h


def _regularized_beta(a: float, b: float, x: float) -> float:
    if not (a > 0.0 and b > 0.0):
        raise ValueError("beta shape parameters must be positive")
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    log_beta_density = (
        math.lgamma(a + b)
        - math.lgamma(a)
        - math.lgamma(b)
        + a * math.log(x)
        + b * math.log1p(-x)
    )
    factor = math.exp(log_beta_density)
    if x < (a + 1.0) / (a + b + 2.0):
        return factor * _beta_continued_fraction(a, b, x) / a
    return 1.0 - factor * _beta_continued_fraction(b, a, 1.0 - x) / b


def _beta_quantile(probability: float, a: float, b: float) -> float:
    if not 0.0 < probability < 1.0:
        raise ValueError("quantile probability must be between 0 and 1")
    lo, hi = 0.0, 1.0
    for _ in range(_QUANTILE_ITERS):
        mid = (lo + hi) / 2.0
        if _regularized_beta(a, b, mid) < probability:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


@dataclass(frozen=True)
class Belief:
    alpha: float = 1.0
    beta: float = 1.0

    def __post_init__(self) -> None:
        if not all(math.isfinite(x) and x > 0.0 for x in (self.alpha, self.beta)):
            raise ValueError("beta shape parameters must be finite and positive")

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def sd(self) -> float:
        n = self.alpha + self.beta
        return math.sqrt(self.alpha * self.beta / (n * n * (n + 1.0)))

    @property
    def interval95(self) -> list[float]:
        """Exact equal-tail 95% credible interval for the Beta posterior."""
        return [_beta_quantile(0.025, self.alpha, self.beta),
                _beta_quantile(0.975, self.alpha, self.beta)]

    @property
    def interval95_approx(self) -> list[float]:
        """Backward-compatible normal approximation; not the primary interval."""
        half = 1.96 * self.sd
        return [max(0.0, self.mean - half), min(1.0, self.mean + half)]


def posterior(
    observations: list[dict[str, Any]], prior: Belief = Belief()
) -> tuple[Belief, dict[str, int]]:
    seen: set[str] = set()
    successes = failures = 0
    belief = prior
    for row in observations:
        if row.get("executed") is not True or row.get("attributed") is not True:
            continue
        outcome = row.get("outcome")
        if type(outcome) is not bool:
            continue
        exp_id = row.get("experiment_id")
        if not exp_id:
            continue
        if exp_id in seen:
            continue
        seen.add(exp_id)
        if outcome is True:
            belief = Belief(belief.alpha + 1.0, belief.beta)
            successes += 1
        else:
            belief = Belief(belief.alpha, belief.beta + 1.0)
            failures += 1
    return belief, {
        "successes": successes,
        "failures": failures,
        "ignored": len(observations) - successes - failures,
    }


def evi(
    current_expected_utility: float,
    expected_post_experiment_utility: float,
    experiment_cost: float,
) -> float:
    values = (
        current_expected_utility,
        expected_post_experiment_utility,
        experiment_cost,
    )
    if not all(math.isfinite(x) for x in values):
        raise ValueError("EVI inputs must be finite")
    return expected_post_experiment_utility - current_expected_utility - experiment_cost


def expected_value_of_information(
    current_expected_utility: float,
    outcome_probabilities: dict[str, float],
    post_information_utilities: dict[str, float],
    experiment_cost: float,
) -> float:
    """Compute EVSI-style expected utility of information before observing outcomes."""
    if set(outcome_probabilities) != set(post_information_utilities):
        raise ValueError("probability and utility outcomes must have identical keys")
    probabilities = list(outcome_probabilities.values())
    if not probabilities or any(
        not math.isfinite(p) or p < 0.0 for p in probabilities
    ):
        raise ValueError("outcome probabilities must be finite and non-negative")
    if abs(math.fsum(probabilities) - 1.0) > 1e-9:
        raise ValueError("outcome probabilities must sum to 1.0")
    utilities = list(post_information_utilities.values())
    if not all(math.isfinite(u) for u in utilities):
        raise ValueError("post-information utilities must be finite")
    return math.fsum(
        outcome_probabilities[key] * post_information_utilities[key]
        for key in outcome_probabilities
    ) - current_expected_utility - experiment_cost


def adversarial_admission(
    *,
    interval_width: float,
    benchmark_regression: bool = False,
    anomaly_density: float = 0.0,
    provenance_gap: float = 0.0,
    change_point: bool = False,
    decision_impact: float = 0.0,
) -> str:
    """Admission heuristic, not a reviewer score or promotion authority."""
    numeric = (interval_width, anomaly_density, provenance_gap, decision_impact)
    if not all(math.isfinite(x) and x >= 0.0 for x in numeric):
        raise ValueError("review-admission numeric inputs must be finite and non-negative")
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
    interval = belief.interval95
    predictive = {
        "next_success_probability": belief.mean,
        "next_failure_probability": 1.0 - belief.mean,
        "three_trial_success_pmf": [
            posterior_predictive_probability(belief.alpha, belief.beta, k, 3)
            for k in range(4)
        ],
        "three_trial_mean": posterior_predictive_mean(belief.alpha, belief.beta, 3),
        "three_trial_variance": posterior_predictive_variance(belief.alpha, belief.beta, 3),
    }
    evsi_value = None
    if payload.get("decision_utilities") is not None:
        evsi_value = evsi_binary_decision(
            belief.alpha,
            belief.beta,
            payload["decision_utilities"],
            float(payload.get("experiment_cost", 0.0)),
        )
    review = adversarial_admission(
        interval_width=interval[1] - interval[0],
        benchmark_regression=bool(payload.get("benchmark_regression", False)),
        anomaly_density=float(payload.get("anomaly_density", 0.0)),
        provenance_gap=float(payload.get("provenance_gap", 0.0)),
        change_point=bool(payload.get("change_point", False)),
        decision_impact=float(payload.get("decision_impact", 0.0)),
    )
    left = {
        "tensor": {
            "axes": ["time", "task_family", "provider", "metric"],
            "observations": len(observations),
        },
        "graph": {
            "nodes": len({x.get("event_id") for x in observations if x.get("event_id")}),
            "edges": "derived",
        },
        "matrix": {"rows": "state/cohort", "columns": "outcome/metric"},
        "constellation": {
            "entities": sorted(
                {x.get("provider") for x in observations if x.get("provider")}
            )
        },
    }
    right = {
        "dag": {"edges": ["hypothesis→treatment", "treatment→observation", "observation→outcome"]},
        "trellis": {"states": ["unknown", "candidate", "observed", "validated", "decision"]},
        "markov": {"transition_semantics": "explicit transition probabilities only"},
    }
    return {
        "schema_version": "1.1",
        "posterior": {
            "belief": asdict(belief),
            "mean": belief.mean,
            "sd": belief.sd,
            "credible_interval_95": interval,
            "credible_interval_95_approx": belief.interval95_approx,
            "counts": counts,
            "entropy": beta_entropy(belief.alpha, belief.beta),
            "one_step_information_gain": one_step_information_gain(belief.alpha, belief.beta),
        },
        "posterior_predictive": predictive,
        "information_value": {
            "evsi_binary_decision": evsi_value,
        },
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
        print("usage: delphic_oracle.py INPUT.json", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as fh:
        payload = json.load(fh)
    json.dump(workflow(payload), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
