#!/usr/bin/env python3
"""Gravitee APIM Management API v2 helper — full build (2026-10-28).

Built from the vendor OpenAPI specs vendored in the official MCP repo
(gravitee-io/gravitee-apim-mcp-server/.speakeasy, targeting APIM 4.12):
149 paths / 189 operations across openapi-apis.yaml + openapi-environments.yaml.
Base shapes (spec `servers:`): root = <host>/management/v2 ;
org base = <host>/management/v2/organizations/{orgId}.

Auth: service-account Personal Access Token, `Authorization: Bearer <PAT>`,
from the registered custom.gravitee connection via surrogate exchange.
Never stored here. STATUS: no instance/credential yet — live calls exit
BLOCKED until an instance host exists (see CONNECTOR.md).

Reads (no flag):  ping envs env apis api api-export plans plan pages page
  subscriptions subscription members analytics health logs audits groups
  integrations integration clusters cluster scoring spg portal-pages
Writes (need --yes): api-create api-import api-update api-delete api-start
  api-stop api-deploy plan-create plan-publish plan-close page-create
  page-publish sub-accept sub-reject sub-close sub-pause sub-resume
  key-renew key-revoke spg-deploy
Generic: get|post|put|patch|delete <path-after-base> [--file body.json]
Utility: mcp-config (official MCP client JSON, token as env placeholder),
  ops (coverage summary)
Global: --base-url <root /management/v2 URL> | GRAVITEE_BASE_URL, --org, --env
"""
import json, os, sys, urllib.request, urllib.parse
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

WRITE_CMDS = {"api-create","api-import","api-update","api-delete","api-start",
  "api-stop","api-deploy","plan-create","plan-publish","plan-close",
  "page-create","page-publish","sub-accept","sub-reject","sub-close",
  "sub-pause","sub-resume","key-renew","key-revoke","spg-deploy",
  "post","put","patch","delete"}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call(base, method, path, body=None):
    host = urllib.parse.urlparse(base).hostname
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base.rstrip("/") + path, data=data, method=method)
    if data: req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, "custom.gravitee", allowed_hosts=[host])
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
            if resp.status == 204:
                return {"ok": True, "status": 204}
            return read_json_response(resp)
    except urllib.error.HTTPError as e:
        print(json.dumps({"ok": False, "status": e.code,
                          "body": e.read().decode(errors="replace")[:2000]}))
        sys.exit(1)

def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default

def pos(args, skip):
    out = []
    i = 0
    while i < len(args):
        if args[i] in skip: i += 2
        elif args[i] == "--yes": i += 1
        else: out.append(args[i]); i += 1
    return out

