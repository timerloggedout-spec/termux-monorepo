"""Tests for autoQuotaCadence derivation (QUE #5160, clause 7).

Fixtures/mocks only: no live provider calls, no credentials, no network.
The derivation is pure -- derive() takes dicts and returns a dict.
"""

import ast
import importlib.util
import json
from datetime import datetime, timezone

import pytest

from scripts.ops import auto_quota_cadence as aqc

NOW = datetime(2026, 11, 12, 16, 0, tzinfo=timezone.utc)
DAY = "2026-11-12"


def _arm(arm_id, *, harness="generic-agent-loop", url="https://api.example.test/v1/chat",
         budget=None, record="example.api", selectable=True, status="candidate"):
    return {
        "arm_id": arm_id,
        "selectable": selectable,
        "status": status,
        "harness": harness,
        "harness_ref": "scripts/ops/build_arm_harness.py",
        "endpoint": {
            "provider": "example",
            "route_id": f"example::{arm_id}",
            "url": url,
        },
        "budget": budget if budget is not None else {
            "class": "free-tier",
            "daily_total": 20,
            "spendable_primary": 16,
            "quota_metric_source": f"AUTO QUOTA LEDGER (#5152); ops/quota/registry.json record {record}",
        },
    }


def _registry(arms, *, census_verdict="eligible", run_id=43045718809,
              generated_at="2026-11-12T15:00:00Z"):
    return {
        "schema": "build-arms/v1",
        "arms": arms,
        "selection_rule": "registry order, free-tier first",
    }


def _census(arm_ids, *, verdict="eligible", generated_at="2026-11-12T15:00:00Z",
            run_id=43045718809, terminal=None):
    doc = {"schema": "arm-census/v1", "generated_at": generated_at, "arms": []}
    if run_id is not None:
        doc["run_id"] = run_id
    for arm_id in arm_ids:
        row = {"arm_id": arm_id, "verdict": verdict,
               "quota_terminal": {"terminal": False}}
        if terminal and arm_id in terminal:
            row["quota_terminal"] = {"terminal": True, "date": DAY}
        doc["arms"].append(row)
    return doc


def _quota_registry(record_ids):
    return {
        "schema": "quota.registry.v2",
        "services": [{"id": rid, "provider": "example"} for rid in record_ids],
    }


def _snapshot(*, generated_at="2026-11-12T15:30:00Z", arms=None, budgets=None,
              coverage=None):
    return {
        "schema": "ledger-snapshot/v1",
        "generated_at": generated_at,
        "arms": arms or {},
        "budgets": budgets or {},
        "coverage": coverage or {"complete": True, "stamped_at": generated_at,
                                 "last_quota_terminal": None},
    }


def _budget(arm_id, *, total=20, spendable=16, reset_window="midnight PT",
            reset_tz="America/Los_Angeles"):
    return {arm_id: {"daily_total": total, "spendable_primary": spendable,
                     "reserved_escalation": 4, "reset_window": reset_window,
                     "reset_tz": reset_tz}}


def _derive(arms, census, registry, snapshot=None, previous=None):
    return aqc.derive(arms, census, registry, snapshot, previous, NOW)


def _row(feed, arm_id):
    return next(a for a in feed["arms"] if a["arm_id"] == arm_id)


# --- gap 1: no snapshot -> ledger unavailable, defer on quota_unknown ---

def test_no_snapshot_defers_everything_quota_unknown():
    arms = [_arm("alpha"), _arm("beta")]
    feed = _derive(_registry(arms), _census(["alpha", "beta"]),
                   _quota_registry(["example.api"]), None)
    assert feed["ledger_read"]["status"] == "unavailable"
    assert feed["ledger_read"]["reason"] == "ledger_snapshot_absent"
    assert feed["pool"]["eligible"] == []
    for row in feed["arms"]:
        assert "quota_unknown" in row["defer_reasons"]
        assert "reset_window_unknown" in row["defer_reasons"]
    assert feed["usage_record"]["arms"] == {}
    assert feed["usage_record"]["coverage"]["complete"] is False


