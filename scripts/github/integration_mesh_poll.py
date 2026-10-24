#!/usr/bin/env python3
"""Integration Mesh poll — runs INSIDE GitHub Actions (integration-mesh-poll.yml).

Ports the fleet census (census.py / census2.py / census3.py / secrets_plus.py /
reviews_updated.py, formerly run by a Muse cron against a local workspace) to
a repo-native workflow so the poll lives where its subject lives.

What it does each run:
  1. Live census of the integration mesh via the GitHub API (names/metadata
     only — secret VALUES are never fetched; list endpoints return names).
  2. Diff against the previous snapshot (restored from the Actions cache —
     poller output is NEVER committed, per matrix rule §9(4)).
  3. Material diffs land on GitHub: one [MUSEai] comment on the standing
     thread (Issue #1505). Structural changes (or 4 accumulated figure-only
     polls) additionally open/update a labeled `mesh-refresh` issue so a
     finding becomes tracked work instead of a diary entry.
  4. The new snapshot is saved back to the cache + uploaded as a run artifact.

Token: MESH_POLL_TOKEN (the provisioned OPERATOR_GITHUB_TOKEN secret) with
fallback to the workflow GITHUB_TOKEN. Surfaces the active token cannot read
are recorded as degraded and skipped by the diff — a missing section is never
reported as a removal.
"""
import argparse
import base64
import collections
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"
REPO = os.environ.get("MESH_REPO", "timerloggedout-spec/termux-monorepo")
ORGS = ("Research-Astute", "search-astute-ly")
STANDING_ISSUE = 1505
REFRESH_LABEL = "mesh-refresh"
LAST_OWNER_REFRESH = "2026-10-22"  # §3/§4 owner-firsthand (Installed list A-H)
FIGURE_ESCALATION = 4  # accumulated figure-only polls before a refresh issue


class Client:
    def __init__(self, token):
        self.token = token
        self.calls = 0

    def _req(self, method, path, body=None):
        self.calls += 1
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(API + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read().decode()).get("message", "")
            except Exception:
                msg = ""
            return {"_error_status": e.code, "_error": msg[:200]}
        except Exception as e:  # network etc.
            return {"_error": str(e)[:200]}

    def get(self, path):
        return self._req("GET", path)

    def post(self, path, body):
        return self._req("POST", path, body)

    def pages(self, path, max_pages=40):
        out, page = [], 1
        while page <= max_pages:
            sep = "&" if "?" in path else "?"
            batch = self.get(f"{path}{sep}per_page=100&page={page}")
            if not isinstance(batch, list):
                return batch if page == 1 else out
            out.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return out


def err(v):
    return isinstance(v, dict) and ("_error_status" in v or "_error" in v)


def name_set(section):
    """Normalize a secret-store section to a sorted list of names."""
    if isinstance(section, dict) and "names" in section:
        return sorted(x for x in section["names"] if x)
    return None  # unreadable / degraded


# ---------------------------------------------------------------- census ---

