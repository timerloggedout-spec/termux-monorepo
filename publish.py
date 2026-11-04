#!/usr/bin/env python3
import base64, json, subprocess, sys, urllib.request, urllib.error
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.github-app-publisher/bin")
import github_app_publisher as pub
PUB = pub.mint_token()["token"]
REPO = "timerloggedout-spec/termux-monorepo"
BASE = "https://api.github.com"
BRANCH = "quota/consumption-kind"
CLONE = "/home/hatch/workspace/scratch/cons"
WF = {".github/workflows/quota-analysis.yml", ".github/workflows/quota-usage-series-refresh.yml"}
def call(method, path, body=None, principal="pub", ok404=False):
    url = BASE + path if path.startswith("/") else path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if principal == "pub":
        req.add_header("Authorization", f"Bearer {PUB}")
    else:
        add_surrogate_to_request(req, "custom.github-pat", allowed_hosts=["api.github.com"])
    if data: req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {"status": resp.status}
    except urllib.error.HTTPError as e:
        if ok404 and e.code == 404: return None
        print("HTTP", e.code, method, path, e.read().decode(errors="replace")[:400]); sys.exit(1)
porc = subprocess.run(["git", "-C", CLONE, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
FILES = [ln[3:] for ln in porc if ln.strip()]
base_sha = subprocess.run(["git", "-C", CLONE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
master_sha = call("GET", f"/repos/{REPO}/git/ref/heads/master")["object"]["sha"]
print("files:", FILES, "| base==master:", base_sha == master_sha)
for path in FILES:
    b = call("GET", f"/repos/{REPO}/contents/{path}?ref={base_sha}", ok404=True)
    m = call("GET", f"/repos/{REPO}/contents/{path}?ref={master_sha}", ok404=True)
    if (b["sha"] if b else None) != (m["sha"] if m else None):
        print("DRIFT", path); sys.exit(2)
print("no drift")
call("POST", f"/repos/{REPO}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": master_sha})
head = None
for path in FILES:
    principal = "pat" if path in WF else "pub"
    content = open(f"{CLONE}/{path}", "rb").read()
    payload = {"message": f"feat(quota): consumption kind + named gap metric (owner fix order 2026-11-03) ({path})",
               "content": base64.b64encode(content).decode(), "branch": BRANCH}
    at_master = call("GET", f"/repos/{REPO}/contents/{path}?ref={master_sha}", ok404=True)
    if at_master: payload["sha"] = at_master["sha"]
    r = call("PUT", f"/repos/{REPO}/contents/{path}", payload, principal=principal)
    head = r["commit"]["sha"]
    print("put", principal.upper(), path, "->", head[:12])
body = """[MUSEai]@{role:{quota-convergence}} Owner fix order 2026-11-03 (16:51 PT): the quota graphs showed activity-proxy dispatch counts, not consumption. This PR builds the consumption data plane; the supply leg (Swarm: stamp assembly carries http-llm-invoke token outputs into stamps) and the reconciliation leg (quota-specialist: quota_delta vs registry entitlements) are briefed and land separately.

**F1 preflight verdict (recorded with the batch; workflow files ride a small PAT sub-batch per the established split - the Publisher app holds no workflows permission):**
{"verdict": "GO-PUBLISHER", "principal": "publisher", "batch": 30, "bulk": true, "remaining": 5000, "limit": 5000, "reserve_required": 0, "reset": 1793757503, "reads": {"publisher": {"remaining": 5000, "limit": 5000}}}

Recon (firsthand): the pipe existed and was dry at one joint - http-llm-invoke extracts tokens_in/tokens_out (null-honest, contract-tested) and stamp_fanout.py maps them into the 3L0 intake usage{}, but stamp assembly never carried them: all 27 committed intake rows carry tokens null, experiment-record usage{} sits at not_established.

What lands here:
- docs/ops/QUOTA-USAGE-RECORDS.md - the per-call usage contract (record shapes, method stamps, no-usage-surface cause, quota_delta ownership, gap definition).
- scripts/quota_usage_series.py - kind "consumption": per-call usage records (ops/3l0/intake.jsonl usage{} + routed-dispatch record usage{}) -> cumulative per-provider and per-model@version series, exact record match, units never mixed; plus pack.consumption_gap {routed_calls, usage_stamped, unstamped, unstamped_share, causes, by_provider} over the same deduped call corpus as the activity pass.
- apps/tribute-dashboard/quota-graphs.html - consumption kind label, summary consumption-coverage line, and a NAMED gap card ("UNMEASURED - unstamped routed calls") on the provider axis: unstamped calls are counted and named, never silently excluded.
- Regenerated usage-series pair (byte-identical): gap at landing = 0/22 usage-stamped, 22 unmeasured (100%), causes all no-usage-record - the honest headline until Swarm's stamps carry values, at which point consumption series render with no further quota-side change (series-refresh trigger paths += ops/3l0/intake.jsonl).
- tests/test_quota_consumption.py (3 tests: series+gap math incl. dedupe and CI exclusion, activity-proxy untouched, page hooks) - added to the quota-analysis battery.

Local battery: new tests 3/3 pass; failure set vs pristine master is identical (pre-existing dashboard page item + sparse-tree artifacts only)."""
pr = call("POST", f"/repos/{REPO}/pulls", {
    "title": "feat(quota): per-call consumption kind + named gap metric (owner fix order 2026-11-03)",
    "head": BRANCH, "base": "master", "body": body})
print("PR_NUMBER", pr["number"])
print("HEAD", head)
