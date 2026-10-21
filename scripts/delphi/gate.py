"""Delphi Oracle RFP gate (docs/ops/DELPHI-ORACLE-RFP-GATE.md).

Stdlib only. Never prints secrets. Never picks a model for live routing: the
panel uses transparent rubric scoring only. Model voting requires a separately
validated no-cost and quota admission implementation; key presence is not enough.

Subcommands
  score   --surface ID [--surface ID ...]   offline: oracle + blind panel + rounds, JSON to stdout
  run     [--reason R] [--depth N]          Actions: process every open delphi:rfp issue idempotently
  feedback --rfp N --outcome confirmed|miss  flywheel: re-weight roles from a real outcome
"""
from __future__ import annotations

import argparse, datetime as dt, hashlib, json, os, re, statistics, sys, urllib.request, urllib.error

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SURFACES = os.path.join(ROOT, "ops", "delphi", "surfaces.json")
PANEL = os.path.join(ROOT, "ops", "delphi", "panel.json")
REGISTRY = os.path.join(ROOT, "ops", "quota", "registry.json")
LEDGER_MARK = "<!-- delphi-ledger v1 -->"
WEIGHTS_MARK = "<!-- delphi-weights v1 -->"
WEIGHTS_TITLE = "Delphi panel weights ledger"
ROLES = ["OPERATOR", "builder", "reviewer", "Scout", "cost_auditor"]
LABELS = {
    "delphi:rfp": ("1d76db", "Delphi Oracle RFP (docs/ops/DELPHI-ORACLE-RFP-GATE.md)"),
    "delphi:converged": ("5319e7", "Delphi panel converged"),
    "delphi:shadow": ("0e8a16", "Awarded a shadow lane (small traffic share)"),
    "delphi:parked": ("fbca04", "Parked in ForeSight with a recheck date"),
    "delphi:promoted": ("006b75", "Shadow lane confirmed by real runs"),
    "delphi:needs-access": ("d93f0b", "Award blocked on an Actions credential (Access lane)"),
}


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def clamp(v: float, lo: int = 1, hi: int = 5) -> int:
    return int(max(lo, min(hi, round(v))))


# ---------------------------------------------------------------- oracle
def oracle(surface: dict, registry: dict | None = None, readings: dict | None = None) -> dict:
    """Attach documented limits (with source URLs), live readings and evidence."""
    reg = {s["id"]: s for s in (registry or {}).get("services", [])}
    r = reg.get(surface.get("registry_id") or "")
    q = surface.get("quota", {})
    mult = (readings or {}).get((r or {}).get("provider", ""), None)
    return {
        "surface_id": surface["id"],
        "documented": {k: q.get(k) for k in ("metric", "limit", "unit", "window", "reset", "zone", "source")},
        "sourced": bool(surface.get("sourced")),
        "registry_entry": (r or {}).get("id"),
        "registry_source": (r or {}).get("source"),
        "live_multiplier": mult,  # 3l0.quota-weights.v1; None = no live reading (neutral)
        "auth": {k: v for k, v in surface.get("auth", {}).items() if k != "value"},
        "evidence": {"foresight_horizon": surface.get("horizon"), "failure_modes": surface.get("failure_modes", [])},
    }


# ---------------------------------------------------------------- blind panel (rubric)
def _auth_ready(s: dict) -> int:
    p = s.get("auth", {}).get("present")
    return 5 if p is True else (3 if p is None else 1)


def _reset_clarity(s: dict) -> int:
    q = s.get("quota", {})
    known = q.get("reset") not in (None, "unknown", "n/a") and q.get("zone")
    if s.get("sourced") and known and q.get("limit") is not None:
        return 5
    if known or q.get("limit") is not None:
        return 3
    return 1


