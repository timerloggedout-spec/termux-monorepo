from pathlib import Path

from archwiz.context_relationships.compiler import (
    compile_seed,
    load_json,
    write_artifacts,
)
from archwiz.context_relationships.query import (
    file_review_timeline,
    render_file_review_markdown,
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


def test_exact_github_permalink_resolves_its_indexed_comment_node(tmp_path):
    result = search_index(
        build_index(tmp_path),
        "https://github.com/timerloggedout-spec/termux-monorepo/pull/232#discussion_r901",
        depth=1,
        max_nodes=10,
    )

    assert result["roots"][0]["kind"] == "review_comment"
    assert result["roots"][0]["reason"] == "exact GitHub permalink"


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


def test_file_review_timeline_consolidates_review_and_permalink_evidence(tmp_path):
    result = file_review_timeline(build_index(tmp_path), "archwiz/context_graph_builder.py", max_nodes=20)

    assert result["projection"] == "file_review_timeline"
    assert result["roots"][0]["kind"] == "file"
    assert {row["relationship"] for row in result["timeline"]} >= {"TOUCHES", "REVIEWS", "COMMENTS_ON", "REFERENCES"}
    assert any("discussion_r901" in url for row in result["timeline"] for url in row["evidence_urls"])
    assert any("issuecomment-902" in url for row in result["timeline"] for url in row["evidence_urls"])
    assert result["candidate_edges"]

    markdown = render_file_review_markdown(result)
    assert "# File review timeline" in markdown
    assert "## Verified review context" in markdown
    assert "## Ranked candidates" in markdown


def test_markdown_and_mermaid_outputs_preserve_candidate_distinction(tmp_path):
    result = search_index(build_index(tmp_path), "file:archwiz/context_graph_builder.py", depth=1, max_nodes=10)

    markdown = render_markdown(result)
    mermaid = render_mermaid(result)

    assert "## Verified timeline" in markdown
    assert "## Ranked candidates" in markdown
    assert "flowchart LR" in mermaid
    assert "SIMILAR_TO score=0.42" in mermaid
    assert "classDef candidate" in mermaid