def test_stale_snapshot_treated_as_absent():
    arms = [_arm("alpha")]
    snap = _snapshot(generated_at="2026-11-12T14:00:00Z",  # 2h old > 3600s
                     arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    assert feed["ledger_read"]["status"] == "unavailable"
    assert feed["ledger_read"]["reason"] == "snapshot_stale"
    assert "quota_unknown" in _row(feed, "alpha")["defer_reasons"]


def test_missing_arm_draws_in_snapshot_is_quota_unknown():
    arms = [_arm("alpha"), _arm("beta")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets={**_budget("alpha"), **_budget("beta")})
    feed = _derive(_registry(arms), _census(["alpha", "beta"]),
                   _quota_registry(["example.api"]), snap)
    assert _row(feed, "alpha")["status"] == "eligible"
    assert _row(feed, "alpha")["headroom"] == 16
    assert "quota_unknown" in _row(feed, "beta")["defer_reasons"]


# --- fresh snapshot: eligibility, headroom, reset ---

def test_fresh_snapshot_makes_arm_eligible_with_headroom_and_reset():
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 3}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    row = _row(feed, "alpha")
    assert row["status"] == "eligible"
    assert row["headroom"] == 13  # 16 spendable_primary - 3 draws
    assert row["reset_window"] == "midnight PT"
    assert row["reset_tz"] == "America/Los_Angeles"
    assert feed["pool"]["eligible"] == ["alpha"]
    assert feed["usage_record"]["arms"]["alpha"][DAY]["draws"] == 3
    assert feed["usage_record"]["coverage"]["complete"] is True


def test_exhausted_headroom_defers():
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 16}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    assert "quota_exhausted" in _row(feed, "alpha")["defer_reasons"]


def test_reset_fields_never_inferred_from_registry_prose():
    # Snapshot budgets without reset fields: the registry's prose reset
    # ("midnight") must NOT be parsed into a window -- defer, don't infer.
    arms = [_arm("alpha")]
    budgets = {"alpha": {"daily_total": 20, "spendable_primary": 16}}
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}}, budgets=budgets)
    feed = _derive(_registry(arms), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    row = _row(feed, "alpha")
    assert "reset_window_unknown" in row["defer_reasons"]
    assert "reset_tz_unknown" in row["defer_reasons"]
    assert row["reset_window"] == "unknown"


def test_reset_timezone_stamped_verbatim_from_snapshot():
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha", reset_window="00:00-01:00",
                                    reset_tz="America/Los_Angeles"))
    feed = _derive(_registry(arms), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    row = _row(feed, "alpha")
    assert row["status"] == "eligible"
    assert row["reset_window"] == "00:00-01:00"
    assert row["reset_tz"] == "America/Los_Angeles"


def test_quota_unbudgeted_when_no_numeric_total():
    arm = _arm("alpha", budget={"class": "free-tier", "daily_total": None,
                                "quota_metric_source": "AUTO QUOTA LEDGER (#5152); "
                                "ops/quota/registry.json record example.api"})
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets={"alpha": {"daily_total": None}})
    feed = _derive(_registry([arm]), _census(["alpha"]),
                   _quota_registry(["example.api"]), snap)
    assert "quota_unbudgeted" in _row(feed, "alpha")["defer_reasons"]


# --- census / environment ---

def test_stale_census_defers():
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms),
                   _census(["alpha"], generated_at="2026-11-10T15:00:00Z"),
                   _quota_registry(["example.api"]), snap)
    assert "census_stale" in _row(feed, "alpha")["defer_reasons"]


def test_missing_census_generation_defers():
    arms = [_arm("alpha")]
    feed = _derive(_registry(arms), _census(["alpha"], generated_at=None),
                   _quota_registry(["example.api"]), None)
    assert "census_stale" in _row(feed, "alpha")["defer_reasons"]


def test_sandbox_only_census_defers_availability_env_unknown():
    # No run_id on the census feed: provenance unknown (sandbox-only is
    # not admission evidence) -> defer, don't treat as Actions evidence.
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms), _census(["alpha"], run_id=None),
                   _quota_registry(["example.api"]), snap)
    assert feed["census"]["availability_env"] == "unknown"
    assert "availability_env_unknown" in _row(feed, "alpha")["defer_reasons"]


def test_quota_terminal_today_defers():
    arms = [_arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha"))
    feed = _derive(_registry(arms),
                   _census(["alpha"], terminal={"alpha"}),
                   _quota_registry(["example.api"]), snap)
    assert "quota_terminal_today" in _row(feed, "alpha")["defer_reasons"]


# --- route / catalog ---

def test_route_dead_when_no_url_and_no_harness_ref():
    arm = _arm("alpha", url=None)
    arm["harness_ref"] = None
    feed = _derive(_registry([arm]), _census(["alpha"]),
                   _quota_registry(["example.api"]), None)
    assert "route_dead" in _row(feed, "alpha")["defer_reasons"]


def test_duplicate_route_id_defers_second_arm():
    a1 = _arm("alpha")
    a2 = _arm("beta")
    a2["endpoint"]["route_id"] = a1["endpoint"]["route_id"]
    feed = _derive(_registry([a1, a2]), _census(["alpha", "beta"]),
                   _quota_registry(["example.api"]), None)
    assert "duplicate_route" not in _row(feed, "alpha")["defer_reasons"]
    assert "duplicate_route" in _row(feed, "beta")["defer_reasons"]


def test_entitlement_unknown_when_no_registry_record():
    arm = _arm("alpha", record="missing.record")
    feed = _derive(_registry([arm]), _census(["alpha"]),
                   _quota_registry(["example.api"]), None)
    assert "entitlement_unknown" in _row(feed, "alpha")["defer_reasons"]


# --- rotation / gemini / zero arms ---

def test_rotation_avoids_consecutive_same_arm():
    arms = [_arm("alpha"), _arm("beta")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}},
                           "beta": {DAY: {"draws": 0}}},
                     budgets={**_budget("alpha"), **_budget("beta")})
    previous = {"rotation": {"last_selected_arm": "alpha"}}
    feed = _derive(_registry(arms), _census(["alpha", "beta"]),
                   _quota_registry(["example.api"]), snap, previous)
    assert feed["pool"]["eligible"] == ["beta", "alpha"]


