import json
import subprocess
import sys

import pytest

from scripts.model_selection_market.cadence import analyze_observations, build_report, schedule_tasks


def test_verified_beta_and_unknown_skipped_stay_separate():
    rows = [
        {"role":"SWE","provider":"p","model":"m","task_type":"fix","outcome":True,"verified":True},
        {"role":"SWE","provider":"p","model":"m","task_type":"fix","outcome":False,"verified":True},
        {"role":"SWE","provider":"p","model":"m","task_type":"fix","outcome":True,"verified":False},
        {"role":"SWE","provider":"p","model":"m","task_type":"fix","outcome":"UNKNOWN"},
        {"role":"SWE","provider":"p","model":"m","task_type":"fix","outcome":"skipped"},
    ]
    p=analyze_observations(rows)["posterior"]["SWE|p|m|fix"]
    assert (p["alpha"],p["beta"],p["verified_n"]) == (2,2,2)
    assert p["mean"] == .5 and p["unknown"] == 2 and p["skipped"] == 1


@pytest.mark.parametrize("bad", [True, float("nan"), float("inf"), -1, 0])
def test_reject_bad_task_durations(bad):
    with pytest.raises(ValueError): schedule_tasks([{"id":"a","duration_minutes":bad}])


def test_reject_bad_reviews_and_duplicate_vote():
    for score in (True, float("nan"), -0.1, 1.1):
        with pytest.raises(ValueError): analyze_observations([{"task_id":"x","reviewer":"r","signed":True,"score":score}])
    row={"task_id":"x","round":1,"reviewer":"r","signed":True,"score":.4}
    with pytest.raises(ValueError, match="duplicate"):
        analyze_observations([row,row])


def test_delphi_keeps_disagreement_and_markov_counts():
    rows=[{"task_id":"x","reviewer":"a","round":1,"signed":True,"score":.1},
          {"task_id":"x","reviewer":"b","round":1,"signed":True,"score":.9},
          {"task_id":"a","sequence":1,"state":"queued"},
          {"task_id":"a","sequence":2,"state":"running"},
          {"task_id":"a","sequence":3,"state":"done"},
          {"task_id":"b","sequence":1,"state":"queued"},
          {"task_id":"b","sequence":2,"state":"running"}]
    result=analyze_observations(rows)
    assert result["delphi"]["x|1"]["disagreement_range"] == .8
    assert result["delphi"]["x|1"]["consensus_claimed"] is False
    assert result["markov"]["transitions"]["queued"]["counts"] == {"running":2}
    assert result["markov"]["transitions"]["queued"]["probabilities"] == {"running":1.0}
    assert result["markov"]["insufficient_data"] is False


def test_scheduler_parallel_roles_serialize_same_lane_and_dependencies():
    tasks=[{"id":"a","role":"SWE","duration_minutes":5},
           {"id":"b","role":"reviewer","duration_minutes":3},
           {"id":"c","role":"SWE","duration_minutes":2},
           {"id":"d","role":"manager","duration_minutes":4,"dependencies":["a","b"]}]
    result=schedule_tasks(tasks); plan={r["id"]:r for r in result["plan"]}
    assert plan["a"]["start_minutes"] == plan["b"]["start_minutes"] == 0
    assert plan["c"]["start_minutes"] == 5
    assert plan["d"]["start_minutes"] == 5
    assert result["provenance"]["promotion_authority"] is False


@pytest.mark.parametrize("tasks", [
    [{"id":"a","duration_minutes":1,"dependencies":["missing"]}],
    [{"id":"a","duration_minutes":1,"dependencies":["b"]},{"id":"b","duration_minutes":1,"dependencies":["a"]}],
    [{"id":"a","duration_minutes":1},{"id":"a","duration_minutes":2}],
])
def test_dependency_and_identity_failures(tasks):
    with pytest.raises(ValueError): schedule_tasks(tasks)


def test_determinism_and_safe_mermaid_identifiers():
    tasks=[{"id":"x; click 1 \"evil\"","duration_minutes":1}, {"id":"x; click 1 \"evil\"!","duration_minutes":2}]
    a=schedule_tasks(tasks); b=schedule_tasks(tasks)
    assert a == b
    assert "click 1" not in a["mermaid_gantt"]
    assert "task_x__click_1__evil__" in a["mermaid_gantt"]


def test_report_cli(tmp_path):
    src=tmp_path/"input.json"; out=tmp_path/"out.json"
    src.write_text(json.dumps({"tasks":[{"id":"one","duration_minutes":2}],"observations":[]}))
    subprocess.run([sys.executable,"-m","scripts.model_selection_market.cadence","--input",str(src),"--output",str(out)],check=True)
    data=json.loads(out.read_text())
    assert data["cadence"]["plan"][0]["finish_minutes"] == 2
    assert data["provenance"]["mode"] == "advisory_only"

@pytest.mark.parametrize("value", [0, 1])
def test_integer_outcome_is_invalid(value):
    with pytest.raises(ValueError):
        analyze_observations([{"outcome": value}])


def test_unverified_boolean_is_unknown_and_roles_normalize():
    result = analyze_observations([
        {"role": "scout", "outcome": True, "verified": False},
        {"role": "SCOUT", "outcome": True, "verified": True},
    ])
    assert result["posterior"]["Scout|UNKNOWN|UNKNOWN|UNKNOWN"]["unknown"] == 1
    assert result["posterior"]["Scout|UNKNOWN|UNKNOWN|UNKNOWN"]["verified_n"] == 1


@pytest.mark.parametrize("row", [
    {"reviewer": "", "signed": True, "task_id": "t", "score": .5},
    {"reviewer": "r", "signed": True, "task_id": "", "score": .5},
    {"reviewer": "r", "signed": True, "task_id": "t", "round": "", "score": .5},
])
def test_signed_reviews_require_nonempty_identity(row):
    with pytest.raises(ValueError):
        analyze_observations([row])


def test_duplicate_markov_sequence_and_invalid_state_rejected():
    with pytest.raises(ValueError, match="duplicate Markov"):
        analyze_observations([{"task_id":"t", "sequence":1, "state":"ready"},
                              {"task_id":"t", "sequence":1, "state":"running"}])
    with pytest.raises(ValueError, match="invalid state"):
        analyze_observations([{"task_id":"t", "sequence":1, "state":"invented"}])


def test_priority_evidence_orders_ready_tasks():
    base = [
        {"id":"a", "duration_minutes":1, "role":"manager", "model":"m1", "provider":"p", "task_type":"x"},
        {"id":"b", "duration_minutes":1, "role":"manager", "model":"m2", "provider":"p", "task_type":"x"},
    ]
    posterior = {
        "Manager|p|m1|x": {"mean":.2, "uncertainty":.01},
        "manager|p|m2|x": {"mean":.9, "uncertainty":.01},
    }
    # Both role spellings normalize identically for evidence lookup and scheduling.
    base[0]["role"] = "MANAGER"
    assert [x["id"] for x in schedule_tasks(base, posterior)["plan"]] == ["b", "a"]
    assert "2000-01-01 00:00" in schedule_tasks(base)["mermaid_gantt"]
