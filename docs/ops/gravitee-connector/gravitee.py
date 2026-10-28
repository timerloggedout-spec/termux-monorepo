#!/usr/bin/env python3
"""Gravitee APIM Management API v2 helper.

STATUS: SCAFFOLD / UNVERIFIED (2026-10-28). No Gravitee instance or account
exists yet and no credential is registered. The base URL is instance-specific
(self-hosted or Gravitee Cloud), so registration via
credentials.request_api_access can only happen once the owner rules on
hosting and an instance host exists.

Credential (once registered): service-account Personal Access Token for
custom.gravitee, read from the registered connection via surrogate exchange;
never stored here. Auth: Authorization: Bearer <PAT>.

Usage:
  gravitee.py --base-url <https://host/management/v2> ping [--org DEFAULT]
  gravitee.py --base-url <url> list-envs [--org DEFAULT]
  gravitee.py --base-url <url> list-apis [--org DEFAULT] [--env DEFAULT]
  gravitee.py --base-url <url> get <path-after-/management/v2>
Base URL may also come from GRAVITEE_BASE_URL (non-secret config only).
"""
import json, os, sys, urllib.request, urllib.parse
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")

def call(base, path):
    host = urllib.parse.urlparse(base).hostname
    req = urllib.request.Request(base.rstrip("/") + path, method="GET")
    add_surrogate_to_request(req, "custom.gravitee", allowed_hosts=[host])
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
            return read_json_response(resp)
    except urllib.error.HTTPError as e:
        print(json.dumps({"ok": False, "status": e.code,
                          "body": e.read().decode(errors="replace")[:2000]}))
        sys.exit(1)

def opt(args, name, default):
    return args[args.index(name) + 1] if name in args else default

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    base = opt(args, "--base-url", os.environ.get("GRAVITEE_BASE_URL", ""))
    if not base.startswith("https://") and not base.startswith("http://localhost"):
        print(json.dumps({"ok": False, "error": "BLOCKED: no instance base URL. "
              "Owner ruling required: self-host vs cloud + instance host. "
              "No account/instance exists; no credential registered."}))
        sys.exit(2)
    org = opt(args, "--org", "DEFAULT"); env = opt(args, "--env", "DEFAULT")
    cmd = next((a for a in args if not a.startswith("--") and
                args[args.index(a) - 1] not in ("--base-url", "--org", "--env")), None)
    if cmd == "ping":
        print(json.dumps(call(base, f"/organizations/{org}"), indent=1))
    elif cmd == "list-envs":
        print(json.dumps(call(base, f"/organizations/{org}/environments"), indent=1))
    elif cmd == "list-apis":
        print(json.dumps(call(base, f"/organizations/{org}/environments/{env}/apis"), indent=1))
    elif cmd == "get":
        print(json.dumps(call(base, args[args.index("get") + 1]), indent=1))
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
