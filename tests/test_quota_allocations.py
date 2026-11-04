"""Focused quota allocations (issue #1884): config validity, the owner
setting, and the feed/Gantt shapes. Offline; no provider calls."""
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("quota_allocations", ROOT / "scripts/quota_allocations.py")
qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(qa)

CFG = json.loads((ROOT / "ops/quota/allocations.json").read_text())
REG = json.loads((ROOT / "ops/quota/registry.json").read_text())
READINGS = json.loads((ROOT / "apps/tribute-dashboard/data/quota.json").read_text())
COUNTDOWNS = json.loads((ROOT / "apps/tribute-dashboard/data/challenge-countdowns-feed.json").read_text())
NOW = datetime(2026, 10, 28, 2, 0, tzinfo=timezone.utc)

REGMAP = {svc["id"]: svc for svc in REG["services"]}


def dead_entitlement(pool):
    """Standing exception (quota-specialist ruling 2026-11-03, encoding
    PR #4574's intent): a pool whose backing registry records are ALL
    limit-0 has nothing to allocate - entitlement death, not an owner
    allocation choice. Such pools carry winning 0/none and full
    reserve; the 100-standing invariant does not apply. The rule names
    no provider and self-heals: if the entitlement is ever established
    (any backing limit > 0), the pool returns under the invariant."""
    services = pool.get("services") or []
    return bool(services) and all(
        REGMAP[sid]["limit"] == 0 for sid in services if sid in REGMAP)



def test_config_is_valid_against_live_registry():
    assert qa.validate(CFG, REG) == []


def test_github_pool_carries_the_repo_replay_app_slice():
    # Planner trigger app_slice_assignment:repo-replay (allocation-plan.json,
    # PR #2450): replay/migration load sits on the AppID buckets, the PAT
    # service is fallback-only with no routine draw.
    gh = next(p for p in CFG["pools"] if p["id"] == "github")
    slices = {s["project"]: s for s in gh.get("slices", []) if "project" in s}
    rr = slices["repo-replay"]
    assert rr["primary_services"] == ["github.api.app_collector", "github.api.app_publisher"]
    assert rr["fallback_service"] == "github.api.user_token"
    assert rr["fallback_mode"] == "fallback-only"
    assert rr["routine_draw_on_fallback"] is False


def test_validator_rejects_a_slice_pointing_outside_its_pool():
    import copy
    bad = copy.deepcopy(CFG)
    gh = next(p for p in bad["pools"] if p["id"] == "github")
    gh["slices"] = [{"project": "repo-replay",
                     "primary_services": ["vercel.deployments"],
                     "fallback_service": "github.api.user_token",
                     "fallback_mode": "fallback-only",
                     "routine_draw_on_fallback": False,
                     "date": "2026-10-30", "reason": "synthetic"}]
    errs = qa.validate(bad, REG)
    assert any("not a service of this pool" in e for e in errs), errs


def test_enroll_batch_lane_slices_are_landed_with_claims():
    # #1884 ENROLL batch 1: lane-keyed slices carry their claim comment id;
    # the github pool holds the batch plus the repo-replay project slice.
    gh = next(p for p in CFG["pools"] if p["id"] == "github")
    lanes = {s["lane"]: s for s in gh["slices"] if "lane" in s}
    assert len(lanes) == 48, sorted(lanes)
    for lane, s in lanes.items():
        assert isinstance(s["claim"], int) and s["claim"] > 6_000_000_000, lane
        assert s["primary_services"], lane
        assert s["routine_draw_on_fallback"] is False, lane
    qs = lanes["quota-specialist"]
    assert qs["primary_services"] == ["github.api.app_publisher", "github.api.app_collector"]
    assert qs["fallback_service"] == "github.api.user_token"
    assert qs["fallback_mode"] == "fallback-only"
    pat = lanes["gap-finder"]
    assert pat["primary_services"] == ["github.api.user_token"]
    assert pat["fallback_mode"] == "none" and pat["fallback_service"] is None
    p201 = next(p for p in CFG["pools"] if p["id"] == "platform201")
    assert [s["lane"] for s in p201["slices"]] == ["platform201-status"]
    goog = next(p for p in CFG["pools"] if p["id"] == "google")
    assert [s["lane"] for s in goog["slices"]] == ["google-ai-studio"]
    assert goog["slices"][0]["primary_services"] == ["gemini.api_free"]
    ver = next(p for p in CFG["pools"] if p["id"] == "vercel")
    assert [s["lane"] for s in ver["slices"]] == ["vercel-specialist"]


