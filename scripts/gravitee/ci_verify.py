#!/usr/bin/env python3
"""Gravitee self-host CI verification (runs inside gravitee-selfhost.yml).

Boot proof chain, all against the ephemeral in-runner stack:
1. Basic-auth (vendor default admin/admin — fresh ephemeral instance only)
   GET /management/user -> admin id.
2. Mint a service PAT via the v1 tokens resource
   POST /management/organizations/DEFAULT/users/{id}/tokens {name}
   (UserTokensResource, gravitee-api-management). PAT stays in this process;
   never printed, never persisted.
3. Drive the REAL connector helper (docs/ops/gravitee-connector/gravitee.py)
   with a stubbed dynamic_credentials module carrying that PAT:
   ping -> apis -> seed sync-in (api-create from ops/gravitee/mesh-echo-api.json
   if absent) -> plan-create -> plan-publish -> api-start -> api readback.
4. Mesh redundancy sync proof: poll BOTH gateways (8082 + 8092) until
   GET /mesh-echo returns the mock body on each — same deployment, synced
   from the shared repository to two gateway nodes.
5. Sync-out: helper api-export -> $GRAVITEE_STATE_DIR/api-export.json
   (workflow caches/uploads it; next run restores it as sync evidence).
Exits non-zero on any failed step. Prints a JSON receipt (no secrets).
"""
import base64, importlib.util, io, json, os, sys, time, types
import urllib.request, urllib.error
from contextlib import redirect_stdout

ROOT = os.environ.get("MAPI", "http://localhost:8083")
STATE = os.environ.get("GRAVITEE_STATE_DIR", "gravitee-state")
BASIC = base64.b64encode(b"admin:admin").decode()
receipt = {"steps": []}

# Diagnostics belong to the workflow's GitHub surfaces, not to anyone
# downloading job logs afterwards: always leave a receipt in the state dir
# (artifact + cache + step summary read it), even on failure.
import atexit
os.makedirs(STATE, exist_ok=True)
atexit.register(lambda: json.dump(receipt, open(f"{STATE}/receipt.json", "w"), indent=1))

def note(step, **kw):
    receipt["steps"].append({"step": step, **kw}); print(f"[{step}] {kw}")

def raw(method, url, body=None, auth=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data: req.add_header("Content-Type", "application/json")
    if auth: req.add_header("Authorization", auth)
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read().decode()
        return r.status, (json.loads(b) if b else {})

# 1-2: admin -> PAT. NOTE: GET /management/user 500s on APIM 4.13 (latest)
# without org context (OrganizationServiceImpl.findById(null), run
# 40756680386 logs) — resolve the admin id via the org-scoped users list.
_, users = raw("GET", f"{ROOT}/management/organizations/DEFAULT/users?size=200",
               auth=f"Basic {BASIC}")
ulist = users.get("data", users if isinstance(users, list) else [])
admin = next(u for u in ulist if u.get("displayName") == "admin" or u.get("sourceId") == "admin")
admin_id = admin["id"]; note("admin-user", id=admin_id)
_, tok = raw("POST", f"{ROOT}/management/organizations/DEFAULT/users/{admin_id}/tokens",
             {"name": "ci-verify"}, auth=f"Basic {BASIC}")
pat = tok["token"]; note("pat-minted", name=tok.get("name"))

# 3: real helper with stubbed credential module
stub = types.ModuleType("dynamic_credentials")
def add_surrogate_to_request(req, provider, allowed_hosts=None):
    assert provider == "custom.gravitee"
    req.add_header("Authorization", f"Bearer {pat}")
stub.add_surrogate_to_request = add_surrogate_to_request
stub.read_json_response = lambda resp: json.loads(resp.read().decode() or "{}")
sys.modules["dynamic_credentials"] = stub
spec = importlib.util.spec_from_file_location(
    "gravitee", "docs/ops/gravitee-connector/gravitee.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

def helper(*argv):
    sys.argv = ["gravitee.py", "--base-url", f"{ROOT}/management/v2"] + list(argv)
    buf = io.StringIO()
    with redirect_stdout(buf):
        try: g.main()
        except SystemExit as e:
            if e.code: raise RuntimeError(f"helper {argv} exit {e.code}: {buf.getvalue()[:400]}")
    return json.loads(buf.getvalue())

org = helper("ping"); note("helper-ping", org=org.get("id") or org.get("name"))
apis = helper("apis")
existing = [a for a in apis.get("data", []) if a.get("name") == "Mesh Echo API"]
if existing:
    api_id = existing[0]["id"]; note("seed-sync-in", mode="already-present", api=api_id)
else:
    created = helper("api-create", "--file", "ops/gravitee/mesh-echo-api.json", "--yes")
    api_id = created["id"]; note("seed-sync-in", mode="created", api=api_id)
plans = helper("plans", api_id)
plist = plans.get("data", plans if isinstance(plans, list) else [])
if not plist:
    plan_file = "/tmp/keyless-plan.json"
    json.dump({"definitionVersion": "V4", "name": "Keyless", "description": "CI keyless plan",
               "characteristics": [], "security": {"type": "KEY_LESS"}, "mode": "STANDARD"},
              open(plan_file, "w"))
    plan = helper("plan-create", api_id, "--file", plan_file, "--yes")
    helper("plan-publish", api_id, plan["id"], "--yes")
    note("plan", mode="created+published", plan=plan["id"])
else:
    note("plan", mode="already-present", plan=plist[0]["id"])
helper("api-start", api_id, "--yes")
state = helper("api", api_id)
note("api-started", state=state.get("state"))

# 4: both gateways serve it
for port in (8082, 8092):
    ok = False
    for _ in range(36):
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/mesh-echo", timeout=5) as r:
                if b"gravitee-mesh-mock-ok" in r.read(): ok = True; break
        except Exception: time.sleep(5)
    assert ok, f"gateway :{port} never served /mesh-echo"
    note("gateway-sync", port=port, serves="/mesh-echo")

# 5: sync-out export
os.makedirs(STATE, exist_ok=True)
exported = helper("api-export", api_id)
json.dump(exported, open(f"{STATE}/api-export.json", "w"), indent=1)
note("sync-out", file=f"{STATE}/api-export.json", bytes=os.path.getsize(f"{STATE}/api-export.json"))
print(json.dumps({"ok": True, "receipt": receipt["steps"]}, indent=1))