def census(c):
    s = {"schema": 1, "repo": REPO, "degraded": []}
    degraded = s["degraded"]

    u = c.get("/user")
    if err(u):
        degraded.append("user")
        s["user"] = None
    else:
        s["user"] = {k: u.get(k) for k in ("login", "public_repos", "total_private_repos",
                                            "two_factor_authentication")}

    installs = {}
    for org in ORGS:
        d = c.get(f"/orgs/{org}/installations?per_page=100")
        if err(d):
            degraded.append(f"org_installs:{org}")
            installs[org] = None
        else:
            installs[org] = sorted(i.get("app_slug") for i in d.get("installations", []))
    s["org_installations"] = installs

    r = c.get(f"/repos/{REPO}")
    s["repo_meta"] = ({k: r.get(k) for k in ("open_issues_count", "stargazers_count",
                                             "forks_count", "pushed_at")} if not err(r) else None)

    hooks = c.get(f"/repos/{REPO}/hooks?per_page=100")
    if err(hooks):
        degraded.append("hooks")
        s["hooks"] = None
    else:
        s["hooks"] = sorted(
            ({"host": urllib.parse.urlparse((h.get("config") or {}).get("url", "")).netloc,
              "active": h.get("active"), "events": len(h.get("events") or []),
              "last_code": (h.get("last_response") or {}).get("code")} for h in hooks),
            key=lambda x: (x["host"], x["events"]))

    def store(path):
        d = c.get(path + "?per_page=100")
        if isinstance(d, dict) and "secrets" in d:
            return {"total": d.get("total_count"), "names": [x.get("name") for x in d["secrets"]]}
        return d

    secrets = {
        "repo_actions": store(f"/repos/{REPO}/actions/secrets"),
        "repo_dependabot": store(f"/repos/{REPO}/dependabot/secrets"),
        "repo_codespaces": store(f"/repos/{REPO}/codespaces/secrets"),
        "user_codespaces": store("/user/codespaces/secrets"),
    }
    envs = c.get(f"/repos/{REPO}/environments")
    env_names = [e.get("name") for e in envs.get("environments", [])] if isinstance(envs, dict) else []
    s["environments"] = sorted(env_names)
    for name in env_names:
        q = urllib.parse.quote(name, safe="")
        secrets[f"env:{name}"] = store(f"/repos/{REPO}/environments/{q}/secrets")
    for org in ORGS:
        for kind in ("actions", "dependabot", "codespaces"):
            secrets[f"org:{org}:{kind}"] = store(f"/orgs/{org}/{kind}/secrets")
    for key, val in secrets.items():
        if name_set(val) is None:
            degraded.append(f"secrets:{key}")
    s["secrets"] = secrets

    vars_ = c.get(f"/repos/{REPO}/actions/variables?per_page=100")
    s["variables"] = (sorted(v.get("name") for v in vars_.get("variables", []))
                      if isinstance(vars_, dict) and "variables" in vars_ else None)
    if s["variables"] is None:
        degraded.append("variables")

    wf = c.pages(f"/repos/{REPO}/actions/workflows", max_pages=3)
    if isinstance(wf, list):
        s["workflows"] = {"total": len(wf),
                          "active": sum(1 for w in wf if w.get("state") == "active"),
                          "names": sorted(w.get("name") for w in wf)}
    else:
        degraded.append("workflows")
        s["workflows"] = None

    # check apps across the last 30 master heads
    commits = c.get(f"/repos/{REPO}/commits?sha=master&per_page=30")
    apps = {}
    if isinstance(commits, list):
        for cm in commits:
            sha, date = cm.get("sha"), ((cm.get("commit") or {}).get("committer") or {}).get("date")
            suites = c.get(f"/repos/{REPO}/commits/{sha}/check-suites?per_page=100")
            if isinstance(suites, dict):
                for su in suites.get("check_suites", []):
                    app = su.get("app") or {}
                    slug = app.get("slug")
                    if not slug:
                        continue
                    e = apps.setdefault(slug, {"name": app.get("name"), "app_id": app.get("id"),
                                               "suites": 0, "conclusions": collections.Counter(),
                                               "last_seen": date})
                    e["suites"] += 1
                    e["conclusions"][su.get("conclusion") or "pending"] += 1
                    e["last_seen"] = max(e["last_seen"], date)
        for e in apps.values():
            e["conclusions"] = dict(e["conclusions"])
    else:
        degraded.append("check_apps")
    s["check_apps_30"] = apps

    # cross-repo reach: head suites on the 60 most recently pushed owned repos
    repos = c.get("/user/repos?affiliation=owner&sort=pushed&direction=desc&per_page=100")
    cross = {}
    if isinstance(repos, list):
        for rp in repos[:60]:
            full = rp.get("full_name")
            heads = c.get(f"/repos/{full}/commits?per_page=1")
            if not isinstance(heads, list) or not heads:
                continue
            suites = c.get(f"/repos/{full}/commits/{heads[0].get('sha')}/check-suites?per_page=100")
            if isinstance(suites, dict):
                for su in suites.get("check_suites", []):
                    app = su.get("app") or {}
                    if app.get("slug"):
                        e = cross.setdefault(app["slug"], {"name": app.get("name"), "repos": set()})
                        e["repos"].add(full)
        s["cross_repo_apps"] = {k: {"name": v["name"], "repo_count": len(v["repos"]),
                                    "repos": sorted(v["repos"])} for k, v in cross.items()}
    else:
        degraded.append("cross_repo")
        s["cross_repo_apps"] = None

    # totals, fully paginated (with verify pass handled by caller re-run)
    s["prs_total"], s["pr_authors"] = count_prs(c)
    s["issues_total_true"], s["issue_authors"] = count_issues(c)

    ic = c.pages(f"/repos/{REPO}/issues/comments?sort=updated&direction=desc", max_pages=20)
    if isinstance(ic, list):
        actors = collections.Counter()
        types = {}
        for cm in ic:
            a = cm.get("user") or {}
            if a.get("login"):
                actors[a["login"]] += 1
                types[a["login"]] = a.get("type")
        s["comment_actors"] = [{"login": l, "type": types.get(l), "comments": n}
                                for l, n in actors.most_common(15)]
    else:
        degraded.append("comment_actors")
        s["comment_actors"] = None

    s["reviews_updated"] = review_census(c)

    cs = c.get("/user/codespaces?per_page=100")
    s["codespaces_total"] = cs.get("total_count") if isinstance(cs, dict) else None
    if s["codespaces_total"] is None:
        degraded.append("codespaces")

    deps = c.pages(f"/repos/{REPO}/deployments", max_pages=3)
    s["deployment_creators"] = (dict(collections.Counter((d.get("creator") or {}).get("login")
                                                         for d in deps)) if isinstance(deps, list) else None)

    s["plan_state"], s["stale_rows"] = plan_state(c)
    return s


