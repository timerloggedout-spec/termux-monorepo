import json, subprocess
HELPER="/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
def get(path):
    r=subprocess.run(["python3",HELPER,"get",path],capture_output=True,text=True,timeout=120)
    try: return json.loads(r.stdout)
    except Exception: return {"_err":(r.stdout or "")[:200]}
census=json.load(open("/home/hatch/workspace/github-integration-census/census.json"))
slugs=[v.get("slug") for v in census["check_apps_on_recent_heads"].values() if v.get("slug")]
out={}
for s in sorted(set(slugs)):
    a=get(f"/apps/{s}")
    if isinstance(a,dict) and a.get("slug"):
        out[s]={"name":a.get("name"),"slug":a.get("slug"),
          "description":(a.get("description") or "")[:240],
          "html_url":a.get("html_url"),
          "owner":(a.get("owner") or {}).get("login"),
          "permissions":{k:v for k,v in (a.get("permissions") or {}).items() if v!="none"},
          "events":a.get("events") or []}
    else:
        out[s]={"_lookup":str(a)[:200]}
# submitted-review actors on open PRs + recently closed
import collections
rev=collections.Counter(); rev_state=collections.Counter()
prs=get("/repos/timerloggedout-spec/termux-monorepo/pulls?state=all&sort=updated&direction=desc&per_page=50")
nums=[p["number"] for p in prs] if isinstance(prs,list) else []
for n in nums[:50]:
    rs=get(f"/repos/timerloggedout-spec/termux-monorepo/pulls/{n}/reviews?per_page=100")
    if isinstance(rs,list):
        for x in rs:
            u=(x.get("user") or {}).get("login")
            if u: rev[u]+=1; rev_state[f"{u}|{x.get('state')}"]+=1
out["_review_actors_50pr"]={"counts":dict(rev.most_common(30)),"states":dict(rev_state.most_common(40)),"prs_scanned":len(nums[:50])}
json.dump(out, open("/home/hatch/workspace/github-integration-census/apps_detail.json","w"), indent=1)
print(json.dumps({"apps":len([k for k in out if not k.startswith('_')]),"review_actors":out["_review_actors_50pr"]["counts"]}, indent=1))
