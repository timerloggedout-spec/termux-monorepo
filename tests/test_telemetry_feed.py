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
DATA = ROOT / "apps" / "tribute-dashboard" / "data"


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
        "apps/tribute-dashboard/data/status.json",
        "apps/tribute-dashboard/data/quota.json",
        "apps/tribute-dashboard/data/quota-usage.json",
        "scripts/dashboards/workflow_observations.json",
        "scripts/dashboards/actions_observations.json",
        "apps/tribute-dashboard/data/puter-pool-runtime.json",
        "agent_telemetry_stream.json",
    }
    assert set(feed["data"]) == {"golden", "executions", "actions",
                                 "outcomes", "quota", "provider_runtime"}


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


def test_puter_pool_runtime_is_projected_with_task_correlation_and_unknown_quota(tmp_path):
    feed = _collect(tmp_path)
    runtime = json.loads((DATA / "puter-pool-runtime.json").read_text())
    projected = feed["data"]["provider_runtime"]
    assert projected["provider_id"] == "g4f.puter"
    assert projected["observed_at"] == runtime["observed_at"]
    assert projected["correlation"] == runtime["correlation"]
    assert projected["quota"]["status"] == "unknown"
    assert projected["quota"]["used"] is None
    assert projected["quota"]["limit"] is None
    assert isinstance(projected["recent_requests"], list)


def test_recent_puter_inference_events_project_task_correlation_without_payloads(tmp_path, monkeypatch):
    import shutil
    from scripts.dashboards import telemetry_feed as module

    for rel in (module.STATUS, module.QUOTA, module.QUOTA_USAGE,
                module.OBSERVATIONS, module.ACTIONS_OBS, module.PROVIDER_RUNTIME):
        source = ROOT / rel
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    event = {
        "schema_version": "eps.v1",
        "event_type": "provider.inference.completed",
        "occurred_at": "2026-11-23T12:00:00.123456Z",
        "provider": "g4f/Puter",
        "entity_id": "g4f.puter",
        "provider_id": "g4f.puter",
        "attributes": {
            "request_id": "request-77",
            "exact_model_id": "model-a",
            "outcome": "success",
            "latency_ms": 180,
            "input_tokens": 12,
            "output_tokens": 24,
            "task_or_entry_ref": "QUE-77",
            "doe_run_id": "DOE-77",
            "workflow_run_id": "GHA-77",
            "run_attempt": 1,
            "temporal_workflow_id": "puter-pool-observability",
            "temporal_run_id": "temporal-77",
            "prompt": "PRIVATE PROMPT",
            "completion": "PRIVATE COMPLETION",
        },
    }
    (tmp_path / module.AGENT_STREAM).write_text(json.dumps(event) + "\n", encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    feed = module.collect()
    recent = feed["data"]["provider_runtime"]["recent_requests"]
    assert recent[0]["request_id"] == "request-77"
    assert recent[0]["task_or_entry_ref"] == "QUE-77"
    assert recent[0]["doe_run_id"] == "DOE-77"
    assert recent[0]["temporal_workflow_id"] == "puter-pool-observability"
    assert "PRIVATE PROMPT" not in json.dumps(feed)
    assert "PRIVATE COMPLETION" not in json.dumps(feed)
