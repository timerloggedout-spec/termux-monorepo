#!/usr/bin/env python3
"""Fix the upload-artifact pin (smoke run 40041027460 failed at job setup:
'unable to find version ea165f8d...' — the correct v4.6.2 commit is
ea165f8d65b6e75b540449e92b4886f43607fa02, resolved live from the
actions/upload-artifact tag refs). One-file PR off current master."""
import base64
import json
import subprocess
import sys

GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "mesh/fix-upload-artifact-pin"
PATH = ".github/workflows/integration-mesh-poll.yml"
SRC = "/home/hatch/workspace/mesh-poll-build/.github/workflows/integration-mesh-poll.yml"


def gh(method, path, body=None):
    args = [GH, "get", path] if method == "GET" else [GH, "api", method, path]
    if body is not None:
        args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:400])
        sys.exit(1)
    return json.loads(out.stdout)


master = gh("GET", f"/repos/{REPO}/branches/master")
msha = master["commit"]["sha"]
print("master head:", msha[:12])
cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref=master")

r = subprocess.run([GH, "api", "POST", f"/repos/{REPO}/git/refs",
                    json.dumps({"ref": f"refs/heads/{BRANCH}", "sha": msha})],
                   capture_output=True, text=True)
print("branch create:", (r.stdout or "")[:140].replace("\n", " "))

content = base64.b64encode(open(SRC, "rb").read()).decode()
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "fix(mesh): correct actions/upload-artifact pin to the real v4.6.2 commit",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("commit:", res["commit"]["sha"][:12])

body = """[MUSEai]@{role:{`Muse`}}

One-line fix. The first smoke dispatch of `integration-mesh-poll.yml` (run 40041027460) failed at **job setup** — annotation on the check run: *"Unable to resolve action `actions/upload-artifact@ea165f8d65b6cb411bff43eea0b33f7d36d5e12c`, unable to find version…"*. That SHA was garbled at authoring time.

The correct pin, resolved live from `actions/upload-artifact` tag refs for this PR: **v4.6.2 = `ea165f8d65b6e75b540449e92b4886f43607fa02`** (commit object). The `actions/cache` pins in the same file were verified the same way (0057852b… = v4.3.0 commit) and are unchanged. Nothing else changes."""
pr = gh("POST", f"/repos/{REPO}/pulls", {
    "title": "fix(mesh): correct actions/upload-artifact pin (v4.6.2 commit)",
    "head": BRANCH, "base": "master", "body": body})
print("PR:", pr["number"], pr["html_url"])
