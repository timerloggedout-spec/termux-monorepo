#!/usr/bin/env python3
"""Fix the stale §9 I1 row on master: #1491 merged 2026-10-22 as an in-job STEP
(not a standalone mirror-checks job — owner-corrected design). Small PR."""
import json, subprocess, base64, re, sys
GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "docs/matrix-i1-status-fix-2026-10-22"
PATH = "docs/ops/INTEGRATION-MESH-MATRIX.md"

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
cur = gh("GET", f"/repos/{REPO}/contents/{PATH}?ref=master")
text = base64.b64decode(cur["content"]).decode()

NEW_I1 = ("| I1 | ECC check runs come from the repo-side mirror, not from any settings approval "
          "| ECC is the top bot actor (**901/2,000 comments, 45%**) but publishes **zero** check runs because the vendor app requests "
          "**no Checks permission in its own configuration** (`GET /apps/ecc-tools`) — no owner approval exists to give, in any UI. "
          "**Done as build, not as an ask — MERGED 2026-10-22 (PR #1491, e6c4d342):** a `Mirror ECC audit outcomes to check runs` **step** "
          "folded into the existing `sweep-prs` job of `agent-ecc-tools-ops.yml` (+ `checks: write` on that job only — zero new jobs, zero new "
          "executions; trigger accounting per the owner's rule), republishing ECC's own audit conclusions as evidence-only check runs on the "
          "existing sweep cadence (06:23/18:23 UTC) "
          "| Landed and verified on master (step + `checks: write` present, no standalone job). First execution on the next regular ecc-ops sweep; "
          "vendor adding Checks app-side would supersede the mirror |")

lines = text.split("\n")
hit = [i for i, l in enumerate(lines) if l.startswith("| I1 |")]
assert len(hit) == 1, f"I1 rows found: {len(hit)}"
lines[hit[0]] = NEW_I1
new_text = "\n".join(lines)
assert "<<<<<<<" not in new_text and ">>>>>>>" not in new_text
assert "mirror-checks` job" not in new_text
open("/tmp/matrix_i1_fixed.md", "w").write(new_text)
print("I1 row replaced on master base", msha[:12], "| new bytes:", len(new_text))

r = subprocess.run([GH, "api", "POST", f"/repos/{REPO}/git/refs",
                    json.dumps({"ref": f"refs/heads/{BRANCH}", "sha": msha})],
                   capture_output=True, text=True)
print("branch:", (r.stdout or "")[:100].replace("\n", " "))
res = gh("PUT", f"/repos/{REPO}/contents/{PATH}", {
    "message": "docs(ops): fix stale §9 I1 — #1491 merged as an in-job step, not a mirror-checks job",
    "branch": BRANCH,
    "content": base64.b64encode(new_text.encode()).decode(),
    "sha": cur["sha"]})
print("commit:", res["commit"]["sha"][:12])
body = """[MUSEai]@{role:{`Muse`}}

**Stale-row fix.** §9 I1 still described PR #1491 in its pre-correction shape ("adds a `mirror-checks` job", "lands through normal lane review"). Reality, verified live: #1491 was amended on the owner's correction to a **step inside the existing `sweep-prs` job** (zero new jobs/executions) and **merged 2026-10-22 as e6c4d342**, content verified on master. The row now says exactly that, including the sweep cadence and the trigger-accounting note.

Single row changed; no figures touched. Found during a design audit of the matrix + poll pipeline (the refresh flow updates figures but nothing owned plan-state — this PR is the manual catch; the poll now flags stale plan rows in its #1505 diffs)."""
pr = gh("POST", f"/repos/{REPO}/pulls", {
    "title": "docs(ops): fix stale §9 I1 — #1491 merged as in-job step",
    "head": BRANCH, "base": "master", "body": body})
print("PR:", pr["number"], pr["html_url"])
