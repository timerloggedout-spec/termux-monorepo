"""Dispatch-tree feed: extraction pins + honesty rules.

The collector parses quota-dispatch-tree.yml — if the tree's guard,
thresholds, or matrix change shape, these tests fail loudly instead of
the feed silently drifting from the workflow it describes.
"""
import importlib.util
import json
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
    rule = mod.parse_tree((ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml").read_text())
    assert rule["guard_threshold"] == 6
    stale = {out: s["threshold_min"] for out, s in rule["stale"].items()}
    assert stale["dispatch_hw_refresh"] == 75
    assert stale["dispatch_hw_pair"] == 150
    assert stale["dispatch_hw_execute"] == 300
    assert stale["dispatch_hw_assist"] == 450
    # q6 is dynamic: threshold_min is None at parse time, derived in build
    assert rule["stale"]["dispatch_q6"]["threshold_min"] is None
    assert rule["stale"]["dispatch_q6"]["measured_workflows"] == ["provider-availability.yml"]


def test_parse_tree_matrix_and_manifest_not_lane_staleness():
    mod = _load()
    rule = mod.parse_tree((ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml").read_text())
    lanes = {e["lane"]: e["output"] for e in rule["lanes"]}
    assert len(lanes) == 32
    assert lanes["help-wanted-status-refresh"] == "dispatch_hw_refresh"
    assert lanes["help-wanted-scout"] == "dispatch_hw_pair"
    assert lanes["provider-availability"] == "dispatch_q6"
    # bridge/probe thresholds are manifest ages, never lane staleness
    assert "dispatch_bridge" not in rule["stale"]
    assert "dispatch_probe" not in rule["stale"]
    assert rule["manifest_stale"]["dispatch_bridge"]["threshold_min"] == 30


def test_feed_shape_and_honesty():
    feed_path = ROOT / "apps" / "help-wanted-dashboard" / "data" / "dispatch-tree-feed.json"
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
