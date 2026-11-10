#!/usr/bin/env python3
"""Build an evidence-backed provider participation index; no provider calls."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def load(root: Path, rel: str) -> dict:
    path=root/rel
    if not path.exists(): raise FileNotFoundError(f"required source missing: {rel}")
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"expected object: {rel}")
    return value

def norm(value: object) -> str: return str(value or "").strip().casefold()

def known_model(value: object) -> str | None:
    if not isinstance(value,str) or not value.strip(): return None
    if value.strip().casefold() in {"not established","not_established","n∅"}: return None
    return value.strip()

def participation_by_provider(nested: dict) -> dict:
    result={}
    for p in nested.get("providers",[]) or []:
        if not isinstance(p,dict): continue
        key=norm(p.get("provider"))
        if not key: continue
        b=result.setdefault(key,{"roles":set(),"models":set(),"tasks":[],"proofs":[]})
        for m in p.get("models",[]) or []:
            if not isinstance(m,dict): continue
            model=known_model(m.get("model"))
            if model: b["models"].add(model)
            for role in m.get("roles",[]) or []:
                if isinstance(role,str) and role.strip(): b["roles"].add(role.strip())
            for t in m.get("tasks",[]) or []:
                if not isinstance(t,dict): continue
                outcome=t.get("outcome")
                if isinstance(outcome,dict): outcome=outcome.get("status")
                ev={"model_id":model,"role":t.get("role") or None,"task_class":t.get("task_class") or None,"source":t.get("source") or None,"source_ref":t.get("source_ref") or None,"run_id":t.get("run_id"),"session_id":t.get("session_id"),"outcome":outcome or None}
                b["tasks"].append(ev)
                if t.get("role"): b["roles"].add(str(t["role"]).strip())
                if norm(t.get("task_class"))=="inference-invoke" and norm(outcome)=="passed": b["proofs"].append(ev)
    return result

def build(root: Path, generated_at: str | None=None) -> dict:
    reg=load(root,"ops/quota/registry.json"); desk=load(root,"ops/challenge/desk-feed.json")
    nested=load(root,"ops/tracking/nested-family.json")
    design=load(root,"experiments/doe/util-1-provider-rotation/DESIGN.json")
    catalog=desk.get("dispatch",{}).get("provider_catalog",{})
    dispatch={}
    for row in catalog.get("inference_availability",{}).get("records",[]) or []:
        if not isinstance(row,dict) or not row.get("id"): continue
        if row["id"] in dispatch: raise ValueError(f"duplicate dispatch record: {row['id']}")
        dispatch[row["id"]]=row
    records=[]; seen=set(); participation=participation_by_provider(nested)
    for s in reg.get("services",[]) or []:
        if not isinstance(s,dict) or s.get("lane")!="model": continue
        rid=s.get("id")
        if not isinstance(rid,str) or not rid: raise ValueError("model-lane registry row missing id")
        if rid in seen: raise ValueError(f"duplicate registry record: {rid}")
        seen.add(rid); d=dispatch.get(rid); ev=participation.get(norm(s.get("provider")),{"roles":set(),"models":set(),"tasks":[],"proofs":[]})
        cls=d.get("class") if d else "unmapped"; routes=d.get("inference_route",[]) if d else []
        if not isinstance(routes,list): routes=[]
        records.append({"id":rid,"provider":s.get("provider"),"family":rid.split(".",1)[0],"lane":"model","dispatch_class":cls,"dispatch_mapping_status":"mapped" if d else "unmapped","availability_probe":d.get("availability_probe") if d else None,"batch_route":d.get("batch") if d else None,"inference_route":routes,"inference_dispatchable":cls in {"proven","wired-unproven","inference-only"} and bool(routes),"catalog_probe_declared":bool(d and norm(d.get("availability_probe")) not in {"","none","not-covered"}),"registry_live_field":s.get("live"),"quota":{k:s.get(k) for k in ("limit","unit","window","reset","source")},"free_eligibility":None,"free_eligibility_reason":"No exact account + model admission receipt is asserted by this index. Catalog price, public plan claims, configured credentials, and provider-family status are not sufficient.","observed_models":sorted(ev["models"]),"observed_roles":sorted(ev["roles"]),"participation":{"task_count":len(ev["tasks"]),"inference_invocations_passed":len(ev["proofs"]),"evidence":ev["tasks"]},"invocation_proofs":ev["proofs"]})
    grouped={}
    for r in records:
        key=norm(r["provider"])
        if not key: continue
        p=grouped.setdefault(key,{"provider":r["provider"],"record_count":0,"record_ids":[],"observed_roles":set(),"observed_models":set(),"task_count":0,"inference_invocations_passed":0})
        p["record_count"]+=1;p["record_ids"].append(r["id"]);p["observed_roles"].update(r["observed_roles"]);p["observed_models"].update(r["observed_models"]);p["task_count"]+=r["participation"]["task_count"];p["inference_invocations_passed"]+=r["participation"]["inference_invocations_passed"]
    providers=[{**{k:v for k,v in p.items() if k not in {"observed_roles","observed_models"}},"record_ids":sorted(p["record_ids"]),"observed_roles":sorted(p["observed_roles"]),"observed_models":sorted(p["observed_models"])} for p in grouped.values()]
    providers.sort(key=lambda p:str(p["provider"]).casefold())
    classes={}
    for r in records: classes[r["dispatch_class"]]=classes.get(r["dispatch_class"],0)+1
    summary={"registry_model_records":len(records),"distinct_provider_names":len(providers),"id_prefix_families":len({r["family"] for r in records}),"dispatch_mapped_records":sum(r["dispatch_mapping_status"]=="mapped" for r in records),"dispatch_unmapped_records":sum(r["dispatch_mapping_status"]=="unmapped" for r in records),"dispatch_classes":dict(sorted(classes.items())),"inference_dispatchable_records":sum(r["inference_dispatchable"] for r in records),"catalog_only_records":classes.get("catalog-only",0),"providers_with_observed_roles":sum(bool(p["observed_roles"]) for p in providers),"providers_with_passed_inference_receipts":sum(p["inference_invocations_passed"]>0 for p in providers),"free_eligibility_established_records":sum(r["free_eligibility"] is not None for r in records),"free_eligibility_unknown_records":sum(r["free_eligibility"] is None for r in records)}
    arms=[{k:a.get(k) for k in ("provider","status","protocols","activation_gates","activation_rule")} for a in design.get("conditional_provider_arms",[]) or [] if isinstance(a,dict)]
    return {"schema":"provider-participation-index/v1","generated_at":generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z"),"generated_by":"scripts/provider_participation_index.py","sources":{"registry":"ops/quota/registry.json","dispatch":"ops/challenge/desk-feed.json#dispatch.provider_catalog.inference_availability","participation":"ops/tracking/nested-family.json","role_contract":"docs/ops/PROVIDER-COLLABORATOR-CAPABILITY-MAP.md","tournament":"experiments/doe/util-1-provider-rotation/DESIGN.json"},"semantics":{"provider_identity":"Registry provider strings are preserved; case-folding is used only for evidence joins.","model_identity":"Exact model IDs appear only where nested-family evidence supplies them; unknown labels become schema null.","roles":"Observed task roles come from nested-family evidence; declared role capabilities remain a separate contract.","inference":"Dispatch route/class is distinct from an actual passed inference-invoke receipt.","free_eligibility":"Null unless an exact account+model admission receipt exists; this generator does not infer eligibility.","quota":"Limits and resets are copied from the quota registry; null is not zero."},"summary":summary,"providers":providers,"records":records,"tournament":{"campaign_id":design.get("campaign_id"),"status":design.get("status"),"assignment":design.get("design",{}).get("assignment"),"window_rule":design.get("design",{}).get("window_rule"),"cull_rule":design.get("design",{}).get("cull_rule"),"provider_stamp_required":["provider","selection_reason","ts"],"desk_rotation_rule":catalog.get("rotation_rule",{}).get("rule"),"conditional_provider_arms":arms}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",default=".");ap.add_argument("--out",default="ops/quota/provider-participation-index.json");a=ap.parse_args()
    root=Path(a.root).resolve();doc=build(root);out=root/a.out;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");print(json.dumps(doc["summary"],sort_keys=True));return 0
if __name__=="__main__": raise SystemExit(main())
