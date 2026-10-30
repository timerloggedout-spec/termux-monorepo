"""Pins for the telemetry-viz Slice 1 feed collector.

The feed must shape only what the committed sources hold: counts equal
the sources, unobserved quota saturation stays absent (never 0), and
the executions proxy + its gaps are named, not hidden.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"


def _collect(tmp_path):
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "dashboards" / "telemetry_feed.py"),
         "--out-dir", str(tmp_path)],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return json.loads((tmp_path / "telemetry-feed.json").read_text())


def test_schema_and_envelope(tmp_path):
    feed = _collect(tmp_path)
    assert feed["schema"] == "telemetry-viz-feed/v1"
    assert feed["surface"] == "telemetry"
    assert {s["path"] for s in feed["sources"]} == {
        "apps/help-wanted-dashboard/data/status.json",
        "apps/help-wanted-dashboard/data/quota.json",
        "apps/help-wanted-dashboard/data/quota-usage.json",
        "scripts/dashboards/workflow_observations.json",
        "scripts/dashboards/actions_observations.json",
    }
    assert set(feed["data"]) == {"golden", "executions", "actions",
                                 "outcomes", "quota"}


def test_outcomes_equal_source(tmp_path):
    feed = _collect(tmp_path)
    status = json.loads((DATA / "status.json").read_text())
    o = feed["data"]["outcomes"]
    assert o["receipts"] == status["receipts"]
    assert o["kinds"] == status["kinds"]
    assert o["outcomes"] == status["outcomes"]
    assert feed["data"]["golden"]["receipts_total"] == status["receipts"]


def test_quota_counts_and_unobserved_saturation(tmp_path):
    feed = _collect(tmp_path)
    quota = json.loads((DATA / "quota.json").read_text())
    readings = quota["readings"]
    q = feed["data"]["quota"]
    assert q["readings_total"] == len(readings)
    measured = [r for r in readings
                if r.get("used") is not None and r.get("limit") is not None]
    assert len(q["measured"]) == len(measured)
    assert q["unmeasured_count"] == len(readings) - len(measured)
    if not measured:
        # Saturation is NOT OBSERVED: absent in golden, named as a gap.
        assert feed["data"]["golden"]["quota_saturation"] is None
        assert any("NOT OBSERVED" in g for g in feed["gaps"])


def test_executions_proxy_is_labeled(tmp_path):
    feed = _collect(tmp_path)
    obs = json.loads((ROOT / "scripts" / "dashboards"
                      / "workflow_observations.json").read_text())
    ex = feed["data"]["executions"]
    assert ex["kind"] == "committed_projection_proxy"
    assert ex["read_at"] == obs["read_at"]
    assert ex["total_runs_observed"] == sum(
        w["total_runs"] for w in obs["workflows"].values())
    # Slice 2 split the combined G1/G3 gap: executions proxy is the G3 gap,
    # Actions corpus is the separate "G1 partial" gap (pinned below).
    assert any(g.startswith("G3:") for g in feed["gaps"])


def test_committed_feed_matches_collector(tmp_path):
    """The committed feed is the collector's output, modulo collection
    timestamps.

    Sources refresh independently of the feed (e.g. the help-wanted
    status-refresh workflow commits status.json direct-to-master), so
    a fresh run's generated_at and sources[].stamped_at legitimately
    differ from the committed feed's. Only those two timestamp fields
    are stripped; every value in data/gaps/honesty_rules must match.
    (Web Design flag on PR #2431: status.json 06:22:26Z -> 06:24:46Z
    with no value differences exposed exactly this brittleness.)
    """
    fresh = _collect(tmp_path)
    committed = json.loads((DATA / "telemetry-feed.json").read_text())
    for feed in (fresh, committed):
        feed.pop("generated_at")
        for src in feed["sources"]:
            src.pop("stamped_at", None)
        # status.json's own generated_at is copied verbatim into two
        # data blocks (outcomes + lane_receipts); it is a source stamp,
        # not a value, so it is stripped with the other timestamps.
        feed["data"]["outcomes"].pop("generated_at", None)
        (feed["data"]["executions"].get("lane_receipts") or {}).pop(
            "generated_at", None)
    assert committed == fresh


def test_actions_block_matches_snapshot(tmp_path):
    """Slice 2: the actions block is the committed Actions snapshot,
    shaped — totals/workflows verbatim, join key named, G1 partial."""
    feed = _collect(tmp_path)
    snap = json.loads((ROOT / "scripts" / "dashboards"
                       / "actions_observations.json").read_text())
    a = feed["data"]["actions"]
    assert a["kind"] == "api_observations_snapshot"
    assert a["read_at"] == snap["read_at"]
    assert a["totals"] == snap["totals"]
    assert a["workflows"] == snap["workflows"]
    assert a["join"]["key"] == "run_id"
    assert "unexecuted" in a["join"]["status"]
    assert feed["data"]["golden"]["actions_runs_sampled"] == snap["totals"]["runs"]
    assert any(g.startswith("G1 partial") for g in feed["gaps"])
