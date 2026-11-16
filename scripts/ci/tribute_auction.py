#!/usr/bin/env python3
"""Tribute claim auction: free inference endpoints ante + bid to take a claim.

Before the lane claims a foreign issue, every candidate free endpoint from the
pool (data/g4f-working/working-endpoints.json, the probed free-inference
universe) must:

  1. ANTE: lock a stake from its own credit ledger (per-endpoint quota credit;
     daily refill, capped). No credit for the ante -> no seat at the table.
  2. BID: a deterministic estimate p(real merge) for THIS issue, from
       - issue prior: label fit, body clarity, difficulty (scout components)
       - capability: model family / size / code affinity, language & stack fit
       - repo prior: Delphi/System 1 outcomes for the repo (decline/spam -> 0)
       - track record: the endpoint's own settled auctions (Beta posterior)
       - quota remaining (can it finish without hitting a free-tier limit?)
       - latency (cost of the attempt)
     EV = p * REWARD - (1 - p) * ante - latency_cost.

The highest-EV bidder above the reserve wins; ties break on lower latency, then
endpoint id (fully deterministic). Only issues that pass System 1
preflight_candidate may be auctioned. The winner must produce a real patch:
`preflight_pr` must pass (no stake/placeholder files) before any claim is
posted. Settlement (replayed deterministically from receipts + the outcome
census, never mutated in place):

  real_merge                   -> ante returned + REWARD           (Delphi +1)
  stake_merge / closed_unmerged / no_patch_after_claim -> ante forfeited (Delphi -0.8)
  no_claim (no patch, so nothing was posted) -> ante returned      (no signal)
  open                         -> ante stays in escrow

No network, no LLM calls in this module; the CLI's --enrich only reads repo
language from the GitHub API.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "tribute-auction/v1"
BUDGET = float(os.environ.get("TRIBUTE_AUCTION_BUDGET", "100"))      # max credit per endpoint
REFILL_PER_DAY = float(os.environ.get("TRIBUTE_AUCTION_REFILL", "10"))
BASE_ANTE = float(os.environ.get("TRIBUTE_AUCTION_ANTE", "10"))
REWARD = float(os.environ.get("TRIBUTE_AUCTION_REWARD", "40"))
RESERVE_EV = float(os.environ.get("TRIBUTE_AUCTION_RESERVE", "0"))
PATCH_DEADLINE_DAYS = 14
GENESIS = "2026-11-01T00:00:00Z"
ROOT = Path(__file__).resolve().parents[2]
POOL_PATH = ROOT / "data" / "g4f-working" / "working-endpoints.json"

NON_TEXT = re.compile(r"image|flux|video|audio|tts|whisper|dall|sdxl|stable-?diffusion|midjourney|embed", re.I)
FAMILY = (  # (pattern, capability, code_affinity)
    (r"coder|codestral|devstral|code", 1.00, 1.0),
    (r"deepseek", 0.95, 0.9),
    (r"qwen", 0.90, 0.85),
    (r"gpt-?4\.1|gpt-?5|o3|o4", 0.95, 0.85),
    (r"claude|sonnet|opus", 1.00, 0.95),
    (r"gemini", 0.90, 0.8),
    (r"kimi|glm|minimax", 0.85, 0.8),
    (r"nemotron|llama|mistral|mixtral", 0.75, 0.65),
    (r"gpt-?4|gpt-?3", 0.70, 0.6),
    (r"command|cohere|c4ai", 0.65, 0.5),
    (r"sonar|perplexity|search", 0.55, 0.4),
)
PROVIDER_FACTOR = {  # how well the free wrapper serves a code-editing task
    "kilocode": 1.05, "anyprovider": 1.0, "gemini": 1.0, "g4fspace": 0.95, "huggingspace": 0.9,
    "cohereforai_c4ai_command": 0.85, "yqcloud": 0.8, "agenttools": 0.8, "pollinations": 0.8, "perplexity": 0.7,
}
OUTDATED = re.compile(r"claude-?2|claude-?instant|gpt-?3|llama-?2|text-davinci", re.I)
EASY_LANGS = {"python", "javascript", "typescript", "html", "css", "markdown", "shell", "go", "java"}
HARD_LANGS = {"rust", "swift", "kotlin", "c++", "c", "solidity", "cairo", "haskell", "scala", "elixir", "zig", "move"}
EASY_LABELS = re.compile(r"good.first.issue|beginner|easy|docs?|documentation|typo|first-timers", re.I)
PROGRAM_LABELS = re.compile(r"wave|bounty|drips|odhack|gssoc|hacktoberfest-accepted|onlydust", re.I)


# ---------------------------------------------------------------- helpers
def _ts(s):
    if not s:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def endpoint_id(e: dict) -> str:
    return f"{e.get('provider')}/{e.get('model')}"


# ---------------------------------------------------------------- pool
def load_pool(path: Path | str = POOL_PATH, max_latency: float = 60.0) -> list[dict]:
    """Text endpoints from the probed free pool, deduped, deterministic order."""
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    rows = doc.get("endpoints") if isinstance(doc, dict) else doc
    out, seen = [], set()
    for e in rows or []:
        eid = endpoint_id(e)
        lat = float(e.get("latency_s") or 99)
        if eid in seen or NON_TEXT.search(eid) or lat > max_latency:
            continue
        seen.add(eid)
        out.append({"id": eid, "provider": e.get("provider"), "model": e.get("model"), "latency_s": lat})
    return sorted(out, key=lambda x: x["id"])


def capability(model: str) -> tuple[float, float]:
    m = (model or "").lower()
    cap, code = 0.6, 0.5
    for pat, c, k in FAMILY:
        if re.search(pat, m):
            cap, code = c, k
            break
    size = re.search(r"(\d+(?:\.\d+)?)\s*b\b", m.replace("-", " "))
    if size:
        b = float(size.group(1))
        cap *= _clamp(0.75 + 0.08 * math.log2(max(b, 1)), 0.75, 1.15)
    if re.search(r"nano|mini|small|lite|tiny|flash", m):
        cap *= 0.9
    if OUTDATED.search(m):
        cap *= 0.6
    return round(cap, 4), code


# ---------------------------------------------------------------- issue + repo priors
def issue_prior(issue: dict) -> tuple[float, float]:
    """(p_prior, difficulty in 0..1) from labels, body clarity and size signals."""
    labels = " ".join(str(l) for l in issue.get("labels") or [])
    comp = issue.get("score_components") or {}
    p = 0.12
    difficulty = 0.5
    if EASY_LABELS.search(labels):
        p += 0.10
        difficulty -= 0.25
    clarity = float(comp.get("body_clarity") or 0) / 15.0
    p += 0.08 * clarity
    difficulty -= 0.15 * clarity
    if int(issue.get("comments") or 0) > 12:
        p -= 0.05
        difficulty += 0.1
    lang = (issue.get("language") or "").lower()
    if lang in HARD_LANGS:
        difficulty += 0.2
    return _clamp(p, 0.02, 0.6), _clamp(difficulty, 0.0, 1.0)


def language_fit(lang: str | None, code_affinity: float, cap: float) -> float:
    lang = (lang or "").lower()
    if not lang:
        return 0.9
    if lang in EASY_LANGS:
        return 1.0 + 0.1 * code_affinity
    if lang in HARD_LANGS:
        return _clamp(0.45 + 0.5 * code_affinity * cap, 0.4, 1.0)
    return 0.85 + 0.1 * code_affinity


def repo_priors(decisions: list[dict] | None = None, census: list[dict] | None = None) -> dict:
    """Per-repo factor from Delphi/System 1 outcomes and the merge census.

    hostile/spam flag -> 0 (cooldown); mean Delphi weight w -> 1 + 0.5 w.
    A stake merge carries weight 0 and so never raises a repo's factor."""
    agg: dict[str, list[float]] = {}
    hostile = set()
    latest: dict[str, dict] = {}
    for d in decisions or []:
        url = ((d.get("subject") or {}).get("url") or "")
        if url:
            latest[url] = d
    for d in latest.values():
        sig = d.get("delphi_signal") or {}
        repo = (sig.get("repo") or (d.get("subject") or {}).get("repo") or "").lower()
        if not repo:
            continue
        if d.get("primary") == "hostile_spam_flag" or sig.get("outcome") == "hostile_spam_flag":
            hostile.add(repo)
        if isinstance(sig.get("weight"), (int, float)):
            agg.setdefault(repo, []).append(float(sig["weight"]))
    for r in census or []:
        repo = (r.get("repo") or "").lower()
        w = {"real_merge": 1.0, "stake_merge": 0.0, "closed_unmerged": -1.0}.get(r.get("class"))
        if repo and w is not None:
            agg.setdefault(repo, []).append(w)
    out = {repo: round(_clamp(1 + 0.5 * (sum(ws) / len(ws)), 0.3, 1.3), 3) for repo, ws in agg.items()}
    for repo in hostile:
        out[repo] = 0.0
    return out


