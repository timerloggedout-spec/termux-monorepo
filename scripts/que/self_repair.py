#!/usr/bin/env python3
"""QDesk self-repair loop (SIE ⇒ Desk QUE).

Proposal: docs/proposals/active/qdesk-self-repair/PROPOSAL.md

One batched pass per scheduled run (no polling):
  observe  — every failing master workflow ∨ stale feed ⇒ one QUE item
             (issue labeled que:self-repair), deduped by workflow ∧ error signature.
  promote  — open PRs labeled que:self-repair: green ∧ additive ∧ ≥2 candidates
             ∧ an outside DoE pass ⇒ self-merge; destructive ∨ secrets ∨ money
             ⇒ Owner packet on hark:queue (no merge).
  learn    — closed items labeled sr:verified ∨ sr:regression ⇒ weight(role, class)
             step in ops/que/self-repair/weights.json.

Stdlib only. Writes only issues/labels/merges through the token it is given;
never prints a token. Owner referenced by moniker only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Script execution sets sys.path[0] to scripts/que; add the repository root for the shared intake module.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.que.branch_reconciliation_intake import branch_reconciliation_groups

REPO = os.environ.get("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
API = "https://api.github.com"
LABEL = "que:self-repair"
MARK = "<!-- que-self-repair-key: {key} -->"
CAND_MARK = "<!-- sr-candidate"
DOE_PASS = "<!-- doe-verdict: pass -->"
HERE = Path(__file__).resolve().parents[2]
CONF = HERE / "ops" / "que" / "self-repair"
OWNER_MONIKER = "LoggedOut Timer"

# Rooms that own a failure class; the loop must not duplicate their work.
OWNED_ELSEWHERE = [
    (re.compile(r"delphi|proposals-feed|proposal-lifecycle", re.I), "delphi-room"),
]
# Bootstrap targets of record (PROPOSAL.md) get the highest blast radius.
BRANCH_GATES = {
    "action-effectiveness-ledger.yml", "repository-development-evaluation.yml",
    "peer-review-orchestrator.yml", "recon-intel-discovery.yml",
    "archwiz-dangle.yml", "repo-gate.yml",
}
SECRET_RX = re.compile(r"^\+.*\bsecrets\.[A-Z0-9_]+|^\+.*(PRIVATE_KEY|API_KEY|TOKEN)\s*[:=]", re.M)
MONEY_RX = re.compile(r"\b(billing|invoice|payment|checkout|purchase|subscription|spend[-_ ]limit)\b", re.I)


# ---------------------------------------------------------------- pure helpers
def now() -> datetime:
    return datetime.now(timezone.utc)


def signature(text: str) -> str:
    """Stable error signature: strip ids, shas, numbers, urls, timestamps."""
    t = (text or "").lower()
    t = re.sub(r"https?://\S+", "<url>", t)
    t = re.sub(r"request id [0-9a-f:]+", "request id <id>", t)
    t = re.sub(r"\b[0-9a-f]{7,40}\b", "<sha>", t)
    t = re.sub(r"\d{4}-\d\d-\d\d[t ][\d:.]+z?", "<ts>", t)
    t = re.sub(r"\d+", "<n>", t)
    t = re.sub(r"\s+", " ", t).strip()[:240]
    return hashlib.sha1(t.encode()).hexdigest()[:12]


def owner_room(workflow_name: str, path: str) -> str | None:
    for rx, room in OWNED_ELSEWHERE:
        if rx.search(workflow_name or "") or rx.search(path or ""):
            return room
    return None


def blast_radius(path: str) -> float:
    base = Path(path or "").name
    return 3.0 if base in BRANCH_GATES else 1.0


def priority(failures: int, total: int, path: str) -> float:
    rate = failures / total if total else 1.0
    return round(rate * blast_radius(path), 3)


def item_key(path: str, sig: str) -> str:
    return f"{Path(path).name}:{sig}"


def item_body(item: dict) -> str:
    rec = "\n".join(f"- run {r['url']} @ `{r['sha'][:8]}`" for r in item["receipts"][:5])
    detail = item.get("detail", "")
    detail_section = f"\n## Branch reconciliation\n{detail}\n" if detail else ""
    return f"""{MARK.format(key=item['key'])}
class: `{item.get('class', 'self-repair')}` · workflow: `{item['path']}` · signature: `{item['sig']}` · priority: {item['priority']}

