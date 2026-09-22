#!/usr/bin/env python3
"""Pure-stdlib HITL control-plane primitives; no GitHub write capability."""
from __future__ import annotations
import argparse,hashlib,json
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from pathlib import Path
from typing import Any,Iterable

TRANSITIONS={
"DRAFT":{"CONTEXTUALIZED","FAILED"},
"CONTEXTUALIZED":{"POLICY_CHECKED","FAILED"},
"POLICY_CHECKED":{"AWAITING_APPROVAL","FAILED"},
"AWAITING_APPROVAL":{"APPROVED","FAILED"},
"APPROVED":{"DISPATCHED","FAILED"},
"DISPATCHED":{"OBSERVED","FAILED"},
"OBSERVED":{"EFFECT_RECORDED","FAILED"},
"EFFECT_RECORDED":{"RECONCILED","FAILED"},
"RECONCILED":set(),"FAILED":set()}

@dataclass(frozen=True)
class Projection:
    snapshot_id:str
    source_sha:str|None
    event_start:str|None
    event_end:str|None
    event_count:int
    projection_kind:str

@dataclass(frozen=True)
class CommandProposal:
    command_id:str
    correlation_id:str
    intent:str
    target:str
    state:str
    approval_required:bool
    context_refs:tuple[str,...]
    proposed_at:str

def stable_id(*parts:str,prefix:str="hitl")->str:
    return f"{prefix}-{hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:32]}"

def propose_command(intent:str,target:str,context_refs:Iterable[str]=())->CommandProposal:
    now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    refs=tuple(context_refs); corr=stable_id(intent,target,*refs,prefix="corr")
    return CommandProposal(stable_id(corr,"command",prefix="cmd"),corr,intent,target,"DRAFT",True,refs,now)

def transition(state:str,next_state:str,approved:bool=False)->str:
    state,next_state=state.upper(),next_state.upper()
    if next_state not in TRANSITIONS.get(state,set()): raise ValueError(f"invalid HITL transition: {state} -> {next_state}")
    if next_state=="DISPATCHED" and not approved: raise PermissionError("DISPATCHED requires explicit HITL approval")
    return next_state

def read_events(lines:Iterable[str])->list[dict[str,Any]]:
    out=[]
    for line in lines:
        if line.strip():
            obj=json.loads(line)
            if isinstance(obj,dict): out.append(obj)
    return sorted(out,key=lambda x:(str(x.get("occurred_at","")),str(x.get("event_id",""))))

def bounded_replay(events:list[dict[str,Any]],start:float=0,stop:float=1)->list[dict[str,Any]]:
    if not 0<=start<=stop<=1: raise ValueError("replay bounds must satisfy 0 <= start <= stop <= 1")
    return events[int(len(events)*start):int(len(events)*stop)]

def make_projection(events:list[dict[str,Any]],source_sha:str|None,kind:str)->Projection:
    ids=[str(e.get("event_id","")) for e in events]
    sid=stable_id(source_sha or "unknown",kind,*ids,prefix="snapshot")
    times=[str(e.get("occurred_at")) for e in events if e.get("occurred_at")]
    return Projection(sid,source_sha,min(times) if times else None,max(times) if times else None,len(events),kind)

def to_gource(events:Iterable[dict[str,Any]])->str:
    lines=[]
    for e in events:
        ts=e.get("occurred_at") or e.get("ts") or 0
        actor=e.get("actor",{}); actor=actor.get("id") if isinstance(actor,dict) else actor
        scope=e.get("scope") or {}; path=scope.get("entity_id") or scope.get("entity_type") or "ops/event"
        op=(e.get("attributes") or {}).get("gource_op","M")
        lines.append(f"{ts}|{actor or 'unknown'}|{op}|{path}")
    return "\n".join(lines)+("\n" if lines else "")

def projection_manifest(projection:Projection)->dict[str,Any]:
    return {"schema":"hitl.projection.v1","projection":asdict(projection)}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("events",nargs="?"); ap.add_argument("--start",type=float,default=0); ap.add_argument("--stop",type=float,default=1); ap.add_argument("--gource",action="store_true"); ap.add_argument("--manifest",action="store_true")
    a=ap.parse_args(); raw=Path(a.events).read_text(encoding="utf-8") if a.events else ""
    events=read_events(raw.splitlines()); selected=bounded_replay(events,a.start,a.stop)
    proj=make_projection(selected,None,"gource" if a.gource else "interactive")
    if a.gource: print(to_gource(selected),end="")
    if a.manifest: print(json.dumps(projection_manifest(proj),indent=2))
    if not a.gource and not a.manifest: print(json.dumps({"projection":projection_manifest(proj),"events":selected},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
