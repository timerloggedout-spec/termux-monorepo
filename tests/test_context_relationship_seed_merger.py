import pytest

from archwiz.context_relationships.compiler import CompilationError
from archwiz.context_relationships.seed_merger import merge_seeds

BASE = {
    "schema_version": "1.0",
    "repository": {"owner": "example", "name": "repo", "default_branch": "main"},
}


def test_merge_seeds_combines_complementary_node_metadata_and_edges():
    source_seed = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "src/app.py",
                "observed_at": "2026-08-18T10:00:00Z",
                "attributes": {"path": "src/app.py", "language": "python"},
            }
        ],
        "edges": [],
    }
    github_seed = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "src/app.py",
                "observed_at": "2026-08-18T11:00:00Z",
                "attributes": {"path": "src/app.py"},
                "url": "https://github.com/example/repo/blob/main/src/app.py",
            }
        ],
        "edges": [{"type": "TOUCHES", "source": "pull_request:1", "target": "file:src/app.py"}],
    }

    merged, report = merge_seeds(source_seed, github_seed)

    assert report["merged_node_count"] == 1
    assert report["merged_edge_count"] == 1
    assert merged["nodes"][0]["attributes"] == {"path": "src/app.py", "language": "python"}
    assert merged["nodes"][0]["observed_at"] == "2026-08-18T11:00:00Z"
    assert merged["nodes"][0]["url"].endswith("src/app.py")


def test_merge_seeds_prefers_the_newest_timestamped_metadata_on_update():
    earlier = {
        **BASE,
        "nodes": [
            {
                "kind": "issue",
                "external_id": "1",
                "observed_at": "2026-08-18T10:00:00Z",
                "attributes": {"state": "open", "title": "Original"},
            }
        ],
        "edges": [],
    }
    later = {
        **BASE,
        "nodes": [
            {
                "kind": "issue",
                "external_id": "1",
                "observed_at": "2026-08-18T11:00:00Z",
                "attributes": {"state": "closed", "title": "Updated"},
            }
        ],
        "edges": [],
    }

    merged, _ = merge_seeds(earlier, later)

    assert merged["nodes"][0]["attributes"] == {"state": "closed", "title": "Updated"}
    assert merged["nodes"][0]["observed_at"] == "2026-08-18T11:00:00Z"


def test_merge_seeds_rejects_conflicting_node_attributes():
    first = {
        **BASE,
        "nodes": [{"kind": "file", "external_id": "src/app.py", "attributes": {"language": "python"}}],
        "edges": [],
    }
    second = {
        **BASE,
        "nodes": [{"kind": "file", "external_id": "src/app.py", "attributes": {"language": "javascript"}}],
        "edges": [],
    }

    with pytest.raises(CompilationError, match="contradictory attribute"):
        merge_seeds(first, second)


def test_merge_seeds_canonicalizes_file_blob_urls_onto_seed_ref():
    historical = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "central_mapper_v420.py",
                "observed_at": "2026-10-01T00:00:00Z",
                "attributes": {"path": "central_mapper_v420.py"},
                "url": "https://github.com/example/repo/blob/master-staging/central_mapper_v420.py",
            }
        ],
        "edges": [],
    }
    current = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "central_mapper_v420.py",
                "observed_at": "2026-10-02T01:26:08Z",
                "attributes": {"path": "central_mapper_v420.py"},
                "url": "https://github.com/example/repo/blob/abc123def/central_mapper_v420.py#L10",
            }
        ],
        "edges": [],
    }

    merged, _ = merge_seeds(historical, current)

    assert merged["nodes"][0]["url"] == "https://github.com/example/repo/blob/main/central_mapper_v420.py"


def test_merge_seeds_still_rejects_distinct_file_urls():
    first = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "central_mapper_v420.py",
                "attributes": {"path": "central_mapper_v420.py"},
                "url": "https://github.com/example/repo/blob/main/central_mapper_v420.py",
            }
        ],
        "edges": [],
    }
    second = {
        **BASE,
        "nodes": [
            {
                "kind": "file",
                "external_id": "central_mapper_v420.py",
                "attributes": {"path": "central_mapper_v420.py"},
                "url": "https://example.invalid/other",
            }
        ],
        "edges": [],
    }

    with pytest.raises(CompilationError, match="contradictory url"):
        merge_seeds(first, second)


def test_merge_seeds_unions_symbol_spans_without_observed_at():
    first = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "central_mapper_v420.py:CentralMapper:36",
                "attributes": {"name": "CentralMapper", "line": 36, "end_line": 80},
            }
        ],
        "edges": [],
    }
    second = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "central_mapper_v420.py:CentralMapper:36",
                "attributes": {"name": "CentralMapper", "line": 36, "end_line": 120},
            }
        ],
        "edges": [],
    }

    merged, _ = merge_seeds(first, second)

    assert merged["nodes"][0]["attributes"]["end_line"] == 120
    assert merged["nodes"][0]["attributes"]["line"] == 36


def test_merge_seeds_coerces_string_end_line_without_observed_at():
    first = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "multi-ai-cli/backends/deepseek.py:DeepSeekBackend:37",
                "attributes": {"name": "DeepSeekBackend", "line": 37, "end_line": 80},
            }
        ],
        "edges": [],
    }
    second = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "multi-ai-cli/backends/deepseek.py:DeepSeekBackend:37",
                "attributes": {"name": "DeepSeekBackend", "line": "37", "end_line": "140"},
            }
        ],
        "edges": [],
    }

    merged, _ = merge_seeds(first, second)

    assert merged["nodes"][0]["attributes"]["end_line"] == 140
    assert merged["nodes"][0]["attributes"]["line"] == 37


def test_span_line_rejects_bool_and_coerces_numeric_string():
    from archwiz.context_relationships.seed_merger import span_line

    assert span_line(True) is None
    assert span_line(False) is None
    assert span_line("37") == 37
    assert span_line(" 140 ") == 140
    assert span_line(37.0) == 37
    assert span_line("37.5") is None


def test_merge_seeds_ignores_bool_span_and_keeps_observed_line():
    first = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "multi-ai-cli/backends/deepseek.py:DeepSeekBackend:37",
                "attributes": {"name": "DeepSeekBackend", "line": True, "end_line": 80},
            }
        ],
        "edges": [],
    }
    second = {
        **BASE,
        "nodes": [
            {
                "kind": "symbol",
                "external_id": "multi-ai-cli/backends/deepseek.py:DeepSeekBackend:37",
                "attributes": {"name": "DeepSeekBackend", "line": "37", "end_line": False},
            }
        ],
        "edges": [],
    }

    merged, _ = merge_seeds(first, second)

    assert merged["nodes"][0]["attributes"]["line"] == 37
    assert merged["nodes"][0]["attributes"]["end_line"] == 80