def count_prs(c):
    prs = c.pages(f"/repos/{REPO}/pulls?state=all&sort=created&direction=desc")
    if not isinstance(prs, list):
        return None, None
    authors = collections.Counter((p.get("user") or {}).get("login") for p in prs)
    authors.pop(None, None)
    return len(prs), dict(authors.most_common(10))


def count_issues(c):
    issues = c.pages(f"/repos/{REPO}/issues?state=all&sort=created&direction=desc")
    if not isinstance(issues, list):
        return None, None
    authors = collections.Counter()
    for i in issues:
        if "pull_request" in i:
            continue
        login = (i.get("user") or {}).get("login")
        if login:
            authors[login] += 1
    return sum(authors.values()), dict(authors.most_common(10))


def review_census(c):
    prs = c.pages(f"/repos/{REPO}/pulls?state=all&sort=updated&direction=desc", max_pages=2)
    if not isinstance(prs, list):
        return None
    rev, states, with_rev = collections.Counter(), collections.Counter(), 0
    for p in prs[:150]:
        rs = c.get(f"/repos/{REPO}/pulls/{p['number']}/reviews?per_page=100")
        if isinstance(rs, list) and rs:
            with_rev += 1
            for x in rs:
                u = (x.get("user") or {}).get("login")
                if u:
                    rev[u] += 1
                    states[f"{u}|{x.get('state')}"] += 1
    return {"prs_scanned": min(150, len(prs)), "prs_with_reviews": with_rev,
            "actors": dict(rev.most_common(15)), "states": dict(states.most_common(30))}


OPEN_WORDS = re.compile(r"\b(open|pending|not yet|awaiting|still open)\b", re.I)


def plan_state(c):
    """§9 rows of the committed matrix reference PRs/issues by number; read each
    live and flag rows whose text claims open/pending for a closed/merged item
    (the I1 failure mode). Returns ({ref: state}, [stale row summaries])."""
    doc = c.get(f"/repos/{REPO}/contents/docs/ops/INTEGRATION-MESH-MATRIX.md?ref=master")
    if err(doc) or "content" not in doc:
        return None, []
    text = base64.b64decode(doc["content"]).decode(errors="replace")
    m = re.search(r"^## 9\..*?(?=^## )", text, re.S | re.M)
    if not m:
        return None, []
    states, stale = {}, []
    for line in m.group(0).splitlines():
        refs = re.findall(r"#(\d{3,5})\b", line)
        if not refs:
            continue
        for ref in refs:
            num = int(ref)
            if num in (184, 1505) or num in states:
                continue
            pr = c.get(f"/repos/{REPO}/pulls/{num}")
            if not err(pr) and pr.get("number") == num:
                states[num] = "merged" if pr.get("merged_at") else pr.get("state")
            else:
                iss = c.get(f"/repos/{REPO}/issues/{num}")
                states[num] = iss.get("state") if not err(iss) else "unknown"
            if states[num] in ("closed", "merged") and OPEN_WORDS.search(line):
                stale.append(f"§9 row references #{num} as open/pending but it is {states[num]}")
    return states, stale


# ------------------------------------------------------------------ diff ---

def set_delta(label, prev, cur, out):
    if prev is None or cur is None:
        return
    added, removed = sorted(set(cur) - set(prev)), sorted(set(prev) - set(cur))
    if added:
        out.append(f"{label} added: {', '.join(added)}")
    if removed:
        out.append(f"{label} removed: {', '.join(removed)}")


