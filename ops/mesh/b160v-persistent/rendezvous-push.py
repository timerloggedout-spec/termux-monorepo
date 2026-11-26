#!/usr/bin/env python3
"""rendezvous-push.py — publish the current tunnel endpoint for the B160V.

Usage: rendezvous-push.py tcp://host:port

Writes mesh/b160v-endpoint.json in timerloggedout-spec/muse-vm-workspace-backup
(the fleet's private backup repo) via the GitHub Contents API. The VM-side
ProxyCommand (b160v-rendezvous-connect.py) reads that file to find us.

Credential (one-time provisioning, shared with the webWrapper streaming
token): a fine-grained GitHub token with Contents read/write on
muse-vm-workspace-backup ONLY, supplied by any of, in order:
  1. env B160V_GH_TOKEN or WEBWRAPPER_GH_TOKEN
  2. ~/b160v-persistent/token.env  (a file containing KEY=VALUE lines, 0600)
Fallback: if ~/b160v-rendezvous is a git checkout whose remote accepts
pushes, the file is committed and pushed there instead.
If no writer is armed, exits 2 and says so — the endpoint is still in
~/b160v-persistent/last-endpoint and printed by install.sh / status.
Stdlib only.
"""
import base64, json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = "timerloggedout-spec/muse-vm-workspace-backup"
PATH = "mesh/b160v-endpoint.json"
DIR = Path.home() / "b160v-persistent"

def load_token():
    for key in ("B160V_GH_TOKEN", "WEBWRAPPER_GH_TOKEN"):
        if os.environ.get(key):
            return os.environ[key].strip()
    env_file = DIR / "token.env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                if k.strip() in ("B160V_GH_TOKEN", "WEBWRAPPER_GH_TOKEN") and v.strip():
                    return v.strip()
    return None

def api(method, url, token, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, data=data, timeout=30) as r:
        return json.loads(r.read().decode() or "{}")

def main():
    if len(sys.argv) != 2 or not sys.argv[1].startswith("tcp://"):
        print("usage: rendezvous-push.py tcp://host:port")
        return 2
    hp = sys.argv[1][len("tcp://"):]
    host, _, port = hp.rpartition(":")
    payload = {
        "device": "b160v",
        "status": "live",
        "host": host,
        "port": int(port),
        "proto": "tcp",
        "source": "pinggy-free",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    text = json.dumps(payload, indent=2) + "\n"
    token = load_token()
    if token:
        url = f"https://api.github.com/repos/{REPO}/contents/{PATH}"
        sha = None
        try:
            cur = api("GET", url, token)
            sha = cur.get("sha")
        except Exception:
            sha = None  # file may not exist yet
        body = {"message": f"b160v endpoint {host}:{port}",
                "content": base64.b64encode(text.encode()).decode()}
        if sha:
            body["sha"] = sha
        out = api("PUT", url, token, body)
        print(f"rendezvous: pushed {host}:{port} commit {out.get('commit', {}).get('sha', '?')[:12]}")
        return 0
    checkout = Path.home() / "b160v-rendezvous"
    if (checkout / ".git").exists():
        target = checkout / PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        def git(*a):
            return subprocess.run(["git", "-C", str(checkout), *a],
                                  capture_output=True, text=True, timeout=60)
        git("add", PATH)
        c = git("commit", "-m", f"b160v endpoint {host}:{port}")
        p = git("push")
        if p.returncode == 0:
            print(f"rendezvous: pushed {host}:{port} via git checkout")
            return 0
        print(f"rendezvous: git push failed: {p.stderr.strip()[:200]}")
        return 2
    print("rendezvous: NO WRITER ARMED — set B160V_GH_TOKEN/WEBWRAPPER_GH_TOKEN "
          "or ~/b160v-persistent/token.env (fine-grained token, Contents RW on "
          "muse-vm-workspace-backup only). Endpoint recorded locally only.")
    return 2

if __name__ == "__main__":
    sys.exit(main())
