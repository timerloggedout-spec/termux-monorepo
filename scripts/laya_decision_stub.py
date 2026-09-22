#!/usr/bin/env python3
"""Laya adapter with deterministic CI fallback and a live Router path."""
from __future__ import annotations
import argparse, json, os
from typing import Any

def mock_predict(state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    answers={}
    for key,q in questions.items():
        qtype=(q or {}).get("type","noul")
        if qtype=="choice":
            criteria=list(((q or {}).get("criteria") or {}).keys()) or ["unknown"]
            pick=criteria[0]
            dist={c:(0.7 if c==pick else 0.3/max(len(criteria)-1,1)) for c in criteria}
            answers[key]={"choice":pick,"distribution":dist,"confidence":0.7}
        elif qtype=="score":
            levels=(q or {}).get("criteria") or ["low","medium","high"]
            answers[key]={"score":float(len(levels)//2),"confidence":0.6}
        else: answers[key]={"noul":0.5,"confidence":0.5}
    return {"answers":answers,"routing":{"model":"mock","reason":"offline stub"},"mode":"mock"}

def live_predict(state,questions):
    try:
        from laya import Router
    except ImportError as exc:
        raise RuntimeError(f"laya package not installed: {exc}. Install with 'pip install laya==0.3.5'.") from exc
    preload=os.getenv("LAYA_PRELOAD","0").lower() in {"1","true","yes"}
    return Router(preload=preload).predict(state,questions)

def sample_request():
    return (
      {"subject":"Duplicate charge on invoice #4411","body":"We were billed twice. Please refund the duplicate today or we will cancel."},
      {"department":{"type":"choice","instructions":"Which department should handle this request?","criteria":{"billing":"invoices, payments, refunds","technical":"bugs, outages","sales":"pricing, contracts","other":"everything else"}},
       "urgency":{"type":"score","instructions":"How urgent is this request?","criteria":["not urgent","soon","critical deadline or blocking issue"]},
       "churn_risk":{"type":"noul","instructions":"Does the user threaten to cancel or leave?"}}
    )

def main():
    p=argparse.ArgumentParser(); p.add_argument("--live",action="store_true"); p.add_argument("--json",action="store_true"); a=p.parse_args()
    state,questions=sample_request()
    result=live_predict(state,questions) if a.live else mock_predict(state,questions)
    print(json.dumps(result,indent=0 if a.json else 2,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
