#!/usr/bin/env python3
"""Deterministic mathematical primitives for the Delphic research lane.

Wolfram is used during design/review to derive and simplify formulas.
This module intentionally has no Wolfram/runtime service dependency.
"""

from __future__ import annotations

import math
from typing import Mapping


_EPS = 1e-12


def _validate_beta(alpha: float, beta: float) -> None:
    if not all(math.isfinite(x) and x > 0.0 for x in (alpha, beta)):
        raise ValueError("beta shape parameters must be finite and positive")


def _digamma(x: float) -> float:
    """Deterministic digamma approximation using recurrence + asymptotic series."""
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError("digamma input must be finite and positive")
    result = 0.0
    while x < 8.0:
        result -= 1.0 / x
        x += 1.0
    inv = 1.0 / x
    inv2 = inv * inv
    return (
        result
        + math.log(x)
        - 0.5 * inv
        - inv2 / 12.0
        + inv2 * inv2 / 120.0
        - inv2 * inv2 * inv2 / 252.0
    )


def log_beta(alpha: float, beta: float) -> float:
    """log(B(alpha,beta)); stable for large shape parameters."""
    _validate_beta(alpha, beta)
    return math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)


def beta_entropy(alpha: float, beta: float) -> float:
    """Differential entropy of Beta(alpha,beta)."""
    _validate_beta(alpha, beta)
    return (
        log_beta(alpha, beta)
        - (alpha - 1.0) * _digamma(alpha)
        - (beta - 1.0) * _digamma(beta)
        + (alpha + beta - 2.0) * _digamma(alpha + beta)
    )


def beta_kl(
    alpha_1: float, beta_1: float, alpha_2: float, beta_2: float
) -> float:
    """KL(Beta(alpha_1,beta_1) || Beta(alpha_2,beta_2))."""
    _validate_beta(alpha_1, beta_1)
    _validate_beta(alpha_2, beta_2)
    value = (
        log_beta(alpha_2, beta_2)
        - log_beta(alpha_1, beta_1)
        + (alpha_1 - alpha_2) * _digamma(alpha_1)
        + (beta_1 - beta_2) * _digamma(beta_1)
        + (alpha_2 - alpha_1 + beta_2 - beta_1) * _digamma(alpha_1 + beta_1)
    )
    # Floating-point roundoff can produce tiny negative values.
    return max(0.0, value)


def posterior_predictive_probability(
    alpha: float, beta: float, successes: int, trials: int
) -> float:
    """P(K=successes | alpha,beta) under the Beta-Binomial posterior predictive."""
    _validate_beta(alpha, beta)
    if not isinstance(trials, int) or trials < 0:
        raise ValueError("trials must be a non-negative integer")
    if not isinstance(successes, int) or successes < 0 or successes > trials:
        raise ValueError("successes must be an integer in [0,trials]")
    log_p = (
        math.lgamma(trials + 1.0)
        - math.lgamma(successes + 1.0)
        - math.lgamma(trials - successes + 1.0)
        + log_beta(alpha + successes, beta + trials - successes)
        - log_beta(alpha, beta)
    )
    return math.exp(log_p)


def posterior_predictive_mean(alpha: float, beta: float, trials: int = 1) -> float:
    _validate_beta(alpha, beta)
    if trials < 0:
        raise ValueError("trials must be non-negative")
    return trials * alpha / (alpha + beta)


def posterior_predictive_variance(
    alpha: float, beta: float, trials: int = 1
) -> float:
    _validate_beta(alpha, beta)
    if trials < 0:
        raise ValueError("trials must be non-negative")
    n = alpha + beta
    return trials * alpha * beta * (n + trials) / (n * n * (n + 1.0))


def one_step_information_gain(alpha: float, beta: float) -> float:
    """Expected KL(prior || posterior) reduction in parameter entropy.

    For one Bernoulli observation:
    H(prior) - E_y[H(posterior | y)].
    """
    _validate_beta(alpha, beta)
    p = alpha / (alpha + beta)
    return max(
        0.0,
        beta_entropy(alpha, beta)
        - p * beta_entropy(alpha + 1.0, beta)
        - (1.0 - p) * beta_entropy(alpha, beta + 1.0),
    )


