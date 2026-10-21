from pathlib import Path

import pytest

from archwiz.context_relationships.temporal import (
    TemporalError,
    build_lineage,
    build_snapshot,
    compare_snapshots,
    load_snapshot,
    write_snapshot,
)


def node(node_id, **extra):
    value = {"id": node_id, "kind": "issue", "external_id": node_id, "attributes": {}}
    value.update(extra)
    return value


def edge(edge_id, source="a", target="b", classification="verified"):
    return {
        "id": edge_id,
        "type": "REFERENCES",
        "source": source,
        "target": target,
        "classification": classification,
        "observed_at": "2026-09-24T00:00:00Z",
        "evidence": [{"kind": "github_api", "source": "https://github.com/example/repo/issues/1", "collector": "test"}],
        "attributes": {},
    }


def test_compare_snapshots_reports_add_remove_change_and_reclassification():
    previous_nodes = [node("a"), node("b", attributes={"title": "old"})]
    current_nodes = [node("a"), node("b", attributes={"title": "new"}), node("c")]
    previous_edges = [edge("e1", classification="candidate"), edge("e2")]
    current_edges = [edge("e1"), edge("e3")]

    delta = compare_snapshots(previous_nodes, previous_edges, current_nodes, current_edges)

    assert delta["counts"] == {
        "nodes_added": 1,
        "nodes_removed": 0,
        "nodes_changed": 1,
        "edges_added": 1,
        "edges_removed": 1,
        "edges_changed": 1,
        "edges_reclassified": 1,
    }
    assert delta["nodes_added"] == ["c"]
    assert delta["nodes_changed"] == ["b"]
    assert delta["edges_reclassified"] == ["e1"]


def test_snapshot_identity_changes_when_graph_content_changes():
    base = dict(
        repository="example/repo",
        source_ref="master",
        source_sha="abc123",
        observed_at="2026-09-24T01:00:00Z",
        history_start_page=2,
        history_next_start_page=3,
        coverage="PARTIAL_CONTINUATION_REQUIRED",
    )
    first = build_snapshot(nodes=[node("a")], edges=[], **base)
    changed = build_snapshot(nodes=[node("a", attributes={"title": "changed"})], edges=[], **base)
    assert first["nodes_hash"] != changed["nodes_hash"]
    assert first["snapshot_id"] != changed["snapshot_id"]


def test_snapshot_is_deterministic_and_lineage_preserves_previous():
    snapshot = build_snapshot(
        repository="example/repo",
        source_ref="master",
        source_sha="abc123",
        observed_at="2026-09-24T01:00:00Z",
        history_start_page=2,
        history_next_start_page=3,
        nodes=[node("a")],
        edges=[],
        coverage="PARTIAL_CONTINUATION_REQUIRED",
        previous_snapshot_id="crg-previous",
        delta={"counts": {"nodes_added": 1}},
    )
    assert snapshot["snapshot_id"].startswith("crg-")
    assert snapshot["previous_snapshot_id"] == "crg-previous"
    lineage = build_lineage({"coverage": "PARTIAL_CONTINUATION_REQUIRED"}, snapshot)
    assert lineage["snapshot_id"] == snapshot["snapshot_id"]
    assert lineage["previous_snapshot_id"] == "crg-previous"


def test_invalid_coverage_and_page_are_rejected():
    with pytest.raises(TemporalError):
        build_snapshot(
            repository="example/repo",
            source_ref="master",
            source_sha="abc123",
            observed_at="2026-09-24T01:00:00Z",
            history_start_page=0,
            history_next_start_page=None,
            nodes=[],
            edges=[],
            coverage="COMPLETE",
        )
    with pytest.raises(TemporalError):
        build_snapshot(
            repository="example/repo",
            source_ref="master",
            source_sha="abc123",
            observed_at="2026-09-24T01:00:00Z",
            history_start_page=1,
            history_next_start_page=None,
            nodes=[],
            edges=[],
            coverage="UNKNOWN",
        )


def test_coverage_state_must_match_continuation_state():
    base = dict(
        repository="example/repo",
        source_ref="master",
        source_sha="abc123",
        observed_at="2026-09-24T01:00:00Z",
        history_start_page=1,
        nodes=[],
        edges=[],
    )
    with pytest.raises(TemporalError):
        build_snapshot(history_next_start_page=2, coverage="COMPLETE", **base)
    with pytest.raises(TemporalError):
        build_snapshot(history_next_start_page=None, coverage="PARTIAL_CONTINUATION_REQUIRED", **base)

def test_snapshot_write_is_immutable(tmp_path):
    snapshot = build_snapshot(
        repository="example/repo",
        source_ref="master",
        source_sha="abc123",
        observed_at="2026-09-24T01:00:00Z",
        history_start_page=1,
        history_next_start_page=None,
        nodes=[node("a")],
        edges=[],
        coverage="COMPLETE",
    )
    lineage = build_lineage(None, snapshot)
    write_snapshot(tmp_path, snapshot=snapshot, nodes=[node("a")], edges=[], lineage=lineage)
    assert load_snapshot(tmp_path, snapshot["snapshot_id"])["snapshot_id"] == snapshot["snapshot_id"]
    with pytest.raises(FileExistsError):
        write_snapshot(tmp_path, snapshot=snapshot, nodes=[node("a")], edges=[], lineage=lineage)
