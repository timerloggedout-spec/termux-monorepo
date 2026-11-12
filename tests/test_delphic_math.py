import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name, path in {
    "delphic_math": ROOT / "scripts" / "delphic_math.py",
    "delphic_graph_lab": ROOT / "scripts" / "delphic_graph_lab.py",
}.items():
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

m = sys.modules["delphic_math"]


def test_beta_entropy_and_kl_match_wolfram_derived_formulas():
    assert abs(m.beta_entropy(2.0, 2.0) - (-0.1250928025613883341)) < 1e-12
    assert abs(m.beta_kl(2.0, 2.0, 3.0, 2.0) - 0.1401861527733880239) < 1e-12
    assert m.beta_kl(2.0, 2.0, 2.0, 2.0) == 0.0


def test_beta_binomial_predictive_moments_and_pmf():
    assert abs(m.posterior_predictive_probability(2.0, 2.0, 2, 3) - 0.3) < 1e-12
    assert abs(m.posterior_predictive_mean(2.0, 2.0, 3) - 1.5) < 1e-12
    assert abs(m.posterior_predictive_variance(2.0, 2.0, 3) - 1.05) < 1e-12


def test_one_step_information_gain_matches_wolfram():
    assert abs(m.one_step_information_gain(2.0, 2.0) - 0.1098138472266119761) < 1e-12


def test_evsi_optimizes_action_after_observation():
    utilities = {
        "A": {"success": 1.0, "failure": 0.0},
        "B": {"success": 0.2, "failure": 0.8},
    }
    # Prior p=.5; current best utility=.5. After one observation,
    # success selects A (EU=.6), failure selects B (EU=.56).
    # EVSI = .5*.6 + .5*.56 - .5 - .05 = .03.
    assert abs(m.evsi_binary_decision(2.0, 2.0, utilities, 0.05) - 0.03) < 1e-12


def test_expected_path_cost_conserves_probability_and_accumulates_edge_cost():
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    transitions = {"A": {"B": 0.25, "C": 0.75}, "B": {"D": 1.0}, "C": {"D": 1.0}, "D": {}}
    costs = {("A", "B"): 2.0, ("A", "C"): 4.0, ("B", "D"): 10.0, ("C", "D"): 6.0}
    cost_mass, terminal_cost = m.expected_path_cost(graph, transitions, costs, "A")
    # 0.25*(2+10) + 0.75*(4+6) = 10.5. The previous 9.0 fixture did not match these edges.
    assert abs(cost_mass["D"] - 10.5) < 1e-12
    assert abs(terminal_cost - 10.5) < 1e-12
