"""Dispatch-tree feed: extraction pins + honesty rules.

The collector parses quota-dispatch-tree.yml — if the tree's guard,
thresholds, or matrix change shape, these tests fail loudly instead of
the feed silently drifting from the workflow it describes.
"""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "dispatch_tree_feed", ROOT / "scripts" / "dashboards" / "dispatch_tree_feed.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_tree_guard_and_thresholds():
    mod = _load()
    workflow = (ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml").read_text()
    admission = (ROOT / "scripts" / "ci" / "dispatch_admission.js").read_text()
    rule = mod.parse_tree(workflow, admission)
    assert rule["guard_threshold"] == 6
    stale = {out: s["threshold_min"] for out, s in rule["stale"].items()}
    assert stale["dispatch_hw_refresh"] == 75
    assert stale["dispatch_hw_pair"] == 150
    assert stale["dispatch_hw_execute"] == 300
    assert stale["dispatch_hw_assist"] == 450
    assert stale["dispatch_reconciliation"] == 75
    assert stale["dispatch_context_backfill"] == 75
    assert rule["stale"]["dispatch_reconciliation"]["measured_workflows"] == ["reconciliation-engine.yml"]
    assert rule["stale"]["dispatch_context_backfill"]["measured_workflows"] == ["context-relationship-backfill.yml"]
    # q6 is dynamic: threshold_min is None at parse time, derived in build
    assert rule["stale"]["dispatch_q6"]["threshold_min"] is None
    assert rule["stale"]["dispatch_q6"]["measured_workflows"] == ["provider-availability.yml"]


def test_parse_tree_matrix_and_manifest_not_lane_staleness():
    mod = _load()
    workflow = (ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml").read_text()
    admission = (ROOT / "scripts" / "ci" / "dispatch_admission.js").read_text()
    rule = mod.parse_tree(workflow, admission)
    lanes = {e["lane"]: e["output"] for e in rule["lanes"]}
    assert len(lanes) == 31
    assert lanes["tribute-status-refresh"] == "dispatch_hw_refresh"
    assert lanes["tribute-scout"] == "dispatch_hw_pair"
    assert lanes["provider-availability"] == "dispatch_q6"
    assert lanes["reconciliation-engine"] == "dispatch_reconciliation"
    assert lanes["context-relationship-backfill"] == "dispatch_context_backfill"
    # bridge/probe thresholds are manifest ages, never lane staleness
    assert "dispatch_bridge" not in rule["stale"]
    assert "dispatch_probe" not in rule["stale"]
    assert rule["manifest_stale"]["dispatch_bridge"]["threshold_min"] == 30
    assert lanes["agent-runtime-stall-watch"] == "dispatch_stall_watch"


def test_lane_state_matches_dispatch_freshness_and_admission():
    from datetime import datetime, timezone

    mod = _load()
    read_at = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
    rule = {
        "outputs": {"dispatch_reconciliation": "reconciliationStaleMin > 75"},
        "stale": {
            "dispatch_reconciliation": {
                "threshold_min": 75,
                "measured_workflows": ["reconciliation-engine.yml"],
            }
        },
    }
    entry = {"lane": "reconciliation-engine", "output": "dispatch_reconciliation"}
    active = mod.lane_state(entry, rule, {
        "reconciliation-engine": [{
            "status": "in_progress", "created_at": "2026-11-19T09:00:00Z"
        }]
    }, read_at)
    assert active["measured_age_min_at_read"] == 0
    assert active["due_at_read"] is False
    assert active["admission_gated"] is True

    completed = mod.lane_state(entry, rule, {
        "reconciliation-engine": [{
            "status": "completed",
            "created_at": "2026-11-19T09:00:00Z",
            "updated_at": "2026-11-19T10:40:00Z",
        }]
    }, read_at)
    assert completed["measured_age_min_at_read"] == 80
    assert completed["due_at_read"] is True

    missing = mod.lane_state(entry, rule, {}, read_at)
    assert missing["measured_age_min_at_read"] == 1e9
    assert missing["due_at_read"] is True

    # Existing help-wanted and q6 lanes retain creation-age semantics,
    # including active runs and recently completed runs.
    legacy_rule = {
        "outputs": {"dispatch_hw_refresh": "firstCycle || hwRefreshStaleMin > 75"},
        "stale": {
            "dispatch_hw_refresh": {
                "variable": "hwRefreshStaleMin",
                "threshold_min": 75,
                "measured_workflows": ["tribute-status-refresh.yml"],
            }
        },
    }
    legacy_entry = {"lane": "tribute-status-refresh", "output": "dispatch_hw_refresh"}
    legacy_completed = mod.lane_state(legacy_entry, legacy_rule, {
        "tribute-status-refresh": [{
            "status": "completed",
            "created_at": "2026-11-19T10:00:00Z",
            "updated_at": "2026-11-19T11:50:00Z",
        }]
    }, read_at)
    assert legacy_completed["measured_age_min_at_read"] == 120
    assert legacy_completed["due_at_read"] is True
    legacy_active = mod.lane_state(legacy_entry, legacy_rule, {
        "tribute-status-refresh": [{
            "status": "in_progress", "created_at": "2026-11-19T10:00:00Z"
        }]
    }, read_at)
    assert legacy_active["measured_age_min_at_read"] == 120
    assert legacy_active["due_at_read"] is True

    exempt = mod.lane_state(
        {"lane": "tribute-status-refresh", "output": "dispatch_hw_refresh"},
        {"outputs": {"dispatch_hw_refresh": "firstCycle"}, "stale": {}},
        {}, read_at,
    )
    assert exempt["admission_gated"] is False


def test_feed_shape_and_honesty():
    feed_path = ROOT / "apps" / "tribute-dashboard" / "data" / "dispatch-tree-feed.json"
    feed = json.loads(feed_path.read_text())
    assert feed["schema"] == "dispatch-tree-feed/v1"
    data = feed["data"]
    assert data["lane_count"] == len(data["lanes"]) == 32
    adm = data["admission"]
    assert adm["guard_threshold"] == 6
    assert adm["samples"], "sample series must start at first collection"
    # samples are append-only readings keyed by read_at, never backfilled
    stamps = [s["read_at"] for s in adm["samples"]]
    assert stamps == sorted(stamps)
    for lane in data["lanes"]:
        if lane["staleness"] is None:
            assert lane["due_at_read"] is None
        assert lane["rule_expression"], "every lane carries its extracted rule"
    gap_ids = {g["id"] for g in feed["gaps"]}
    assert "busy-history-starts-at-first-collection" in gap_ids
    assert data["supabase_verdicts"]["anon_select_visible_rows"] == 0


class TestDispatchTreeFeed(unittest.TestCase):
    """Expose the pytest-style contract functions to stdlib unittest CI."""

    def test_parse_tree_guard_and_thresholds(self):
        test_parse_tree_guard_and_thresholds()

    def test_parse_tree_matrix_and_manifest_not_lane_staleness(self):
        test_parse_tree_matrix_and_manifest_not_lane_staleness()

    def test_lane_state_matches_dispatch_freshness_and_admission(self):
        test_lane_state_matches_dispatch_freshness_and_admission()

    def test_feed_shape_and_honesty(self):
        test_feed_shape_and_honesty()
