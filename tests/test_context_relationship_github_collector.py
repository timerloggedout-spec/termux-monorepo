import json
from pathlib import Path

from archwiz.context_relationships.compiler import compile_seed
from archwiz.context_relationships.github_collector import collect_github_seed

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "config/context_relationships/schema.json"


class FakeGitHubClient:
    def __init__(self):
        self.request_count = 0
        self.responses = {
            "/repos/example/repo/issues": [
                {
                    "number": 86,
                    "state": "open",
                    "title": "Relate index work",
                    "body": "Related to #232",
                    "created_at": "2026-08-18T10:00:00Z",
                    "updated_at": "2026-08-18T11:00:00Z",
                    "html_url": "https://github.com/example/repo/issues/86",
                    "labels": [{"name": "P1"}],
                },
                {
                    "number": 236,
                    "state": "open",
                    "title": "APK Investigation List",
                    "body": "Timeline target",
                    "created_at": "2026-08-18T12:35:00Z",
                    "updated_at": "2026-08-18T12:35:00Z",
                    "html_url": "https://github.com/example/repo/issues/236",
                    "labels": [],
                }
            ],
            "/repos/example/repo/pulls": [
                {
                    "number": 232,
                    "state": "closed",
                    "title": "ICM integration",
                    "body": "Fixes #86",
                    "created_at": "2026-08-18T10:00:00Z",
                    "updated_at": "2026-08-18T12:00:00Z",
                    "merged_at": "2026-08-18T12:00:00Z",
                    "html_url": "https://github.com/example/repo/pull/232",
                    "labels": [{"name": "P1"}],
                    "base": {"ref": "master-staging"},
                    "head": {"ref": "feature/graph"},
                }
            ],
            "/repos/example/repo/issues/86/comments": [
                {
                    "id": 10,
                    "body": "See #232 and https://github.com/example/repo/pull/232#issuecomment-11 and https://github.com/example/repo/pull/232#pullrequestreview-12 and https://github.com/example/repo/pull/232#discussion_r13.",
                    "created_at": "2026-08-18T11:10:00Z",
                    "updated_at": "2026-08-18T11:10:00Z",
                    "html_url": "https://github.com/example/repo/issues/86#issuecomment-10",
                }
            ],
            "/repos/example/repo/issues/236/timeline": [
                {
                    "event": "cross-referenced",
                    "created_at": "2026-08-18T12:40:00Z",
                    "actor": {"login": "example-user"},
                    "source": {
                        "type": "issue",
                        "issue": {
                            "number": 243,
                            "state": "open",
                            "title": "Game Teams",
                            "html_url": "https://github.com/example/repo/issues/243",
                        },
                    },
                }
            ],
            "/repos/example/repo/issues/232/comments": [
                {
                    "id": 11,
                    "body": "Tracks #86.",
                    "created_at": "2026-08-18T12:10:00Z",
                    "updated_at": "2026-08-18T12:10:00Z",
                    "html_url": "https://github.com/example/repo/pull/232#issuecomment-11",
                }
            ],
            "/repos/example/repo/pulls/232/files": [
                {"filename": "archwiz/example.py", "status": "modified"},
                {"filename": ".deepcli/session_store/private.py", "status": "modified"},
            ],
            "/repos/example/repo/pulls/232/commits": [
                {
                    "sha": "a" * 40,
                    "html_url": "https://github.com/example/repo/commit/" + "a" * 40,
                    "commit": {"committer": {"date": "2026-08-18T12:00:00Z"}},
                }
            ],
            "/repos/example/repo/pulls/232/reviews": [
                {
                    "id": 12,
                    "body": "Fixes #86 after review.",
                    "state": "APPROVED",
                    "submitted_at": "2026-08-18T12:20:00Z",
                    "html_url": "https://github.com/example/repo/pull/232#pullrequestreview-12",
                }
            ],
            "/repos/example/repo/pulls/232/comments": [
                {
                    "id": 13,
                    "body": "See #86.",
                    "path": ".deepcli/session_store/private.py",
                    "line": 4,
                    "created_at": "2026-08-18T12:30:00Z",
                    "updated_at": "2026-08-18T12:30:00Z",
                    "html_url": "https://github.com/example/repo/pull/232#discussion_r13",
                },
                {
                    "id": 14,
                    "body": "Review the changed file.",
                    "path": "archwiz/example.py",
                    "line": 9,
                    "created_at": "2026-08-18T12:31:00Z",
                    "updated_at": "2026-08-18T12:31:00Z",
                    "html_url": "https://github.com/example/repo/pull/232#discussion_r14",
                }
            ],
            "/repos/example/repo/commits": [
                {
                    "sha": "a" * 40,
                    "html_url": "https://github.com/example/repo/commit/" + "a" * 40,
                    "commit": {"committer": {"date": "2026-08-18T12:00:00Z"}},
                }
            ],
        }

    def paginate(self, path, params=None, limit=100, start_page=1):
        self.request_count += 1
        return iter(self.responses.get(path, []))

    def get_json(self, path, params=None):
        self.request_count += 1
        if path == "/repos/example/repo/commits/" + "a" * 40:
            return (
                {
                    "files": [
                        {"filename": "archwiz/example.py", "status": "modified"},
                        {"filename": "archwiz/helper.py", "status": "added"},
                        {"filename": ".deepcli/session_store/private.py", "status": "modified"},
                    ]
                },
                None,
            )
        raise AssertionError(f"unexpected GitHub API path: {path}")


