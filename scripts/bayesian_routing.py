#!/usr/bin/env python3
"""Small stdlib-only uncertainty engine for optimized routing experiments.

This module intentionally does not select a provider by itself. It computes
uncertainty-aware candidate statistics after hard admission has happened.
"""

from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BetaBelief:
    alpha: float = 1.0
    beta: float = 1.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def variance(self) -> float:
        a, b = self.alpha, self.beta
        n = a + b
        return a * b / (n * n * (n + 1.0))

    def update(self, success: bool, weight: float = 1.0) -> "BetaBelief":
        if weight < 0:
            raise ValueError("weight must be non-negative")
        return BetaBelief(
            self.alpha + (weight if success else 0.0),
            self.beta + (0.0 if success else weight),
        )


def _posterior_and_executed_count(
    observations: list[dict[str, Any]],
    *,
    alpha: float = 1.0,
    beta: float = 1.0,
) -> tuple[BetaBelief, int]:
    cur_alpha = float(alpha)
    cur_beta = float(beta)
    executed_count = 0
    seen: set[str] = set()
    for item in observations:
        if item.get("executed") is not True or item.get("attributed") is not True:
            continue
        experiment_id = item.get("experiment_id")
        if experiment_id:
            if experiment_id in seen:
                continue
            seen.add(experiment_id)
        outcome = item.get("outcome")
        if outcome is True:
            cur_alpha += 1.0
            executed_count += 1
        elif outcome is False:
            cur_beta += 1.0
            executed_count += 1
    return BetaBelief(cur_alpha, cur_beta), executed_count


def posterior(
    observations: list[dict[str, Any]],
    *,
    alpha: float = 1.0,
    beta: float = 1.0,
) -> BetaBelief:
    """Update only observations explicitly marked as executed/attributed.

    admission failures, unknown outcomes, and retries sharing an experiment
    identity must not silently become independent performance failures.
    """
    belief, _ = _posterior_and_executed_count(observations, alpha=alpha, beta=beta)
    return belief


def sample_beta(belief: BetaBelief, rng: random.Random) -> float:
    return rng.betavariate(belief.alpha, belief.beta)


def probability_a_exceeds_b(
    a: BetaBelief,
    b: BetaBelief,
    *,
    draws: int = 20000,
    seed: int = 0,
) -> float:
    if draws <= 0:
        raise ValueError("draws must be positive")
    rng = random.Random(seed)
    betavariate = rng.betavariate
    a_alpha, a_beta = a.alpha, a.beta
    b_alpha, b_beta = b.alpha, b.beta
    wins = sum(betavariate(a_alpha, a_beta) > betavariate(b_alpha, b_beta) for _ in range(draws))
    return wins / draws


def expected_value_of_information(
    current_expected_utility: float,
    expected_post_experiment_utility: float,
    experiment_cost: float,
) -> float:
    """Simple EVI proxy; callers should preserve the underlying assumptions."""
    return expected_post_experiment_utility - current_expected_utility - experiment_cost


def summarize_candidate(
    candidate: dict[str, Any],
    observations: list[dict[str, Any]],
    *,
    seed: int = 0,
) -> dict[str, Any]:
    belief, executed_count = _posterior_and_executed_count(observations)
    rng = random.Random(seed)
    return {
        "candidate": candidate,
        "posterior": {"alpha": belief.alpha, "beta": belief.beta},
        "posterior_mean": belief.mean,
        "posterior_sd": math.sqrt(belief.variance),
        "thompson_sample": sample_beta(belief, rng),
        "executed_observations": executed_count,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: bayesian_routing.py INPUT.json", file=sys.stderr)
        return 2
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    output = []
    for item in data.get("candidates", []):
        output.append(
            summarize_candidate(
                item.get("candidate", {}),
                item.get("observations", []),
                seed=int(item.get("seed", 0)),
            )
        )
    json.dump({"version": 1, "candidates": output}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
