#!/usr/bin/env python3
"""Emit declaration telemetry and a sanitized GitHub App G4 runtime receipt."""
import argparse, datetime, json, math, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ops/github-apps/registry.json"
API = "https://api.github.com"
CONCLUSIONS = {"success","failure","cancelled","timed_out","action_required","neutral","skipped","stale","startup_failure"}

class Probe:
    def __init__(self, token):
        if not token: raise ValueError("installation token is required")
        self._token, self.status_counts = token, Counter()
    def get(self, path):
        if not path.startswith("/") or path.startswith("//"): raise ValueError("API path must be relative")
        req=urllib.request.Request(API+path,headers={"Authorization":"Bearer "+self._token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
        try:
            with urllib.request.urlopen(req,timeout=20) as response:
                status,payload,headers=response.status,json.load(response),response.headers
        except urllib.error.HTTPError as exc: status,payload,headers=exc.code,{},exc.headers
        except (OSError,TimeoutError): status,payload,headers=0,{},{}
        self.status_counts[str(status)]+=1
        return status,payload,headers

def load_registry(path=REGISTRY):
    data=json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version")!=1 or not isinstance(data.get("apps"),list): raise ValueError("invalid GitHub App registry")
    seen=set()
    for app in data["apps"]:
        slug=app.get("slug")
        if not isinstance(slug,str) or not slug or slug in seen: raise ValueError("app slugs must be unique non-empty strings")
        seen.add(slug)
        manifest=json.loads((ROOT/app["manifest_path"]).read_text(encoding="utf-8"))
        if not isinstance(manifest.get("default_permissions"),dict) or not isinstance(manifest.get("default_events"),list): raise ValueError(f"{slug}: manifest must declare permissions and events")
        app["declared_permissions"],app["declared_events"]=manifest["default_permissions"],manifest["default_events"]
    return data

def rate_limit(probe):
    status,payload,_=probe.get("/rate_limit")
    if status!=200: raise RuntimeError(f"rate-limit request failed with HTTP {status}")
    core=(payload.get("resources") or {}).get("core")
    if not isinstance(core,dict): raise ValueError("rate-limit response missing core bucket")
    reading={k:core.get(k) for k in ("limit","remaining","reset")}
    if any(type(reading[k]) is not int or reading[k]<0 for k in reading) or reading["remaining"]>reading["limit"]: raise ValueError("invalid rate-limit counters")
    return reading

def installation_repositories(probe):
    path="/installation/repositories?per_page=100"; repos=[]; visited=set()
    while path:
        if path in visited: raise ValueError("installation repository pagination loop detected")
        visited.add(path); status,payload,headers=probe.get(path)
        if status!=200 or not isinstance(payload.get("repositories"),list): raise RuntimeError(f"installation repository request failed with HTTP {status}")
        repos.extend(x["full_name"] for x in payload["repositories"] if isinstance(x,dict) and isinstance(x.get("full_name"),str))
        next_path=None
        for part in (headers.get("Link","") if headers else "").split(","):
            if 'rel="next"' in part:
                url=part[part.find("<")+1:part.find(">")]; parsed=urllib.parse.urlparse(url)
                if parsed.scheme!="https" or parsed.netloc!="api.github.com": raise ValueError("pagination link escaped GitHub API host")
                next_path=parsed.path+(("?"+parsed.query) if parsed.query else ""); break
        path=next_path
    return sorted(set(repos))

def validate_receipt(r):
    required={"schema_version","receipt_type","app_slug","mint_outcome","rate_limit_before","rate_limit_after","api_calls_by_status","repositories_inspected","workflow","duration_seconds","conclusion","observed_at"}
    if not isinstance(r,dict) or set(r)!=required: raise ValueError("G4 receipt has missing or unexpected fields")
    if type(r["schema_version"]) is not int or r["schema_version"]!=1 or r["receipt_type"]!="github_app_g4_runtime_receipt": raise ValueError("unsupported G4 receipt schema")
    if not isinstance(r["app_slug"],str) or not r["app_slug"]: raise ValueError("app_slug required")
    if r["mint_outcome"] not in ("success","failure"): raise ValueError("invalid mint outcome")
    for key in ("rate_limit_before","rate_limit_after"):
        row=r[key]
        if not isinstance(row,dict) or set(row)!={"limit","remaining","reset"} or any(type(row[k]) is not int or row[k]<0 for k in row) or row["remaining"]>row["limit"]: raise ValueError("invalid rate-limit reading")
    if not isinstance(r["api_calls_by_status"],dict): raise ValueError("API status counts must be an object")
    for status,count in r["api_calls_by_status"].items():
        if not isinstance(status,str) or len(status)!=3 or not status.isdigit() or status[0] not in "12345" or type(count) is not int or count<0: raise ValueError("invalid API status counter")
    if type(r["repositories_inspected"]) is not int or r["repositories_inspected"]<0: raise ValueError("invalid repositories_inspected")
    w=r["workflow"]
    if not isinstance(w,dict) or set(w)!={"run_id","attempt","head_sha"} or any(type(w[k]) is not int or w[k]<=0 for k in ("run_id","attempt")) or not isinstance(w["head_sha"],str) or len(w["head_sha"])!=40 or any(c not in "0123456789abcdef" for c in w["head_sha"]): raise ValueError("invalid workflow identity")
    d=r["duration_seconds"]
    if type(d) not in (int,float) or not math.isfinite(d) or d<0: raise ValueError("invalid duration")
    if r["conclusion"] not in CONCLUSIONS: raise ValueError("invalid conclusion")
    if datetime.datetime.fromisoformat(r["observed_at"].replace("Z","+00:00")).tzinfo is None: raise ValueError("timestamp must include timezone")
    return True

def collect(token,app_slug,workflow,conclusion="success"):
    registry=load_registry(); app=next((x for x in registry["apps"] if x["slug"]==app_slug),None)
    if app is None: raise ValueError("probe app is not registered")
    probe=Probe(token); started=time.monotonic(); before=rate_limit(probe); repos=installation_repositories(probe); after=rate_limit(probe)
    receipt={"schema_version":1,"receipt_type":"github_app_g4_runtime_receipt","app_slug":app_slug,"mint_outcome":"success","rate_limit_before":before,"rate_limit_after":after,"api_calls_by_status":dict(sorted(probe.status_counts.items())),"repositories_inspected":len(repos),"workflow":workflow,"duration_seconds":round(time.monotonic()-started,3),"conclusion":conclusion,"observed_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    validate_receipt(receipt)
    app["live_observation"]={"observed_at":receipt["observed_at"],"rate_limit":after,"repository_scope":repos,"evidence":"observed"}
    return {"schema_version":1,"registry_id":registry["registry_id"],"observed_at":receipt["observed_at"],"apps":registry["apps"],"planned_roles":registry.get("planned_roles",[]),"g4_runtime_receipt":receipt,"credential_policy":"short-lived token is never serialized"}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--output",required=True); p.add_argument("--probe-app",default="termux-fleet-collector"); a=p.parse_args(argv)
    try:
        workflow={"run_id":int(os.environ["GITHUB_RUN_ID"]),"attempt":int(os.environ.get("GITHUB_RUN_ATTEMPT","1")),"head_sha":os.environ["GITHUB_SHA"].lower()}
        result=collect(os.environ.get("GITHUB_APP_INSTALLATION_TOKEN"),a.probe_app,workflow)
        pathlib.Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        summary=os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            r=result["g4_runtime_receipt"]
            with open(summary,"a",encoding="utf-8") as f:
                f.write("## GitHub App Collector — G4 runtime receipt\n\n")
                for k in ("mint_outcome","rate_limit_before","rate_limit_after","api_calls_by_status","repositories_inspected","workflow","duration_seconds","conclusion","observed_at"): f.write(f"- {k}: {r[k]}\n")
        return 0
    except (OSError,ValueError,RuntimeError,KeyError,json.JSONDecodeError) as exc:
        print(f"GitHub App telemetry failed: {exc}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
