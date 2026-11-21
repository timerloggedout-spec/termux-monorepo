import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"/"que"))
from flywheel_compounding_efficiency import COST_FIELDS,DIMENSION_WEIGHTS,score_compounding

def evidence(scale=1.0,costs=None):
    return {"observation_id":"obs-1","cohort_id":"cohort-1","task_id":"task-1","manager_policy_id":"manager-v1","source_ref":"refs/heads/test","source_sha":"a"*40,"observed_at":"2026-11-18T10:00:00Z","task_contract_sha256":"b"*64,"environment_fingerprint":"linux-py312","validation_suite_sha256":"c"*64,"cohort_manifest_sha256":"d"*64,"cost_normalization_id":"budget-v1","evidence_refs":[{"kind":"actions_run","uri":"https://example.invalid/run/1","sha256":"e"*64}],"dimensions":{k:min(1.0,scale) for k in DIMENSION_WEIGHTS},"costs":costs or {k:0.1 for k in COST_FIELDS},"realization":0.8}

def test_fce_is_deterministic_and_includes_all_costs():
    r=score_compounding(evidence()); assert r["eligible"] and r["benefit_points"]==100.0
    assert r["normalized_total_cost"]==0.7 and r["fce_raw"]==round(100*80/0.7,9)
    assert r["dimensions"]["reuse_leverage"]==1.0 and r["provenance"]["source_sha"]=="a"*40

def test_baseline_requires_same_frozen_basis_and_provenance():
    e=evidence(); b={k:e[k] for k in ("cohort_id","task_id","task_contract_sha256","environment_fingerprint","validation_suite_sha256","cohort_manifest_sha256","cost_normalization_id")}
    b.update({"method":"flywheel-compounding-efficiency/v1","observation_id":"base-1","source_ref":"refs/heads/base","source_sha":"f"*40,"observed_at":"2026-11-18T09:00:00Z","evidence_refs":[{"kind":"run","uri":"https://example.invalid/run/0","sha256":"1"*64}],"fce_raw":1000.0})
    r=score_compounding(e,b); assert r["baseline_status"]=="COMPARABLE" and r["fce_vs_baseline"]==round(r["fce_raw"]/1000,9)
    b["environment_fingerprint"]="other"; assert score_compounding(e,b)["baseline_status"]=="INCOMPARABLE"

def test_zero_cost_is_not_infinite_efficiency():
    r=score_compounding(evidence(costs={k:0.0 for k in COST_FIELDS}))
    assert not r["eligible"] and r["missing"]==["costs.total_cost_must_be_positive"]

def test_missing_provenance_and_invalid_values_fail_closed():
    e=evidence(); e["source_sha"]="unknown"; e["dimensions"]["reuse_leverage"]=True
    r=score_compounding(e); assert not r["eligible"]
    assert "source_sha" in r["missing"] and "dimensions.reuse_leverage" in r["missing"]

def test_missing_evidence_is_not_zero_imputed():
    e=evidence(); del e["costs"]["human_intervention"]
    assert "costs.human_intervention" in score_compounding(e)["missing"]
