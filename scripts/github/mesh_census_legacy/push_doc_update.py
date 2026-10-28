#!/usr/bin/env python3
"""Update INTEGRATION-MESH-MATRIX.md on PR #1490's branch via the PAT helper."""
import json, subprocess, base64, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "docs/integration-mesh-matrix-2026-10-21"
PATH = "docs/ops/INTEGRATION-MESH-MATRIX.md"
SRC = "/home/hatch/workspace/github-integration-census/INTEGRATION-MESH-MATRIX.md"

def gh(method, path, body=None):
    if method == "GET":
        args = [GH, "get", path]
    else:
        args = [GH, "api", method, path]
        if body is not None:
            args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:300]); sys.exit(1)
    return json.loads(out.stdout)

cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref={BRANCH}")
content = base64.b64encode(open(SRC, "rb").read()).decode()
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "docs(ops): close Installations union list as NOT ESTABLISHED by design (fleet credential rule)",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("updated commit:", res["commit"]["sha"][:12])
cmt = gh("POST", f"/repos/{REPO}/issues/1490/comments", {"body":
    "[MUSEai]@{role:{`Muse`}}\n\nFleet credential alignment applied (owner order, 2026-10-21): all GitHub access runs through the custom PAT helper only; the manual interactive browser process for GitHub is refused permanently. The Settings → Installations union list is therefore **closed as NOT ESTABLISHED by design** in this doc (`/user/installations` refuses PATs with 403 by GitHub's design) — §3 + §4 + §5 are the answer of record, not a placeholder awaiting a sign-in. No content rows changed; the two framing passages (evidence-classes note + NOT ESTABLISHED) were updated in place."})
print("comment:", cmt["html_url"])
