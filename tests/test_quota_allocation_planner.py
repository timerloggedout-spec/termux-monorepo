import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import quota_allocation_planner as planner


REG = {"services": [
    {"id": "x.numeric", "limit": 100, "live": "api"},
    {"id": "x.status", "limit": None, "live": "api"},
    {"id": "x.unknown", "limit": None, "live": "none"},
]}
ALLOC = {"pools": [
    {"id": "x", "services": ["x.numeric", "x.status"]},
    {"id": "github", "services": ["x.unknown"]},
]}


def test_pool_class():
    assert planner.pool_class(REG["services"][:1]) == "A"
    assert planner.pool_class(REG["services"][1:2]) == "B"
    assert planner.pool_class(REG["services"][2:]) == "C"


def test_pacing_multiplier_rule():
    assert planner.pacing_multiplier(None, None, None) == 1.0
    assert planner.pacing_multiplier(100, 100, 0.5) == 0.0
    assert planner.pacing_multiplier(50, 100, 0.5) == 1.0
    assert planner.pacing_multiplier(10, 100, 0.9) == 2.0  # capped


def test_stranded_never_invented():
    assert planner.stranded_estimate(None, 100, 10) is None
    assert planner.stranded_estimate(10, None, 10) is None
    assert planner.stranded_estimate(10, 100, None) is None
    assert planner.stranded_estimate(10, 100, 30) == 60
    assert planner.stranded_estimate(95, 100, 30) == 0


def test_plan_states_and_triggers():
    readings = {"readings": [
        {"resource_id": "x.numeric", "used": 100, "limit": 100, "status": "exhausted"},
    ]}
    out = planner.plan(REG, ALLOC, readings)
    pool_x = next(p for p in out["pools"] if p["id"] == "x")
    assert pool_x["class"] == "A" and pool_x["pacing_multiplier"] == 0.0
    assert pool_x["stranded"] is None  # no forecast clock -> not established
    assert any(t["trigger"] == "readings_state:exhausted" for t in out["triggers_fired"])
    gh = next(p for p in out["pools"] if p["id"] == "github")
    assert gh["class"] == "C" and gh["limit"] is None


def test_deadline_trigger():
    out = planner.plan(REG, ALLOC, {"readings": []},
                       countdowns=[{"id": "d4", "hours_remaining": 71},
                                   {"id": "d9", "hours_remaining": 200}])
    kinds = [t["trigger"] for t in out["triggers_fired"]]
    assert "deadline_t72h:d4" in kinds and "deadline_t72h:d9" not in kinds


def test_repo_replay_app_slice_trigger():
    reg = {"services": REG["services"] + [
        {"id": "github.api.app_collector", "limit": 5000, "live": "api"},
        {"id": "github.api.app_publisher", "limit": 5000, "live": "api"},
        {"id": "github.api.user_token", "limit": 5000, "live": "api"},
    ]}
    alloc = {"pools": [{"id": "github", "services": [
        "github.api.app_collector", "github.api.app_publisher",
        "github.api.user_token"]}]}
    # assignment logic (hold set empty since the 2026-10-30 lift)
    planner.SLICE_ASSIGNMENT_HOLDS.discard("repo-replay")
    out = planner.plan(reg, alloc, {"readings": []})
    hits = [t for t in out["triggers_fired"]
            if t["trigger"] == "app_slice_assignment:repo-replay"]
    assert len(hits) == 1
    sl = hits[0]["slice"]
    assert sl["primary_services"] == ["github.api.app_collector",
                                      "github.api.app_publisher"]
    assert sl["fallback_service"] == "github.api.user_token"
    assert sl["fallback_mode"] == "fallback-only"
    assert sl["routine_draw_on_fallback"] is False
    # absent when the app pair is not pooled
    out2 = planner.plan(reg, ALLOC, {"readings": []})
    assert not any(t["trigger"].startswith("app_slice_assignment")
                   for t in out2["triggers_fired"])
    # and suppressed while a hold stands (mechanism check)
    planner.SLICE_ASSIGNMENT_HOLDS.add("repo-replay")
    out3 = planner.plan(reg, alloc, {"readings": []})
    assert not any(t["trigger"].startswith("app_slice_assignment")
                   for t in out3["triggers_fired"])


def test_lane_slices_carried_verbatim():
    alloc = {"pools": [{"id": "github", "services": [],
                        "slices": [{"project": "repo-replay",
                                    "claim": 6519135715}]}]}
    out = planner.plan({"services": []}, alloc, {"readings": []})
    gh = out["pools"][0]
    assert gh["lane_slices"] == [{"project": "repo-replay",
                                  "claim": 6519135715}]
    assert gh["slices"] == []  # focus slices stay distinct