def _expected_binary_utility(
    probability_success: float, utility: Mapping[str, float]
) -> float:
    if set(utility) != {"success", "failure"}:
        raise ValueError("utility must contain success and failure")
    if not all(math.isfinite(float(v)) for v in utility.values()):
        raise ValueError("utility values must be finite")
    return (
        probability_success * float(utility["success"])
        + (1.0 - probability_success) * float(utility["failure"])
    )


def _best_action(
    probability_success: float, utilities: Mapping[str, Mapping[str, float]]
) -> tuple[str, float]:
    if not utilities:
        raise ValueError("at least one action is required")
    scored = [
        (action, _expected_binary_utility(probability_success, utility))
        for action, utility in utilities.items()
    ]
    # Lexical tie-break makes results deterministic.
    return max(scored, key=lambda item: (item[1], item[0]))


def evsi_binary_decision(
    alpha: float,
    beta: float,
    utilities: Mapping[str, Mapping[str, float]],
    experiment_cost: float = 0.0,
) -> float:
    """Exact EVSI for one future Bernoulli observation.

    EVSI = E_y[max_a EU(a | y)] - max_a EU(a) - cost.
    """
    _validate_beta(alpha, beta)
    if not math.isfinite(experiment_cost):
        raise ValueError("experiment cost must be finite")
    p = alpha / (alpha + beta)
    current_action, current_utility = _best_action(p, utilities)
    del current_action
    p_success = p
    p_failure = 1.0 - p
    posterior_success = (alpha + 1.0) / (alpha + beta + 1.0)
    posterior_failure = alpha / (alpha + beta + 1.0)
    _, success_utility = _best_action(posterior_success, utilities)
    _, failure_utility = _best_action(posterior_failure, utilities)
    return (
        p_success * success_utility
        + p_failure * failure_utility
        - current_utility
        - experiment_cost
    )


def expected_path_cost(
    graph: Mapping[str, list[str] | tuple[str, ...]],
    transitions: Mapping[str, Mapping[str, float]],
    edge_costs: Mapping[tuple[str, str], float],
    start: str,
) -> tuple[dict[str, float], float]:
    """Propagate expected accumulated edge cost through a normalized DAG.

    Returns (expected_cost_mass_by_node, expected_terminal_cost).
    """
    # Local import avoids making the math module depend on Graph Lab internals.
    from scripts.delphic_graph_lab import topological_sort, _adjacency

    adj = _adjacency(graph)
    order = topological_sort(adj)
    mass = {node: 0.0 for node in order}
    cost_mass = {node: 0.0 for node in order}
    if start not in mass:
        raise KeyError(start)
    mass[start] = 1.0
    for node in order:
        children = adj[node]
        if not children:
            continue
        if node not in transitions or set(transitions[node]) != set(children):
            raise ValueError(f"transition keys for {node!r} must exactly match graph children")
        probs = [float(transitions[node][child]) for child in children]
        if any(not math.isfinite(p) or p < 0.0 for p in probs):
            raise ValueError("transition probabilities must be finite and non-negative")
        if abs(sum(probs) - 1.0) > _EPS:
            raise ValueError("transition probabilities must sum to 1")
        for child, p in zip(children, probs):
            edge = (node, child)
            if edge not in edge_costs:
                raise ValueError(f"missing edge cost for {edge!r}")
            cost = float(edge_costs[edge])
            if not math.isfinite(cost):
                raise ValueError("edge costs must be finite")
            mass_to_child = mass[node] * p
            cost_mass[child] += p * (cost_mass[node] + mass[node] * cost)
            mass[child] += mass_to_child
    terminal = [node for node, children in adj.items() if not children]
    return cost_mass, sum(cost_mass[node] for node in terminal)
