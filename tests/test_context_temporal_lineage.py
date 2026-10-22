import json
from pathlib import Path

import pytest

from scripts.ci.verify_context_temporal_lineage import validate


def event(start, next_page, snapshot, observed, sha="a" * 40, previous=None):
    return {
        "schema": "context-relationship-temporal/v1",
        "event": "OBSERVED",
        "coverage": "PARTIAL_CONTINUATION_REQUIRED" if next_page is not None else "COMPLETE",
        "history_window": {"start_page": start, "next_start_page": next_page},
        "observed_at": observed,
        "previous_coverage": None,
        "previous_snapshot_id": previous,
        "snapshot_id": snapshot,
        "source_ref": "master",
        "source_sha": sha,
    }


def write_case(tmp_path: Path, events: list[dict], manifest_event: dict):
    lineage = tmp_path / "lineage.jsonl"
    lineage.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "history_window": manifest_event["history_window"],
        "latest_observed_at": manifest_event["observed_at"],
    }), encoding="utf-8")
    return lineage, manifest


def test_accepts_monotonic_page_continuation(tmp_path):
    events = [
        event(2, 3, "s2", "2026-10-02T12:00:00Z"),
        event(3, 4, "s3", "2026-10-02T18:00:00Z", previous="s2"),
        event(4, 5, "s4", "2026-10-02T23:00:00Z", previous="s3"),
    ]
    lineage, manifest = write_case(tmp_path, events, events[-1])
    result = validate(lineage, manifest)
    assert result["status"] == "VALIDATED"
    assert result["next_start_page"] == 5


def test_rejects_page_skip(tmp_path):
    events = [
        event(2, 3, "s2", "2026-10-02T12:00:00Z"),
        event(4, 5, "s4", "2026-10-02T23:00:00Z", previous="s2"),
    ]
    lineage, manifest = write_case(tmp_path, events, events[-1])
    with pytest.raises(ValueError, match="discontinuity"):
        validate(lineage, manifest)


def test_rejects_manifest_drift(tmp_path):
    events = [
        event(2, 3, "s2", "2026-10-02T12:00:00Z"),
        event(3, 4, "s3", "2026-10-02T18:00:00Z", previous="s2"),
    ]
    lineage, manifest = write_case(tmp_path, events, events[-1])
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["history_window"]["next_start_page"] = 99
    manifest.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="manifest next_start_page"):
        validate(lineage, manifest)



def test_accepts_new_page_one_backfill_after_complete_window(tmp_path):
    events = [
        event(2, 3, "s2", "2026-10-02T12:00:00Z"),
        event(3, None, "s3", "2026-10-02T18:00:00Z", previous="s2"),
        event(1, 2, "s1-restart", "2026-10-03T12:00:00Z", previous="s3"),
    ]
    lineage, manifest = write_case(tmp_path, events, events[-1])
    result = validate(lineage, manifest)
    assert result["status"] == "VALIDATED"
    assert result["first_start_page"] == 2
    assert result["last_start_page"] == 1
    assert result["next_start_page"] == 2


def test_rejects_new_window_after_complete_if_not_page_one(tmp_path):
    events = [
        event(2, None, "s2", "2026-10-02T12:00:00Z"),
        event(3, 4, "s3", "2026-10-02T18:00:00Z", previous="s2"),
    ]
    lineage, manifest = write_case(tmp_path, events, events[-1])
    with pytest.raises(ValueError, match="restart at page 1"):
        validate(lineage, manifest)