def test_validator_rejects_none_mode_with_a_fallback_set():
    import copy
    bad = copy.deepcopy(CFG)
    gh = next(p for p in bad["pools"] if p["id"] == "github")
    s = next(x for x in gh["slices"] if x.get("lane") == "gap-finder")
    s["fallback_service"] = "github.api.github_token"
    errs = qa.validate(bad, REG)
    assert any("fallback_mode none but fallback_service is set" in e for e in errs), errs


def test_feed_surfaces_pool_slices():
    f = qa.build_feed(CFG, REG, READINGS, COUNTDOWNS, NOW)
    gh = next(p for p in f["pools"] if p["pool"] == "github")
    assert gh["slices"][0]["project"] == "repo-replay"
    p201 = next(p for p in f["pools"] if p["pool"] == "platform201")
    assert [s["lane"] for s in p201["slices"]] == ["platform201-status"]
    others = [p for p in f["pools"] if p["pool"] not in ("github", "platform201", "google", "vercel")]
    assert all(p["slices"] == [] for p in others)


def test_every_registry_service_is_pooled_or_explicitly_excluded():
    pooled = {s for p in CFG["pools"] for s in p["services"]}
    excluded = {e["id"] for e in CFG["excluded_services"]}
    assert pooled | excluded == {s["id"] for s in REG["services"]}
    assert not pooled & excluded


def test_owner_setting_winning_stands_at_100_elsewhere_leftover_only():
    for pool in CFG["pools"]:
        rows = {a["focus"]: a for a in pool["allocations"]}
        if pool["id"] == "github.codespaces":
            continue
        if dead_entitlement(pool):
            assert rows["winning"]["pct"] == 0 and rows["winning"]["mode"] == "none", pool["id"]
            for focus in ("repo-development", "research"):
                assert rows[focus]["pct"] == 0 and rows[focus]["mode"] == "leftover-only", pool["id"]
            assert qa.reserve_pct(pool) == 100, pool["id"]
            continue
        assert rows["winning"]["pct"] == 100 and rows["winning"]["mode"] == "standing", pool["id"]
        for focus in ("repo-development", "research"):
            assert rows[focus]["pct"] == 0 and rows[focus]["mode"] == "leftover-only", pool["id"]
        assert qa.reserve_pct(pool) == 0, pool["id"]


def test_boinc_is_leftover_only_only_on_github_provider_pools():
    for pool in CFG["pools"]:
        row = next(a for a in pool["allocations"] if a["focus"] == "boinc-donations")
        assert row["pct"] == 0
        if pool["id"].startswith("github.") and pool["id"] != "github.codespaces":
            assert row["mode"] == "leftover-only", pool["id"]
        else:
            assert row["mode"] == "none", pool["id"]


def test_codespaces_pool_is_excluded_with_full_reserve():
    pool = next(p for p in CFG["pools"] if p["id"] == "github.codespaces")
    assert any("excluded-interim" in c for c in pool["constraints"])
    assert all(a["pct"] == 0 and a["mode"] == "none" for a in pool["allocations"])
    assert qa.reserve_pct(pool) == 100


def test_validator_rejects_overcommit_and_unknowns():
    bad = json.loads(json.dumps(CFG))
    bad["pools"][0]["allocations"].append(
        {"focus": "research", "pct": 5, "mode": "standing", "date": "2026-10-27", "reason": "x"})
    assert any("> 100" in e for e in qa.validate(bad, REG))
    bad2 = json.loads(json.dumps(CFG))
    bad2["pools"][0]["services"].append("nope.service")
    assert any("unknown registry service" in e for e in qa.validate(bad2, REG))


def feed():
    return qa.build_feed(CFG, REG, READINGS, COUNTDOWNS, NOW)


