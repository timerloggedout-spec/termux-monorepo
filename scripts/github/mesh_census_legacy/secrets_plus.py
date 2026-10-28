#!/usr/bin/env python3
"""Issue #184 (Credential Authorizations & Last-Used Evidence) + every other
secret/credential NAME list the GitHub API exposes. NAMES ONLY — the API never
returns secret values on list endpoints, and nothing here prints token values."""
import json, subprocess

HELPER = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
BASE = "/home/hatch/workspace/github-integration-census"

def get(path):
    r = subprocess.run(["python3", HELPER, "get", path], capture_output=True, text=True, timeout=120)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return {"_error": (r.stdout or "")[:200]}
    if isinstance(d, dict) and d.get("ok") is False:
        return {"_error_status": d.get("status")}
    return d

def names(path):
    d = get(path)
    if isinstance(d, dict) and "secrets" in d:
        return {"total": d.get("total_count"), "names": [s.get("name") for s in d["secrets"]]}
    return d

# 1) Issue #184 full body -> file for parsing
iss = get(f"/repos/{REPO}/issues/184")
body = iss.get("body") or ""
with open(f"{BASE}/issue184_body.txt", "w") as f:
    f.write(body)
out = {"issue184": {"title": iss.get("title"), "state": iss.get("state"), "body_chars": len(body)}}

# 2) Environment secrets for every environment on the repo
envs = ["env_Termux-MonoRepo","github-pages","hindsight-prod","Preview",
        "Preview – help-wanted-dash","Preview – help-wanted-oversight","Preview – mcp-hub",
        "Preview – termux-monorepo","Production","Production – help-wanted-dash",
        "Production – help-wanted-oversight","Production – mcp-hub","Production – termux-monorepo","staging"]
import urllib.parse
out["environment_secrets"] = {}
for e in envs:
    out["environment_secrets"][e] = names(f"/repos/{REPO}/environments/{urllib.parse.quote(e, safe='')}/secrets?per_page=100")

# 3) Org-level stores (user is admin of both orgs)
for org in ("Research-Astute", "search-astute-ly"):
    out[f"org_{org}"] = {
        "actions_secrets": names(f"/orgs/{org}/actions/secrets?per_page=100"),
        "dependabot_secrets": names(f"/orgs/{org}/dependabot/secrets?per_page=100"),
        "codespaces_secrets": names(f"/orgs/{org}/codespaces/secrets?per_page=100"),
        "actions_variables": (lambda d: [v.get("name") for v in d.get("variables", [])] if isinstance(d, dict) and "variables" in d else d)(get(f"/orgs/{org}/actions/variables?per_page=100")),
        "hooks": (lambda d: [{"active": h.get("active"), "events": h.get("events"),
                              "url_host": urllib.parse.urlparse((h.get("config") or {}).get("url", "")).netloc}
                             for h in d] if isinstance(d, list) else d)(get(f"/orgs/{org}/hooks?per_page=100")),
    }

# 4) User-level codespaces secrets
out["user_codespaces_secrets"] = names("/user/codespaces/secrets?per_page=100")

# 5) Repo stores recap (fresh)
out["repo_actions_secrets"] = names(f"/repos/{REPO}/actions/secrets?per_page=100")
out["repo_dependabot_secrets"] = names(f"/repos/{REPO}/dependabot/secrets?per_page=100")
out["repo_codespaces_secrets"] = names(f"/repos/{REPO}/codespaces/secrets?per_page=100")

json.dump(out, open(f"{BASE}/secrets_plus.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
