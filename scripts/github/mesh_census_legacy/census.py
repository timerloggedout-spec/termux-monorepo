#!/usr/bin/env python3
"""Firsthand GitHub integration census for timerloggedout-spec via the PAT helper.
Names/metadata only. Secret VALUES are never fetched (API returns names only for
secret lists anyway); webhook secrets arrive masked from GitHub and are stripped.
Output: census.json in this directory."""
import json, subprocess, sys, collections, urllib.parse

HELPER = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
OUT = {}

def get(path):
    r = subprocess.run(["python3", HELPER, "get", path], capture_output=True, text=True, timeout=120)
    txt = (r.stdout or "").strip()
    try:
        data = json.loads(txt)
    except Exception:
        return {"_error": txt[:300], "_rc": r.returncode, "_stderr": (r.stderr or "")[:200]}
    if isinstance(data, dict) and data.get("ok") is False:
        return {"_error_status": data.get("status"), "_error_body": str(data.get("body"))[:300]}
    return data

def pages(path, max_pages=8):
    out, page = [], 1
    while page <= max_pages:
        sep = "&" if "?" in path else "?"
        batch = get(f"{path}{sep}per_page=100&page={page}")
        if not isinstance(batch, list):
            return batch if page == 1 else out
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out

def actor(a):
    if not a: return None
    return {"login": a.get("login"), "type": a.get("type"), "html_url": a.get("html_url")}

# --- account level ---
u = get("/user")
OUT["user"] = {k: u.get(k) for k in ("login","id","type","plan","public_repos","total_private_repos",
    "followers","following","created_at","two_factor_authentication","disk_usage")} if isinstance(u, dict) else u
OUT["orgs"] = [{"login": o.get("login"), "id": o.get("id")} for o in get("/user/orgs?per_page=100")]
mem = get("/user/memberships/orgs?per_page=100")
OUT["org_memberships"] = [{"org": (m.get("organization") or {}).get("login"), "role": m.get("role"), "state": m.get("state")} for m in mem] if isinstance(mem, list) else mem
OUT["social_accounts"] = get("/user/social_accounts")
OUT["ssh_keys"] = [{"id": k.get("id"), "title": k.get("title"), "created_at": k.get("created_at")} for k in get("/user/keys?per_page=100")] if isinstance(get("/user/keys?per_page=100"), list) else "error"
gpg = get("/user/gpg_keys?per_page=100")
OUT["gpg_keys"] = [{"id": k.get("id"), "name": k.get("name"), "primary_key_id": k.get("primary_key_id")} for k in gpg] if isinstance(gpg, list) else gpg
sig = get("/user/ssh_signing_keys?per_page=100")
OUT["ssh_signing_keys"] = [{"id": k.get("id"), "title": k.get("title")} for k in sig] if isinstance(sig, list) else sig

# all user repos (owned) summary
repos = pages("/user/repos?affiliation=owner&sort=updated", max_pages=10)
if isinstance(repos, list):
    OUT["user_repos"] = {"count": len(repos),
        "forks": sum(1 for r in repos if r.get("fork")),
        "archived": sum(1 for r in repos if r.get("archived")),
        "languages": dict(collections.Counter(r.get("language") for r in repos if r.get("language")).most_common(15)),
        "names": sorted(r.get("full_name") for r in repos)}
for org in ("Research-Astute", "search-astute-ly"):
    oreps = pages(f"/orgs/{org}/repos", max_pages=3)
    if isinstance(oreps, list):
        OUT.setdefault("org_repos", {})[org] = {"count": len(oreps), "names": sorted(r.get("full_name") for r in oreps)[:100]}

# codespaces
cs = get("/user/codespaces?per_page=100")
if isinstance(cs, dict) and "codespaces" in cs:
    OUT["codespaces"] = [{"name": c.get("name"), "state": c.get("state"),
        "repo": (c.get("repository") or {}).get("full_name"),
        "machine": (c.get("machine") or {}).get("display_name"),
        "created_at": c.get("created_at"), "last_used_at": c.get("last_used_at")} for c in cs["codespaces"]]
    OUT["codespaces_total"] = cs.get("total_count")
else:
    OUT["codespaces"] = cs

