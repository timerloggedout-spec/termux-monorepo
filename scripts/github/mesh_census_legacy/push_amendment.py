#!/usr/bin/env python3
"""Push the census-v2 amendment to PR #1490's branch + post a summary comment."""
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
        print("FAILED", method, path, out.stdout[:300]); sys.exit(1)
    return json.loads(out.stdout)

cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref={BRANCH}")
content = base64.b64encode(open(SRC, "rb").read()).decode()
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "docs(ops): census v2 amendment — live-derived counts, org installations (§5A), ECC mechanism correction",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("updated commit:", res["commit"]["sha"][:12])
body = """[MUSEai]@{role:{`Muse`}}

**Census v2 amendment** (owner correction applied: no copied stats — every figure below was derived from live API responses in this pass, fully paginated):

- **New §5A — org installations retrieved.** `GET /orgs/{org}/installations` answers the owner PAT chat-side AND the stored classic admin tokens from inside Actions (probe run 39639440245, receipts on #184 as comment 6321665538; four credentials, identical results): Research-Astute has 6 installations (jules, render, manus-connector, mintlify, blacksmith-sh, codecov), search-astute-ly has 3 — all `repository_selection: all`, none suspended. Includes the 6-token capability matrix.
- **`/user/installations` is now a proven boundary, not an assumption:** refused (403/404) to all five credential classes the fleet holds, receipts in §5A. The personal-account slice stays reconstructed from activity; the org slice is established.
- **Counts replaced with v2 firsthand totals:** 1,292 PRs (Jules authored 279), 193 true issues, 2,000 newest comments with only 10 distinct actors (ECC 901 = 45%; bots 79%), check suites across 30 master heads (Actions alone: 1,446 suites), submitted reviews in two labeled frames (updated-frame: Devin 154, CodeRabbit 61; created-frame: CodeRabbit leads, 18).
- **ECC row + I1 corrected:** `GET /apps/ecc-tools` shows the vendor app requests no Checks permission at all — there is no owner approval to give in any UI. I1 now records the actual fix: the repo-side mirror (PR #1491's `mirror-checks` job).
- **New §6 facts:** Actions default workflow permissions = write with `can_approve_pull_request_reviews: true`; deploy keys 0; autolinks 0; collaborators owner-only; Pages = legacy gh-pages.
- #184's 31/38 counts are labeled everywhere as the Aug-13 floor, superseded as current totals (live floor: ≥29 distinct apps active on this repo alone)."""
cmt = gh("POST", f"/repos/{REPO}/issues/1490/comments", {"body": body})
print("comment:", cmt["html_url"])
