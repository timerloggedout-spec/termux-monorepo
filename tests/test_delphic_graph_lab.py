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
