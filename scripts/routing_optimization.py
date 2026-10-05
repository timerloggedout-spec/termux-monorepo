#!/usr/bin/env python3
"""Dependency-free multi-objective and uncertainty-aware route utilities.

Hard admission must happen before these functions. They optimize among
already-eligible treatments; they never override policy or safety gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt
from typing import Iterable, Sequence


@dataclass(frozen=True)
class RouteMetrics:
    name: str
    correctness: float
    latency: float
    cost: float
    risk: float = 0.0

    def vector(self) -> tuple[float, float, float, float]:
        return (self.correctness, self.latency, self.cost, self.risk)


def dominates(a: RouteMetrics, b: RouteMetrics) -> bool:
    """True when a is no worse in every objective and strictly better in one."""
    return (
        a.correctness >= b.correctness
        and a.latency <= b.latency
        and a.cost <= b.cost
        and a.risk <= b.risk
        and (a.correctness > b.correctness
             or a.latency < b.latency
             or a.cost < b.cost
             or a.risk < b.risk)
    )


def pareto_frontier(routes: Iterable[RouteMetrics]) -> list[RouteMetrics]:
    rows = list(routes)
    return [candidate for candidate in rows
            if not any(dominates(other, candidate) for other in rows if other != candidate)]


def constrained_utility(
    route: RouteMetrics,
    *,
    correctness_floor: float = 0.0,
    latency_ceiling: float | None = None,
    cost_ceiling: float | None = None,
    risk_ceiling: float | None = None,
    correctness_weight: float = 1.0,
    latency_weight: float = 0.0,
    cost_weight: float = 0.0,
    risk_weight: float = 0.0,
) -> float | None:
    """Score only an admitted route; return None when utility constraints fail."""
    if route.correctness < correctness_floor:
        return None
    if latency_ceiling is not None and route.latency > latency_ceiling:
        return None
    if cost_ceiling is not None and route.cost > cost_ceiling:
        return None
    if risk_ceiling is not None and route.risk > risk_ceiling:
        return None
    return (
        correctness_weight * route.correctness
        - latency_weight * route.latency
        - cost_weight * route.cost
        - risk_weight * route.risk
    )


def expected_value_of_information(
    probability_of_better_decision: float,
    value_if_better: float,
    value_if_not_better: float,
    experiment_cost: float,
) -> float:
    """Expected decision improvement minus experiment cost."""
    return (
        probability_of_better_decision * value_if_better
        + (1.0 - probability_of_better_decision) * value_if_not_better
        - experiment_cost
    )


def beta_mean(alpha: float, beta: float) -> float:
    if alpha <= 0 or beta <= 0:
        raise ValueError("Beta parameters must be positive")
    return alpha / (alpha + beta)


def beta_normal_approx_interval(alpha: float, beta: float, z: float = 1.96) -> tuple[float, float]:
    """Fast approximate interval; exact intervals remain preferable when available."""
    if alpha <= 0 or beta <= 0:
        raise ValueError("Beta parameters must be positive")
    n = alpha + beta
    mean = alpha / n
    sd = sqrt(alpha * beta / (n * n * (n + 1)))
    return max(0.0, mean - z * sd), min(1.0, mean + z * sd)


def correlation_adjusted_weight(observation_count: int, correlation: float = 0.0) -> float:
    """Effective sample-size weight for exchangeable correlation."""
    if observation_count < 1:
        return 0.0
    if not 0.0 <= correlation <= 1.0:
        raise ValueError("correlation must be between 0 and 1")
    return observation_count / (1.0 + (observation_count - 1) * correlation)