def repo_of(issue: dict) -> str:
    repo = issue.get("repo") or ""
    m = re.search(r"github\.com/([^/]+/[^/#?]+)", repo or issue.get("url") or "")
    return (m.group(1) if m else repo).lower()


# ---------------------------------------------------------------- ledger replay
def new_state(pool: list[dict]) -> dict:
    return {"credits": {e["id"]: BUDGET for e in pool}, "escrow": {}, "record": {}, "last_refill": GENESIS}


def refill(state: dict, now: datetime) -> None:
    last = _ts(state.get("last_refill")) or _ts(GENESIS)
    days = (now - last).total_seconds() / 86400 if now > last else 0
    if days <= 0:
        return
    for eid in state["credits"]:
        c = state["credits"][eid]
        state["credits"][eid] = round(max(c, min(BUDGET, c + REFILL_PER_DAY * days)), 3)  # refill never claws back a reward
    state["last_refill"] = _iso(now)


def record_of(state: dict, eid: str) -> dict:
    return state["record"].setdefault(eid, {"wins": 0, "real_merges": 0, "forfeits": 0, "refunds": 0})


# ---------------------------------------------------------------- the auction
def bid(endpoint: dict, issue: dict, state: dict, repo_factor: float) -> dict | None:
    eid = endpoint["id"]
    credit = state["credits"].get(eid, BUDGET)
    p0, difficulty = issue_prior(issue)
    cap, code = capability(endpoint.get("model") or eid)
    cap = round(cap * PROVIDER_FACTOR.get(str(endpoint.get("provider") or "").lower(), 0.85), 4)
    lang_fit = language_fit(issue.get("language"), code, cap)
    quota_frac = _clamp(credit / BUDGET, 0.0, 1.0)
    p_complete = 0.6 + 0.4 * quota_frac
    rec = record_of(state, eid) if eid in state["record"] else {"wins": 0, "real_merges": 0, "forfeits": 0}
    settled = rec["real_merges"] + rec["forfeits"]
    p_model = _clamp(p0 * cap * lang_fit * repo_factor * p_complete, 0.0, 0.95)
    k = 4.0  # prior strength: four pseudo-auctions at the model estimate
    p = (p_model * k + rec["real_merges"]) / (k + settled)
    ante = round(BASE_ANTE * (1 + difficulty), 2)
    if credit < ante:
        return None  # cannot ante -> no seat
    latency_cost = round(min(endpoint.get("latency_s") or 0, 60) / 60.0, 3)
    ev = round(p * REWARD - (1 - p) * ante - latency_cost, 4)
    return {"endpoint": eid, "p_real_merge": round(p, 4), "ante": ante, "ev": ev, "credit": credit,
            "factors": {"issue_prior": round(p0, 3), "difficulty": round(difficulty, 3), "capability": cap,
                        "language_fit": round(lang_fit, 3), "repo_factor": repo_factor,
                        "quota_frac": round(quota_frac, 3), "track_record": f"{rec['real_merges']}/{settled}",
                        "latency_s": endpoint.get("latency_s")}}