def rubric_vote(role: str, s: dict) -> dict:
    fit, head, lock = s.get("fit", 3), s.get("headroom", 3), s.get("lock_in", 3)
    fm, sourced = len(s.get("failure_modes", [])), bool(s.get("sourced"))
    veto = False
    if role == "OPERATOR":
        imp, impt = fit, (_auth_ready(s) + (5 if sourced else 2) + (6 - lock)) / 3
        why = "policy fit: sourced limits, Actions auth, low lock-in"
    elif role == "builder":
        imp, impt = (fit + head) / 2, _auth_ready(s)
        why = "integration: credential reachable from Actions, room to build"
    elif role == "reviewer":
        imp, impt = fit, 5 - fm + (0 if sourced else -1)
        why = f"{fm} failure modes; {'sourced' if sourced else 'unsourced'} limits"
    elif role == "Scout":
        imp, impt = {"H0": 3, "H1": 4, "H2": 5, "H3": 4}.get(s.get("horizon"), 3), fit
        why = f"horizon {s.get('horizon')}: novelty vs fit"
    elif role == "cost_auditor":
        imp, impt = head, _reset_clarity(s)
        veto = bool(s.get("card_required") or s.get("overage_autobill"))
        why = "free headroom and a documented reset" + ("; VETO: needs money/card" if veto else "")
    else:
        raise ValueError(role)
    imp, impt = clamp(imp), clamp(impt)
    score = imp * impt
    if veto:
        score = min(score, 4)
    return {"role": role, "impact": imp, "importance": impt, "score": score, "veto": veto, "reason": why, "via": "rubric"}


def llm_vote(role: str, s: dict, feedback: str, budget: dict) -> dict | None:
    """Model ballots are disabled pending separate no-cost and quota admission.

    A key, :free suffix, role label or neutral multiplier is not admission.
    Keep the callable for compatibility; callers use the transparent rubric.
    """
    return None


def sign(vote: dict, rfp: str, rnd: int, session: str) -> dict:
    canon = json.dumps({k: vote[k] for k in ("role", "impact", "importance", "score", "veto")}, sort_keys=True)
    vote = dict(vote)
    vote["sha256"] = hashlib.sha256(f"{rfp}|{rnd}|{canon}".encode()).hexdigest()[:16]
    vote["signed"] = f"Signed-off-by: Delphi-{vote['role']} (OPERATOR) {session} / {rfp}#r{rnd}"
    return vote


# ---------------------------------------------------------------- weights + rounds
def role_weight(r: dict) -> float:
    return float(r.get("base", 1.0)) * (0.5 + float(r.get("gate_pass_rate", 0.5))) * (float(r.get("elo", 1500)) / 1500.0)


def effective(votes: list[dict], roles: dict) -> float:
    ws = [(role_weight(roles[v["role"]]), v["score"]) for v in votes]
    return round(sum(w * s for w, s in ws) / sum(w for w, _ in ws), 2)


def spread(scores: list[float]) -> tuple[float, float, float]:
    med = statistics.median(scores)
    q = statistics.quantiles(scores, n=4, method="inclusive") if len(scores) > 1 else [scores[0]] * 3
    return med, q[0], q[2]


def delphi(surface: dict, panel: dict, rfp: str = "local", session: str = "local", budget: dict | None = None) -> dict:
    budget = budget if budget is not None else {"llm": int(os.environ.get("DELPHI_LLM_MAX", "30"))}
    cfg, roles = panel["rounds"], panel["roles"]
    votes = [sign(llm_vote(r, surface, "", budget) or rubric_vote(r, surface), rfp, 1, session) for r in ROLES]
    history = []
    for rnd in range(1, cfg["max"] + 1):
        scores = [v["score"] for v in votes]
        med, q1, q3 = spread(scores)
        iqr = q3 - q1
        outliers = [v["reason"] for v in votes if v["score"] < q1 or v["score"] > q3]
        history.append({"round": rnd, "median": med, "iqr": round(iqr, 2), "range": max(scores) - min(scores),
                        "effective": effective(votes, roles), "outlier_reasons": outliers, "votes": votes})
        if iqr <= cfg["converge_iqr"] or (max(scores) - min(scores)) <= cfg["converge_range"] or rnd == cfg["max"]:
            break
        # next round: each role sees ONLY median, IQR and anonymous outlier reasons
        fb = f"Round {rnd} panel median {med}, IQR {q1}-{q3}. Anonymous outlier reasons: {outliers}. Revise if persuaded.\n"
        nxt = []
        for v in votes:
            alt = llm_vote(v["role"], surface, fb, budget)
            if alt is None:
                alt = dict(v)
                if not v["veto"] and (v["score"] < q1 or v["score"] > q3):
                    alt["score"] = round(v["score"] + cfg["pull_to_median"] * (med - v["score"]), 1)
                    alt["reason"] = v["reason"] + " (moved toward median)"
            nxt.append(sign(alt, rfp, rnd + 1, session))
        votes = nxt
    last = history[-1]
    converged = last["iqr"] <= cfg["converge_iqr"] or last["range"] <= cfg["converge_range"]
    return {"surface_id": surface["id"], "rounds": history, "converged": converged,
            "effective_score": last["effective"], "veto": any(v["veto"] for v in last["votes"])}


