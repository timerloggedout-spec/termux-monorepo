import json
from pathlib import Path

from archwiz.context_relationships.temporal import build_lineage, build_snapshot, write_snapshot
from scripts.ci.validate_context_relationship_temporal import validate_temporal_history


def node(node_id):
    return {"id": node_id, "kind": "issue", "external_id": node_id, "attributes": {}}


def edge(edge_id, source="a", target="b"):
    return {
        "id": edge_id,
        "type": "REFERENCES",
        "source": source,
        "target": target,
        "classification": "verified",
        "observed_at": "2026-10-01T00:00:00Z",
        "evidence": [{"kind": "github_api", "source": "https://github.com/example/repo/issues/1", "collector": "test"}],
        "attributes": {},
    }


def add_snapshot(root: Path, *, previous=None, observed_at="2026-10-01T00:00:00Z"):
    previous_manifest = previous
    snapshot = build_snapshot(
        repository="example/repo",
        source_ref="master",
        source_sha="a" * 40,
        observed_at=observed_at,
        history_start_page=1,
        history_next_start_page=None,
        nodes=[node("a"), node("b")],
        edges=[edge("e1")],
        coverage="COMPLETE",
        previous_snapshot_id=previous_manifest["snapshot_id"] if previous_manifest else None,
    )
    event = build_lineage(previous_manifest, snapshot)
    write_snapshot(
        root / "temporal",
        snapshot=snapshot,
        nodes=[node("a"), node("b")],
        edges=[edge("e1")],
        lineage=event,
    )
    lineage_path = root / "temporal" / "lineage.jsonl"
    with lineage_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True) + "\n")
    return snapshot


def test_valid_temporal_history_passes(tmp_path):
    first = add_snapshot(tmp_path)
    add_snapshot(tmp_path, previous=first, observed_at="2026-10-02T00:00:00Z")

    result = validate_temporal_history(tmp_path)

    assert result["status"] == "PASS"
    assert result["snapshot_count"] == 2
    assert result["errors"] == []


def test_tampered_snapshot_content_is_unverified(tmp_path):
    snapshot = add_snapshot(tmp_path)
    nodes_path = tmp_path / "temporal" / "snapshots" / snapshot["snapshot_id"] / "nodes.jsonl"
    nodes_path.write_text(json.dumps(node("tampered")) + "\n", encoding="utf-8")

    result = validate_temporal_history(tmp_path)

    assert result["status"] == "UNVERIFIED"
    assert any("nodes_hash mismatch" in error for error in result["errors"])
    assert any("node_count does not match" in error for error in result["errors"])


def test_missing_referenced_snapshot_is_unverified(tmp_path):
    snapshot = add_snapshot(tmp_path)
    (tmp_path / "temporal" / "snapshots" / snapshot["snapshot_id"] / "manifest.json").unlink()

    result = validate_temporal_history(tmp_path)

    assert result["status"] == "UNVERIFIED"
    assert any("missing artifacts" in error for error in result["errors"])


def test_unresolved_edge_endpoint_is_unverified(tmp_path):
    snapshot = build_snapshot(
        repository="example/repo",
        source_ref="master",
        source_sha="b" * 40,
        observed_at="2026-10-01T00:00:00Z",
        history_start_page=1,
        history_next_start_page=None,
        nodes=[node("a")],
        edges=[edge("e1", source="a", target="missing")],
        coverage="COMPLETE",
    )
    event = build_lineage(None, snapshot)
    write_snapshot(
        tmp_path / "temporal",
        snapshot=snapshot,
        nodes=[node("a")],
        edges=[edge("e1", source="a", target="missing")],
        lineage=event,
    )
    (tmp_path / "temporal" / "lineage.jsonl").write_text(
        json.dumps(event, sort_keys=True) + "\n", encoding="utf-8"
    )

    result = validate_temporal_history(tmp_path)

    assert result["status"] == "UNVERIFIED"
    assert any("unresolved target endpoint" in error for error in result["errors"])


def test_empty_or_missing_lineage_fails_closed(tmp_path):
    result = validate_temporal_history(tmp_path)

    assert result["status"] == "UNVERIFIED"
    assert result["errors"]