def run_auction(issue: dict, pool: list[dict], state: dict, preflight: dict, repo_factors: dict | None = None,
                now: datetime | None = None, max_bids: int = 10) -> dict:
    """One sealed-bid round for one issue. Pure: returns a receipt; apply() books it."""
    now = now or datetime.now(timezone.utc)
    url = issue.get("url") or issue.get("html_url") or ""
    base = {"schema": SCHEMA, "kind": "auction", "issue": url, "repo": repo_of(issue), "at": _iso(now),
            "reward": REWARD, "reserve_ev": RESERVE_EV}
    if not (preflight or {}).get("eligible"):
        return {**base, "result": "not_eligible", "reasons": (preflight or {}).get("reasons") or ["no_preflight"],
                "winner": None, "bids": []}
    if PROGRAM_LABELS.search(" ".join(str(l) for l in issue.get("labels") or [])):
        return {**base, "result": "not_eligible", "reasons": ["program_assigned_issue"], "winner": None, "bids": []}
    rf = (repo_factors or {}).get(repo_of(issue), 1.0)
    if rf <= 0:
        return {**base, "result": "not_eligible", "reasons": ["repo_cooldown"], "winner": None, "bids": []}
    sim = json.loads(json.dumps(state))
    refill(sim, now)
    bids = [b for b in (bid(e, issue, sim, rf) for e in pool) if b]
    bids.sort(key=lambda b: (-b["ev"], next((e["latency_s"] for e in pool if e["id"] == b["endpoint"]), 99), b["endpoint"]))
    top = bids[:max_bids]
    if not top:
        return {**base, "result": "no_bidders", "winner": None, "bids": []}
    if top[0]["ev"] <= RESERVE_EV:
        return {**base, "result": "below_reserve", "winner": None, "bids": top}
    w = top[0]
    return {**base, "result": "won", "winner": w["endpoint"], "ante": w["ante"], "ev": w["ev"],
            "p_real_merge": w["p_real_merge"], "bids": top}


