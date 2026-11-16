#!/usr/bin/env python3
"""Push the CodeRabbit review fixes for PR #1490 to its branch + comment."""
import json, subprocess, base64, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "docs/integration-mesh-matrix-2026-10-21"
PATH = "docs/ops/INTEGRATION-MESH-MATRIX.md"
SRC = "/home/hatch/workspace/github-integration-census/INTEGRATION-MESH-MATRIX.md"

def gh(method, path, body=None):
    args = [GH, "get", path] if method == "GET" else [GH, "api", method, path]
    if body is not None:
        args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:400]); sys.exit(1)
    return json.loads(out.stdout)

cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref={BRANCH}")
content = base64.b64encode(open(SRC, "rb").read()).decode()
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "docs(ops): address CodeRabbit review — scope over-broad claims, fix §2c heading, Qodo row cell",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("fix commit:", res["commit"]["sha"])
print("new head:", res["commit"]["sha"][:12])
