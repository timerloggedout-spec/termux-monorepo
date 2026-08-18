from pathlib import Path

from archwiz.context_relationships.compiler import (
    compile_seed,
    load_json,
    write_artifacts,
)
from archwiz.context_relationships.query import (
    render_markdown,
    render_mermaid,
    search_index,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/context_relationships/seed.json"
SCOPE_REGISTRY = ROOT / "config/context_relationships/scope_registry.json"
SCHEMA = ROOT / "config/context_relationships/schema.json"


def build_index(tmp_path):
    seed = load_json(FIXTURE, "fixture")
    nodes, edges, matrix, manifest = compile_seed(seed, SCOPE_REGISTRY, SCHEMA)
    write_artifacts(tmp_path, nodes, edges, matrix, manifest, FIXTURE)
    return tmp_path


def test_exact_file_query_separates_verified_timeline_from_candidate_links(tmp_path):
    result = search_index(build_index(tmp_path), "file:archwiz/context_graph_builder.py", depth=1, max_nodes=10)

    assert result["roots"][0]["reason"] == "exact selector"
    assert result["verified_edges"]
    assert all(edge["classification"] == "verified" for edge in result["verified_edges"])
    assert len(result["candidate_edges"]) == 1
    assert result["candidate_edges"][0]["type"] == "SIMILAR_TO"
    assert all(row["evidence_urls"] for row in result["timeline"])


def test_missing_typed_root_never_falls_back_to_unrelated_fuzzy_matches(tmp_path):
    result = search_index(build_index(tmp_path), "pr:999999", depth=2, max_nodes=10)

    assert result["roots"] == []
    assert result["visible_nodes"] == []
    assert result["timeline"] == []


def test_fuzzy_scope_query_explains_token_match_and_honors_node_bound(tmp_path):
    result = search_index(build_index(tmp_path), "context relationship", depth=2, max_nodes=2, fuzzy_limit=3)

    assert result["roots"]
    assert all(root["reason"].startswith("token overlap") for root in result["roots"])
    assert len(result["visible_nodes"]) <= 2


def test_markdown_and_mermaid_outputs_preserve_candidate_distinction(tmp_path):
    result = search_index(build_index(tmp_path), "file:archwiz/context_graph_builder.py", depth=1, max_nodes=10)

    markdown = render_markdown(result)
    mermaid = render_mermaid(result)

    assert "## Verified timeline" in markdown
    assert "## Ranked candidates" in markdown
    assert "flowchart LR" in mermaid
    assert "SIMILAR_TO score=0.42" in mermaid
    assert "classDef candidate" in mermaid
