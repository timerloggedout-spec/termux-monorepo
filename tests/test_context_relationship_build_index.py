from pathlib import Path

from archwiz.context_relationships import build_index as builder

ROOT = Path(__file__).resolve().parents[1]
SCOPE_REGISTRY = ROOT / "config/context_relationships/scope_registry.json"
SCHEMA = ROOT / "config/context_relationships/schema.json"


def test_build_index_publishes_only_canonical_artifacts_and_uses_checkpoint(monkeypatch, tmp_path):
    source_seed = {
        "schema_version": "1.0",
        "repository": {"owner": "example", "name": "repo", "default_branch": "main"},
        "nodes": [
            {
                "kind": "repository",
                "external_id": "example/repo",
                "observed_at": "2026-08-18T10:00:00Z",
                "attributes": {"ref": "main"},
            },
            {
                "kind": "file",
                "external_id": "src/app.py",
                "observed_at": "2026-08-18T10:00:00Z",
                "attributes": {"path": "src/app.py", "language": "python"},
            },
        ],
        "edges": [],
    }
    github_seed = {
        "schema_version": "1.0",
        "repository": {"owner": "example", "name": "repo", "default_branch": "main"},
        "nodes": [
            {
                "kind": "issue",
                "external_id": "1",
                "observed_at": "2026-08-18T11:00:00Z",
                "attributes": {"number": 1, "state": "open"},
            }
        ],
        "edges": [],
    }
    observed_since = []

    monkeypatch.setattr(builder, "collect_source_seed", lambda *args: (source_seed, {"parser_failures": []}))

    def fake_github_collect(client, owner, repo, ref, registry, since, **kwargs):
        observed_since.append(since)
        return github_seed, {"collected_at": "2026-08-18T12:00:00Z", "request_count": 0, "counts": {}}

    monkeypatch.setattr(builder, "collect_github_seed", fake_github_collect)
    output = tmp_path / "index"

    first = builder.build_index(
        tmp_path,
        "example",
        "repo",
        "main",
        "token",
        SCOPE_REGISTRY,
        SCHEMA,
        output,
        1,
        1,
        1,
        1,
        False,
        0,
    )
    second = builder.build_index(
        tmp_path,
        "example",
        "repo",
        "main",
        "token",
        SCOPE_REGISTRY,
        SCHEMA,
        output,
        1,
        1,
        1,
        1,
        False,
        0,
    )
    builder.build_index(
        tmp_path,
        "example",
        "repo",
        "main",
        "token",
        SCOPE_REGISTRY,
        SCHEMA,
        output,
        1,
        1,
        1,
        1,
        False,
        0,
        full_refresh=True,
    )

    assert first["node_count"] == 3
    assert second["incremental_since"] == "2026-08-18T12:00:00Z"
    assert observed_since == [None, "2026-08-18T12:00:00Z", None]
    assert {path.name for path in output.iterdir()} == {
        "build-summary.json",
        "checkpoint.json",
        "edges.jsonl",
        "github-report.json",
        "manifest.json",
        "matrix.json",
        "merge-report.json",
        "nodes.jsonl",
        "source-report.json",
    }


def test_build_index_retains_prior_history_when_later_collection_omits_it(monkeypatch, tmp_path):
    repository = {"owner": "example", "name": "repo", "default_branch": "main"}
    source_seed = {
        "schema_version": "1.0",
        "repository": repository,
        "nodes": [
            {
                "kind": "repository",
                "external_id": "example/repo",
                "observed_at": "2026-08-18T10:00:00Z",
                "attributes": {"ref": "main"},
            }
        ],
        "edges": [],
    }
    historical_pr_seed = {
        "schema_version": "1.0",
        "repository": repository,
        "nodes": [
            {
                "kind": "pull_request",
                "external_id": "232",
                "observed_at": "2026-08-18T11:00:00Z",
                "attributes": {"number": 232, "state": "merged", "title": "Historical relation"},
            }
        ],
        "edges": [],
    }
    empty_window_seed = {"schema_version": "1.0", "repository": repository, "nodes": [], "edges": []}
    calls = []

    monkeypatch.setattr(builder, "collect_source_seed", lambda *args: (source_seed, {"parser_failures": []}))

    def fake_github_collect(client, owner, repo, ref, registry, since, **kwargs):
        calls.append(since)
        payload = historical_pr_seed if len(calls) == 1 else empty_window_seed
        return payload, {"collected_at": "2026-08-18T12:00:00Z", "request_count": 0, "counts": {}}

    monkeypatch.setattr(builder, "collect_github_seed", fake_github_collect)
    output = tmp_path / "index"
    common = (tmp_path, "example", "repo", "main", "token", SCOPE_REGISTRY, SCHEMA, output, 1, 1, 1, 1, False, 0)

    builder.build_index(*common)
    second = builder.build_index(*common)

    assert second["retained_history"] is True
    assert calls == [None, "2026-08-18T12:00:00Z"]
    assert '"external_id":"232"' in (output / "nodes.jsonl").read_text()