## Observe
- failures: {item['failures']} / {item['total']} runs on master in {item['window_h']}h
- failing step: `{item['step'] or 'n/a'}`
- error: {item['message'] or 'n/a'}
{rec}
{detail_section}
## Loop (PROPOSAL.md)
- [ ] Research: diagnosis note with receipts (run URL ∧ SHA)
- [ ] RFP: fix spec ∧ acceptance test ∧ replay of the failing run
- [ ] Implementation: ≥ 2 candidate patches from the free-inference pool, each a PR labeled `{LABEL}` linking this item, each announced here with `{CAND_MARK} pr=#N -->`
- [ ] Evaluate: CI green on replay ∧ a DoE reviewer (not the PR author) comments `{DOE_PASS}` on the winning PR
- [ ] Promote: additive ∧ green ⇒ self-merge; destructive ∨ secrets ∨ money ⇒ Owner packet on hark:queue
- [ ] Learn: close with `sr:verified` (or `sr:regression`) ∧ `role:<role>` ⇒ weight(role, class) step
"""


def promote_decision(files: list[dict], checks: list[dict], candidates: int,
                     doe_pass_by: list[str], pr_author: str) -> dict:
    """Decide self-merge vs Owner packet vs wait for one self-repair PR."""
    reasons = []
    destructive = [f["filename"] for f in files if f.get("status") in ("removed", "renamed")]
    patches = "\n".join(f.get("patch") or "" for f in files)
    if destructive:
        reasons.append("destructive:" + ",".join(destructive[:5]))
    if SECRET_RX.search(patches):
        reasons.append("secrets")
    if MONEY_RX.search(patches):
        reasons.append("money")
    if reasons:
        return {"action": "owner_packet", "reasons": reasons}
    pending = [c["name"] for c in checks if c.get("status") != "completed"]
    red = [c["name"] for c in checks if c.get("status") == "completed"
           and c.get("conclusion") not in ("success", "skipped", "neutral")]
    if pending:
        return {"action": "wait", "reasons": ["checks_pending"]}
    if red:
        return {"action": "wait", "reasons": ["checks_red:" + ",".join(red[:5])]}
    if candidates < 2:
        return {"action": "wait", "reasons": [f"candidates:{candidates}<2"]}
    outside = [u for u in doe_pass_by if u.lower() != (pr_author or "").lower()]
    if not outside:
        return {"action": "wait", "reasons": ["doe_review_missing"]}
    return {"action": "self_merge", "reasons": ["additive", "green", f"candidates:{candidates}", f"doe:{outside[0]}"]}


def learn(weights: dict, closed_items: list[dict]) -> tuple[dict, list[str]]:
    """Apply verified/regression outcomes once each. weights = {"applied": [...], "w": {role: {class: n}}}."""
    weights = {"schema": "que-self-repair-weights/v1", "applied": [], "w": {}, **weights}
    done = set(weights["applied"])
    changed = []
    for it in closed_items:
        labels = {l if isinstance(l, str) else l.get("name") for l in it.get("labels", [])}
        if it["number"] in done:
            continue
        roles = [l.split(":", 1)[1] for l in labels if l and l.startswith("role:")]
        cls = next((l.split(":", 1)[1] for l in labels if l and l.startswith("class:")), "self-repair")
        delta = 1 if "sr:verified" in labels else (-1 if "sr:regression" in labels else 0)
        if not delta or not roles:
            continue
        for r in roles:
            weights["w"].setdefault(r, {})
            weights["w"][r][cls] = weights["w"][r].get(cls, 0) + delta
        weights["applied"].append(it["number"])
        changed.append(f"#{it['number']}:{','.join(roles)}:{cls}:{delta:+d}")
    return weights, changed


# ---------------------------------------------------------------- GitHub I/O
class ApiBudgetExceeded(RuntimeError):
    pass


class GH:
    def __init__(self, token: str, max_calls: int = 80):
        self.token = token
        self.max_calls = max(1, max_calls)
        self.calls = 0
        self.stage = "initialize"
        self.statuses: dict[str, int] = {}
        self.routes: dict[str, int] = {}
        self.latencies_ms: list[float] = []
        self.rate_limit = {"remaining": None, "limit": None, "reset_epoch": None,
                           "retry_after": None, "resource": None, "request_id": None}

    def req(self, method: str, path: str, body: Any = None) -> Any:
        if self.calls >= self.max_calls:
            raise ApiBudgetExceeded(f"cycle API budget exhausted ({self.calls}/{self.max_calls})")
        url = path if path.startswith("http") else API + path
        route = urllib.parse.urlsplit(path).path
        route = re.sub(r"(/actions/runs)/\d+", r"\1/{run_id}", route)
        route = re.sub(r"(/check-runs)/\d+", r"\1/{check_run_id}", route)
        route = re.sub(r"(/issues)/\d+", r"\1/{issue_number}", route)
        route = re.sub(r"(/pulls)/\d+", r"\1/{pull_number}", route)
        route = re.sub(r"(/workflows)/\d+", r"\1/{workflow_id}", route)
        route = re.sub(r"(/commits)/[0-9a-f]{7,40}", r"\1/{sha}", route)
        data = None if body is None else json.dumps(body).encode()
        r = urllib.request.Request(url, data=data, method=method, headers={
            "Accept": "application/vnd.github+json", "User-Agent": "que-self-repair",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {self.token}"} if self.token else {})})
        if data is not None:
            r.add_header("Content-Type", "application/json")
        self.calls += 1
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(r, timeout=40) as resp:
                raw = resp.read()
                self._record(resp.headers, resp.status, route, started)
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            self._record(exc.headers, exc.code, route, started)
            raise
        except urllib.error.URLError:
            self._record(None, 0, route, started)
            raise

    def _record(self, headers: Any, status: int, route: str, started: float) -> None:
        key = str(status)
        self.statuses[key] = self.statuses.get(key, 0) + 1
        self.routes[route] = self.routes.get(route, 0) + 1
        self.latencies_ms.append(round((time.perf_counter() - started) * 1000, 2))
        if headers is not None:
            for header, field in (("X-RateLimit-Remaining", "remaining"),
                                  ("X-RateLimit-Limit", "limit"),
                                  ("X-RateLimit-Reset", "reset_epoch"),
                                  ("Retry-After", "retry_after"),
                                  ("X-RateLimit-Resource", "resource"),
                                  ("X-GitHub-Request-Id", "request_id")):
                value = headers.get(header)
                if value is not None:
                    self.rate_limit[field] = value

    def metrics(self) -> dict:
        values = sorted(self.latencies_ms)
        p95 = values[min(len(values) - 1, max(0, int(0.95 * len(values) + 0.999) - 1))] if values else None
        return {"api_calls": self.calls, "api_call_budget": self.max_calls,
                "budget_remaining": max(0, self.max_calls - self.calls),
                "http_statuses": dict(sorted(self.statuses.items())),
                "route_calls": dict(sorted(self.routes.items())),
                "latency_ms": {"count": len(values),
                               "p50": round(statistics.median(values), 2) if values else None,
                               "p95": p95, "max": max(values) if values else None},
                "rate_limit": self.rate_limit}

    def get(self, path: str) -> Any:
        return self.req("GET", path)


def failing_groups(gh: GH, window_h: int, max_groups: int = 8) -> list[dict]:
    since = (now() - timedelta(hours=window_h)).strftime("%Y-%m-%dT%H:%M:%SZ")
    runs = gh.get(f"/repos/{REPO}/actions/runs?branch=master&status=failure&per_page=100&created=%3E%3D{since}")
    groups: dict[str, list[dict]] = {}
    for r in runs.get("workflow_runs", []):
        groups.setdefault(r.get("path") or r["name"], []).append(r)
    out = []
    for path, rs in groups.items():
        latest = max(rs, key=lambda r: r["created_at"])
        room = owner_room(latest["name"], path)
        step, message = "", ""
        try:
            for j in gh.get(f"/repos/{REPO}/actions/runs/{latest['id']}/jobs").get("jobs", []):
                if j.get("conclusion") != "failure":
                    continue
                step = next((s["name"] for s in j.get("steps", []) if s.get("conclusion") == "failure"), "")
                anns = gh.get(f"/repos/{REPO}/check-runs/{j['id']}/annotations")
                msgs = [a["message"] for a in anns if a.get("annotation_level") == "failure"
                        and "Node.js" not in a.get("message", "")]
                message = (msgs[0] if msgs else "")[:300]
                break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise
            message = f"jobs unreadable: HTTP {e.code}"
        wf_id = latest.get("workflow_id")
        total = len(rs)
        try:
            total = gh.get(f"/repos/{REPO}/actions/workflows/{wf_id}/runs?branch=master&per_page=1&created=%3E%3D{since}").get("total_count", total)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise
        sig = signature(f"{step} {message}")
        out.append({
            "path": path, "name": latest["name"], "room": room, "step": step, "message": message,
            "sig": sig, "key": item_key(path, sig), "failures": len(rs), "total": max(total, len(rs)),
            "window_h": window_h, "priority": priority(len(rs), max(total, len(rs)), path),
            "receipts": [{"url": r["html_url"], "sha": r["head_sha"]} for r in sorted(rs, key=lambda r: r["created_at"], reverse=True)],
        })
    # Bootstrap order: branch gates first, then priority.
    return sorted(out, key=lambda g: (Path(g["path"]).name not in BRANCH_GATES, -g["priority"]))[:max_groups]


def stale_feeds(gh: GH) -> list[dict]:
    reg = json.loads((CONF / "feeds.json").read_text(encoding="utf-8"))
    out = []
    for f in reg.get("feeds", []):
        try:
            c = gh.get(f"/repos/{REPO}/commits?path={urllib.parse.quote(f['path'])}&sha=master&per_page=1")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise
            continue
        if not c:
            continue
        at = datetime.fromisoformat(c[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
        age_h = (now() - at).total_seconds() / 3600
        if age_h > f["max_age_h"]:
            sig = signature(f"stale feed {f['path']}")
            out.append({
                "path": f["path"], "name": f"stale feed {f['path']}", "room": f.get("owner") if f.get("owner") != "que" else None,
                "step": "freshness", "message": f"last commit {age_h:.1f}h ago (max {f['max_age_h']}h)",
                "sig": sig, "key": item_key(f["path"], sig), "failures": 1, "total": 1, "window_h": int(age_h),
                "priority": round(min(age_h / f["max_age_h"], 5.0), 3),
                "receipts": [{"url": c[0]["html_url"], "sha": c[0]["sha"]}],
            })
    return out


def open_items(gh: GH) -> dict[str, dict]:
    items = gh.get(f"/repos/{REPO}/issues?labels={urllib.parse.quote(LABEL)}&state=open&per_page=100")
    out = {}
    for it in items:
        m = re.search(r"que-self-repair-key: (\S+) -->", it.get("body") or "")
        if m:
            out[m.group(1)] = it
    return out


def file_items(gh: GH, groups: list[dict], dry: bool, cap: int) -> list[str]:
    existing = open_items(gh) if not dry else {}
    log = []
    for g in groups:
        if g["room"]:
            log.append(f"skip {g['key']} owned_by={g['room']}")
            continue
        if g["key"] in existing:
            it = existing[g["key"]]
            if not dry:
                gh.req("PATCH", f"/repos/{REPO}/issues/{it['number']}", {"body": item_body(g)})
            log.append(f"update #{it['number']} {g['key']}")
            continue
        if cap <= 0:
            log.append(f"defer {g['key']} (per-run cap)")
            continue
        cap -= 1
        prefix = "branch-reconciliation" if g.get("class") == "branch-reconciliation" else "self-repair"
        title = f"{prefix}: {g['name']} · {g['step'] or 'failure'} [{g['sig']}]"[:200]
        if dry:
            log.append(f"would-open {g['key']} p={g['priority']}")
        else:
            it = gh.req("POST", f"/repos/{REPO}/issues", {"title": title, "body": item_body(g), "labels": [LABEL, "class:self-repair"]})
            log.append(f"open #{it['number']} {g['key']} p={g['priority']}")
    return log


def promote(gh: GH, dry: bool, max_prs: int = 5) -> list[str]:
    log = []
    prs = gh.get(f"/repos/{REPO}/issues?labels={urllib.parse.quote(LABEL)}&state=open&per_page=50")
    for pr in [p for p in prs if p.get("pull_request")][:max_prs]:
        n = pr["number"]
        detail = gh.get(f"/repos/{REPO}/pulls/{n}")
        files = gh.get(f"/repos/{REPO}/pulls/{n}/files?per_page=100")
        checks = gh.get(f"/repos/{REPO}/commits/{detail['head']['sha']}/check-runs?per_page=100").get("check_runs", [])
        checks = [c for c in checks if c.get("name") != "qdesk self-repair"]
        m = re.search(r"#(\d+)", detail.get("body") or "")
        candidates, doe = 0, []
        if m:
            cm = gh.get(f"/repos/{REPO}/issues/{m.group(1)}/comments?per_page=100")
            candidates = len({re.search(r"pr=#(\d+)", c["body"]).group(1) for c in cm
                              if CAND_MARK in (c.get("body") or "") and re.search(r"pr=#(\d+)", c["body"])})
        for c in gh.get(f"/repos/{REPO}/issues/{n}/comments?per_page=100"):
            if DOE_PASS in (c.get("body") or ""):
                doe.append(c["user"]["login"])
        d = promote_decision(files, checks, candidates, doe, detail["user"]["login"])
        log.append(f"#{n} {d['action']} {','.join(d['reasons'])}")
        if dry or d["action"] == "wait":
            continue
        if d["action"] == "self_merge":
            gh.req("PUT", f"/repos/{REPO}/pulls/{n}/merge", {"merge_method": "squash", "sha": detail["head"]["sha"],
                                                              "commit_title": f"{detail['title']} (#{n}) [skip render]"})
        else:
            key = f"que-self-repair-owner-packet:{n}"
            q = gh.get(f"/repos/{REPO}/issues?labels=hark%3Aqueue&state=open&per_page=100")
            if not any(key in (i.get("body") or "") for i in q):
                gh.req("POST", f"/repos/{REPO}/issues", {
                    "title": f"Owner packet: self-repair PR #{n} needs {OWNER_MONIKER}'s decision",
                    "labels": ["hark:queue"],
                    "body": f"<!-- hark-key: {key} -->\npriority: P2\nPR: {detail['html_url']}\nreasons: {', '.join(d['reasons'])}\n"
                            f"done_when: Owner approves or rejects; nothing merges without it."})
    return log


def run_learn(gh: GH, dry: bool) -> list[str]:
    path = CONF / "weights.json"
    weights = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    closed = gh.get(f"/repos/{REPO}/issues?labels={urllib.parse.quote(LABEL)}&state=closed&per_page=100")
    weights, changed = learn(weights, [c for c in closed if not c.get("pull_request")])
    if changed and not dry:
        weights["updated_at"] = now().strftime("%Y-%m-%dT%H:%M:%SZ")
        path.write_text(json.dumps(weights, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-hours", type=int, default=int(os.environ.get("QUE_SR_WINDOW_HOURS", "6")))
    ap.add_argument("--max-new", type=int, default=int(os.environ.get("QUE_SR_MAX_NEW", "5")))
    ap.add_argument("--max-api-calls", type=int, default=int(os.environ.get("QUE_SR_MAX_API_CALLS", "80")))
    ap.add_argument("--max-failing-groups", type=int, default=int(os.environ.get("QUE_SR_MAX_FAILING_GROUPS", "8")))
    ap.add_argument("--max-promotions", type=int, default=int(os.environ.get("QUE_SR_MAX_PROMOTIONS", "5")))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--branch-inventory", default=None)
    a = ap.parse_args(argv)
    gh = GH(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "", a.max_api_calls)
    summary = {"observe": [], "promote": [], "learn": []}
    completed_stages = []
    state, reason = "COMPLETED", None
    try:
        gh.stage = "observe"
        groups = failing_groups(gh, a.window_hours, a.max_failing_groups) + stale_feeds(gh)
        if a.branch_inventory:
            groups += branch_reconciliation_groups(a.branch_inventory)
        summary["observe"] = file_items(gh, groups, a.dry_run, a.max_new)
        completed_stages.append("observe")
        gh.stage = "promote"
        summary["promote"] = promote(gh, a.dry_run, a.max_promotions)
        completed_stages.append("promote")
        gh.stage = "learn"
        summary["learn"] = run_learn(gh, a.dry_run)
        completed_stages.append("learn")
    except ApiBudgetExceeded as e:
        state, reason = "DEFERRED_BUDGET", str(e)
    except urllib.error.HTTPError as e:
        detail = e.read(500).decode("utf-8", "replace")
        limited = e.code == 429 or str(gh.rate_limit["remaining"]) == "0" or "rate limit" in detail.lower()
        state = "DEFERRED_RATE_LIMIT" if limited else "DEFERRED_PERMISSION"
        reason = f"HTTP {e.code}: {detail[:240]}"
    except urllib.error.URLError as e:
        state, reason = "DEFERRED_TRANSPORT", str(e.reason)[:240]
    receipt = {
        "schema": "qdesk-self-repair-cycle/v2", "state": state, "reason": reason,
        "stage": gh.stage, "completed_stages": completed_stages,
        "deferred_work_count": 1 if state.startswith("DEFERRED_") else 0,
        "repo": REPO, "ref": os.environ.get("GITHUB_REF", "unknown"),
        "sha": os.environ.get("GITHUB_SHA", "unknown"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "unknown"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "unknown"),
        "observed_at": now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary, "api": gh.metrics(),
    }
    receipt_path = Path(os.environ.get("QUE_SR_RECEIPT_PATH", "artifacts/qdesk-self-repair/receipt.json"))
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out = json.dumps(receipt, indent=1)
    print(out)
    step = os.environ.get("GITHUB_STEP_SUMMARY")
    if step:
        with open(step, "a", encoding="utf-8") as f:
            f.write("### QDesk self-repair: " + state + "\n```json\n" + out + "\n```\n")
    if state.startswith("DEFERRED_"):
        print(f"::warning::QDesk cycle {state}: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
