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
