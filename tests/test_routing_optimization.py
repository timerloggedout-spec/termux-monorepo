from scripts.routing_optimization import (
    RouteMetrics,
    beta_mean,
    beta_normal_approx_interval,
    correlation_adjusted_weight,
    constrained_utility,
    dominates,
    expected_value_of_information,
    pareto_frontier,
)


def test_pareto_frontier_keeps_tradeoffs():
    routes = [
        RouteMetrics("A", .94, 8, 3),
        RouteMetrics("B", .91, 4, 1),
        RouteMetrics("C", .88, 2, 0),
    ]
    assert {r.name for r in pareto_frontier(routes)} == {"A", "B", "C"}
    assert dominates(RouteMetrics("D", .95, 3, 0), routes[0])


def test_constraints_precede_utility():
    route = RouteMetrics("A", .94, 8, 3)
    assert constrained_utility(route, correctness_floor=.95) is None
    assert constrained_utility(route, correctness_floor=.90, latency_ceiling=8) == .94


def test_evi_is_decision_value_minus_cost():
    assert expected_value_of_information(.75, 100, 80, 5) == 90


def test_beta_mean_and_fast_interval():
    assert beta_mean(9, 3) == .75
    lo, hi = beta_normal_approx_interval(9, 3)
    assert .50 < lo < .60
    assert .90 < hi < .98


def test_correlated_observations_do_not_count_as_independent_trials():
    assert correlation_adjusted_weight(10, 0.0) == 10
    assert correlation_adjusted_weight(10, 1.0) == 1
