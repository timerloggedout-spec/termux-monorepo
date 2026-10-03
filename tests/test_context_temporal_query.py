from pathlib import Path

from archwiz.context_relationships.temporal import build_lineage, build_snapshot, write_snapshot
from archwiz.context_relationships.temporal_query import (
    TemporalQueryError,
    between_projection,
    changes_between,
    snapshot_at,
    snapshots_between,
    temporal_timeline,
)


def make_snapshot(tmp_path: Path, observed_at: str, start: int, next_page: int | None, title: str, delta_counts=None):
    snapshot = build_snapshot(
        repository="example/repo",
        source_ref="master",
        source_sha=("a" * 40),
        observed_at=observed_at,
        history_start_page=start,
        history_next_start_page=next_page,
        nodes=[{
            "id": "node:a",
            "kind": "issue",
            "external_id": "1",
            "attributes": {"title": title},
        }],
        edges=[],
        coverage="COMPLETE" if next_page is None else "PARTIAL_CONTINUATION_REQUIRED",
        delta={"counts": delta_counts if delta_counts is not None else {"nodes_added": 1 if title == "one" else 0, "nodes_changed": 1 if title != "one" else 0}},
    )
    temporal = tmp_path / "temporal"
    write_snapshot(
        temporal,
        snapshot=snapshot,
        nodes=snapshot_nodes(snapshot, title),
        edges=[],
        lineage=build_lineage(None, snapshot),
    )
    return snapshot


def snapshot_nodes(snapshot, title):
    return [{
        "id": "node:a",
        "kind": "issue",
        "external_id": "1",
        "attributes": {"title": title},
    }]


def test_snapshot_at_selects_latest_observation_not_future(tmp_path):
    first = make_snapshot(tmp_path, "2026-10-01T10:00:00Z", 1, 2, "one")
    make_snapshot(tmp_path, "2026-10-02T10:00:00Z", 2, None, "two")

    result = snapshot_at(tmp_path, "2026-10-01T18:00:00Z")

    assert result["snapshot"]["snapshot_id"] == first["snapshot_id"]
    assert result["nodes"][0]["attributes"]["title"] == "one"


def test_snapshot_at_requires_an_available_historical_observation(tmp_path):
    make_snapshot(tmp_path, "2026-10-02T10:00:00Z", 2, None, "two")

    try:
        snapshot_at(tmp_path, "2026-10-01T18:00:00Z")
    except TemporalQueryError as exc:
        assert "at or before" in str(exc)
    else:
        raise AssertionError("query before first snapshot must fail")


def test_between_and_changes_only_are_deterministic(tmp_path):
    first = make_snapshot(tmp_path, "2026-10-01T10:00:00Z", 1, 2, "one")
    second = make_snapshot(tmp_path, "2026-10-02T10:00:00Z", 2, 3, "two")
    third = make_snapshot(tmp_path, "2026-10-03T10:00:00Z", 3, None, "three")
    fourth = make_snapshot(tmp_path, "2026-10-04T10:00:00Z", 4, None, "three", delta_counts={})

    selected = snapshots_between(tmp_path, "2026-10-01T00:00:00Z", "2026-10-02T23:59:59Z")
    assert [row["snapshot_id"] for row in selected] == [first["snapshot_id"], second["snapshot_id"]]

    between = between_projection(tmp_path, "2026-10-01T00:00:00Z", "2026-10-04T23:59:59Z")
    assert between["event_count"] == 4

    result = changes_between(tmp_path, "2026-10-01T00:00:00Z", "2026-10-04T23:59:59Z")
    assert result["event_count"] == 3
    assert result["changes_only"] is True
    assert [event["snapshot_id"] for event in result["events"]] == [
        first["snapshot_id"], second["snapshot_id"], third["snapshot_id"]
    ]
    assert result["events"][1]["delta"]["counts"]["nodes_changed"] == 1
    assert fourth["snapshot_id"] not in [event["snapshot_id"] for event in result["events"]]


def test_timeline_is_sorted_by_observation_time(tmp_path):
    first = make_snapshot(tmp_path, "2026-10-02T10:00:00Z", 2, 3, "two")
    second = make_snapshot(tmp_path, "2026-10-01T10:00:00Z", 1, 2, "one")

    result = temporal_timeline(tmp_path)
    assert [row["snapshot_id"] for row in result["snapshots"]] == [
        second["snapshot_id"], first["snapshot_id"]
    ]