def main():
    args = sys.argv[1:]
    if not args: print(__doc__); return
    _p = pos(args, ("--base-url", "--org", "--env", "--file"))
    cmd = _p[0] if _p else ""
    if cmd == "ops":
        print(json.dumps({"spec": "mAPI v2 (APIM 4.12, via official MCP repo .speakeasy)",
          "paths": 149, "operations": 189,
          "named_commands": 42, "generic_fallback": "get/post/put/patch/delete any spec path",
          "mcp_equivalent": "@gravitee/apim-mcp-server (npx, dynamic or full mode)"}, indent=1)); return
    if cmd == "mcp-config":
        base = opt(args, "--base-url", os.environ.get("GRAVITEE_BASE_URL", "<instance>/management/v2"))
        print(json.dumps({"mcpServers": {"GraviteeApim": {"command": "npx",
          "args": ["-y", "@gravitee/apim-mcp-server", "start", "--mode", "dynamic",
                   "--bearer-auth", "${APIM_BEARER_TOKEN}", "--server-url", base]}}}, indent=1)); return
    base = opt(args, "--base-url", os.environ.get("GRAVITEE_BASE_URL", ""))
    if not (base.startswith("https://") or base.startswith("http://localhost")):
        print(json.dumps({"ok": False, "error": "BLOCKED: no instance base URL. "
              "No Gravitee instance/account exists (no signup/card per owner rule; "
              "this VM has no docker + ~0.5G RAM free, self-host infeasible here). "
              "Unblock: instance host + service-account PAT registration."}))
        sys.exit(2)
    if cmd in WRITE_CMDS and "--yes" not in args:
        print(json.dumps({"ok": False, "error": f"{cmd} is a write; pass --yes"})); sys.exit(3)
    org, env = opt(args, "--org", "DEFAULT"), opt(args, "--env", "DEFAULT")
    root, ob = base.rstrip("/"), base.rstrip("/") + f"/organizations/{org}"
    eb = ob + f"/environments/{env}"
    p = pos(args, ("--base-url", "--org", "--env", "--file"))[1:] + ["", "", ""]
    body = json.load(open(opt(args, "--file"))) if opt(args, "--file") else None
    A = f"/apis/{p[0]}" if p else ""
    routes = {
      "ping": ("GET", root, f"/organizations/{org}"),
      "envs": ("GET", root, f"/organizations/{org}/environments"),
      "env": ("GET", root, f"/organizations/{org}/environments/{env}"),
      "apis": ("GET", ob, f"/environments/{env}/apis"),
      "api": ("GET", ob, f"/environments/{env}{A}"),
      "api-export": ("GET", ob, f"/environments/{env}{A}/_export/definition"),
      "plans": ("GET", ob, f"/environments/{env}{A}/plans"),
      "plan": ("GET", ob, f"/environments/{env}{A}/plans/{p[1]}"),
      "pages": ("GET", ob, f"/environments/{env}{A}/pages"),
      "page": ("GET", ob, f"/environments/{env}{A}/pages/{p[1]}"),
      "subscriptions": ("GET", ob, f"/environments/{env}{A}/subscriptions"),
      "subscription": ("GET", ob, f"/environments/{env}{A}/subscriptions/{p[1]}"),
      "members": ("GET", ob, f"/environments/{env}{A}/members"),
      "analytics": ("GET", ob, f"/environments/{env}{A}/analytics/requests-count"),
      "health": ("GET", ob, f"/environments/{env}{A}/health/availability"),
      "logs": ("GET", ob, f"/environments/{env}{A}/logs"),
      "audits": ("GET", ob, f"/environments/{env}{A}/audits"),
      "groups": ("GET", ob, f"/environments/{env}/groups"),
      "integrations": ("GET", ob, f"/environments/{env}/integrations"),
      "integration": ("GET", ob, f"/environments/{env}/integrations/{p[0]}"),
      "clusters": ("GET", ob, "/clusters"),
      "cluster": ("GET", ob, f"/clusters/{p[0]}"),
      "scoring": ("GET", ob, "/scoring/overview"),
      "spg": ("GET", ob, "/shared-policy-groups"),
      "portal-pages": ("GET", ob, "/portal-pages"),
      "api-create": ("POST", ob, f"/environments/{env}/apis"),
      "api-import": ("POST", ob, f"/environments/{env}/apis/_import/definition"),
      "api-update": ("PUT", ob, f"/environments/{env}{A}"),
      "api-delete": ("DELETE", ob, f"/environments/{env}{A}"),
      "api-start": ("POST", ob, f"/environments/{env}{A}/_start"),
      "api-stop": ("POST", ob, f"/environments/{env}{A}/_stop"),
      "api-deploy": ("POST", ob, f"/environments/{env}{A}/deployments"),
      "plan-create": ("POST", ob, f"/environments/{env}{A}/plans"),
      "plan-publish": ("POST", ob, f"/environments/{env}{A}/plans/{p[1]}/_publish"),
      "plan-close": ("POST", ob, f"/environments/{env}{A}/plans/{p[1]}/_close"),
      "page-create": ("POST", ob, f"/environments/{env}{A}/pages"),
      "page-publish": ("POST", ob, f"/environments/{env}{A}/pages/{p[1]}/_publish"),
      "sub-accept": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/_accept"),
      "sub-reject": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/_reject"),
      "sub-close": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/_close"),
      "sub-pause": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/_pause"),
      "sub-resume": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/_resume"),
      "key-renew": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/api-keys/_renew"),
      "key-revoke": ("POST", ob, f"/environments/{env}{A}/subscriptions/{p[1]}/api-keys/{p[2]}/_revoke"),
      "spg-deploy": ("POST", ob, f"/shared-policy-groups/{p[0]}/_deploy"),
    }
    if cmd in routes:
        m, b, path = routes[cmd]
        print(json.dumps(call(b, m, path, body), indent=1)); return
    if cmd in ("get", "post", "put", "patch", "delete"):
        print(json.dumps(call(ob, cmd.upper(), p[0], body), indent=1)); return
    print(__doc__)

if __name__ == "__main__":
    main()
