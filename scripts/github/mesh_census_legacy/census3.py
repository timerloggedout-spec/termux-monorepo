#!/usr/bin/env python3
"""Census v3 — the PERSONAL account (timerloggedout-spec) itself.
Cross-repo check-suite census: an app installed on the personal account with
repository_selection=all leaves suites on every active repo; a selected-repos
install appears only where chosen. Plus sign-in surfaces. PAT helper only."""
import json, subprocess, collections

HELPER = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
OUT = {}

def get(path):
    r = subprocess.run(["python3", HELPER, "get", path], capture_output=True, text=True, timeout=120)
    try:
        d = json.loads(r.stdout)
    except Exception:
        return {"_error": (r.stdout or "")[:200]}
    if isinstance(d, dict) and d.get("ok") is False:
        return {"_error_status": d.get("status")}
    return d

# sign-in / identity surfaces
em = get("/user/emails")
OUT["emails"] = [{"email": e.get("email"), "primary": e.get("primary"), "verified": e.get("verified"),
                  "visibility": e.get("visibility")} for e in em] if isinstance(em, list) else em
OUT["user_installations_receipt"] = get("/user/installations")

# repos by recent push
repos = get("/user/repos?affiliation=owner&sort=pushed&direction=desc&per_page=100")
repos = repos if isinstance(repos, list) else []
OUT["repos_scanned_pool"] = len(repos)
top = repos[:60]
app_repos = collections.defaultdict(set)   # slug -> repo names
app_names = {}
repo_heads = {}
for r in top:
    full = r.get("full_name")
    commits = get(f"/repos/{full}/commits?per_page=1")
    if not isinstance(commits, list) or not commits:
        continue
    sha = commits[0].get("sha")
    repo_heads[full] = sha
    suites = get(f"/repos/{full}/commits/{sha}/check-suites?per_page=100")
    if isinstance(suites, dict):
        for s in suites.get("check_suites", []):
            app = s.get("app") or {}
            slug = app.get("slug")
            if slug:
                app_repos[slug].add(full)
                app_names[slug] = app.get("name")
OUT["repos_with_heads"] = len(repo_heads)
OUT["cross_repo_apps"] = {slug: {"name": app_names.get(slug), "repo_count": len(rs),
                                 "repos": sorted(rs)} for slug, rs in
                          sorted(app_repos.items(), key=lambda kv: -len(kv[1]))}

# hooks on the top 15 pushed repos
hooks_out = {}
for r in top[:15]:
    full = r.get("full_name")
    hk = get(f"/repos/{full}/hooks?per_page=100")
    if isinstance(hk, list):
        hooks_out[full] = [{"active": h.get("active"),
                            "host": __import__("urllib.parse", fromlist=["urlparse"]).urlparse((h.get("config") or {}).get("url", "")).netloc,
                            "events": len(h.get("events") or []),
                            "last_code": (h.get("last_response") or {}).get("code")} for h in hk]
OUT["hooks_top15"] = hooks_out

json.dump(OUT, open("/home/hatch/workspace/github-integration-census/census3.json", "w"), indent=1)
print(json.dumps({"emails": OUT["emails"], "installations_receipt": OUT["user_installations_receipt"],
                  "repos_with_heads": OUT["repos_with_heads"],
                  "apps": {k: v["repo_count"] for k, v in OUT["cross_repo_apps"].items()},
                  "hooks_nonempty": {k: v for k, v in hooks_out.items() if v}}, indent=1)[:4000])
