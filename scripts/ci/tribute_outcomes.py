#!/usr/bin/env python3
"""Honest Tribute outcome census + outcome SLO.

The old status page counted *operational receipts* (a skip receipt is an
"ok" observation), so "failed 0" sat next to zero real merges. This module
counts *outcomes* of foreign PRs authored by the lane, and reports a
FAILURE when the lane is not producing real merges.

Census (search API, read-only):
  is:pr author:<AUTHOR> -user:<AUTHOR>   in three states: merged, closed-unmerged, open
Each merged PR is classified from its diff and merger:
  real_merge   - merged by someone other than the author, non-placeholder diff
  stake_merge  - merged, but the diff is only stake/placeholder files (weight 0)
  self_merge   - merged by the author (an org the author runs; not a foreign win)
Closed-unmerged PRs count as failures. System 1 decisions (optional) add
yielded / retired / dropped thread counts.

SLO (window default 30d), status FAIL when any of:
  zero_real_merges          real_merges_<W>d == 0
  real_merge_rate_below     real / (real + stake + closed_unmerged) < --min-rate  (with >= --min-decided decided)
  real_merge_drought        days since the last real merge > --max-drought-days
WARN (never OK) when stake merges exist in the window (they are counted at weight 0).

  python3 scripts/ci/tribute_outcomes.py                       # live census -> generated JSON/MD
  python3 scripts/ci/tribute_outcomes.py --census fixture.json # offline
  python3 scripts/ci/tribute_outcomes.py --merge-into docs/ops/generated/tribute-status.json \
      --merge-into apps/tribute-dashboard/data/status.json
  python3 scripts/ci/tribute_outcomes.py --check-file docs/ops/generated/tribute-outcomes.json  # exit 1 on FAIL
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://api.github.com"
AUTHOR = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")
SCHEMA = "tribute-outcomes/v1"
WINDOWS = (7, 14, 30, 90)
PLACEHOLDER_PATHS = re.compile(r"(^|/)(help-wanted-lane-stake\.md|placeholder[^/]*|stake[^/]*\.md|TODO[^/]*)$", re.I)
STAKE_TITLE = re.compile(r"help-wanted:\s*stake\b", re.I)
YIELD_ACTIONS = {"yield_lane"}
RETIRE_ACTIONS = {"retire_lane", "retire_lane_cooldown"}
DROP_ACTIONS = {"drop_candidate"}
# Orgs the lane account runs itself: anything merged there is self_merge, never a foreign win.
SELF_OWNERS = {o.strip().lower() for o in os.environ.get("TRIBUTE_SELF_OWNERS", "Research-Astute,search-astute-ly").split(",") if o.strip()}
LANE_MARKER = re.compile(r"(help-wanted|tribute)[ -]lane|via termux-monorepo|termux-monorepo help-wanted|help-wanted:\s*stake", re.I)
LANE_HEAD = re.compile(r"^(help-wanted|tribute|fix/|feat/|docs/|chore/)", re.I)
SEARCH_CAP = 1000

try:  # package import (tests) or script import (CI)
    from scripts.ci import tribute_audit_rev as audit_rev
except ImportError:  # pragma: no cover
    import tribute_audit_rev as audit_rev  # type: ignore


def _ts(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _iso(d: datetime | None) -> str | None:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


# ---------------------------------------------------------------- classification
def is_stake_diff(files: list[dict] | None) -> bool:
    files = list(files or [])
    return bool(files) and all(PLACEHOLDER_PATHS.search(f.get("filename") or "") for f in files)


def classify(pr: dict, author: str = AUTHOR) -> str:
    """One of real_merge | stake_merge | self_merge | closed_unmerged | open."""
    state = (pr.get("state") or "").lower()
    if pr.get("merged_at"):
        owner = (pr.get("repo") or "").split("/")[0].lower()
        if (pr.get("merged_by") or "").lower() == author.lower() or owner in SELF_OWNERS:
            return "self_merge"
        files = pr.get("files")
        if files is not None:
            return "stake_merge" if is_stake_diff(files) else "real_merge"
        return "stake_merge" if STAKE_TITLE.search(pr.get("title") or "") else "real_merge"
    if state == "closed":
        return "closed_unmerged"
    return "open"


def attribution(pr: dict, cls: str, author: str = AUTHOR) -> dict | None:
    """Who merged a merged PR and in what relationship (owner correction 3, 2026-11-12).

    merged_by            login that pressed merge
    merger_association   the merger's author_association on the target repo (OWNER/MEMBER/COLLABORATOR/...),
                         read from the merger's review/comment on the PR; OWNER when the merger owns the repo
    author_association   the lane account's association on the target repo at read time
    lane_produced        the PR was opened by the Tribute lane (marker in body/title/head), not by hand
    collaborator_integration  the merge integrated our work through a collaborator relationship
                         (we hold COLLABORATOR/MEMBER/OWNER on the target, or the merger is a known collaborator
                         of the lane account's own repos) rather than a maintainer accepting a stranger's patch
    attribution_class    maintainer_accept_lane | maintainer_accept_manual | collaborator_integration | self | n/a
    """
    if cls not in ("real_merge", "stake_merge", "self_merge"):
        return None
    repo_owner = (pr.get("repo") or "").split("/")[0]
    merged_by = pr.get("merged_by")
    assoc = pr.get("merger_association")
    if not assoc and merged_by and repo_owner and merged_by.lower() == repo_owner.lower():
        assoc = "OWNER"
    ours = (pr.get("author_association") or "").upper()
    text = " ".join(str(pr.get(k) or "") for k in ("title", "body"))
    lane = bool(LANE_MARKER.search(text)) or (pr.get("lane_produced") is True)
    if pr.get("lane_produced") is False:
        lane = False
    known = {u.strip().lower() for u in os.environ.get("TRIBUTE_KNOWN_COLLABORATORS", "").split(",") if u.strip()}
    collab = ours in ("COLLABORATOR", "MEMBER", "OWNER") or (merged_by or "").lower() in known
    if cls == "self_merge":
        klass = "self"
    elif collab:
        klass = "collaborator_integration"
    else:
        klass = "maintainer_accept_lane" if lane else "maintainer_accept_manual"
    return {"merged_by": merged_by, "merger_association": assoc or "UNKNOWN", "author_association": ours or "UNKNOWN",
            "lane_produced": lane, "collaborator_integration": collab, "attribution_class": klass}


def outcome_time(pr: dict, cls: str):
    if cls in ("real_merge", "stake_merge", "self_merge"):
        return _ts(pr.get("merged_at"))
    if cls == "closed_unmerged":
        return _ts(pr.get("closed_at"))
    return _ts(pr.get("created_at"))


# ---------------------------------------------------------------- System 1 decisions
def s1_counts(decisions: list[dict], since: datetime | None = None) -> dict:
    """Latest decision per thread -> yielded / retired / dropped counts."""
    latest: dict[str, dict] = {}
    for d in decisions:
        url = ((d.get("subject") or {}).get("url") or "").strip()
        if url:
            latest[url] = d
    out = {"threads": len(latest), "yielded": 0, "retired": 0, "dropped": 0, "placeholder_merges": 0}
    for d in latest.values():
        a = d.get("action")
        out["yielded"] += a in YIELD_ACTIONS
        out["retired"] += a in RETIRE_ACTIONS
        out["dropped"] += a in DROP_ACTIONS
        out["placeholder_merges"] += a == "record_placeholder_merge"
    return out


# ---------------------------------------------------------------- report
def build(prs: list[dict], now: datetime, window: int = 30, decisions: list[dict] | None = None,
          min_rate: float = 0.10, min_decided: int = 10, max_drought_days: int = 21,
          author: str = AUTHOR, source: str = "live", census_check: dict | None = None) -> dict:
    rows = []
    for pr in prs:
        cls = classify(pr, author)
        row = {"url": pr.get("html_url"), "repo": pr.get("repo"), "title": (pr.get("title") or "")[:120],
               "class": cls, "at": _iso(outcome_time(pr, cls)), "weight": {"real_merge": 1.0}.get(cls, 0.0)
               if cls != "closed_unmerged" else -1.0, "created_at": _iso(_ts(pr.get("created_at")))}
        att = attribution(pr, cls, author)
        if att:
            row["attribution"] = att
        rows.append(row)
    windows = {}
    for w in sorted(set(WINDOWS) | {window}):
        since = now - timedelta(days=w)
        c = {k: 0 for k in ("real_merge", "stake_merge", "self_merge", "closed_unmerged", "opened")}
        for r in rows:
            t = _ts(r["at"])
            if not t or t < since:
                continue
            if r["class"] == "open":
                c["opened"] += 1
            else:
                c[r["class"]] += 1
        decided = c["real_merge"] + c["stake_merge"] + c["closed_unmerged"]
        windows[f"{w}d"] = {
            "real_merges": c["real_merge"], "stake_only_merges": c["stake_merge"], "self_merges_excluded": c["self_merge"],
            "closed_unmerged": c["closed_unmerged"], "opened_still_open": c["opened"], "decided": decided,
            "real_merge_rate": round(c["real_merge"] / decided, 4) if decided else None,
            # stake merges carry weight 0; closed-unmerged are failures
            "weighted_score": round(c["real_merge"] * 1.0 + c["stake_merge"] * 0.0 - c["closed_unmerged"] * 1.0, 2),
        }
    totals = {k: sum(1 for r in rows if r["class"] == k) for k in ("real_merge", "stake_merge", "self_merge", "closed_unmerged", "open")}
    real_times = [_ts(r["at"]) for r in rows if r["class"] == "real_merge" and _ts(r["at"])]
    last_real = max(real_times) if real_times else None
    drought = round((now - last_real).total_seconds() / 86400, 1) if last_real else None
    W = windows[f"{window}d"]
    failures, warnings = [], []
    if W["real_merges"] == 0:
        failures.append({"code": "zero_real_merges", "detail": f"0 real foreign merges in the last {window}d"})
    if W["decided"] >= min_decided and (W["real_merge_rate"] or 0) < min_rate:
        failures.append({"code": "real_merge_rate_below",
                         "detail": f"real merge rate {W['real_merge_rate']:.1%} < {min_rate:.0%} over {W['decided']} decided PRs ({window}d)"})
    if drought is None or drought > max_drought_days:
        failures.append({"code": "real_merge_drought",
                         "detail": f"last real merge {('never' if drought is None else f'{drought}d ago')} (> {max_drought_days}d)"})
    if W["stake_only_merges"]:
        warnings.append({"code": "stake_only_merges_weight_0",
                         "detail": f"{W['stake_only_merges']} stake-only merges in {window}d counted at weight 0"})
    if W["closed_unmerged"]:
        warnings.append({"code": "closed_unmerged",
                         "detail": f"{W['closed_unmerged']} PRs closed without merge in {window}d (counted as failures)"})
    s1 = s1_counts(decisions or [])
    status = "FAIL" if failures else ("WARN" if warnings else "OK")
    # Primary SLO (owner correction 1): whole corpus + activity-aware recency; windows above are secondary.
    corpus = audit_rev.corpus_items({"prs": rows}, decisions or [])
    primary = audit_rev.slo_primary(corpus, now, min_rate=min_rate, min_decided=min_decided)
    attributions = [{"url": r["url"], **r["attribution"]} for r in rows if r["class"] == "real_merge" and r.get("attribution")]
    return {
        "schema": SCHEMA,
        "generated_at": _iso(now),
        "source": source,
        "author": author,
        "query": f"is:pr author:{author} -user:{author} (merged | closed-unmerged | open)",
        "window_days": window,
        "slo": {"status": status, "failures": failures, "warnings": warnings,
                "outcome_failures": len(failures) + W["closed_unmerged"],
                "thresholds": {"min_real_merge_rate": min_rate, "min_decided": min_decided,
                               "max_drought_days": max_drought_days}},
        "totals": {"real_merges": totals["real_merge"], "stake_only_merges": totals["stake_merge"],
                   "self_merges_excluded": totals["self_merge"], "closed_unmerged": totals["closed_unmerged"],
                   "open": totals["open"]},
        "windows": windows,
        "windows_role": "secondary (primary view = audit_rev whole corpus, slo_primary)",
        "slo_primary": primary,
        "real_merge_attribution": attributions,
        "census_check": census_check,
        "last_real_merge_at": _iso(last_real),
        "days_since_real_merge": drought,
        "system1": s1,
        "semantics": {
            "real_merge": "merged by a foreign maintainer with a non-placeholder diff (weight 1)",
            "stake_only_merge": "merged but only stake/placeholder files changed (weight 0, never a win)",
            "self_merge": "merged by the author into an org the author runs (excluded)",
            "closed_unmerged": "closed without merge (failure, weight -1)",
            "yielded/retired/dropped": "System 1 thread decisions (latest per thread)",
        },
        "prs": sorted(rows, key=lambda r: r["at"] or "", reverse=True),
    }


def markdown(rep: dict) -> str:
    s, W = rep["slo"], rep["windows"][f"{rep['window_days']}d"]
    lines = [f"## Tribute outcome SLO: **{s['status']}** ({rep['window_days']}d window)", "",
             f"real merges **{W['real_merges']}** · stake-only merges **{W['stake_only_merges']}** (weight 0) · "
             f"closed-unmerged **{W['closed_unmerged']}** · real merge rate **{W['real_merge_rate'] if W['real_merge_rate'] is not None else 'n/a'}** · "
             f"open now **{rep['totals']['open']}** · days since real merge **{rep['days_since_real_merge']}**", ""]
    P = rep.get("slo_primary")
    if P:
        c = P["corpus"]
        lines = [f"## Tribute outcome SLO (primary, whole corpus): **{P['status']}** · activity {P['activity_state']}", "",
                 f"corpus decided **{c['decided']}** · real **{c['real_merges']}** (lane-produced {c['real_merges_lane']}) · "
                 f"stake-only **{c['stake_only_merges']}** · closed-unmerged **{c['closed_unmerged']}** · open **{c['open']}** · "
                 f"rate **{c['real_merge_rate']}** · active attempts since real merge **{P['recency']['active_attempts_since_real']}**", ""]
        lines += [f"- FAIL `{f['code']}`: {f['detail']}" for f in P["failures"]]
        lines += [f"- WARN `{w['code']}`: {w['detail']}" for w in P["warnings"]]
        lines += ["", f"### Secondary: {rep['window_days']}d window ({s['status']})", "",
                  f"real merges **{W['real_merges']}** · stake-only **{W['stake_only_merges']}** · closed-unmerged **{W['closed_unmerged']}**", ""]
    lines += [f"- FAIL `{f['code']}`: {f['detail']}" for f in s["failures"]]
    lines += [f"- WARN `{w['code']}`: {w['detail']}" for w in s["warnings"]]
    s1 = rep["system1"]
    lines += ["", f"System 1 threads {s1['threads']}: yielded {s1['yielded']} · retired {s1['retired']} · dropped {s1['dropped']} · placeholder merges {s1['placeholder_merges']}",
              "", "| window | real | stake (w0) | self (excl) | closed-unmerged | rate |", "|---|---|---|---|---|---|"]
    for k, v in rep["windows"].items():
        lines.append(f"| {k} | {v['real_merges']} | {v['stake_only_merges']} | {v['self_merges_excluded']} | {v['closed_unmerged']} | {v['real_merge_rate']} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- live census (read-only)
def _token() -> str:
    for k in ("OPERATOR_GITHUB_TOKEN", "OPERATOR_TOKEN", "ARCHWIZ_GITHUB_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return ""


def _get(path: str):
    req = urllib.request.Request(path if path.startswith("http") else API + path,
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "tribute-outcomes",
                                          **({"Authorization": f"Bearer {_token()}"} if _token() else {})})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def search_all(q: str, fetch=None, per_page: int = 100, lo: str = "2008-01-01", hi: str = "2100-01-01") -> tuple[list[dict], int]:
    """Every search hit for q. Pages until total_count is reached; when total_count exceeds the
    search API cap (1000) the created: range is bisected so no page cap can truncate the census.
    Returns (items, total_count reported by the API for the unsplit query)."""
    fetch = fetch or _get

    def run(query):
        items, total, page = [], None, 1
        while True:
            data = fetch(f"/search/issues?q={urllib.parse.quote(query)}&per_page={per_page}&page={page}&sort=created&order=asc")
            if total is None:
                total = int(data.get("total_count") or 0)
            batch = data.get("items") or []
            items.extend(batch)
            if not batch or len(items) >= min(total, SEARCH_CAP) or len(batch) < per_page:
                return items, total
            page += 1

    def ranged(a, b):
        items, total = run(f"{q} created:{a}..{b}")
        if total <= SEARCH_CAP:
            return items
        da, db = datetime.fromisoformat(a), datetime.fromisoformat(b)
        if (db - da).days < 1:
            raise RuntimeError(f"census: >{SEARCH_CAP} hits within one day for {q!r}; cannot split further")
        mid = (da + (db - da) / 2).date()
        return ranged(a, mid.isoformat()) + ranged((mid + timedelta(days=1)).isoformat(), b)

    items, total = run(q)
    if total > SEARCH_CAP:
        items = ranged(lo, hi)
    return items, total


def census_assert(total: int, parts: dict) -> dict:
    """Owner correction 2: total foreign PRs must equal merged + closed-unmerged + open."""
    s = sum(parts.values())
    ok = s == total
    return {"ok": ok, "total": total, "parts": parts, "sum": s,
            "detail": ("total == merged + closed_unmerged + open" if ok
                       else f"census mismatch: total {total} != sum {s} {parts}")}


def _attribution_detail(repo: str, number: int, merged_by: str | None) -> dict:
    full = _get(f"/repos/{repo}/pulls/{number}")
    out = {"merged_by": (full.get("merged_by") or {}).get("login") or merged_by,
           "author_association": full.get("author_association"), "body": (full.get("body") or "")[:2000],
           "head_ref": (full.get("head") or {}).get("ref")}
    m = (out["merged_by"] or "").lower()
    assoc = None
    for path in (f"/repos/{repo}/pulls/{number}/reviews?per_page=100", f"/repos/{repo}/issues/{number}/comments?per_page=100"):
        try:
            for ev in _get(path):
                if ((ev.get("user") or {}).get("login") or "").lower() == m and ev.get("author_association"):
                    assoc = ev["author_association"]
        except Exception:
            pass
        if assoc:
            break
    out["merger_association"] = assoc
    return out


def live_census_checked(author: str = AUTHOR) -> tuple[list[dict], dict]:
    out, seen, parts = [], set(), {}
    base = f"is:pr author:{author} -user:{author}"
    _, total = search_all(base)
    for name, qual in (("merged", "is:merged"), ("closed_unmerged", "is:closed is:unmerged"), ("open", "is:open")):
        items, t = search_all(f"is:pr {qual} author:{author} -user:{author}")
        parts[name] = t
        if len(items) != t:
            print(f"::warning::tribute-outcomes: {name} fetched {len(items)} != total_count {t}", file=sys.stderr)
        for it in items:
            url = it.get("html_url")
            if not url or url in seen:
                continue
            seen.add(url)
            parts_ = (it.get("repository_url") or "").rstrip("/").split("/")
            repo = f"{parts_[-2]}/{parts_[-1]}"
            pr = {"html_url": url, "repo": repo, "number": it.get("number"), "title": it.get("title"),
                  "state": it.get("state"), "created_at": it.get("created_at"), "closed_at": it.get("closed_at"),
                  "merged_at": (it.get("pull_request") or {}).get("merged_at"), "body": (it.get("body") or "")[:2000]}
            if pr["merged_at"]:
                try:
                    pr.update({k: v for k, v in _attribution_detail(repo, it["number"], None).items() if v is not None})
                    pr["files"] = [{"filename": f.get("filename"), "additions": f.get("additions")}
                                   for f in _get(f"/repos/{repo}/pulls/{it['number']}/files?per_page=100")]
                except Exception as e:  # keep the title heuristic on a read error
                    print(f"::warning::tribute-outcomes: detail read failed for {url}: {e}", file=sys.stderr)
            out.append(pr)
    chk = census_assert(total, parts)
    chk["fetched"] = len(out)
    if chk["ok"] and len(out) != total:
        chk.update(ok=False, detail=f"fetched {len(out)} unique PRs != total {total}")
    return out, chk


def live_census(author: str = AUTHOR) -> list[dict]:
    return live_census_checked(author)[0]


def read_jsonl(paths: list[str]) -> list[dict]:
    rows = []
    for p in paths:
        for f in (sorted(Path(p).glob("*.jsonl")) if Path(p).is_dir() else [Path(p)]):
            if not f.exists():
                continue
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def merge_into(status_path: Path, rep: dict) -> None:
    """Add the honest outcome block to an existing status.json without touching other keys."""
    if not status_path.exists():
        return
    doc = json.loads(status_path.read_text(encoding="utf-8"))
    slim = {k: v for k, v in rep.items() if k != "prs"}
    doc["outcome_slo"] = slim
    W = rep["windows"][f"{rep['window_days']}d"]
    doc["tribute_outcomes"] = {
        "status": rep["slo"]["status"],
        "window_days": rep["window_days"],
        "merged_real": W["real_merges"],
        "merged_stake_only": W["stake_only_merges"],
        "closed_unmerged": W["closed_unmerged"],
        "open": rep["totals"]["open"],
        "yielded": rep["system1"]["yielded"],
        "retired": rep["system1"]["retired"],
        "outcome_failures": rep["slo"]["outcome_failures"],
        "real_merge_rate": W["real_merge_rate"],
        "days_since_real_merge": rep["days_since_real_merge"],
    }
    if rep.get("slo_primary"):
        P = rep["slo_primary"]
        doc["tribute_outcomes"].update({
            "status_windowed": rep["slo"]["status"],
            "status": P["status"],
            "status_basis": P["basis"],
            "activity_state": P["activity_state"],
            "corpus_real_merges": P["corpus"]["real_merges"],
            "corpus_real_merges_lane": P["corpus"]["real_merges_lane"],
            "corpus_decided": P["corpus"]["decided"],
            "corpus_real_merge_rate": P["corpus"]["real_merge_rate"],
            "active_attempts_since_real": P["recency"]["active_attempts_since_real"],
        })
    doc["outcome_semantics"] = ("actioned/skipped/failed are operational receipt states; "
                                "tribute_outcomes/outcome_slo are the honest merge outcomes")
    status_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def check(rep: dict) -> int:
    """Gate on the primary (whole-corpus, activity-aware) SLO when present; windowed SLO otherwise."""
    s = rep.get("slo_primary") or rep["slo"]
    cc = rep.get("census_check") or {}
    if cc and not cc.get("ok", True):
        print(f"::error title=Tribute census incomplete::{cc.get('detail')}")
    for f in s["failures"]:
        print(f"::error title=Tribute outcome SLO FAIL::{f['code']}: {f['detail']}")
    for w in s["warnings"]:
        print(f"::warning title=Tribute outcome SLO::{w['code']}: {w['detail']}")
    return 1 if s["status"] == "FAIL" or (cc and not cc.get("ok", True)) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Honest Tribute outcome census + SLO")
    ap.add_argument("--census", default="", help="offline census JSON (list of PR dicts)")
    ap.add_argument("--decisions", nargs="*", default=[], help="System 1 decisions JSONL file(s)/dir(s)")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--min-rate", type=float, default=0.10)
    ap.add_argument("--min-decided", type=int, default=10)
    ap.add_argument("--max-drought-days", type=int, default=21)
    ap.add_argument("--now", default="")
    ap.add_argument("--out", default="docs/ops/generated/tribute-outcomes.json")
    ap.add_argument("--dashboard", default="apps/tribute-dashboard/data/tribute-outcomes.json")
    ap.add_argument("--md", default="docs/ops/generated/tribute-outcomes.md")
    ap.add_argument("--merge-into", action="append", default=[])
    ap.add_argument("--summary", default="")
    ap.add_argument("--check", action="store_true", help="exit 1 when the SLO status is FAIL")
    ap.add_argument("--check-file", default="", help="only read an existing report and gate on it")
    a = ap.parse_args(argv)
    if a.check_file:
        rep = json.loads(Path(a.check_file).read_text(encoding="utf-8"))
        md = markdown(rep)
        print(md)
        if a.summary:
            with open(a.summary, "a", encoding="utf-8") as fh:
                fh.write(md)
        return check(rep)
    now = _ts(a.now) or datetime.now(timezone.utc)
    if a.census:
        prs, source = json.loads(Path(a.census).read_text(encoding="utf-8")), f"census:{a.census}"
    else:
        prs, source = None, "live:search-api"
    census_check = None
    if prs is None:
        prs, census_check = live_census_checked()
    rep = build(prs, now, a.window, read_jsonl(a.decisions), a.min_rate, a.min_decided, a.max_drought_days, source=source,
                census_check=census_check)
    text = json.dumps(rep, indent=1) + "\n"
    for p in (a.out, a.dashboard):
        if p:
            Path(p).parent.mkdir(parents=True, exist_ok=True)
            Path(p).write_text(text, encoding="utf-8")
    md = markdown(rep)
    if a.md:
        Path(a.md).write_text(md, encoding="utf-8")
    for p in a.merge_into:
        merge_into(Path(p), rep)
    print(md)
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(md)
    return check(rep) if a.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