def claim_gate(receipt: dict, patch_files: list[dict] | None, preflight_pr) -> dict:
    """The winner must bring a real patch before any claim is posted."""
    if receipt.get("result") != "won":
        return {"claim": False, "reason": receipt.get("result")}
    if not patch_files:
        return {"claim": False, "reason": "no_patch"}
    gate = preflight_pr(patch_files)
    if not gate.get("allowed"):
        return {"claim": False, "reason": "placeholder_patch", "placeholder": gate.get("placeholder")}
    return {"claim": True, "reason": "real_patch"}


# ---------------------------------------------------------------- settlement
def match_pr(receipt: dict, census: list[dict]) -> dict | None:
    m = re.search(r"github\.com/([^/]+/[^/]+)/issues/(\d+)", receipt.get("issue") or "")
    if not m:
        return None
    repo, num = m.group(1).lower(), m.group(2)
    at = _ts(receipt.get("at"))
    cands = [r for r in census if (r.get("repo") or "").lower() == repo
             and re.search(rf"#\s*{num}\b", r.get("title") or "")
             and (not at or not _ts(r.get("created_at")) or _ts(r.get("created_at")) >= at - timedelta(hours=1))]
    cands.sort(key=lambda r: r.get("created_at") or r.get("at") or "")
    return cands[0] if cands else None