def test_feed_carries_entitlement_allocations_reserve_and_countdowns():
    f = feed()
    assert f["schema"] == "quota-allocations-feed/v1" and f["issue"] == 1884
    assert {e["id"] for e in f["countdowns"]} >= {"D1", "D2", "D3", "D4"}
    aws = next(p for p in f["pools"] if p["pool"] == "aws.credits")
    svc = aws["services"][0]
    assert svc["service"] == "aws.account_credits"
    # Entitlement joins from the registry record — an owner-supplied /
    # documented figure, not an invented balance.
    assert svc["entitlement"] == {"limit": 200, "unit": "USD", "window": "one-time (6 months)"}
    for p in f["pools"]:
        standing = sum(a["pct"] for a in p["allocations"] if a["mode"] == "standing")
        assert standing + p["reserve_pct"] == 100


def test_feed_never_invents_focus_attribution():
    f = feed()
    for p in f["pools"]:
        assert p["observed_consumption_by_focus"] is None
    gh = next(p for p in f["pools"] if p["pool"] == "github")
    observed = {s["service"]: s["observed"] for s in gh["services"]}
    # Join canary: a probe-observed row, so the pin survives snapshot
    # promotions. (Was github.api.user_token == "ok" from the #1764
    # hand-promoted H0 row; the first converted-snapshot promotion
    # supersedes hand-promoted rows per QUOTA-PROJECTION-CONVERGENCE
    # procedure step 5, and the probe does not observe the PAT row.)
    assert observed["github.api.github_token"]["status"] in (
        "ok", "watch", "exhausted", "cap_tripped")  # from the public readings snapshot
    # No reading, no claim: the complete converted snapshot carries an
    # unobserved row for every record, so the no-claim shape is now an
    # unknown status with no observation time (was: observed is None,
    # when the snapshot carried no row for the service at all).
    assert observed["github.artifacts.retention"]["status"] == "unknown"
    assert observed["github.artifacts.retention"]["observed_at"] is None


def test_committed_feed_matches_config():
    committed = json.loads((ROOT / "apps/tribute-dashboard/data/quota-allocations-feed.json").read_text())
    assert committed["schema"] == "quota-allocations-feed/v1"
    assert [p["pool"] for p in committed["pools"]] == [p["id"] for p in CFG["pools"]]
    for cp, p in zip(committed["pools"], CFG["pools"]):
        assert cp["allocations"] == p["allocations"]
        assert cp["reserve_pct"] == qa.reserve_pct(p)


def test_gantt_rows_cover_every_pool_focus_plus_reserve():
    f = feed()
    rows = f["gantt"]
    assert len(rows) == len(CFG["pools"]) * (len(CFG["focuses"]) + 1)
    dead = {p["id"] for p in CFG["pools"] if dead_entitlement(p)}
    winning = [r for r in rows if r["focus"] == "winning" and r["pool"] != "github.codespaces" and r["pool"] not in dead]
    assert all(r["plan_pct"] == 100 and r["actual_pct"] is None for r in winning)
    dead_rows = [r for r in rows if r["focus"] == "winning" and r["pool"] in dead]
    assert all(r["plan_pct"] == 0 for r in dead_rows)
    assert max(r["plan_end"] for r in rows) == "2026-12-04T14:00:00-08:00"  # D4 close, from #1880 feed
    mermaid = qa.render_gantt_mermaid(f)
    assert "D4 window" in mermaid and "winning 100%" in mermaid


# ---- Admin Desk Plane 5: validate_shares / presets / gauge state ----

def _shares(pool_id):
    pool = next(p for p in CFG["pools"] if p["id"] == pool_id)
    return qa.current_shares(pool)


def test_validate_shares_owner_default_ok_no_warnings():
    verdict = qa.validate_shares("vercel", _shares("vercel"), REG, CFG)
    assert verdict == {"ok": True, "errors": [], "warnings": []}


