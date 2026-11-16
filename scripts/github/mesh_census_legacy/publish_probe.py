#!/usr/bin/env python3
"""Publish the probe workflow to its own branch (push triggers the run). No PR."""
import json, subprocess, base64, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "mesh/installations-probe-2026-10-21"
PATH = ".github/workflows/mesh-installations-probe.yml"
SRC = "/home/hatch/workspace/github-integration-census/mesh-installations-probe.yml"

def gh(method, path, body=None):
    args = [GH, "get", path] if method == "GET" else [GH, "api", method, path]
    if body is not None:
        args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:400]); sys.exit(1)
    return json.loads(out.stdout)

master = gh("GET", f"/repos/{REPO}/git/ref/heads/master")["object"]["sha"]
print("master:", master[:12])
try:
    gh("POST", f"/repos/{REPO}/git/refs", {"ref": f"refs/heads/{BRANCH}", "sha": master})
    print("branch created")
except SystemExit:
    print("branch may already exist, continuing")
content = base64.b64encode(open(SRC, "rb").read()).decode()
sha = None
chk = subprocess.run([GH, "get", f"/repos/{REPO}/contents/{PATH}?ref={BRANCH}"], capture_output=True, text=True)
if chk.returncode == 0:
    sha = json.loads(chk.stdout).get("sha")
payload = {"message": "ci(probe): installations probe via stored tokens (names-only, Issue #184)", "branch": BRANCH, "content": content}
if sha:
    payload["sha"] = sha
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", payload)
print("workflow committed:", res["commit"]["sha"][:12])