def outcome_for(receipt: dict, census: list[dict], now: datetime) -> str:
    if receipt.get("result") != "won":
        return "not_won"
    if not receipt.get("claimed"):
        return "no_claim"
    pr = match_pr(receipt, census)
    if pr is None:
        at = _ts(receipt.get("at")) or now
        return "no_patch_after_claim" if now - at > timedelta(days=PATCH_DEADLINE_DAYS) else "open"
    return {"real_merge": "real_merge", "stake_merge": "stake_merge", "closed_unmerged": "closed_unmerged",
            "self_merge": "closed_unmerged"}.get(pr.get("class"), "open")


def replay(receipts: list[dict], census: list[dict], pool: list[dict], now: datetime | None = None) -> dict:
    """Deterministic ledger from receipts (in time order) + the outcome census."""
    now = now or datetime.now(timezone.utc)
    state = new_state(pool)
    settlements, signals = [], []
    claimed = {c.get("issue") for c in receipts if c.get("kind") == "claim" and c.get("issue")}
    receipts = [dict(r, claimed=bool(r.get("claimed")) or r.get("issue") in claimed)
                for r in receipts if r.get("kind", "auction") == "auction"]
    for r in sorted(receipts, key=lambda x: (x.get("at") or "", x.get("issue") or "")):
        at = _ts(r.get("at")) or now
        refill(state, at)
        if r.get("result") != "won":
            continue
        eid, ante = r["winner"], float(r.get("ante") or BASE_ANTE)
        state["credits"].setdefault(eid, BUDGET)
        if state["credits"][eid] < ante:
            settlements.append({"issue": r["issue"], "endpoint": eid, "outcome": "void_insufficient_credit"})
            continue
        state["credits"][eid] = round(state["credits"][eid] - ante, 3)
        rec = record_of(state, eid)
        rec["wins"] += 1
        out = outcome_for(r, census, now)
        if out == "open":
            state["escrow"][r["issue"]] = {"endpoint": eid, "ante": ante, "since": r.get("at")}
            delta = 0.0
        elif out == "real_merge":
            state["credits"][eid] = round(min(BUDGET + REWARD, state["credits"][eid] + ante + REWARD), 3)
            rec["real_merges"] += 1
            delta = ante + REWARD
        elif out == "no_claim":
            state["credits"][eid] = round(state["credits"][eid] + ante, 3)
            rec["refunds"] += 1
            delta = ante
        else:  # stake_merge, closed_unmerged, no_patch_after_claim -> forfeit
            rec["forfeits"] += 1
            delta = 0.0
        settlements.append({"issue": r["issue"], "endpoint": eid, "outcome": out, "ante": ante, "returned": delta})
        if out in ("real_merge", "stake_merge", "closed_unmerged", "no_patch_after_claim"):
            signals.append({"surface": "tribute-auction", "repo": r.get("repo") or "", "outcome": out,
                            "weight": 1.0 if out == "real_merge" else -0.8,
                            "key": f"auction:{eid}:{r['issue']}"[:250]})
    refill(state, now)
    leaderboard = sorted(({"endpoint": e, **record_of(state, e), "credit": state["credits"].get(e, BUDGET)}
                          for e in state["record"]), key=lambda x: (-x["real_merges"], x["forfeits"], x["endpoint"]))
    return {"schema": SCHEMA + "-ledger", "generated_at": _iso(now), "pool_size": len(pool),
            "params": {"budget": BUDGET, "refill_per_day": REFILL_PER_DAY, "base_ante": BASE_ANTE,
                       "reward": REWARD, "reserve_ev": RESERVE_EV, "patch_deadline_days": PATCH_DEADLINE_DAYS},
            "receipts": len(receipts), "settlements": settlements, "escrow": state["escrow"],
            "leaderboard": leaderboard, "delphi_signals": signals,
            "totals": {k: sum(1 for s in settlements if s["outcome"] == k)
                       for k in ("real_merge", "stake_merge", "closed_unmerged", "no_patch_after_claim", "no_claim", "open")},
            "credits_low": sorted(e for e, c in state["credits"].items() if c < BASE_ANTE)}


