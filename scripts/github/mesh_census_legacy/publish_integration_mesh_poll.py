#!/usr/bin/env python3
"""Publish the Actions-native mesh poll: branch off current master, PUT files, open PR."""
import base64
import json
import subprocess
import sys

GH = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BRANCH = "mesh/integration-mesh-poll-workflow"
BASE = "/home/hatch/workspace/mesh-poll-build"

FILES = [
    (".github/workflows/integration-mesh-poll.yml", f"{BASE}/.github/workflows/integration-mesh-poll.yml",
     "ci(mesh): integration mesh poll as an Actions workflow (6h schedule + dispatch)"),
    ("scripts/github/integration_mesh_poll.py", f"{BASE}/scripts/github/integration_mesh_poll.py",
     "feat(mesh): census+diff poll script — port of the chat-side census suite"),
    ("scripts/github/test_integration_mesh_poll.py", f"{BASE}/scripts/github/test_integration_mesh_poll.py",
     "test(mesh): diff/plan-state unit tests for the poll script"),
    ("docs/ops/INTEGRATION-MESH-MATRIX.md", f"{BASE}/docs/ops/INTEGRATION-MESH-MATRIX.md",
     "docs(mesh): §9 rule 4 + §10 — poll is now the Actions workflow; cron retired"),
]


def gh(method, path, body=None):
    args = [GH, "get", path] if method == "GET" else [GH, "api", method, path]
    if body is not None:
        args.append(json.dumps(body))
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        print("FAILED", method, path, out.stdout[:400], out.stderr[:200])
        sys.exit(1)
    return json.loads(out.stdout)


master = gh("GET", f"/repos/{REPO}/branches/master")
msha = master["commit"]["sha"]
print("master head:", msha[:12])

r = subprocess.run([GH, "api", "POST", f"/repos/{REPO}/git/refs",
                    json.dumps({"ref": f"refs/heads/{BRANCH}", "sha": msha})],
                   capture_output=True, text=True)
print("branch create:", (r.stdout or "")[:140].replace("\n", " "))

for path, src, msg in FILES:
    cur = subprocess.run([GH, "get", f"/repos/{REPO}/contents/{path}?ref={BRANCH}"],
                         capture_output=True, text=True)
    sha = None
    try:
        d = json.loads(cur.stdout)
        if isinstance(d, dict) and d.get("sha"):
            sha = d["sha"]
    except Exception:
        pass
    content = base64.b64encode(open(src, "rb").read()).decode()
    body = {"message": msg, "branch": BRANCH, "content": content}
    if sha:
        body["sha"] = sha
    res = gh("PUT", f"/repos/{REPO}/contents/{path}", body)
    print("committed", path, res["commit"]["sha"][:12])

body = """[MUSEai]@{role:{`Muse`}}

**The Integration Mesh poll moves into GitHub Actions — the Muse cron is retired.**

Owner order (2026-10-23): "this poll is required to be an Automated Actions WorkFlow for use there." Done as a fix + upgrade, not a copy:

**What lands**
- `.github/workflows/integration-mesh-poll.yml` — schedule `41 */6 * * *` UTC + `workflow_dispatch` (dry_run / force_comment inputs), concurrency-guarded, `contents: read` + `issues: write` only.
- `scripts/github/integration_mesh_poll.py` — full port of the chat-side census suite (`census.py`/`census2.py`/`census3.py`/`secrets_plus.py`/`reviews_updated.py`): 30-head check apps, cross-repo reach (60 pushed repos), both orgs' installations, every secret store (**names only**), variables/environments/workflows, fully-paginated PR + true-issue totals, comment-actor + updated-PR review censuses, codespaces, deployment creators, and the §9 plan-state check. Runs on the provisioned `OPERATOR_GITHUB_TOKEN` with `GITHUB_TOKEN` fallback; any section the token can't read is recorded **degraded** and skipped by the diff (never read as a removal). Verify pass re-runs a headline total once if it drops/zeroes before anything publishes.
- `scripts/github/test_integration_mesh_poll.py` — 9 unit tests over the diff classification (structural vs figure, degraded-section safety, webhook flips, stale-row detection); the workflow runs them before every census.
- Matrix doc: §9 rule (4) + §10 rewritten to name this workflow as the poll of record.

**Landing rules — same as the cron design, one upgrade**
- Material diff → one `[MUSEai]` comment on the standing thread #1505. No change = no comment.
- **Upgrade:** structural changes (or 4 accumulated figure-only polls) also open/update a single labeled `mesh-refresh` issue carrying the diff + a refresh checklist — findings become tracked work instead of looping forever as comments (the GitLab-400 / ZenHub-422 loop this lane flagged on 2026-10-22).
- Poller output is **never committed** (rule §9(4) stands): the previous snapshot persists in the Actions cache (key prefix `integration-mesh-state-`) and every run uploads its snapshot as a 30-day artifact. Nothing pushes to master.

**Trigger accounting:** this *adds* one scheduled workflow (4 runs/day, ~430 API calls each against the PAT's 5,000/hr) and *removes* the external Muse cron that did the same census from chat. First run after merge is a baseline capture (announced on #1505); diffs start from the second run.

The Muse-side cron `github-integration-matrix-poll` has already been removed; this PR is its replacement, not a duplicate."""

pr = gh("POST", f"/repos/{REPO}/pulls", {
    "title": "ci(mesh): integration mesh poll as an Actions workflow — Muse cron retired",
    "head": BRANCH, "base": "master", "body": body})
print("PR:", pr["number"], pr["html_url"])
