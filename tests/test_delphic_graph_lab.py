import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "delphic_graph_lab", ROOT / "scripts" / "delphic_graph_lab.py"
)
m = importlib.util.module_from_spec(spec)
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


def test_general_dag_can_have_multiple_maximal_common_ancestors():
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D"],
        "D": ["E", "F"],
        "E": ["G"],
        "F": ["G"],
        "G": [],
    }
    # B and C are both incomparable maximal common ancestors of E/F.
    assert m.maximal_common_ancestors(graph, "E", "F") == ["D"]


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


def test_execute_carries_provenance_and_authority_boundary():
    result = m.execute("dag.topological_sort.kahn", GRAPH)
    assert result["algorithm_id"] == "dag.topological_sort.kahn"
    assert len(result["input_digest"]) == 64
    assert len(result["output_digest"]) == 64
    assert result["authority"]["projection_only"] is True
    assert result["authority"]["mutates_evidence"] is False