def write_registry(path):
    path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "exclusions": {"path_globs": [".deepcli/**"], "max_file_bytes": 500000},
                "scopes": [
                    {
                        "id": "priority-work",
                        "title": "Priority work",
                        "path_globs": [],
                        "aliases": [],
                        "labels": ["P1"],
                    }
                ],
            }
        )
    )


def test_collect_github_seed_preserves_evidence_without_persisting_discussion_bodies(tmp_path):
    registry = tmp_path / "scopes.json"
    write_registry(registry)
    client = FakeGitHubClient()

    seed, report = collect_github_seed(
        client,
        "example",
        "repo",
        "master-staging",
        registry,
        max_items=10,
        max_commits=10,
        max_comments_per_item=10,
        include_comments=True,
    )
    nodes, edges, _, manifest = compile_seed(seed, registry, SCHEMA)

    refs = {f"{node['kind']}:{node['external_id']}" for node in nodes}
    assert {"issue:86", "issue:236", "issue:243", "pull_request:232", "issue_comment:10", "review:12", "review_comment:13"} <= refs
    assert "file:archwiz/example.py" in refs
    assert not any("session_store" in json.dumps(record) for record in [*nodes, *edges])
    assert not any("Tracks #86" in json.dumps(record) for record in [*nodes, *edges])
    assert any(edge["type"] == "CLOSES" and edge["source"].startswith("node:") for edge in edges)
    assert any(edge["type"] == "COMMENTS_ON" for edge in edges)
    assert any(edge["type"] == "REVIEWS" for edge in edges)
    assert any(
        edge["type"] == "MENTIONS"
        and edge["source"] == next(node["id"] for node in nodes if node["kind"] == "issue" and node["external_id"] == "243")
        and edge["target"] == next(node["id"] for node in nodes if node["kind"] == "issue" and node["external_id"] == "236")
        for edge in edges
    )
    comment_10 = next(node["id"] for node in nodes if node["kind"] == "issue_comment" and node["external_id"] == "10")
    for kind, external_id in (("issue_comment", "11"), ("review", "12"), ("review_comment", "13")):
        target = next(node["id"] for node in nodes if node["kind"] == kind and node["external_id"] == external_id)
        assert any(edge["type"] == "REFERENCES" and edge["source"] == comment_10 and edge["target"] == target for edge in edges)
    review_comment_14 = next(node["id"] for node in nodes if node["kind"] == "review_comment" and node["external_id"] == "14")
    file_node = next(node["id"] for node in nodes if node["kind"] == "file" and node["external_id"] == "archwiz/example.py")
    assert any(edge["type"] == "TOUCHES" and edge["source"] == review_comment_14 and edge["target"] == file_node for edge in edges)
    assert any(edge["type"] == "HAS_COMMIT" for edge in edges)
    assert any(edge["type"] == "CHANGED_IN" for edge in edges)
    assert any(edge["type"] == "CO_CHANGED_WITH" and edge["classification"] == "candidate" for edge in edges)
    assert manifest["edge_count"] == len(edges)
    assert report["counts"]["excluded_history_paths"] == 3
    assert report["counts"]["timeline_cross_references"] == 1
    assert report["counts"]["permalink_references"] == 3
    assert report["unresolved_internal_reference_count"] == 0