# packages, all types
OUT["packages"] = {}
for t in ("container","npm","maven","nuget","rubygems","docker"):
    pk = get(f"/user/packages?package_type={t}&per_page=100")
    if isinstance(pk, list) and pk:
        OUT["packages"][t] = [{"name": p.get("name"), "visibility": p.get("visibility"),
            "repo": (p.get("repository") or {}).get("full_name")} for p in pk]

# --- repo level ---
r = get(f"/repos/{REPO}")
OUT["repo"] = {k: r.get(k) for k in ("full_name","default_branch","private","fork","archived","size",
    "stargazers_count","forks_count","open_issues_count","watchers_count","has_issues","has_projects",
    "has_wiki","has_pages","has_discussions","visibility","created_at","pushed_at")} if isinstance(r, dict) else r
head_sha = None
commits = get(f"/repos/{REPO}/commits?per_page=5")
if isinstance(commits, list) and commits:
    head_sha = commits[0].get("sha")
    OUT["head"] = {"sha": head_sha, "date": ((commits[0].get("commit") or {}).get("committer") or {}).get("date")}

hooks = get(f"/repos/{REPO}/hooks?per_page=100")
OUT["hooks"] = [{"id": h.get("id"), "active": h.get("active"), "events": h.get("events"),
    "url_host": urllib.parse.urlparse((h.get("config") or {}).get("url","")).netloc,
    "url_path_tail": urllib.parse.urlparse((h.get("config") or {}).get("url","")).path.rsplit("/",1)[-1][:12],
    "last_code": (h.get("last_response") or {}).get("code")} for h in hooks] if isinstance(hooks, list) else hooks

for label, path in (("actions_secrets", f"/repos/{REPO}/actions/secrets"),
                    ("dependabot_secrets", f"/repos/{REPO}/dependabot/secrets"),
                    ("codespaces_secrets", f"/repos/{REPO}/codespaces/secrets")):
    s = get(path + "?per_page=100")
    if isinstance(s, dict) and "secrets" in s:
        OUT[label] = {"total": s.get("total_count"), "names": [x.get("name") for x in s["secrets"]]}
    else:
        OUT[label] = s
env_sec = get(f"/repos/{REPO}/environments")
OUT["environments"] = [e.get("name") for e in env_sec.get("environments", [])] if isinstance(env_sec, dict) else env_sec
vars_ = get(f"/repos/{REPO}/actions/variables?per_page=100")
OUT["variables"] = [v.get("name") for v in vars_.get("variables", [])] if isinstance(vars_, dict) else vars_

# deployments: distinct creators / environments / descriptions
deps = pages(f"/repos/{REPO}/deployments", max_pages=3)
if isinstance(deps, list):
    OUT["deployments_sample"] = {"count_sampled": len(deps),
        "creators": dict(collections.Counter((d.get("creator") or {}).get("login") for d in deps)),
        "environments": dict(collections.Counter(d.get("environment") for d in deps)),
        "descriptions": dict(collections.Counter(d.get("description") for d in deps))}

# check suites + combined status on HEAD and recent commits -> App census
apps = {}
for c in (commits if isinstance(commits, list) else [])[:5]:
    sha = c.get("sha")
    suites = get(f"/repos/{REPO}/commits/{sha}/check-suites?per_page=100")
    if isinstance(suites, dict):
        for s in suites.get("check_suites", []):
            app = s.get("app") or {}
            key = app.get("slug") or str(app.get("id"))
            if key and key != "None":
                e = apps.setdefault(key, {"app_id": app.get("id"), "slug": app.get("slug"),
                    "name": app.get("name"), "owner": (app.get("owner") or {}).get("login"), "suites": 0})
                e["suites"] += 1
    st = get(f"/repos/{REPO}/commits/{sha}/status?per_page=100")
    if isinstance(st, dict):
        for s in st.get("statuses", []):
            ctx = (s.get("context") or "").split("/")[0]
            e = apps.setdefault("status:"+ctx, {"context": s.get("context"), "suites": 0})
            e["suites"] += 1
OUT["check_apps_on_recent_heads"] = apps