def test_validate_shares_codes():
    bad_sum = {"winning": {"pct": 90, "mode": "standing"},
               "research": {"pct": 20, "mode": "standing"}}
    v = qa.validate_shares("vercel", bad_sum, REG, CFG)
    assert not v["ok"] and any(e["code"] == "SUM_EXCEEDS_100" for e in v["errors"])
    coupling = {"winning": {"pct": 5, "mode": "leftover-only"}}
    v = qa.validate_shares("vercel", coupling, REG, CFG)
    assert any(e["code"] == "MODE_PCT_COUPLING" for e in v["errors"])
    oob = {"winning": {"pct": 101, "mode": "standing"}}
    v = qa.validate_shares("vercel", oob, REG, CFG)
    assert any(e["code"] == "PCT_OUT_OF_BOUNDS" for e in v["errors"])
    v = qa.validate_shares("nope", {}, REG, CFG)
    assert any(e["code"] == "UNKNOWN_POOL" for e in v["errors"])
    boinc = dict(_shares("vercel"))
    boinc["boinc-donations"] = {"pct": 0, "mode": "leftover-only"}
    v = qa.validate_shares("vercel", boinc, REG, CFG)
    assert any(e["code"] == "BOINC_SCOPE" for e in v["errors"])


def test_validate_shares_locks_and_deviation_warning():
    changed = dict(_shares("github.codespaces"))
    changed["winning"] = {"pct": 50, "mode": "standing"}
    v = qa.validate_shares("github.codespaces", changed, REG, CFG)
    assert any(e["code"] == "POOL_LOCKED" for e in v["errors"])
    v = qa.validate_shares("github.codespaces", _shares("github.codespaces"), REG, CFG)
    assert v["ok"]  # identical shares on a locked pool are a no-op, not a change
    changed_fly = dict(_shares("fly"))
    changed_fly["winning"] = {"pct": 100, "mode": "standing"}
    v = qa.validate_shares("fly", changed_fly, REG, CFG)
    assert any(e["code"] == "POOL_LOCKED" for e in v["errors"])
    dev = dict(_shares("vercel"))
    dev["winning"] = {"pct": 80, "mode": "standing"}
    v = qa.validate_shares("vercel", dev, REG, CFG)
    assert v["ok"] and any(w["code"] == "DEVIATES_OWNER_SETTING" for w in v["warnings"])


def test_preset_round_trip_and_locked_change_refused():
    import copy
    method = {"route": "preset-create", "receipt_id": "t-1", "gate_id": None}
    preset = qa.make_preset(CFG, "unit-test", method)
    assert preset["schema"] == "quota-allocation-preset/v1"
    assert qa.validate_preset(preset, REG, CFG) == []
    new_cfg, errs = qa.apply_preset(CFG, preset,
                                    REG, {"route": "preset-apply",
                                          "receipt_id": "t-2", "gate_id": "g-1"})
    assert errs == [] and new_cfg["last_applied"]["preset"] == "unit-test"
    bad = copy.deepcopy(preset)
    fly = next(p for p in bad["config"]["pools"] if p["id"] == "fly")
    fly["allocations"][0]["pct"] = 100
    fly["allocations"][0]["mode"] = "standing"
    errs = qa.validate_preset(bad, REG, CFG)
    assert any("POOL_LOCKED" in e for e in errs)


def test_pool_state_shape_validated():
    import copy
    bad = copy.deepcopy(CFG)
    bad["pools"][0]["state"] = {"value": "bogus", "at": "2026-11-04T00:00:00Z",
                                "method": {"route": "lifecycle", "receipt_id": "r-1"}}
    assert any("state.value" in e for e in qa.validate(bad, REG))
    good = copy.deepcopy(CFG)
    good["pools"][0]["state"] = {"value": "paused", "at": "2026-11-04T00:00:00Z",
                                 "method": {"route": "lifecycle", "receipt_id": "r-1"}}
    assert qa.validate(good, REG) == []
    stopped = copy.deepcopy(CFG)
    stopped["pools"][0]["state"] = {"value": "stopped", "at": "2026-11-04T00:00:00Z",
                                    "method": {"route": "lifecycle", "receipt_id": "r-1"}}
    assert qa.validate(stopped, REG) == []
    retired = copy.deepcopy(CFG)
    retired["pools"][0]["state"] = {"value": "retired", "at": "2026-11-04T00:00:00Z",
                                    "method": {"route": "lifecycle", "receipt_id": "r-1"}}
    assert any("state.value" in e for e in qa.validate(retired, REG))
