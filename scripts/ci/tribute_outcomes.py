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
        if (pr.get("merged_by") or "").lower() == author.lower():
            return "self_merge"
        files = pr.get("files")
        if files is not None:
            return "stake_merge" if is_stake_diff(files) else "real_merge"
        return "stake_merge" if STAKE_TITLE.search(pr.get("title") or "") else "real_merge"
    if state == "closed":
        return "closed_unmerged"
    return "open"


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
          author: str = AUTHOR, source: str = "live") -> dict:
    rows = []
    for pr in prs:
        cls = classify(pr, author)
        rows.append({"url": pr.get("html_url"), "repo": pr.get("repo"), "title": (pr.get("title") or "")[:120],
                     "class": cls, "at": _iso(outcome_time(pr, cls)), "weight": {"real_merge": 1.0}.get(cls, 0.0)
                     if cls != "closed_unmerged" else -1.0})
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


def live_census(author: str = AUTHOR) -> list[dict]:
    out, seen = [], set()
    for qual in ("is:merged", "is:closed is:unmerged", "is:open"):
        q = f"is:pr {qual} author:{author} -user:{author}"
        for page in range(1, 11):
            data = _get(f"/search/issues?q={urllib.parse.quote(q)}&per_page=100&page={page}&sort=created&order=asc")
            items = data.get("items") or []
            for it in items:
                url = it.get("html_url")
                if not url or url in seen:
                    continue
                seen.add(url)
                parts = (it.get("repository_url") or "").rstrip("/").split("/")
                repo = f"{parts[-2]}/{parts[-1]}"
                pr = {"html_url": url, "repo": repo, "number": it.get("number"), "title": it.get("title"),
                      "state": it.get("state"), "created_at": it.get("created_at"), "closed_at": it.get("closed_at"),
                      "merged_at": (it.get("pull_request") or {}).get("merged_at")}
                if pr["merged_at"]:
                    try:
                        full = _get(f"/repos/{repo}/pulls/{it['number']}")
                        pr["merged_by"] = (full.get("merged_by") or {}).get("login")
                        pr["files"] = [{"filename": f.get("filename"), "additions": f.get("additions")}
                                       for f in _get(f"/repos/{repo}/pulls/{it['number']}/files?per_page=100")]
                    except Exception as e:  # keep the title heuristic on a read error
                        print(f"::warning::tribute-outcomes: detail read failed for {url}: {e}", file=sys.stderr)
                out.append(pr)
            if len(items) < 100:
                break
    return out


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
    doc["outcome_semantics"] = ("actioned/skipped/failed are operational receipt states; "
                                "tribute_outcomes/outcome_slo are the honest merge outcomes")
    status_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def check(rep: dict) -> int:
    for f in rep["slo"]["failures"]:
        print(f"::error title=Tribute outcome SLO FAIL::{f['code']}: {f['detail']}")
    for w in rep["slo"]["warnings"]:
        print(f"::warning title=Tribute outcome SLO::{w['code']}: {w['detail']}")
    return 1 if rep["slo"]["status"] == "FAIL" else 0


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
        prs, source = live_census(), "live:search-api"
    rep = build(prs, now, a.window, read_jsonl(a.decisions), a.min_rate, a.min_decided, a.max_drought_days, source=source)
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