# bot / actor census from issue comments + PR authors + reviewers
actors = collections.Counter(); actor_type = {}
ic = pages(f"/repos/{REPO}/issues/comments?sort=updated&direction=desc", max_pages=4)
if isinstance(ic, list):
    for cm in ic:
        a = cm.get("user") or {}
        if a.get("login"):
            actors[a["login"]] += 1; actor_type[a["login"]] = a.get("type")
    OUT["issue_comments_sampled"] = len(ic)
prs_open = pages(f"/repos/{REPO}/pulls?state=open", max_pages=3)
prs_closed = pages(f"/repos/{REPO}/pulls?state=closed&sort=updated&direction=desc", max_pages=2)
pr_authors = collections.Counter(); reviewers = collections.Counter()
for prs in (prs_open, prs_closed):
    if isinstance(prs, list):
        for p in prs:
            a = (p.get("user") or {}).get("login")
            if a: pr_authors[a] += 1; actor_type[a] = (p.get("user") or {}).get("type")
            for rv in p.get("requested_reviewers") or []:
                reviewers[rv.get("login")] += 1
OUT["pr_authors_sample"] = dict(pr_authors.most_common(30))
OUT["requested_reviewers_sample"] = dict(reviewers.most_common(30))
OUT["top_comment_actors"] = [{"login": l, "type": actor_type.get(l), "issue_comments_in_sample": n} for l, n in actors.most_common(40)]
OUT["open_prs_count_sampled"] = len(prs_open) if isinstance(prs_open, list) else prs_open

# workflows
wf = get(f"/repos/{REPO}/actions/workflows?per_page=100")
wf2 = get(f"/repos/{REPO}/actions/workflows?per_page=100&page=2")
wlist = []
if isinstance(wf, dict): wlist += wf.get("workflows", [])
if isinstance(wf2, dict): wlist += wf2.get("workflows", [])
OUT["workflows"] = {"total": (wf or {}).get("total_count"), "active": sum(1 for w in wlist if w.get("state")=="active"),
                    "names_sample": [w.get("name") for w in wlist[:40]]}
runs = get(f"/repos/{REPO}/actions/runs?per_page=100")
if isinstance(runs, dict):
    OUT["recent_run_actors"] = dict(collections.Counter(((x.get("actor") or {}).get("login")) for x in runs.get("workflow_runs", [])))
    OUT["recent_run_events"] = dict(collections.Counter(x.get("event") for x in runs.get("workflow_runs", [])))

# contributors + root tree config signals
contrib = get(f"/repos/{REPO}/contributors?per_page=100")
if isinstance(contrib, list):
    OUT["contributors"] = [{"login": c.get("login"), "type": c.get("type"), "contributions": c.get("contributions")} for c in contrib]
tree = get(f"/repos/{REPO}/git/trees/master")
if isinstance(tree, dict):
    OUT["root_entries"] = sorted(t.get("path") for t in tree.get("tree", []))
ghdir = get(f"/repos/{REPO}/contents/.github")
if isinstance(ghdir, list):
    OUT["dot_github_entries"] = sorted(x.get("name") for x in ghdir)
prot = get(f"/repos/{REPO}/branches/master/protection")
OUT["master_protection"] = prot if not isinstance(prot, dict) or "_error_status" in prot else {
    "required_status_checks": (prot.get("required_status_checks") or {}).get("contexts"),
    "required_reviews": (prot.get("required_pull_request_reviews") or {}).get("required_approving_review_count"),
    "enforce_admins": (prot.get("enforce_admins") or {}).get("enabled")}
rs = get(f"/repos/{REPO}/rulesets/24394235")
if isinstance(rs, dict) and "_error_status" not in rs:
    OUT["ruleset_master_no_rewind"] = {"name": rs.get("name"), "enforcement": rs.get("enforcement"),
        "rules": [x.get("type") for x in rs.get("rules", [])]}

# dependabot / code-scanning enablement probes (status only)
for label, path in (("vuln_alerts", f"/repos/{REPO}/vulnerability-alerts"),
                    ("automated_security_fixes", f"/repos/{REPO}/automated-security-fixes")):
    OUT[label] = get(path)

print(json.dumps({"ok": True, "keys": list(OUT.keys())}, indent=1))
with open("/home/hatch/workspace/github-integration-census/census.json", "w") as f:
    json.dump(OUT, f, indent=1)
