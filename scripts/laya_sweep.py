#!/usr/bin/env python3
"""Run a bounded Laya sweep across representative decision categories."""
from __future__ import annotations
import argparse,json,os,platform,time
from pathlib import Path
CASES=[
 {"id":"routing-billing","category":"routing","state":{"body":"Refund duplicate invoice payment."}},
 {"id":"routing-technical","category":"routing","state":{"body":"Production API is returning 503 errors."}},
 {"id":"security-suspicious","category":"security","state":{"body":"Unexpected login from a new location; please investigate."}},
 {"id":"agent-evidence","category":"agent","state":{"body":"The agent claims completion but has no test receipt."}},
 {"id":"code-review","category":"code","state":{"body":"PR changes the parser and adds regression tests."}},
 {"id":"ops-escalation","category":"ops","state":{"body":"Deployment is blocked by a failing health check."}},
]
QUESTIONS={"route":{"type":"choice","instructions":"Which bounded action category should handle this state?","criteria":{"billing":"payments, invoices, refunds","technical":"bugs, outages, service failures","security":"security incidents or suspicious access","agent":"agent evidence, completion, orchestration","code":"code changes, review, tests","ops":"deployment, runtime, operational failures","general":"none of the above"}},"urgency":{"type":"score","instructions":"How urgent is this state?","criteria":["low","medium","high"]}}
def main():
 p=argparse.ArgumentParser(); p.add_argument("--live",action="store_true"); p.add_argument("--output",default="-"); a=p.parse_args()
 router=None
 if a.live:
  os.environ.setdefault("USE_TF","0")
  from laya import Router
  router=Router(preload=False)
 rows=[]
 for case in CASES:
  started=time.perf_counter()
  result=router.predict(case["state"],QUESTIONS) if a.live else {"answers":{"route":{"choice":"general","confidence":0.5},"urgency":{"score":1.0,"confidence":0.5}}}
  rows.append({"schema_version":"laya-sweep.v1","case_id":case["id"],"category":case["category"],"mode":"live" if a.live else "mock","latency_ms":round((time.perf_counter()-started)*1000,3),"routing":result.get("routing",{}),"answers":result.get("answers",{}),"runtime":{"python":platform.python_version(),"platform":platform.platform()}})
 payload="\n".join(json.dumps(x,sort_keys=True) for x in rows)+"\n"
 if a.output=="-": print(payload,end="")
 else: Path(a.output).write_text(payload,encoding="utf-8")
if __name__=="__main__": main()
