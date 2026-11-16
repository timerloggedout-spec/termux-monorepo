#!/usr/bin/env python3
"""Census v2 — FULL programmatic enumeration via the PAT helper. No copied stats.
Every count below is produced by paginating the live API in this run.
Output: census2.json"""
import json, subprocess, collections

HELPER = "/home/hatch/workspace/custom-connectors/custom.github-pat/bin/github_pat.py"
REPO = "timerloggedout-spec/termux-monorepo"
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

def pages(path, max_pages=40):
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
    OUT.setdefault("_pages", {})[path.split("?")[0]] = page
    return out

# 1) Untried repo surfaces
OUT["deploy_keys"] = [{"id": k.get("id"), "title": k.get("title"), "read_only": k.get("read_only"),
                        "created_at": k.get("created_at")} for k in get(f"/repos/{REPO}/keys?per_page=100")] \
    if isinstance(get(f"/repos/{REPO}/keys?per_page=100"), list) else "error"
collab = pages(f"/repos/{REPO}/collaborators?affiliation=all")
OUT["collaborators"] = [{"login": c.get("login"), "type": c.get("type"),
                         "role": (c.get("permissions") or {})} for c in collab] if isinstance(collab, list) else collab
al = get(f"/repos/{REPO}/autolinks?per_page=100")
OUT["autolinks"] = [{"id": a.get("id"), "key_prefix": a.get("key_prefix"), "url_template": a.get("url_template")} for a in al] if isinstance(al, list) else al
OUT["actions_permissions"] = get(f"/repos/{REPO}/actions/permissions")
OUT["actions_workflow_permissions"] = get(f"/repos/{REPO}/actions/permissions/workflow")
OUT["pages"] = get(f"/repos/{REPO}/pages")

# 2) Check suites across the last 30 master commits -> per-app activity window
commits = get(f"/repos/{REPO}/commits?sha=master&per_page=30")
apps = {}
if isinstance(commits, list):
    OUT["commits_scanned"] = len(commits)
    for c in commits:
        sha, date = c.get("sha"), ((c.get("commit") or {}).get("committer") or {}).get("date")
        suites = get(f"/repos/{REPO}/commits/{sha}/check-suites?per_page=100")
        if isinstance(suites, dict):
            for s in suites.get("check_suites", []):
                app = s.get("app") or {}
                slug = app.get("slug")
                if not slug:
                    continue
                e = apps.setdefault(slug, {"name": app.get("name"), "app_id": app.get("id"),
                    "owner": (app.get("owner") or {}).get("login"), "suites": 0,
                    "conclusions": collections.Counter(), "first_seen": date, "last_seen": date})
                e["suites"] += 1
                e["conclusions"][s.get("conclusion") or "pending"] += 1
                e["last_seen"] = date  # commits are newest-first: first assignment is newest
                e["first_seen"] = date
    for e in apps.values():
        e["conclusions"] = dict(e["conclusions"])
OUT["check_apps_30_heads"] = apps

# 3) ALL PRs (state=all, full pagination): authors, requested reviewers, assignees
prs = pages(f"/repos/{REPO}/pulls?state=all&sort=created&direction=desc", max_pages=40)
if isinstance(prs, list):
    authors = collections.Counter(); reviewers = collections.Counter(); assignees = collections.Counter()
    for p in prs:
        a = (p.get("user") or {}).get("login")
        if a: authors[a] += 1
        for rv in p.get("requested_reviewers") or []:
            reviewers[rv.get("login")] += 1
        for asg in p.get("assignees") or []:
            assignees[asg.get("login")] += 1
    OUT["prs_total"] = len(prs)
    OUT["pr_authors_all"] = dict(authors.most_common(40))
    OUT["pr_requested_reviewers_all"] = dict(reviewers.most_common(40))
    OUT["pr_assignees_all"] = dict(assignees.most_common(40))
    pr_nums_recent = [p["number"] for p in prs[:150]]

# 4) Submitted reviews across the 150 most recent PRs
rev = collections.Counter(); rev_states = collections.Counter(); reviewed_prs = 0
for n in pr_nums_recent:
    rs = get(f"/repos/{REPO}/pulls/{n}/reviews?per_page=100")
    if isinstance(rs, list) and rs:
        reviewed_prs += 1
        for x in rs:
            u = (x.get("user") or {}).get("login")
            if u:
                rev[u] += 1; rev_states[f"{u}|{x.get('state')}"] += 1
OUT["reviews_150pr"] = {"prs_with_reviews": reviewed_prs, "prs_scanned": len(pr_nums_recent),
                        "actors": dict(rev.most_common(40)), "states": dict(rev_states.most_common(60))}

# 5) Issue comments: 20 pages = up to 2000 newest, actor census
ic = pages(f"/repos/{REPO}/issues/comments?sort=updated&direction=desc", max_pages=20)
if isinstance(ic, list):
    actors = collections.Counter(); types = {}
    for cm in ic:
        a = cm.get("user") or {}
        if a.get("login"):
            actors[a["login"]] += 1; types[a["login"]] = a.get("type")
    OUT["issue_comments_2000"] = {"count": len(ic),
        "actors": [{"login": l, "type": types.get(l), "comments": n} for l, n in actors.most_common(50)]}

# 6) All issues (state=all) authors — catches bot-filed issues (dependabot etc.)
issues = pages(f"/repos/{REPO}/issues?state=all&sort=created&direction=desc", max_pages=40)
if isinstance(issues, list):
    ia = collections.Counter()
    for i in issues:
        if "pull_request" in i:  # issues endpoint mixes PRs; count only true issues
            continue
        u = (i.get("user") or {}).get("login")
        if u: ia[u] += 1
    OUT["issues_total_true"] = sum(ia.values())
    OUT["issue_authors_all"] = dict(ia.most_common(40))

# 7) /apps detail for any slug not already detailed
known = set(json.load(open("/home/hatch/workspace/github-integration-census/apps_detail.json")).keys())
new_slugs = [s for s in apps if s not in known and s not in ("github-actions", "github-pages")]
extra = {}
for s in sorted(new_slugs):
    a = get(f"/apps/{s}")
    if isinstance(a, dict) and a.get("slug"):
        extra[s] = {"name": a.get("name"), "owner": (a.get("owner") or {}).get("login"),
                    "description": (a.get("description") or "")[:160]}
OUT["new_app_details"] = extra

json.dump(OUT, open("/home/hatch/workspace/github-integration-census/census2.json", "w"), indent=1, default=str)
print(json.dumps({k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in OUT.items() if not k.startswith("_")}, indent=1))
print("pages:", OUT.get("_pages"))
