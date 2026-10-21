import json
from pathlib import Path

from archwiz.context_relationships.compiler import (
    compile_seed,
    load_json,
    write_artifacts,
)
from archwiz.context_relationships.linear_freshness import compare_linear_freshness

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/context_relationships/seed.json"
SCOPE_REGISTRY = ROOT / "config/context_relationships/scope_registry.json"
SCHEMA = ROOT / "config/context_relationships/schema.json"


def build_index(tmp_path):
    seed = load_json(FIXTURE, "fixture")
    nodes, edges, matrix, manifest = compile_seed(seed, SCOPE_REGISTRY, SCHEMA)
    write_artifacts(tmp_path, nodes, edges, matrix, manifest, FIXTURE)
    return tmp_path


def test_linear_freshness_compares_explicit_github_links_without_emitting_descriptions(tmp_path):
    linear_issues = {
        "issues": [
            {
                "id": "TER-900",
                "title": "Review feedback rollup",
                "url": "https://linear.app/example/issue/TER-900/review-feedback-rollup",
                "updatedAt": "2026-08-18T01:00:30Z",
                "status": "Triage",
                "description": "Source: https://github.com/timerloggedout-spec/termux-monorepo/pull/232#discussion_r901",
            },
            {
                "id": "TER-901",
                "title": "Unknown source",
                "url": "https://linear.app/example/issue/TER-901/unknown-source",
                "updatedAt": "2026-08-18T02:00:00Z",
                "status": "Backlog",
                "description": "Source: https://github.com/timerloggedout-spec/termux-monorepo/issues/9999#issuecomment-123",
            },
        ]
    }
    input_path = tmp_path / "linear.json"
    input_path.write_text(json.dumps(linear_issues), encoding="utf-8")

    report = compare_linear_freshness(build_index(tmp_path), input_path, "timerloggedout-spec", "termux-monorepo")

    stale = next(item for item in report["records"] if item["linear_id"] == "TER-900")
    missing = next(item for item in report["records"] if item["linear_id"] == "TER-901")
    assert stale["status"] == "stale"
    assert stale["github_targets"] == ["review_comment:901"]
    assert missing["status"] == "missing"
    assert missing["github_targets"] == ["issue_comment:123"]
    assert "description" not in json.dumps(report)
    assert report["counts"] == {"missing": 1, "stale": 1}
