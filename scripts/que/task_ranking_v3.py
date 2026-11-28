#!/usr/bin/env python3
"""QUE shadow ranker backed by the shared FCE measurement contract."""
from __future__ import annotations
import math
from collections import defaultdict
from typing import Any
from flywheel_compounding_efficiency import METHOD as FCE_METHOD,score_compounding
METHOD="que-task-rank/v3-compounding"

def _issue_number(row:dict[str,Any])->int|None:
    v=row.get("issue"); return v if isinstance(v,int) and not isinstance(v,bool) and v>=0 else None

def _finite(v:Any)->float|None:
    if isinstance(v,bool) or not isinstance(v,(int,float)): return None
    n=float(v); return n if math.isfinite(n) else None

def _percentiles(items:list[dict[str,Any]])->dict[int,float]:
    ordered=sorted((x["fce_raw"],x["issue"]) for x in items); groups=defaultdict(list)
    for score,issue in ordered: groups[score].append(issue)
    n=len(ordered); out={}; before=0
    for score in sorted(groups):
        count=len(groups[score]); pct=100.0 if n==1 else (50.0 if len(groups)==1 else 100.0*(before+(count-1)/2.0)/(n-1))
        for issue in groups[score]: out[issue]=round(pct,6)
        before+=count
    return out

def rank_compounding(rows:list[dict[str,Any]],evidence_by_issue:dict[int,Any],baselines_by_issue:dict[int,Any]|None=None)->dict[str,Any]:
    evidence_by_issue=evidence_by_issue or {}; baselines_by_issue=baselines_by_issue or {}
    eligible=[]; fallback=[]; seen=set(); cohort_keys=set()
    for row in rows:
        issue=_issue_number(row)
        if issue is None or issue in seen: raise ValueError("rows require unique non-negative integer issue ids")
        seen.add(issue); evidence=evidence_by_issue.get(issue)
        score=score_compounding(evidence,baselines_by_issue.get(issue))
        if not score["eligible"]:
            fallback.append({"issue":issue,"v1_score":row.get("v1_score"),"v1_rank":row.get("v1_rank"),"reason":score["missing"]}); continue
        cohort_keys.add(tuple(evidence.get(k) for k in ("cohort_id","task_contract_sha256","environment_fingerprint","validation_suite_sha256","cohort_manifest_sha256","cost_normalization_id")))
        eligible.append({"issue":issue,**score,"wall_in_min":row.get("wall_in_min"),"v1_score":row.get("v1_score")})
    if len(cohort_keys)>1: raise ValueError("eligible rows must share one frozen cohort and normalization basis")
    pct=_percentiles(eligible)
    for item in eligible:
        item["cohort_percentile"]=pct[item["issue"]]; wall=_finite(item["wall_in_min"])
        item["wall_imminent"]=wall is not None and wall<=48.0*60.0
    eligible.sort(key=lambda x:(not x["wall_imminent"],-x["cohort_percentile"],-(_finite(x["v1_score"]) or 0.0),x["issue"]))
    for rank,item in enumerate(eligible,1): item["candidate_rank"]=rank
    fallback.sort(key=lambda x:(x["v1_rank"] if isinstance(x["v1_rank"],int) and not isinstance(x["v1_rank"],bool) else 10**12,-(_finite(x["v1_score"]) or 0.0),x["issue"]))
    return {"method":METHOD,"fce_method":FCE_METHOD,"advisory":True,"claim_order_binding":False,"complete_coverage":not fallback,"eligible_count":len(eligible),"fallback_count":len(fallback),"eligible":eligible,"v1_fallback":fallback,"claim_order":None}
