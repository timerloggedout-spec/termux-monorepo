import json
from pathlib import Path

from archwiz.context_relationships.source_collector import collect_source_seed


def write_registry(path: Path):
    path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "exclusions": {
                    "path_globs": [".deepcli/**"],
                    "max_file_bytes": 200,
                },
                "scopes": [
                    {
                        "id": "core",
                        "title": "Core source",
                        "path_globs": ["src/**/*.py", "src/*.py"],
                        "aliases": ["core"],
                        "labels": [],
                    }
                ],
            }
        )
    )


def test_collect_source_seed_emits_exact_python_symbols_imports_and_scopes(tmp_path):
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src/__init__.py").write_text("")
    (root / "src/helper.py").write_text("VALUE = 1\n")
    (root / "src/main.py").write_text(
        "from . import helper\n\nclass Runner:\n    def execute(self):\n        return helper.VALUE\n"
    )
    (root / ".deepcli/session_store").mkdir(parents=True)
    (root / ".deepcli/session_store/ignored.py").write_text("password = 'never indexed'\n")
    (root / "generated").mkdir()
    (root / "generated/large.py").write_text("x = '" + "a" * 250 + "'\n")
    registry = tmp_path / "scopes.json"
    write_registry(registry)

    seed, report = collect_source_seed(root, "example", "repo", "main", registry)

    node_refs = {(node["kind"], node["external_id"]) for node in seed["nodes"]}
    assert ("file", "src/main.py") in node_refs
    assert ("symbol", "src/main.py:Runner:3") in node_refs
    assert ("symbol", "src/main.py:Runner.execute:4") in node_refs
    assert not any("session_store" in external_id for _, external_id in node_refs)
    assert report["excluded_files"] == 1
    assert report["oversized_files"] == 1
    assert report["scopes_matched"] == 3
    assert any(
        edge["type"] == "IMPORTS"
        and edge["source"] == "file:src/main.py"
        and edge["target"] == "file:src/helper.py"
        for edge in seed["edges"]
    )
    assert all(edge["classification"] == "verified" for edge in seed["edges"])


def test_collect_source_seed_reports_bad_python_without_fabricating_symbols(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "bad.py").write_text("def incomplete(:\n")
    registry = tmp_path / "scopes.json"
    write_registry(registry)

    seed, report = collect_source_seed(root, "example", "repo", "main", registry)

    assert any(item["path"] == "bad.py" for item in report["parser_failures"])
    assert not any(node["kind"] == "symbol" for node in seed["nodes"])


def test_collect_source_seed_rejects_symlinked_files_before_reading_targets(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("password = 'must not be indexed'\n")
    (root / "linked.py").symlink_to(outside)
    registry = tmp_path / "scopes.json"
    write_registry(registry)

    seed, report = collect_source_seed(root, "example", "repo", "main", registry)

    assert not any(node.get("external_id") == "linked.py" for node in seed["nodes"])
    assert report["symlink_files"] == 1


def test_collect_source_seed_records_recursion_error_and_continues(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "deep.py").write_text("x = 1\n")
    registry = tmp_path / "scopes.json"
    write_registry(registry)

    from archwiz.context_relationships import source_collector

    monkeypatch.setattr(source_collector.ast, "parse", lambda *args, **kwargs: (_ for _ in ()).throw(RecursionError("deep tree")))
    seed, report = collect_source_seed(root, "example", "repo", "main", registry)

    assert any(item["path"] == "deep.py" and "deep tree" in item["error"] for item in report["parser_failures"])
    assert not any(node.get("kind") == "symbol" for node in seed["nodes"])
