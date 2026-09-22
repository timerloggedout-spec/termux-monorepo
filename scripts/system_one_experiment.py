#!/usr/bin/env python3
"""Run bounded System One decision-engine experiments."""
from __future__ import annotations
import argparse,json,subprocess,time
from dataclasses import asdict,dataclass
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class DecisionReceipt:
    schema_version:str
    experiment_id:str
    cohort_id:str
    lane_id:str
    engine:str
    policy_version:str
    status:str
    decision:dict[str,Any]
    confidence:float|None
    latency_ms:float
    failure_class:str|None=None

def deterministic_decision(state):
    body=str(state.get("body","")).lower()
    if any(w in body for w in ("cancel","outage","blocked","critical")): return {"route":"escalate","confidence":0.99}
    if any(w in body for w in ("refund","invoice","payment")): return {"route":"billing","confidence":0.99}
    return {"route":"general","confidence":0.99}

def run_laya_stub(live=False):
    cmd=["python3",str(ROOT/"scripts/laya_decision_stub.py"),"--json"]
    if live: cmd.insert(-1,"--live")
    completed=subprocess.run(cmd,cwd=ROOT,check=False,capture_output=True,text=True,timeout=180)
    if completed.returncode: raise RuntimeError(completed.stderr.strip() or "laya adapter failed")
    return json.loads(completed.stdout)

def normalize(raw):
    answer=raw.get("answers",{}).get("department",{})
    confidence=answer.get("confidence")
    return {"route":answer.get("choice") or "unknown","confidence":float(confidence) if confidence is not None else None,"raw":raw}

def run_jev(state,live):
    if not live:
        return "UNAVAILABLE",{},None,"ENGINE_UNAVAILABLE"
    from scripts.system_one_adapters import DecisionRequest,TypeSafeJevAdapter
    result=TypeSafeJevAdapter().evaluate(DecisionRequest(state=state,questions={
        "department":{"type":"choice","instructions":"Which department should handle this request?","criteria":{"billing":"invoices, payments, refunds","technical":"bugs, outages","sales":"pricing, contracts","other":"everything else"}}
    },experiment_id="system-one",lane_id="C",category="routing"))
    if result.status=="UNAVAILABLE": return result.status,{},None,"ENGINE_UNAVAILABLE"
    if result.status!="OK": return result.status,{"error":result.metadata.get("error")},None,result.metadata.get("failure_class","ENGINE_ERROR")
    return "OK",{"route":result.answers.get("department",{}).get("choice","unknown"),"confidence":result.confidence,"raw":result.answers},result.confidence,None

def run_lane(lane_id,engine,policy_version,state,experiment_id,cohort_id,live=False):
    started=time.perf_counter()
    try:
        if engine=="deterministic": decision=deterministic_decision(state); status="OK"; failure=None
        elif engine=="laya": decision=normalize(run_laya_stub(live)); status="OK"; failure=None
        elif engine=="jev": status,decision,_,failure=run_jev(state,live)
        else: raise ValueError(f"unknown engine: {engine}")
        return DecisionReceipt("system-one.v1",experiment_id,cohort_id,lane_id,engine,policy_version,status,decision,decision.get("confidence"),(time.perf_counter()-started)*1000,failure)
    except subprocess.TimeoutExpired:
        return DecisionReceipt("system-one.v1",experiment_id,cohort_id,lane_id,engine,policy_version,"FAILED",{},None,(time.perf_counter()-started)*1000,"ENGINE_ERROR")
    except (OSError,RuntimeError,ValueError,TypeError,json.JSONDecodeError,ImportError) as exc:
        return DecisionReceipt("system-one.v1",experiment_id,cohort_id,lane_id,engine,policy_version,"FAILED",{"error":str(exc)},None,(time.perf_counter()-started)*1000,"ENGINE_ERROR")

def run_experiment(cohort_id,state,live=False):
    experiment_id=f"system-one:{cohort_id}"
    lanes=[("A","deterministic","M0-control"),("B","laya","M1-fast-gate"),("C","jev","M1-fast-gate")]
    return [run_lane(l,e,p,state,experiment_id,cohort_id,live) for l,e,p in lanes]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cohort",default="local-smoke"); p.add_argument("--output",default="-"); p.add_argument("--live",action="store_true")
    a=p.parse_args()
    state={"subject":"Duplicate charge on invoice #4411","body":"We were billed twice. Please refund or we will cancel."}
    payload="\n".join(json.dumps(asdict(r),sort_keys=True) for r in run_experiment(a.cohort,state,a.live))+"\n"
    if a.output=="-": print(payload,end="")
    else: Path(a.output).write_text(payload,encoding="utf-8")
if __name__=="__main__": main()