def award(result: dict, surface: dict, panel: dict, at: dt.datetime | None = None) -> dict:
    at = at or now()
    a, e = panel["award"], result["effective_score"]
    band = "P0" if e >= 20 else "High" if e >= 15 else "Medium" if e >= 9 else "Backlog"
    if result["veto"]:
        days = a["park_recheck_days"]["backlog"]
        out = {"decision": "parked", "why": "cost auditor veto: needs money or a card"}
    elif e >= a["shadow_min"]:
        out = {"decision": "shadow", "traffic_share": a["shadow_traffic_share"],
               "promote_after_confirmed_runs": a["promote_after_confirmed_runs"], "why": f"effective {e} >= {a['shadow_min']}"}
        if surface.get("auth", {}).get("present") is False:
            out["blocked_on"] = f"Actions credential {surface['auth'].get('actions_secret') or '(none)'} (Access lane)"
        days = None
    else:
        days = a["park_recheck_days"]["medium" if e >= 9 else "backlog"]
        out = {"decision": "parked", "why": f"effective {e} below shadow bar {a['shadow_min']}"}
    out["band"] = band
    if days:
        out["recheck_after"] = (at + dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%MZ")
    return out


def records(result: dict, aw: dict, surface: dict, oracle_facts: dict, rfp: str) -> dict:
    """HindSight retain + ForeSight evidence (foresight/schema.json) + 3l0.moneyball.v1-shaped row."""
    ts = now().strftime("%Y-%m-%dT%H:%M:%SZ")
    src = surface["quota"]["source"]
    fs = {"resource_id": surface["id"], "item_id": f"delphi:{rfp}", "lane_id": "delphi-oracle",
          "title": surface["title"], "category": surface["lane"], "horizon": surface.get("horizon", "H1"),
          "evidence_status": "confirmed" if surface.get("sourced") else "attributed_claim",
          "summary": f"Delphi {aw['decision']} at effective {result['effective_score']} ({aw['band']})",
          "source": {"url": src}, "canonical_source": src, "observed_at": ts,
          "confidence": round(min(1.0, result["effective_score"] / 25.0), 2),
          "procurement": {"decision": aw["decision"], "recheck_after": aw.get("recheck_after")}}
    hs = {"bank_id": "deepagent::termux-monorepo",
          "content": f"[delphi] {surface['id']} -> {aw['decision']} eff={result['effective_score']} band={aw['band']} rfp={rfp} "
                     f"forecast={'pass' if aw['decision'] == 'shadow' else 'fail'} ts={ts}"}
    mb = {"contract_version": "3l0.moneyball.v1", "task_id": f"delphi:{rfp}", "agent_id": "delphi-panel",
          "terminal_state": aw["decision"], "status": "converged" if result["converged"] else "max_rounds",
          "started_at": ts, "ended_at": ts, "trigger": os.environ.get("DELPHI_REASON", "manual")}
    return {"foresight": fs, "hindsight": hs, "moneyball": mb, "oracle": oracle_facts}


def score_surface(s: dict, panel: dict, registry: dict | None, readings: dict | None, rfp: str, session: str, budget=None) -> dict:
    facts = oracle(s, registry, readings)
    res = delphi(s, panel, rfp, session, budget)
    aw = award(res, s, panel)
    return {"rfp": rfp, "surface": s["id"], "title": s["title"], "result": res, "award": aw,
            "records": records(res, aw, s, facts, rfp)}


# ---------------------------------------------------------------- flywheel
def feedback(roles: dict, final_votes: list[dict], outcome: str, panel: dict) -> dict:
    """outcome 'confirmed' = shadow lane held up in real runs; 'miss' = forecast was wrong."""
    a, k = panel["flywheel"]["ewma_alpha"], panel["flywheel"]["elo_k"]
    bar = panel["award"]["shadow_min"]
    truth = outcome == "confirmed"
    roles = json.loads(json.dumps(roles))
    for v in final_votes:
        r = roles[v["role"]]
        hit = (v["score"] >= bar) == truth
        r["gate_pass_rate"] = round((1 - a) * r["gate_pass_rate"] + a * (1.0 if hit else 0.0), 4)
        r["elo"] = round(r["elo"] + (k if hit else -k), 1)
        r["hits" if hit else "misses"] += 1
    return roles


# ---------------------------------------------------------------- adaptive cadence
def cadence(registry: dict, readings: dict, pending: int, depth: int, max_depth: int = 3) -> dict:
    """Quota-aware: accelerate when free quota sits unused before its reset, defer near caps.
    Bounded by the GitHub API budget in the registry and a chain-depth cap."""
    reg = {s["id"]: s for s in registry.get("services", [])}
    api = reg.get("github.api.github_token", {})
    cap = int((api.get("limit") or 1000) * (api.get("planned_use", {}).get("safety", 0.8)))
    per_rfp_calls = 6
    max_rfps = max(1, cap // per_rfp_calls // 4)  # never spend more than a quarter of the hourly budget per run
    mults = [float(v) for v in (readings or {}).values()]
    pace = round(sum(mults) / len(mults), 2) if mults else 1.0
    if pending and pace >= 1.2 and depth < max_depth:
        mode = "accelerate"
    elif pace < 0.5:
        mode = "defer"
    else:
        mode = "steady"
    return {"mode": mode, "pace": pace, "max_rfps_per_run": max_rfps, "api_cap_per_hour": cap, "depth": depth}


# ---------------------------------------------------------------- GitHub (Actions mode)
class RateLimited(Exception):
    """GitHub 403/429 rate-limit wall: defer, never fail the gate (access-resilience: rate_limit)."""


class GH:
    def __init__(self, repo: str, token: str):
        self.repo, self.token, self.calls = repo, token, 0

    def req(self, method: str, path: str, body=None):
        self.calls += 1
        url = path if path.startswith("http") else f"https://api.github.com/repos/{self.repo}{path}"
        r = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                   headers={"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                                            "X-GitHub-Api-Version": "2022-11-28"})
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 422 and method == "POST" and path == "/labels":
                return {}
            if e.code in (403, 429):
                h = e.headers or {}
                raise RateLimited(f"{e.code} remaining={h.get('x-ratelimit-remaining')} reset={h.get('x-ratelimit-reset')} "
                                  f"retry-after={h.get('retry-after')} on {method} {path.split('?')[0]}") from None
            raise


def parse_form(body: str) -> dict:
    out, key = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            key = re.sub(r"[^a-z0-9]+", "_", m.group(1).lower()).strip("_")
            out[key] = ""
        elif key is not None:
            out[key] = (out[key] + "\n" + line).strip()
    return {k: ("" if v == "_No response_" else v) for k, v in out.items()}


def surface_from_issue(issue: dict, catalog: dict) -> dict:
    f = parse_form(issue.get("body", ""))
    sid = (f.get("surface_id") or "").strip()
    if sid in catalog:
        return catalog[sid]
    m = re.search(r"\[delphi:rfp\]\s*([a-z0-9._-]+)", issue.get("title", ""))
    if m and m.group(1) in catalog:
        return catalog[m.group(1)]
    # unknown surface: oracle has no sourced facts, rubric scores from the form only
    lock = re.search(r"\d", f.get("lock_in", "") or "3")
    return {"id": sid or f"issue-{issue['number']}", "title": issue["title"], "lane": f.get("lane", "unknown"),
            "horizon": "H2", "registry_id": None, "sourced": False,
            "quota": {"metric": f.get("free_quota", ""), "limit": None, "unit": "", "window": "", "reset": f.get("reset_and_zone", ""),
                      "zone": "", "source": issue["html_url"]},
            "auth": {"actions_secret": f.get("auth_from_actions") or None, "present": None},
            "lock_in": int(lock.group(0)) if lock else 3, "fit": 3, "headroom": 3,
            "failure_modes": [x.strip("-* ") for x in (f.get("failure_modes") or "").splitlines() if x.strip()],
            "card_required": "card" in (f.get("free_quota", "") + f.get("failure_modes", "")).lower(), "overage_autobill": False}


def input_hash(s: dict, roles: dict, registry: dict, readings: dict) -> str:
    reg = {x["id"]: x for x in registry.get("services", [])}.get(s.get("registry_id") or "", {})
    blob = json.dumps([s, roles, reg, readings], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def comment_md(out: dict, ih: str, reason: str) -> str:
    r, a = out["result"], out["award"]
    lines = [LEDGER_MARK, f"### Delphi round result: `{out['surface']}`", "",
             f"**Award:** {a['decision']}" + (f" at {int(a['traffic_share']*100)}% traffic share" if a.get("traffic_share") else "")
             + (f", recheck after {a['recheck_after']}" if a.get("recheck_after") else "")
             + (f". Blocked on {a['blocked_on']}" if a.get("blocked_on") else "") + f". Band {a['band']}.",
             f"**effective_score** {r['effective_score']} / 25 · converged {r['converged']} after {len(r['rounds'])} round(s) · trigger `{reason}`", "",
             "| Round | Median | IQR | Effective |", "|---|---|---|---|"]
    lines += [f"| {h['round']} | {h['median']} | {h['iqr']} | {h['effective']} |" for h in r["rounds"]]
    o = out["records"]["oracle"]["documented"]
    lines += ["", f"Oracle: {o['metric']} = {o['limit']} {o['unit']}, reset {o['reset']} {o['zone']} ([source]({o['source']}))", "",
              "<details><summary>Signed votes + HindSight/ForeSight/3l0.moneyball.v1 records</summary>", "", "```json",
              json.dumps({"input_hash": ih, "final_votes": r["rounds"][-1]["votes"], "award": a,
                          "records": {k: v for k, v in out["records"].items() if k != "oracle"}}, indent=1), "```", "</details>"]
    return "\n".join(lines)


def last_ledger(gh: GH, number: int) -> dict | None:
    comments = gh.req("GET", f"/issues/{number}/comments?per_page=100")
    for c in reversed(comments):
        if c.get("body", "").startswith(LEDGER_MARK):
            m = re.search(r"```json\n(.*?)\n```", c["body"], re.S)
            if m:
                try:
                    return json.loads(m.group(1))
                except ValueError:
                    return None
    return None


def weights_issue(gh: GH, panel: dict) -> tuple[int | None, dict]:
    found = gh.req("GET", "/issues?state=open&labels=delphi:weights&per_page=5")
    if not found:
        return None, panel["roles"]
    n = found[0]["number"]
    for c in reversed(gh.req("GET", f"/issues/{n}/comments?per_page=100")):
        if c.get("body", "").startswith(WEIGHTS_MARK):
            m = re.search(r"```json\n(.*?)\n```", c["body"], re.S)
            if m:
                return n, json.loads(m.group(1))["roles"]
    return n, panel["roles"]


def load_readings() -> dict:
    p = os.environ.get("QUOTA_WEIGHTS_PATH", "quota-out/routing-weights.json")
    try:
        return load(p).get("multipliers", {})
    except (OSError, ValueError):
        return {}


def cmd_run(args) -> int:
    try:
        return _run(args)
    except RateLimited as e:
        # GITHUB_TOKEN budget is shared by every workflow in the repo; defer to the next event/heartbeat.
        print(f"::warning::delphi deferred on GitHub rate limit: {e}")
        return 0


def _run(args) -> int:
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    gh = GH(repo, token)
    panel, registry, readings = load(PANEL), load(REGISTRY), load_readings()
    catalog = {s["id"]: s for s in load(SURFACES)["surfaces"]}
    for name, (color, desc) in LABELS.items():
        gh.req("POST", "/labels", {"name": name, "color": color, "description": desc})
    _, roles = weights_issue(gh, panel)
    panel = dict(panel, roles=roles)
    issues = [i for i in gh.req("GET", "/issues?state=open&labels=delphi:rfp&per_page=100") if "pull_request" not in i]
    plan = cadence(registry, readings, len(issues), args.depth)
    print(f"::notice::delphi cadence mode={plan['mode']} pace={plan['pace']} open_rfps={len(issues)} cap={plan['max_rfps_per_run']}")
    if plan["mode"] == "defer" and args.reason not in ("issues", "issue_comment", "workflow_dispatch"):
        print("::notice::delphi deferred: free quotas near cap; waiting for reset or an explicit event")
        return 0
    budget, done, pending = {"llm": int(os.environ.get("DELPHI_LLM_MAX", "30"))}, 0, 0
    session = f"run-{os.environ.get('GITHUB_RUN_ID', 'local')}"
    os.environ["DELPHI_REASON"] = args.reason
    summary = []
    for issue in sorted(issues, key=lambda i: i["number"]):
        if done >= plan["max_rfps_per_run"]:
            pending += 1
            continue
        s = surface_from_issue(issue, catalog)
        ih = input_hash(s, roles, registry, readings)
        prev = last_ledger(gh, issue["number"])
        due = prev and prev.get("award", {}).get("recheck_after") and prev["award"]["recheck_after"] <= now().strftime("%Y-%m-%dT%H:%MZ")
        if prev and prev.get("input_hash") == ih and not due:
            summary.append(f"#{issue['number']} {s['id']}: unchanged")
            continue
        out = score_surface(s, panel, registry, readings, f"#{issue['number']}", session, budget)
        gh.req("POST", f"/issues/{issue['number']}/comments", {"body": comment_md(out, ih, args.reason)})
        labels = {l["name"] for l in issue.get("labels", [])} - {"delphi:shadow", "delphi:parked", "delphi:converged", "delphi:needs-access"}
        labels.add("delphi:" + out["award"]["decision"])
        if out["result"]["converged"]:
            labels.add("delphi:converged")
        if out["award"].get("blocked_on"):
            labels.add("delphi:needs-access")
        gh.req("PUT", f"/issues/{issue['number']}/labels", {"labels": sorted(labels)})
        with open(os.environ.get("DELPHI_OUT", "delphi-out.jsonl"), "a") as f:
            f.write(json.dumps(out) + "\n")
        summary.append(f"#{issue['number']} {s['id']}: {out['award']['decision']} eff={out['result']['effective_score']}")
        done += 1
    for line in summary[:9]:
        print(f"::notice::{line}")
    print(f"::notice::delphi processed={done} pending={pending} api_calls={gh.calls}")
    if pending and plan["mode"] == "accelerate":
        gh.req("POST", "/actions/workflows/delphi-gate.yml/dispatches",
               {"ref": os.environ.get("GITHUB_REF_NAME", "master"), "inputs": {"reason": "delphi-tick", "depth": str(args.depth + 1)}})
        print(f"::notice::delphi accelerate: chained tick depth={args.depth + 1}")
    return 0


def cmd_feedback(args) -> int:
    """Flywheel: needs GITHUB_TOKEN; reads the RFP's last ledger, re-weights roles, appends to the weights ledger issue."""
    gh = GH(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])
    panel = load(PANEL)
    n, roles = weights_issue(gh, panel)
    prev = last_ledger(gh, args.rfp)
    if not prev:
        print("::error::no delphi ledger on that issue")
        return 1
    new = feedback(roles, prev["final_votes"], args.outcome, panel)
    if n is None:
        n = gh.req("POST", "/issues", {"title": WEIGHTS_TITLE, "labels": ["delphi:weights"],
                                       "body": "Append-only Delphi role weights (flywheel). docs/ops/DELPHI-WEIGHTING.md"})["number"]
    body = f"{WEIGHTS_MARK}\nFeedback from #{args.rfp}: outcome **{args.outcome}**\n```json\n{json.dumps({'roles': new}, indent=1)}\n```"
    gh.req("POST", f"/issues/{n}/comments", {"body": body})
    if args.outcome == "confirmed":
        gh.req("POST", f"/issues/{args.rfp}/labels", {"labels": ["delphi:promoted"]})
    print(f"::notice::delphi feedback rfp=#{args.rfp} outcome={args.outcome} weights_issue=#{n}")
    return 0


def cmd_score(args) -> int:
    panel, registry = load(PANEL), load(REGISTRY)
    catalog = {s["id"]: s for s in load(SURFACES)["surfaces"]}
    ids = args.surface or list(catalog)
    budget = {"llm": int(os.environ.get("DELPHI_LLM_MAX", "30"))}
    outs = [score_surface(catalog[i], panel, registry, load_readings(), args.rfp or i, args.session, budget) for i in ids]
    json.dump(outs, sys.stdout, indent=1)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="delphi-gate")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score"); s.add_argument("--surface", action="append"); s.add_argument("--rfp"); s.add_argument("--session", default="local")
    r = sub.add_parser("run"); r.add_argument("--reason", default="manual"); r.add_argument("--depth", type=int, default=0)
    f = sub.add_parser("feedback"); f.add_argument("--rfp", type=int, required=True); f.add_argument("--outcome", choices=["confirmed", "miss"], required=True)
    a = p.parse_args(argv)
    return {"score": cmd_score, "run": cmd_run, "feedback": cmd_feedback}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
