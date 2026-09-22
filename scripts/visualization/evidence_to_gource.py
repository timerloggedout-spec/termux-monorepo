#!/usr/bin/env python3
import argparse,json,sys
from datetime import datetime
ACTION={"file.added":"A","file.modified":"M","file.deleted":"D","repository.file_added":"A","repository.file_modified":"M","repository.file_deleted":"D"}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("input",nargs="?",default="-"); ap.add_argument("--actor-attribute",default="actor"); a=ap.parse_args()
 fh=sys.stdin if a.input=="-" else open(a.input,encoding="utf-8")
 for line in fh:
  if not line.strip(): continue
  e=json.loads(line)
  if e.get("schema_version")!="eps.v1" or not e.get("event_id") or not e.get("provenance",{}).get("source_ref"): raise ValueError("invalid EPS provenance")
  attrs=e.get("attributes",{}); action=ACTION.get(e.get("event_type"),attrs.get("gource_action")); path=attrs.get("path") or attrs.get("file_path"); actor=attrs.get(a.actor_attribute) or e.get("entity_id")
  if action not in "AMD" or not path or not actor: continue
  ts=int(datetime.fromisoformat(e["occurred_at"].replace("Z","+00:00")).timestamp())
  print(f"{ts}|{str(actor).replace('|','/')}|{action}|{str(path).replace('|','/')}")
if __name__=="__main__": main()