# ---------------------------------------------------------------- CLI
def _read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _read_jsonl(paths):
    rows = []
    for p in paths:
        path = Path(p)
        for f in (sorted(path.glob("*.jsonl")) if path.is_dir() else [path]):
            if f.exists():
                for line in f.read_text(encoding="utf-8").splitlines():
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return rows


def _repo_language(repo: str) -> str | None:
    tok = os.environ.get("GITHUB_TOKEN") or ""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "tribute-auction", **({"Authorization": f"Bearer {tok}"} if tok else {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode()).get("language")
    except Exception:
        return None


def _gh(path: str):
    tok = os.environ.get("GITHUB_TOKEN") or ""
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "tribute-auction", **({"Authorization": f"Bearer {tok}"} if tok else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def live_preflight(url: str, s1) -> dict:
    """Read-only System 1 preflight for an issue that did not come from the scout catalog."""
    m = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url or "")
    if not m:
        return {"eligible": False, "reasons": ["not_an_issue_url"]}
    repo, num = f"{m.group(1)}/{m.group(2)}", m.group(3)
    try:
        iss = _gh(f"/repos/{repo}/issues/{num}")
        cms = _gh(f"/repos/{repo}/issues/{num}/comments?per_page=100")
    except Exception as e:  # unreadable = not ours to take (fail closed)
        return {"eligible": False, "reasons": [f"unreadable:{type(e).__name__}"]}
    issue = {"repo": repo, "number": int(num), "state": iss.get("state"), "body": iss.get("body") or "",
             "assignees": [a["login"] for a in iss.get("assignees") or []], "labels": [l["name"] for l in iss.get("labels") or []]}
    comments = [{"id": c["id"], "author": c["user"]["login"], "author_type": c["user"]["type"],
                 "association": c["author_association"], "created_at": c["created_at"], "body": c.get("body") or ""} for c in cms]
    pf = dict(s1.preflight_candidate(issue, comments))
    pf["labels"], pf["comments"] = issue["labels"], len(comments)
    return pf


def merge_summary(status_path: Path, led: dict) -> None:
    if not status_path.exists():
        return
    doc = json.loads(status_path.read_text(encoding="utf-8"))
    doc["tribute_auction"] = {"receipts": led["receipts"], "totals": led["totals"], "escrow": len(led["escrow"]),
                              "leaderboard_top": led["leaderboard"][:5], "params": led["params"],
                              "pool_size": led["pool_size"], "generated_at": led["generated_at"]}
    status_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def new_signals(led: dict, previous: dict | None) -> list[dict]:
    """Signals whose key+outcome were not in the previously committed ledger."""
    seen = {(s.get("key"), s.get("outcome")) for s in (previous or {}).get("delphi_signals") or []}
    return [s for s in led["delphi_signals"] if (s.get("key"), s.get("outcome")) not in seen][:200]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tribute claim auction (ante + bid)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("auction", help="auction the top eligible catalog issue(s)")
    a1.add_argument("--catalog", required=True, help="tribute_scout.py catalog JSON (preflighted items)")
    a1.add_argument("--issue", default="", help="auction only this issue URL")
    a1.add_argument("--pool", default=str(POOL_PATH))
    a1.add_argument("--ledger", default="", help="current ledger receipts JSONL (for credits/track record)")
    a1.add_argument("--census", default="", help="tribute-outcomes.json (prs list) for repo priors + settlement")
    a1.add_argument("--decisions", nargs="*", default=[], help="System 1 decisions JSONL (Delphi repo priors)")
    a1.add_argument("--enrich", action="store_true", help="read repo language from the GitHub API (read-only)")
    a1.add_argument("--live-preflight", action="store_true", help="re-run System 1 preflight from the live issue (read-only)")
    a1.add_argument("--max-issues", type=int, default=1)
    a1.add_argument("--now", default="")
    a1.add_argument("--out", default="auction-receipts.jsonl")
    a2 = sub.add_parser("settle", help="replay receipts against the outcome census")
    a2.add_argument("--receipts", nargs="*", default=[])
    a2.add_argument("--census", default="docs/ops/generated/tribute-outcomes.json")
    a2.add_argument("--pool", default=str(POOL_PATH))
    a2.add_argument("--now", default="")
    a2.add_argument("--out", default="docs/ops/generated/tribute-auction-ledger.json")
    a2.add_argument("--dashboard", default="apps/tribute-dashboard/data/tribute-auction-ledger.json")
    a2.add_argument("--merge-into", action="append", default=[])
    a2.add_argument("--new-signals", default="", help="write signals new since the previous ledger (Delphi changed-only)")
    a = ap.parse_args(argv)
    now = _ts(a.now) or datetime.now(timezone.utc)
    pool = load_pool(a.pool)
    census_doc = _read_json(a.census) if a.census else None
    census = (census_doc or {}).get("prs") or [] if isinstance(census_doc, dict) else (census_doc or [])

    if a.cmd == "settle":
        led = replay(_read_jsonl(a.receipts), census, pool, now)
        previous = _read_json(a.out) if a.out else None
        if a.new_signals:
            Path(a.new_signals).write_text(json.dumps(new_signals(led, previous), separators=(",", ":")) + "\n", encoding="utf-8")
        for p in a.merge_into:
            merge_summary(Path(p), led)
        text = json.dumps(led, indent=1) + "\n"
        for p in (a.out, a.dashboard):
            if p:
                Path(p).parent.mkdir(parents=True, exist_ok=True)
                Path(p).write_text(text, encoding="utf-8")
        print(json.dumps({"receipts": led["receipts"], "totals": led["totals"], "escrow": len(led["escrow"]),
                          "signals": len(led["delphi_signals"])}))
        return 0

    sys.path.insert(0, str(ROOT))
    from scripts.ci import tribute_system1 as s1  # preflight + preflight_pr
    cat = _read_json(a.catalog) or {}
    items = cat.get("items") or []
    if a.issue:
        items = [i for i in items if (i.get("url") or "") == a.issue] or [{"url": a.issue, "labels": []}]
    receipts_prev = _read_jsonl([a.ledger]) if a.ledger else []
    led_state = new_state(pool)
    # credits/track record as of now from prior receipts
    prior = replay(receipts_prev, census, pool, now)
    for e in prior["leaderboard"]:
        led_state["record"][e["endpoint"]] = {k: e[k] for k in ("wins", "real_merges", "forfeits", "refunds")}
        led_state["credits"][e["endpoint"]] = e["credit"]
    led_state["last_refill"] = _iso(now)
    rf = repo_priors(_read_jsonl(a.decisions), census)
    out = []
    for issue in items[: max(1, a.max_issues)]:
        if a.enrich and not issue.get("language"):
            issue["language"] = _repo_language(repo_of(issue))
        # Catalog items were preflighted by the scout; anything else (or --live-preflight)
        # is re-checked against the live issue. No preflight evidence -> not eligible.
        if a.live_preflight or cat.get("preflight") != "tribute_system1.preflight_candidate":
            pf = live_preflight(issue.get("url") or "", s1)
        else:
            pf = {"eligible": True, "reasons": []}
        if not issue.get("labels") and pf.get("labels"):
            issue["labels"], issue["comments"] = pf["labels"], pf.get("comments", 0)
        r = run_auction(issue, pool, led_state, pf, rf, now)
        r["claimed"] = False  # set true only by the claim job after claim_gate passes
        out.append(r)
        print(f"auction {r['issue']}: {r['result']} winner={r.get('winner')} ev={r.get('ev')} bids={len(r['bids'])}")
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in out:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    won = next((r for r in out if r["result"] == "won"), None)
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"auction_result={(won or (out[0] if out else {})).get('result', 'no_candidates')}\n")
            fh.write(f"auction_winner={(won or {}).get('winner') or ''}\n")
            fh.write(f"auction_issue={(won or {}).get('issue') or ''}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
