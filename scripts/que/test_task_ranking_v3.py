import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"/"que"))
import task_ranking_v3 as v3
from flywheel_compounding_efficiency import COST_FIELDS,DIMENSION_WEIGHTS

def evidence(scale=1.0):
    return {"observation_id":f"obs-{scale}","cohort_id":"cohort-1","task_id":"task-1","manager_policy_id":"manager-v1","source_ref":"refs/heads/test","source_sha":"a"*40,"observed_at":"2026-11-18T10:00:00Z","task_contract_sha256":"b"*64,"environment_fingerprint":"linux-py312","validation_suite_sha256":"c"*64,"cohort_manifest_sha256":"d"*64,"cost_normalization_id":"budget-v1","evidence_refs":[{"kind":"actions_run","uri":"https://example.invalid/run/1","sha256":"e"*64}],"dimensions":{k:min(1.0,scale) for k in DIMENSION_WEIGHTS},"costs":{k:0.1 for k in COST_FIELDS},"realization":0.8}

def test_weights_and_fce_are_deterministic():
    assert sum(DIMENSION_WEIGHTS.values())==100.0
    assert v3.rank_compounding([{"issue":1}],{1:evidence()})["eligible_count"]==1

def test_missing_rows_fall_back_to_v1_without_mixed_claim_order():
    r=v3.rank_compounding([{"issue":10,"v1_score":20,"v1_rank":2},{"issue":11,"v1_score":30,"v1_rank":1}],{10:evidence()})
    assert r["eligible_count"]==1 and r["fallback_count"]==1 and r["v1_fallback"][0]["issue"]==11
    assert r["claim_order"] is None and not r["claim_order_binding"]

def test_mixed_cohort_is_rejected():
    other=evidence(0.5); other["cohort_id"]="cohort-2"
    try: v3.rank_compounding([{"issue":1},{"issue":2}],{1:evidence(),2:other})
    except ValueError: return
    raise AssertionError("cross-cohort ranking must fail closed")

def test_wall_imminence_is_lexicographic_inside_shadow_arm():
    r=v3.rank_compounding([{"issue":1,"wall_in_min":49*60},{"issue":2,"wall_in_min":48*60}],{1:evidence(1.0),2:evidence(0.5)})
    assert r["eligible"][0]["issue"]==2 and r["eligible"][0]["wall_imminent"]

def test_duplicate_issue_ids_rejected():
    try: v3.rank_compounding([{"issue":1},{"issue":1}],{})
    except ValueError: return
    raise AssertionError("duplicate issue IDs must fail closed")

def test_tied_fce_scores_share_cohort_midrank():
    r=v3.rank_compounding([{"issue":1},{"issue":2},{"issue":3}],{1:evidence(0.5),2:evidence(0.5),3:evidence(1.0)})
    by_id={x["issue"]:x for x in r["eligible"]}
    assert by_id[1]["cohort_percentile"]==by_id[2]["cohort_percentile"]
    assert by_id[3]["cohort_percentile"]>by_id[1]["cohort_percentile"]
