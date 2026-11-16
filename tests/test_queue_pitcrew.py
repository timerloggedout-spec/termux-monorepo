import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("qp", pathlib.Path(__file__).parents[1] / "scripts/ci/queue_pitcrew.py")
qp = importlib.util.module_from_spec(spec); spec.loader.exec_module(qp)

def r(i, name, ev="workflow_run", br="master", t=None, st="queued"):
    return {"id": i, "name": name, "event": ev, "head_branch": br, "created_at": t or f"2026-11-12T0{i%10}:00:00Z", "status": st}

def test_keeps_newest_per_group_and_ignores_unlisted():
    runs = [r(1, "Quota Dispatch Tree"), r(2, "Quota Dispatch Tree"), r(3, "Quota Dispatch Tree"),
            r(4, "Quota Dispatch Tree", ev="schedule"), r(5, "lane events recorder"),
            r(6, "Quota Dispatch Tree", st="in_progress")]
    d = qp.plan(runs, {"supersede": ["Quota Dispatch Tree"], "amplifier_threshold": 1})
    assert sorted(d["cancel"]) == [1, 2]
    assert "lane events recorder" in d["suggest_supersede"]
    assert "Quota Dispatch Tree" not in d["suggest_supersede"]

def test_cap():
    runs = [r(i, "X") for i in range(1, 9)]
    d = qp.plan(runs, {"supersede": ["X"], "max_cancels_per_pass": 3})
    assert len(d["cancel"]) == 3
