#!/usr/bin/env python3
import argparse,hashlib,json,re,sys
from datetime import datetime
FORBIDDEN={"prompt","completion","messages","message","tool_payload","tool_call","credential","token","secret","password","repository_content"}
STATUSES={"observed","queued","running","completed","failed","cancelled","partial","unverified"}
def expected_id(e):
 s=[e.get(k) for k in ("event_type","source","repo","git_sha","run_id","run_attempt","entity_type","entity_id","status")]
 return "eps-"+hashlib.sha256(json.dumps(s,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()[:32]
def validate(e):
 req={"schema_version","event_id","event_type","occurred_at","source","repo","entity_type","entity_id","status","provenance","attributes"}
 if req-set(e): raise ValueError("missing:"+",".join(sorted(req-set(e))))
 if e["schema_version"]!="eps.v1": raise ValueError("schema_version")
 if not re.fullmatch(r"^[^/\\s]+/[^/\\s]+$",e["repo"]): raise ValueError("repo")
 if e.get("git_sha") is not None and not re.fullmatch(r"[0-9a-f]{40}",e["git_sha"]): raise ValueError("git_sha")
 if e["status"] not in STATUSES: raise ValueError("status")
 if not isinstance(e["attributes"],dict): raise ValueError("attributes")
 if FORBIDDEN & set(e["attributes"]): raise ValueError("forbidden")
 datetime.fromisoformat(e["occurred_at"].replace("Z","+00:00"))
 if not isinstance(e["provenance"],dict) or not e["provenance"].get("source_ref"): raise ValueError("provenance")
 c=e["provenance"].get("attribution_confidence")
 if c is not None and (not isinstance(c,(int,float)) or not 0<=c<=1): raise ValueError("confidence")
 if e["event_id"]!=expected_id(e): raise ValueError("event_id")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",default="-"); ap.add_argument("--unique",action="store_true"); a=ap.parse_args()
 fh=sys.stdin if a.input=="-" else open(a.input,encoding="utf-8"); seen=set()
 for n,line in enumerate(fh,1):
  if not line.strip(): continue
  try:
   e=json.loads(line); validate(e)
   if a.unique and e["event_id"] in seen: raise ValueError("duplicate event_id")
   seen.add(e["event_id"])
  except Exception as exc: print(f"line {n}: {exc}",file=sys.stderr); return 1
 return 0
if __name__=="__main__": raise SystemExit(main())
