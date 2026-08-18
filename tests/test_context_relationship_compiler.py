import json
from pathlib import Path

import pytest

from archwiz.context_relationships.compiler import (
    CompilationError,
    compile_seed,
    load_json,
    write_artifacts,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/context_relationships/seed.json"
SCOPE_REGISTRY = ROOT / "config/context_relationships/scope_registry.json"
SCHEMA = ROOT / "config/context_relationships/schema.json"


def seed_data():
    return load_json(FIXTURE, "fixture")


def test_compile_seed_is_deterministic_and_keeps_classification_boundaries():
    first = compile_seed(seed_data(), SCOPE_REGISTRY, SCHEMA)
    second = compile_seed(seed_data(), SCOPE_REGISTRY, SCHEMA)

    nodes, edges, matrix, manifest = first
    assert first == second
    assert manifest["node_count"] == 7
    assert manifest["edge_count"] == 5
    assert manifest["verified_edge_count"] == 4
    assert manifest["candidate_edge_count"] == 1
    assert manifest["schema_sha256"]
    assert all(node["id"].startswith("node:") for node in nodes)
    assert all(edge["id"].startswith("edge:") for edge in edges)
    assert {edge["classification"] for edge in edges} == {"verified", "candidate"}
    assert any(row["candidate"] for row in matrix["rows"])
    assert all("evidence" in edge and edge["evidence"] for edge in edges)


def test_duplicate_edges_merge_evidence_without_changing_the_relationship():
    seed = seed_data()
    duplicate = json.loads(json.dumps(seed["edges"][0]))
    duplicate["evidence"][0]["details"] = {"matched_path": "archwiz/context_graph_builder.py", "scope_rule": "legacy"}
    seed["edges"].append(duplicate)

    _, edges, _, manifest = compile_seed(seed, SCOPE_REGISTRY, SCHEMA)

    assert manifest["edge_count"] == 5
    scoped_edge = next(edge for edge in edges if edge["type"] == "IN_SCOPE" and len(edge["evidence"]) == 2)
    assert len(scoped_edge["evidence"]) == 2


def test_write_artifacts_creates_canonical_jsonl_matrix_and_manifest(tmp_path):
    nodes, edges, matrix, manifest = compile_seed(seed_data(), SCOPE_REGISTRY, SCHEMA)

    write_artifacts(tmp_path, nodes, edges, matrix, manifest, FIXTURE)

    assert (tmp_path / "nodes.jsonl").read_text().count("\n") == 7
    assert (tmp_path / "edges.jsonl").read_text().count("\n") == 5
    rendered_matrix = json.loads((tmp_path / "matrix.json").read_text())
    rendered_manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert rendered_matrix["node_order"] == [node["id"] for node in nodes]
    assert rendered_manifest["input_sha256"]
    assert rendered_manifest["scope_registry_sha256"]


@pytest.mark.parametrize(
    "mutate, message",
    [
        (
            lambda seed: seed["edges"][0].update({"target": "file:not-in-seed"}),
            "unknown node",
        ),
        (
            lambda seed: seed["edges"][0].update({"classification": "candidate", "score": 0.2}),
            "must use verified classification",
        ),
        (
            lambda seed: seed["nodes"][0]["attributes"].update({"body": "do not persist full discussion text"}),
            "prohibited field",
        ),
        (
            lambda seed: seed["nodes"][2]["attributes"].update({"path": ".deepcli/session_store/secret.json"}),
            "excluded path",
        ),
    ],
)
def test_compile_seed_rejects_unsafe_or_inconsistent_records(mutate, message):
    seed = seed_data()
    mutate(seed)

    with pytest.raises(CompilationError, match=message):
        compile_seed(seed, SCOPE_REGISTRY, SCHEMA)