def diff_snapshots(prev, cur):
    """Pure diff. Returns (structural_lines, figure_lines). Degraded sections
    (None on either side) never produce removal lines."""
    structural, figure = [], []
    if prev is None:
        return structural, figure

    set_delta("check apps (30-head)", (prev.get("check_apps_30") or {}).keys() if prev.get("check_apps_30") is not None else None,
              (cur.get("check_apps_30") or {}).keys() if cur.get("check_apps_30") is not None else None, structural)
    pc = prev.get("cross_repo_apps")
    cc = cur.get("cross_repo_apps")
    set_delta("cross-repo check apps", pc.keys() if pc else None, cc.keys() if cc else None, structural)
    if pc and cc:
        for slug in sorted(set(pc) & set(cc)):
            if pc[slug]["repo_count"] != cc[slug]["repo_count"]:
                structural.append(f"cross-repo reach {slug}: {pc[slug]['repo_count']} -> {cc[slug]['repo_count']} repos")

    for org in ORGS:
        set_delta(f"org installations {org}", (prev.get("org_installations") or {}).get(org),
                  (cur.get("org_installations") or {}).get(org), structural)

    ph = {(h["host"], h["last_code"]) for h in prev["hooks"]} if prev.get("hooks") is not None else None
    ch = {(h["host"], h["last_code"]) for h in cur["hooks"]} if cur.get("hooks") is not None else None
    set_delta("webhooks (host,last_code)", [f"{a}:{b}" for a, b in ph] if ph is not None else None,
              [f"{a}:{b}" for a, b in ch] if ch is not None else None, structural)

    for key in sorted(set((prev.get("secrets") or {})) | set((cur.get("secrets") or {}))):
        set_delta(f"secret names [{key}]", name_set((prev.get("secrets") or {}).get(key, {})),
                  name_set((cur.get("secrets") or {}).get(key, {})), structural)

    set_delta("environments", prev.get("environments"), cur.get("environments"), structural)
    set_delta("repo variables", prev.get("variables"), cur.get("variables"), structural)

    pw, cw = prev.get("workflows"), cur.get("workflows")
    if pw and cw:
        set_delta("workflows", pw["names"], cw["names"], structural)
        if pw["total"] != cw["total"]:
            figure.append(f"workflows total {pw['total']} -> {cw['total']} (active {cw['active']})")

    for row in cur.get("stale_rows") or []:
        if row not in (prev.get("stale_rows") or []):
            structural.append(f"stale plan row: {row}")

    for key, label in (("prs_total", "PRs total"), ("issues_total_true", "true issues"),
                       ("codespaces_total", "codespaces")):
        if prev.get(key) is not None and cur.get(key) is not None and prev[key] != cur[key]:
            figure.append(f"{label} {prev[key]} -> {cur[key]}")

    pa = {a["login"]: a["comments"] for a in prev.get("comment_actors") or []}
    ca = {a["login"]: a["comments"] for a in cur.get("comment_actors") or []}
    if pa and ca and set(pa) != set(ca):
        figure.append(f"top comment actors changed: {', '.join(sorted(set(pa) ^ set(ca)))}")

    pd_, cd_ = prev.get("deployment_creators"), cur.get("deployment_creators")
    if pd_ and cd_ and set(pd_) != set(cd_):
        figure.append(f"deployment creators changed: {', '.join(sorted(set(pd_) ^ set(cd_)))}")

    return structural, figure


def render_comment(cur, structural, figure, counter, run_url, baseline=False):
    now = datetime.datetime.now(datetime.timezone.utc)
    try:
        days = (now.date() - datetime.date.fromisoformat(LAST_OWNER_REFRESH)).days
    except ValueError:
        days = "?"
    lines = ["[MUSEai]@{role:{`Muse`}}", "",
             f"## Integration mesh poll — {now:%Y-%m-%d %H:%M} UTC (Actions workflow)", ""]
    if baseline:
        lines.append("Baseline snapshot captured by the new repo-native workflow "
                     "(`integration-mesh-poll.yml`). The Muse cron poll is retired; "
                     "state now persists in the Actions cache + run artifacts — never committed.")
    else:
        if structural:
            lines.append("**Structural changes:**")
            lines += [f"- {x}" for x in structural]
            lines.append("")
        if figure:
            lines.append("**Figure movement:**")
            lines += [f"- {x}" for x in figure]
            lines.append("")
        lines.append(f"Figure-only polls accumulated toward refresh: {counter}/{FIGURE_ESCALATION}")
    if cur.get("degraded"):
        lines.append(f"Degraded sections this run (skipped by diff): {', '.join(cur['degraded'])}")
    lines.append(f"§3/§4 owner-firsthand refresh: {LAST_OWNER_REFRESH} ({days} days ago)")
    if run_url:
        lines.append(f"Run: {run_url}")
    return "\n".join(lines)


