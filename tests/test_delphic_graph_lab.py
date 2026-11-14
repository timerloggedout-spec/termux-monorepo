import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "delphic_graph_lab", ROOT / "scripts" / "delphic_graph_lab.py"
)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


GRAPH = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": ["F"],
    "E": ["F"],
    "F": [],
}


def test_topological_sort_is_deterministic():
    assert m.topological_sort(GRAPH) == ["A", "B", "C", "D", "E", "F"]


def test_longest_path_runs_on_dag():
    path, distance = m.longest_path(GRAPH)
    assert path == ["A", "C", "E", "F"]
    assert distance == 3


def test_generator_edges_are_materialized_once_and_preserved():
    graph = {"A": (x for x in ["B", "C"]), "B": [], "C": []}
    assert m.topological_sort(graph) == ["A", "B", "C"]


def test_general_dag_can_have_multiple_maximal_common_ancestors():
    graph = {
        "A": ["B", "C"],
        "B": ["E", "X"],
        "C": ["Y", "F"],
        "X": ["F"],
        "Y": ["E"],
        "E": [],
        "F": [],
    }
    assert m.maximal_common_ancestors(graph, "E", "F") == ["B", "C"]


def test_ancestor_queries_include_the_target():
    assert m.maximal_common_ancestors({"A": ["B"], "B": []}, "A", "B") == ["A"]
    assert m.maximal_common_ancestors({"A": ["B"], "B": []}, "B", "B") == ["B"]


def test_forward_probability_requires_normalized_transitions():
    transitions = {
        "A": {"B": 0.7, "C": 0.3},
        "B": {"D": 1.0},
        "C": {"D": 0.6, "E": 0.4},
        "D": {"F": 1.0},
        "E": {"F": 1.0},
        "F": {},
    }
    mass = m.forward_probability(GRAPH, transitions, "A")
    assert abs(mass["F"] - 1.0) < 1e-9
    assert abs(mass["D"] - 0.88) < 1e-9
    assert abs(mass["E"] - 0.12) < 1e-9


def test_forward_probability_rejects_non_finite_probabilities():
    bad = {"A": {"B": float("nan"), "C": 1.0}}
    try:
        m.forward_probability(GRAPH, bad, "A")
    except ValueError as exc:
        assert "finite" in str(exc)
    else:
        raise AssertionError("expected finite-probability validation")


def test_forward_probability_requires_explicit_child_keys():
    bad = {"A": {"B": 1.0}}
    try:
        m.forward_probability(GRAPH, bad, "A")
    except ValueError as exc:
        assert "exactly match graph children" in str(exc)
    else:
        raise AssertionError("expected explicit transition-key validation")


def test_execute_carries_complete_provenance_inputs_and_terminal_mass():
    transitions = {
        "A": {"B": 0.7, "C": 0.3},
        "B": {"D": 1.0},
        "C": {"D": 0.6, "E": 0.4},
        "D": {"F": 1.0},
        "E": {"F": 1.0},
        "F": {},
    }
    result = m.execute(
        "dag.forward_probability",
        GRAPH,
        transitions=transitions,
        start="A",
    )
    assert result["algorithm_id"] == "dag.forward_probability"
    assert len(result["input_digest"]) == 64
    assert len(result["parameters_digest"]) == 64
    assert len(result["output_digest"]) == 64
    terminal = result["output"]["terminal_mass"]
    assert set(terminal) == {"F"}
    assert abs(terminal["F"] - 1.0) < 1e-12
    assert abs(result["output"]["terminal_mass_total"] - 1.0) < 1e-12
    assert result["authority"]["projection_only"] is True
    assert result["authority"]["mutates_evidence"] is False


def test_topological_sort_rejects_cycles():
    try:
        m.topological_sort({"A": ["B"], "B": ["A"]})
    except ValueError as exc:
        assert "cycle" in str(exc)
    else:
        raise AssertionError("expected cycle detection")


def test_forward_probability_rejects_missing_non_terminal_transition_map():
    try:
        m.forward_probability(GRAPH, {"A": {"B": 0.7, "C": 0.3}}, "A")
    except ValueError as exc:
        assert "missing transition probabilities" in str(exc)
    else:
        raise AssertionError("expected missing transition detection")


def test_three_way_reconciliation_preserves_explicit_none_and_deletions():
    result = m.three_way_diff(
        {"x": "base", "keep": "base", "delete": "base"},
        {"x": "left", "keep": None},
        {"x": "right", "keep": "base"},
    )
    assert result["conflicts"] == ["x"]
    assert result["merged"]["keep"] is None
    assert "delete" not in result["merged"]