def test_rotation_free_tier_before_credit_funded():
    credit = _arm("credit", budget={"class": "credit-funded", "daily_total": 10,
                                    "quota_metric_source": "AUTO QUOTA LEDGER (#5152); "
                                    "ops/quota/registry.json record example.api"})
    arms = [credit, _arm("alpha")]
    snap = _snapshot(arms={"credit": {DAY: {"draws": 0}},
                           "alpha": {DAY: {"draws": 0}}},
                     budgets={"credit": {"daily_total": 10, "reset_window": "daily",
                                         "reset_tz": "UTC"},
                              **_budget("alpha")})
    feed = _derive(_registry(arms), _census(["credit", "alpha"]),
                   _quota_registry(["example.api"]), snap)
    assert feed["pool"]["eligible"] == ["alpha", "credit"]


def test_gemini_unavailable_does_not_block_pool_generation():
    # Gemini-class arm fails census; the other arm still derives eligible.
    gemini = _arm("gemini-cli", harness="run-gemini-cli",
                  url=None, record="gemini.api_free")
    gemini["harness_ref"] = ".github/workflows/build-dispatch.yml"
    arms = [gemini, _arm("alpha")]
    snap = _snapshot(arms={"alpha": {DAY: {"draws": 0}}},
                     budgets=_budget("alpha"))
    census = _census(["alpha", "gemini-cli"])
    census["arms"][1]["verdict"] = "failed"
    feed = _derive(_registry(arms), census,
                   _quota_registry(["example.api", "gemini.api_free"]), snap)
    assert feed["pool"]["eligible"] == ["alpha"]
    assert "census_not_passed" in _row(feed, "gemini-cli")["defer_reasons"]


def test_zero_eligible_arms_still_generates():
    arms = [_arm("alpha")]
    feed = _derive(_registry(arms), _census(["alpha"], verdict="failed"),
                   _quota_registry(["example.api"]), None)
    assert feed["schema"] == "pool-cadence/v1"
    assert feed["pool"]["eligible"] == []
    assert feed["pool"]["eligible_count"] == 0


# --- no inference: static source scan ---

def test_derivation_module_makes_no_network_or_subprocess_calls():
    src = open("scripts/ops/auto_quota_cadence.py").read()
    tree = ast.parse(src)
    banned = {"socket", "urllib", "requests", "subprocess", "http"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned), f"banned imports: {imported & banned}"


def test_snapshot_schema_rejected(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema": "other/v1", "generated_at": NOW.isoformat()}))
    out = tmp_path / "out.json"
    usage = tmp_path / "usage.json"
    arms = tmp_path / "arms.json"
    arms.write_text(json.dumps(_registry([_arm("alpha")])))
    census = tmp_path / "census.json"
    census.write_text(json.dumps(_census(["alpha"])))
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps(_quota_registry(["example.api"])))
    rc = aqc.main(["--arms", str(arms), "--census", str(census),
                   "--registry", str(reg), "--snapshot", str(bad),
                   "--now", NOW.isoformat(), "--out", str(out),
                   "--usage-out", str(usage)])
    assert rc == 2


def test_main_writes_feed_and_usage_files(tmp_path):
    arms = tmp_path / "arms.json"
    arms.write_text(json.dumps(_registry([_arm("alpha")])))
    census = tmp_path / "census.json"
    census.write_text(json.dumps(_census(["alpha"])))
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps(_quota_registry(["example.api"])))
    out = tmp_path / "pool.json"
    usage = tmp_path / "usage.json"
    rc = aqc.main(["--arms", str(arms), "--census", str(census),
                   "--registry", str(reg), "--now", NOW.isoformat(),
                   "--out", str(out), "--usage-out", str(usage)])
    assert rc == 0
    feed = json.loads(out.read_text())
    assert feed["schema"] == "pool-cadence/v1"
    assert "sources" in feed and feed["sources"]["arms_sha256"]
    usage_rec = json.loads(usage.read_text())
    assert usage_rec["coverage"]["complete"] is False
