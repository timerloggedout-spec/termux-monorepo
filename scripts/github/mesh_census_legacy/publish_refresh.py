#!/usr/bin/env python3
"""Publish the §4B refresh: branch off current master, PUT doc, open PR."""
import json, subprocess, base64, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "docs/integration-mesh-matrix-refresh-2026-10-22"
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

master = gh("GET", f"/repos/{REPO}/branches/master")
msha = master["commit"]["sha"]
print("master head:", msha[:12])
cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref=master")
print("master file blob:", cur["sha"][:12])

# create branch (tolerate already-existing)
r = subprocess.run([GH, "api", "POST", f"/repos/{REPO}/git/refs",
                    json.dumps({"ref": f"refs/heads/{BRANCH}", "sha": msha})],
                   capture_output=True, text=True)
print("branch create:", (r.stdout or "")[:160].replace("\n", " "))

content = base64.b64encode(open(SRC, "rb").read()).decode()
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "docs(ops): matrix refresh — §4B installed apps (owner-firsthand), 46-name reconciliation, I8",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("commit:", res["commit"]["sha"][:12])

body = """[MUSEai]@{role:{`Muse`}}

**Matrix refresh — the Installed list joins the evidence base.**

Source: the owner's firsthand screenshot of Settings → Applications → **Installed GitHub Apps** (2026-10-22, visible A–H portion, 24 apps), transcribed and reconciled on Issue #184 (comment 6335646953). These are **app integrations** — this matrix is the integration inventory; #184 stays the credential inventory of record.

What this PR changes in `docs/ops/INTEGRATION-MESH-MATRIX.md`:

- **New evidence class OWNER-UI** + intro rewrite: the Installed tab's A–H portion is now firsthand-evidenced; the `/user/installations` API boundary is unchanged and still proven.
- **New §4B** — all 24 visible apps mapped against §4 (Aug-13 authorized) and the Oct-21 live census. **8 installed-only names** (Aikido PR Checks, blacksmith.sh, Codecov, endor-labs-github-agenthq, FalconerAI, GitHub Copilot for Linear, Hark, Hex - GitHub sync) → **46 distinct GitHub App names evidenced** (38 + 8); installed total remains NOT ESTABLISHED (list continues past H).
- **Four "Permission updates requested" flags** recorded (coderabbitai, Cursor, Devin.ai Integration, Factory Droid) as owner-UI items of record + new **§9 move I8**. ECC explicitly contrasted: no update is flagged for it, consistent with the vendor-config mechanism in §4.
- §5 preamble cross-check, §10 updated to the GitHub-landing rule (diffs → #1505, refresh PRs through gates), closing NOT ESTABLISHED bullet updated for the §4B partial evidence.
- Two substring traps avoided: the doc's prior "endor" hits were all the word *vendor*, and its "Hex" hits are a CellCog secret name — both apps are genuinely new coverage here.

No census figures were changed; all counts carry source + vintage labels. Diff note also posted on the standing thread #1505."""
pr = gh("POST", f"/repos/{REPO}/pulls", {
    "title": "docs(ops): matrix refresh — §4B installed apps (owner-firsthand) + 46-name reconciliation",
    "head": BRANCH, "base": "master", "body": body})
print("PR:", pr["number"], pr["html_url"])