# ------------------------------------------------------------------ main ---

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-in", default="mesh-state-prev.json")
    ap.add_argument("--state-out", default="mesh-state.json")
    ap.add_argument("--dry-run", action="store_true", help="census + diff only; post nothing")
    ap.add_argument("--force-comment", action="store_true", help="comment even when nothing changed")
    args = ap.parse_args()

    token = os.environ.get("MESH_POLL_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("::error::no token (MESH_POLL_TOKEN / GITHUB_TOKEN)")
        return 1
    c = Client(token)

    cur = census(c)
    # verify pass: implausible headline totals (drop or zero) get one re-run
    prev = None
    if os.path.exists(args.state_in):
        try:
            prev = json.load(open(args.state_in))
        except Exception:
            prev = None
    if prev:
        for key, fn in (("prs_total", count_prs), ("issues_total_true", count_issues)):
            old, new = prev.get(key), cur.get(key)
            if new is not None and old is not None and (new == 0 or new < old):
                print(f"verify pass: {key} {old} -> {new} looks implausible; re-running once")
                again = fn(c)
                if again[0] is not None:
                    cur[key] = again[0]
                    if key == "prs_total":
                        cur["pr_authors"] = again[1]
                    else:
                        cur["issue_authors"] = again[1]

    cur["observed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    structural, figure = diff_snapshots(prev, cur)
    counter = (prev.get("figure_counter", 0) if prev else 0)
    if structural:
        counter = 0
    elif figure:
        counter += 1
    cur["figure_counter"] = counter

    json.dump(cur, open(args.state_out, "w"), indent=1, sort_keys=True, default=str)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    run_url = None
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_RUN_ID"):
        run_url = (f"{os.environ['GITHUB_SERVER_URL']}/{REPO}/actions/runs/"
                   f"{os.environ['GITHUB_RUN_ID']}")

    print(f"api calls: {c.calls}; degraded: {cur['degraded']}")
    print(f"structural: {len(structural)}; figure: {len(figure)}; counter: {counter}")
    for x in structural + figure:
        print(" -", x)
    if summary:
        with open(summary, "a") as f:
            f.write(render_comment(cur, structural, figure, counter, run_url,
                                   baseline=prev is None) + "\n")

    if args.dry_run:
        print("dry run — nothing posted")
        return 0
    if prev is None:
        body = render_comment(cur, structural, figure, counter, run_url, baseline=True)
        c.post(f"/repos/{REPO}/issues/{STANDING_ISSUE}/comments", {"body": body})
        return 0
    if not structural and not figure and not args.force_comment:
        print("no material change — no comment (standing rule)")
        return 0

    body = render_comment(cur, structural, figure, counter, run_url)
    c.post(f"/repos/{REPO}/issues/{STANDING_ISSUE}/comments", {"body": body})

    if structural or counter >= FIGURE_ESCALATION:
        cur["figure_counter"] = 0
        json.dump(cur, open(args.state_out, "w"), indent=1, sort_keys=True, default=str)
        ensure_refresh_issue(c, structural, figure, body)
    return 0


def ensure_refresh_issue(c, structural, figure, diff_body):
    """A structural finding becomes tracked work: one open `mesh-refresh`
    issue, updated in place — never a duplicate per poll."""
    c.post(f"/repos/{REPO}/labels", {"name": REFRESH_LABEL, "color": "5319e7",
                                     "description": "Integration mesh matrix needs a doc refresh"})
    open_issues = c.get(f"/repos/{REPO}/issues?labels={REFRESH_LABEL}&state=open&per_page=10")
    if isinstance(open_issues, list) and open_issues:
        num = open_issues[0]["number"]
        c.post(f"/repos/{REPO}/issues/{num}/comments",
               {"body": f"[MUSEai]@{{role:{{`Muse`}}}}\n\nNew poll diff while this refresh is open:\n\n{diff_body}"})
        print(f"refresh issue #{num} updated")
        return
    title_hint = (structural[0] if structural else "figure accumulation reached threshold")[:80]
    body = ("[MUSEai]@{role:{`Muse`}}\n\n"
            "The Actions integration-mesh poll found the committed matrix "
            "(`docs/ops/INTEGRATION-MESH-MATRIX.md`) stale:\n\n"
            f"{diff_body}\n\n"
            "Refresh checklist:\n"
            "- [ ] Update the matrix figures/rows named above from this diff\n"
            "- [ ] Re-verify landed content on master after the refresh PR merges\n"
            "- [ ] Close this issue with the refresh PR number + merge SHA\n")
    res = c.post(f"/repos/{REPO}/issues", {"title": f"[mesh] Matrix refresh needed — {title_hint}",
                                           "body": body, "labels": [REFRESH_LABEL]})
    print("refresh issue:", res.get("number") if isinstance(res, dict) else res)


if __name__ == "__main__":
    sys.exit(main())
