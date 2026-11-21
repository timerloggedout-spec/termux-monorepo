#!/usr/bin/env python3
"""Pure, provenance-gated Flywheel Compounding Efficiency (FCE) scorer."""
from __future__ import annotations
import math, re
from datetime import datetime
from typing import Any

METHOD="flywheel-compounding-efficiency/v1"
DIMENSION_WEIGHTS={"direct_verified_outcome":20.0,"downstream_unlock":20.0,"recurrence_eliminated":20.0,"reuse_leverage":15.0,"reliability_risk_reduction":15.0,"evidence_confidence":10.0}
COST_FIELDS=("execution_effort","elapsed_delay","context_consumption","feedback_cycles","conflicts_retries","human_intervention","provider_cost")
COMPARABILITY_FIELDS=("cohort_id","task_id","task_contract_sha256","environment_fingerprint","validation_suite_sha256","cohort_manifest_sha256","cost_normalization_id")
_SHA1=re.compile(r"^[0-9a-f]{40}$"); _SHA256=re.compile(r"^[0-9a-f]{64}$")

def _unit(v:Any)->float|None:
    if isinstance(v,bool) or not isinstance(v,(int,float)): return None
    n=float(v); return n if math.isfinite(n) and 0<=n<=1 else None

def _nonempty(v:Any)->bool: return isinstance(v,str) and bool(v.strip())

def _valid_time(v:Any)->bool:
    if not _nonempty(v): return False
    try: return datetime.fromisoformat(v.replace("Z","+00:00")).tzinfo is not None
    except ValueError: return False

def _valid_refs(refs:Any)->bool:
    return isinstance(refs,list) and bool(refs) and all(isinstance(r,dict) and _nonempty(r.get("kind")) and _nonempty(r.get("uri")) and _SHA256.fullmatch(str(r.get("sha256",""))) for r in refs)

def _provenance_gaps(e:dict[str,Any])->list[str]:
    gaps=[]
    for k in ("observation_id","cohort_id","task_id","manager_policy_id","source_ref","cost_normalization_id","environment_fingerprint"):
        if not _nonempty(e.get(k)): gaps.append(k)
    if not _SHA1.fullmatch(str(e.get("source_sha",""))): gaps.append("source_sha")
    for k in ("task_contract_sha256","validation_suite_sha256","cohort_manifest_sha256"):
        if not _SHA256.fullmatch(str(e.get(k,""))): gaps.append(k)
    if not _valid_time(e.get("observed_at")): gaps.append("observed_at")
    if not _valid_refs(e.get("evidence_refs")): gaps.append("evidence_refs")
    return gaps

def score_compounding(evidence:Any,baseline:Any=None)->dict[str,Any]:
    """Score one immutable observation; missing/invalid evidence is never zero-filled."""
    if not isinstance(evidence,dict): return {"method":METHOD,"eligible":False,"missing":["evidence"]}
    missing=_provenance_gaps(evidence); dims=evidence.get("dimensions"); costs=evidence.get("costs")
    dv={}; cv={}
    for k in DIMENSION_WEIGHTS:
        v=_unit(dims.get(k) if isinstance(dims,dict) else None)
        if v is None: missing.append("dimensions."+k)
        else: dv[k]=v
    for k in COST_FIELDS:
        v=_unit(costs.get(k) if isinstance(costs,dict) else None)
        if v is None: missing.append("costs."+k)
        else: cv[k]=v
    realization=_unit(evidence.get("realization"))
    if realization is None: missing.append("realization")
    if missing: return {"method":METHOD,"eligible":False,"missing":sorted(set(missing))}
    components={k:round(dv[k]*w,6) for k,w in DIMENSION_WEIGHTS.items()}
    benefit=round(sum(components.values()),6); realized=round(benefit*realization,6); total=round(sum(cv.values()),6)
    if total<=0: return {"method":METHOD,"eligible":False,"missing":["costs.total_cost_must_be_positive"]}
    fce=round(100.0*realized/total,9)
    out={"method":METHOD,"eligible":True,"observation_id":evidence["observation_id"],"cohort_id":evidence["cohort_id"],"dimensions":dv,"provenance":{k:evidence[k] for k in ("task_id","manager_policy_id","source_ref","source_sha","observed_at","task_contract_sha256","environment_fingerprint","validation_suite_sha256","cohort_manifest_sha256","cost_normalization_id","evidence_refs")},"components":components,"benefit_points":benefit,"realized_benefit_points":realized,"costs":cv,"normalized_total_cost":total,"realization":realization,"fce_raw":fce,"raw_efficiency":fce,"baseline_status":"NOT_SUPPLIED","fce_vs_baseline":None,"fce_delta":None}
    if baseline is not None:
        if not isinstance(baseline,dict): out["baseline_status"]="INVALID"
        elif any(baseline.get(k)!=evidence.get(k) for k in COMPARABILITY_FIELDS): out["baseline_status"]="INCOMPARABLE"
        else:
            bf=baseline.get("fce_raw")
            valid=(baseline.get("method")==METHOD and _nonempty(baseline.get("observation_id")) and _nonempty(baseline.get("source_ref")) and _SHA1.fullmatch(str(baseline.get("source_sha",""))) and _valid_time(baseline.get("observed_at")) and _valid_refs(baseline.get("evidence_refs")) and not isinstance(bf,bool) and isinstance(bf,(int,float)) and math.isfinite(float(bf)) and float(bf)>0)
            if not valid: out["baseline_status"]="INVALID"
            else:
                out["baseline_status"]="COMPARABLE"; out["baseline_observation_id"]=baseline["observation_id"]
                out["fce_vs_baseline"]=round(fce/float(bf),9); out["fce_delta"]=round(fce-float(bf),9)
    return out