def test_three_way_reconciliation_exposes_conflicts_via_execute():
    result = m.execute(
        "state.three_way_diff",
        {},
        reconciliation=(
            {"x": "base"},
            {"x": "left"},
            {"x": "right"},
        ),
    )
    assert result["output"]["conflicts"] == ["x"]


def test_execute_normalizes_generator_graph_once_for_algorithm_and_digest():
    graph = {"A": (node for node in ["B", "C"]), "B": [], "C": []}
    result = m.execute("dag.topological_sort.kahn", graph)
    assert result["output"]["ordered_nodes"] == ["A", "B", "C"]
    assert len(result["input_digest"]) == 64


def test_maximal_common_ancestors_preserves_generator_edges():
    graph = {"A": (node for node in ["B", "C"]), "B": ["D"], "C": ["D"], "D": []}
    assert m.maximal_common_ancestors(graph, "D", "D") == ["D"]



def test_ast_preorder_preserves_child_order_and_rejects_non_tree_edges():
    tree = {"Module": ["Class", "Function"], "Class": ["Method"], "Method": [], "Function": []}
    assert m.ast_preorder(tree, "Module") == ["Module", "Class", "Method", "Function"]
    try:
        m.ast_preorder({"Root": ["A", "B"], "A": ["C"], "B": ["C"], "C": []}, "Root")
    except ValueError as exc:
        assert "multiple parents" in str(exc)
    else:
        raise AssertionError("expected AST multiple-parent rejection")


def test_ast_preorder_rejects_unreachable_nodes_and_cycles():
    try:
        m.ast_preorder({"Root": [], "Orphan": []}, "Root")
    except ValueError as exc:
        assert "unreachable" in str(exc)
    else:
        raise AssertionError("expected unreachable AST node rejection")
    try:
        m.ast_preorder({"Root": ["Child"], "Child": ["Root"]}, "Root")
    except ValueError as exc:
        assert "parent" in str(exc) or "cycle" in str(exc)
    else:
        raise AssertionError("expected AST cycle rejection")


def test_markov_layer_propagation_conserves_mass_at_every_layer():
    result = m.markov_layer_propagation(
        ["A", "B", "C"],
        {"A": {"B": 0.7, "C": 0.3}, "B": {"B": 0.5, "C": 0.5}, "C": {"C": 1.0}},
        {"A": 1.0},
        4,
    )
    assert len(result["layers"]) == 5
    assert all(abs(total - 1.0) < 1e-9 for total in result["layer_mass"])
    assert abs(result["layers"][1]["B"] - 0.7) < 1e-9
    assert abs(result["layers"][1]["C"] - 0.3) < 1e-9


def test_markov_layer_propagation_rejects_unnormalized_rows():
    try:
        m.markov_layer_propagation(["A", "B"], {"A": {"B": 0.8}, "B": {"B": 1.0}}, {"A": 1.0}, 1)
    except ValueError as exc:
        assert "sum to 1.0" in str(exc)
    else:
        raise AssertionError("expected transition row normalization failure")


def test_temporal_lineage_preserves_missing_provenance_and_checks_parent_order():
    result = m.temporal_lineage([
        {"id": "s1", "observed_at": "2026-11-01T00:00:00Z", "source_sha": "abc", "parent_id": None},
        {"id": "s2", "observed_at": "2026-11-02T00:00:00Z", "source_sha": None, "parent_id": "s1"},
    ])
    assert result["structurally_valid"] is True
    assert result["provenance_complete"] is False
    assert result["edges"] == [{"from": "s1", "to": "s2"}]
    assert {"snapshot_id": "s2", "reason": "source_sha_missing"} in result["warnings"]


def test_temporal_lineage_rejects_forward_parent_and_non_monotonic_time():
    result = m.temporal_lineage([
        {"id": "s1", "observed_at": "2026-11-02T00:00:00Z", "source_sha": "abc", "parent_id": "s2"},
        {"id": "s2", "observed_at": "2026-11-01T00:00:00Z", "source_sha": "def", "parent_id": None},
    ])
    reasons = {item["reason"] for item in result["warnings"]}
    assert "parent_not_previously_observed" in reasons
    assert "non_monotonic_timestamp" in reasons
    assert result["structurally_valid"] is False


def test_markov_layer_propagation_rejects_non_finite_or_negative_tolerance():
    import math
    for tolerance in (math.nan, math.inf, -1.0):
        try:
            m.markov_layer_propagation(
                ["A"], {"A": {"A": 1.0}}, {"A": 1.0}, 1,
                tolerance=tolerance,
            )
        except ValueError as exc:
            assert "tolerance" in str(exc)
        else:
            raise AssertionError("expected invalid tolerance rejection")
