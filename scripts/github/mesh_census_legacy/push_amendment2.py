#!/usr/bin/env python3
"""Push the census-v3 amendment (§5B personal account) to PR #1490 + comment."""
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
    "message": "docs(ops): census v3 — §5B personal account (cross-repo app reach + sign-in inventory)",
    "branch": BRANCH, "content": content, "sha": cur["sha"]})
print("updated commit:", res["commit"]["sha"][:12])
body = """[MUSEai]@{role:{`Muse`}}

**Census v3 amendment — new §5B: the personal account itself** (the org counterpart was §5A).

- **Cross-repo app reach, firsthand:** head-commit check suites across the 60 most recently pushed personal repos. Only 10 repos show any app activity; the full 19–23 app cluster (CodeRabbit/Devin/Cursor/Vercel/Render/Travis/Sentry/Tembo/Graphite/Mintlify/Kilo/Pulumi/Blacksmith et al.) is active on exactly **7 repos** — termux-monorepo, timerloggedout-spec.github.io, gh-aw-mcpg_fork, gh-aw_fork, agentos_fork, gpt4free_fork, zero. Codecov reaches 5 of them, Hark 4, Pages 2. Three repos show Actions only; the other 50 show nothing on their heads. Only the hub has webhooks (top-15 check).
- **Sign-in inventory from direct endpoints:** 1 verified primary email, 1 SSH key (`DeepSeek_Account-1_ssh`), 0 GPG / 0 signing keys, 1 social account, 2FA on. Login sessions/devices are not exposed by any GitHub API and are recorded as such — no API record is claimed.
- §5B states its own limit in place: cross-repo suites prove effective reach/activity; the personal account's installation *records* remain behind the §5A proven boundary (`/user/installations` refused to all five credential classes)."""
cmt = gh("POST", f"/repos/{REPO}/issues/1490/comments", {"body": body})
print("comment:", cmt["html_url"])
