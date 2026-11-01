#!/usr/bin/env python3
"""Repo-org tracking surface — ONE board: lane x project x state x last-merge x next.

Builds ON the existing systems, replaces none of them (contract:
docs/ops/REPO-TRACKING.md):

  records of record (read, never written here)
    ops/challenge/coordinator.json   challenge events, deadlines, submissions
    ops/challenge/desk-feed.json     desk traversals: status, evidence, next
    ops/quota/registry.json          provider/quota services of record
    experiments/doe/*/DESIGN.json    DoE campaigns of record
  stamped observation snapshots (the collector never calls the network;
  fetch_snapshots.py refreshes them in the workflow, stamped with read_at,
  exactly like scripts/dashboards/*_observation.json)
    scripts/tracking/pr_feed_snapshot.json      GitHub PR API read
    scripts/tracking/lane_events_snapshot.json  Neon lane_events read
  seed registry (identity + match rules only — no state)
    ops/tracking/projects.json

Outputs (single-writer = .github/workflows/repo-tracking-collect.yml):
  ops/tracking/tracking.json                       canonical feed
  ops/tracking/tracking.md                         human board (ops doc surface)
  apps/help-wanted-dashboard/data/tracking-feed.json  desk/viz render copy

Honesty rules (surface-feeds pattern): a value no source holds is emitted
as NOT_ESTABLISHED / a named gap, never synthesized. `next` is derived in
a fixed priority order (record next > deadline > open PR > lane-event
failure > NOT_ESTABLISHED); it is never free-hand prose.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "repo-tracking/v1"
NOT_ESTABLISHED = "NOT_ESTABLISHED"

STATE_ENUM = ("landed", "in-flight", "active", "blocked", "quiet", "stale", "closed", "unknown")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(s):
    if not s or s == NOT_ESTABLISHED:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def _read_json(rel, default=None):
    p = ROOT / rel
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def classify(text: str, projects: list[dict]) -> dict | None:
    """First seed project whose any match token appears in text (lowercased).

    Order in projects.json is load-bearing: specific projects (d1, nc-1)
    precede generic domain buckets (doe-campaigns, providers-registry).
    """
    t = (text or "").lower()
    for proj in projects:
        for tok in proj.get("match", []):
            if tok.lower() in t:
                return proj
    return None


def pr_text(pr: dict) -> str:
    labels = " ".join((l.get("name", "") if isinstance(l, dict) else str(l)) for l in pr.get("labels", []))
    head = (pr.get("head") or {}).get("ref", "") if isinstance(pr.get("head"), dict) else pr.get("head_ref", "")
    return f"{pr.get('title','')} {head} {labels}"


def derive_state(record_state, open_prs, last_merge_at, lane_failures, now):
    """Deterministic state. Record terminal states win; then open work;
    then recency of last merge; lane-event failures alone never block —
    they surface as evidence/next, not state (a red workflow != blocked lane).
    """
    rs = (record_state or "").lower()
    if rs in ("landed", "done", "complete", "completed", "submitted"):
        base = "landed"
    elif rs in ("closed", "abandoned", "superseded"):
        base = "closed"
    elif rs in ("blocked",):
        base = "blocked"
    else:
        base = None
    if base in ("landed", "closed", "blocked"):
        return base
    if open_prs:
        return "in-flight"
    if last_merge_at:
        age = (now - last_merge_at).total_seconds() / 86400.0
        if age <= 14:
            return "active"
        if age <= 45:
            return "quiet"
        return "stale"
    if base:
        return base
    return "unknown"


def derive_next(record_next, deadline, open_prs, lane_failures):
    """Fixed priority; returns (next_text, basis)."""
    if record_next:
        return record_next, "record"
    if deadline:
        return f"deadline {deadline}", "record-deadline"
    if open_prs:
        p = open_prs[0]
        return f"land/close PR #{p.get('number')} — {p.get('title','')}", "open-pr"
    if lane_failures:
        f = lane_failures[0]
        return (f"investigate lane-event failure: {f.get('workflow')} "
                f"{f.get('occurred_at')}"), "lane-events"
    return NOT_ESTABLISHED, "none"


def build(now=None) -> dict:
    now = now or _now()
    gaps: list[str] = []
    projects_seed = _read_json("ops/tracking/projects.json", {"projects": []})
    projects = projects_seed.get("projects", [])
    if not projects:
        gaps.append("ops/tracking/projects.json missing/empty: seed registry absent")

    pr_snap = _read_json("scripts/tracking/pr_feed_snapshot.json")
    if pr_snap is None:
        pr_snap = {"read_at": None, "merged": [], "open": []}
        gaps.append("pr_feed_snapshot missing: last-merge/open state NOT_ESTABLISHED")
    elif pr_snap.get("status") not in (None, "ok"):
        gaps.append(f"pr feed source status={pr_snap.get('status')}: "
                    "last-merge/open state NOT_ESTABLISHED this run")
    lane_snap = _read_json("scripts/tracking/lane_events_snapshot.json")
    if lane_snap is None:
        lane_snap = {"read_at": None, "status": "missing", "events": [], "count": None}
        gaps.append("lane_events_snapshot missing: Neon lane-events NOT_ESTABLISHED")
    elif lane_snap.get("status") != "ok":
        gaps.append(f"lane-events source status={lane_snap.get('status')}: "
                    "events contribute no evidence this run")

    merged = pr_snap.get("merged", [])
    open_prs = pr_snap.get("open", [])

    # ---- record-derived facts per seed project -------------------------
    record: dict[str, dict] = {}  # id -> {state, next, deadline, evidence[]}

    coord = _read_json("ops/challenge/coordinator.json")
    if coord is None:
        gaps.append("coordinator.json unreadable: challenge record state absent")
    else:
        for ev in coord.get("events", []):
            eid = (ev.get("id") or "").lower()
            proj = classify(eid + " " + (ev.get("name") or ""), projects)
            if not proj:
                continue
            r = record.setdefault(proj["id"], {"evidence": []})
            r["state"] = ev.get("status")
            dl = ((ev.get("dates") or {}).get("deadline") or {})
            if isinstance(dl, dict) and dl.get("at"):
                r["deadline"] = dl["at"]
            sub = (ev.get("submission") or {}).get("state")
            if sub:
                r["evidence"].append(f"coordinator submission={sub}")
            r["evidence"].append(f"coordinator event {ev.get('id')} status={ev.get('status')}")

    desk = _read_json("ops/challenge/desk-feed.json")
    if desk is None:
        gaps.append("desk-feed.json unreadable: desk traversal state absent")
    else:
        r = record.setdefault("desk", {"evidence": []})
        r["evidence"].append(f"desk-feed traversals={len(desk.get('traversals', []))} "
                             f"generated_at={desk.get('generated_at')}")
        for tr in desk.get("traversals", []):
            proj = classify(f"{tr.get('entry','')} {tr.get('project','')}", projects)
            if not proj:
                continue
            r = record.setdefault(proj["id"], {"evidence": []})
            r.setdefault("state", tr.get("status"))
            if tr.get("next"):
                r["next"] = tr["next"]
            evd = tr.get("evidence") or {}
            if evd.get("pr"):
                r["evidence"].append(f"desk-feed traversal {tr.get('entry')} pr=#{evd['pr']}")

    registry = _read_json("ops/quota/registry.json")
    if registry is not None:
        n = len(registry.get("services", []))
        r = record.setdefault("providers-registry", {"evidence": []})
        r["evidence"].append(f"quota registry services={n}")
        r2 = record.setdefault("quota-system", {"evidence": []})
        r2["evidence"].append(f"quota registry services={n}")

    doe_designs = 0
    for p in sorted((ROOT / "experiments" / "doe").glob("*/DESIGN.json")) if (ROOT / "experiments" / "doe").exists() else []:
        doe_designs += 1
    if doe_designs:
        r = record.setdefault("doe-campaigns", {"evidence": []})
        r["evidence"].append(f"doe DESIGN.json campaigns={doe_designs}")

    # ---- PR + lane-event evidence per project --------------------------
    by_proj_merged: dict[str, list] = {}
    by_proj_open: dict[str, list] = {}
    unclassified_merged = 0
    for pr in merged:
        proj = classify(pr_text(pr), projects)
        if not proj:
            unclassified_merged += 1
            continue
        by_proj_merged.setdefault(proj["id"], []).append(pr)
    for pr in open_prs:
        proj = classify(pr_text(pr), projects)
        if proj:
            by_proj_open.setdefault(proj["id"], []).append(pr)
    if unclassified_merged:
        gaps.append(f"merged PRs unclassified by seed match rules: {unclassified_merged}/"
                    f"{len(merged)} (extend ops/tracking/projects.json match rules)")

    lane_events = lane_snap.get("events", []) if lane_snap.get("status") == "ok" else []
    failures_by_lane: dict[str, list] = {}
    latest_by_lane: dict[str, dict] = {}
    for ev in lane_events:
        lane = ev.get("lane") or ""
        if lane and lane not in latest_by_lane:
            latest_by_lane[lane] = ev
        if (ev.get("conclusion") or "").lower() == "failure":
            failures_by_lane.setdefault(lane, []).append(ev)

    # ---- rows ----------------------------------------------------------
    rows = []
    seen_ids = set()
    for proj in projects:
        pid = proj["id"]
        seen_ids.add(pid)
        r = record.get(pid, {})
        m = sorted(by_proj_merged.get(pid, []),
                   key=lambda x: x.get("merged_at") or "", reverse=True)
        o = sorted(by_proj_open.get(pid, []),
                   key=lambda x: x.get("updated_at") or "", reverse=True)
        last = None
        last_at = None
        if m:
            top = m[0]
            last_at = _parse_ts(top.get("merged_at"))
            last = {"pr": top.get("number"), "sha": (top.get("merge_commit_sha") or "")[:12] or None,
                    "at": top.get("merged_at"), "title": top.get("title")}
        le = latest_by_lane.get(proj["lane"])
        evidence = list(r.get("evidence", []))
        if le:
            evidence.append(f"lane-events latest: {le.get('workflow')} "
                            f"{le.get('event_type')} {le.get('conclusion')} @{le.get('occurred_at')}")
        if o:
            evidence.append(f"open PRs: {', '.join('#'+str(x.get('number')) for x in o[:5])}")
        state = derive_state(r.get("state"), o, last_at,
                             failures_by_lane.get(proj["lane"], []), now)
        nxt, basis = derive_next(r.get("next"), r.get("deadline"), o,
                                 failures_by_lane.get(proj["lane"], []))
        rows.append({
            "lane": proj["lane"], "project": proj["project"], "domain": proj["domain"],
            "project_id": pid, "state": state,
            "last_merge": last, "next": nxt, "next_basis": basis,
            "evidence": evidence, "updated_at": _iso(now),
        })

    # unseeded domains present in PR feed still surface as gaps, not rows:
    # a row without a seed project has no lane of record (honesty rule).

    by_domain, by_state = {}, {}
    for row in rows:
        by_domain[row["domain"]] = by_domain.get(row["domain"], 0) + 1
        by_state[row["state"]] = by_state.get(row["state"], 0) + 1

    return {
        "schema": SCHEMA,
        "generated_at": _iso(now),
        "generated_by": "scripts/tracking/repo_tracking.py via repo-tracking-collect.yml (single-writer)",
        "sources": {
            "pr_feed": {"read_at": pr_snap.get("read_at"), "merged": len(merged), "open": len(open_prs)},
            "lane_events": {"read_at": lane_snap.get("read_at"), "status": lane_snap.get("status"),
                            "count": lane_snap.get("count"), "events_in_snapshot": len(lane_events)},
            "records": ["ops/challenge/coordinator.json", "ops/challenge/desk-feed.json",
                        "ops/quota/registry.json", "experiments/doe/*/DESIGN.json",
                        "ops/tracking/projects.json (seed: identity+match only)"],
        },
        "honesty_rules": [
            "State/last-merge/next are derived at generation time from the stamped snapshots + records; never copied forward, never hand-edited in the outputs.",
            "A value no source holds renders as NOT_ESTABLISHED or a named gap, never synthesized.",
            "lane-events failures are evidence/next hints, never a state by themselves.",
        ],
        "summary": {"rows": len(rows), "by_domain": by_domain, "by_state": by_state},
        "rows": rows,
        "gaps": gaps,
    }


def render_md(feed: dict) -> str:
    lines = [
        "# Repo tracking — lane × project × state × last-merge × next",
        "",
        f"Generated: `{feed['generated_at']}` · schema `{feed['schema']}` · "
        "single-writer: `repo-tracking-collect.yml` — **do not hand-edit** "
        "(contract: [REPO-TRACKING.md](../../docs/ops/REPO-TRACKING.md))",
        "",
        f"Sources: PR feed read_at=`{feed['sources']['pr_feed']['read_at']}` "
        f"(merged {feed['sources']['pr_feed']['merged']} · open {feed['sources']['pr_feed']['open']}) · "
        f"lane-events(Neon) status=`{feed['sources']['lane_events']['status']}` "
        f"count=`{feed['sources']['lane_events']['count']}` read_at=`{feed['sources']['lane_events']['read_at']}`",
        "",
        f"Rows: {feed['summary']['rows']} · by_state: "
        + " · ".join(f"{k}={v}" for k, v in sorted(feed['summary']['by_state'].items())),
        "",
        "| domain | lane | project | state | last-merge | next |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(feed["rows"], key=lambda x: (x["domain"], x["lane"], x["project"])):
        lm = r["last_merge"]
        lm_s = f"#{lm['pr']} `{lm['sha']}` {lm['at']}" if lm else NOT_ESTABLISHED
        nxt = str(r["next"]).replace("|", "/")
        lines.append(f"| {r['domain']} | `{r['lane']}` | {r['project']} | {r['state']} | {lm_s} | {nxt} |")
    if feed["gaps"]:
        lines += ["", "## Gaps (named, never synthesized)", ""]
        lines += [f"- {g}" for g in feed["gaps"]]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build in memory only, print summary")
    ns = ap.parse_args()
    feed = build()
    if ns.check:
        print(json.dumps(feed["summary"], indent=1))
        print("gaps:", len(feed["gaps"]))
        return 0
    (ROOT / "ops" / "tracking").mkdir(parents=True, exist_ok=True)
    out = json.dumps(feed, indent=1, sort_keys=False) + "\n"
    (ROOT / "ops" / "tracking" / "tracking.json").write_text(out)
    (ROOT / "ops" / "tracking" / "tracking.md").write_text(render_md(feed))
    dash = ROOT / "apps" / "help-wanted-dashboard" / "data"
    dash.mkdir(parents=True, exist_ok=True)
    (dash / "tracking-feed.json").write_text(out)
    print(f"tracking: rows={feed['summary']['rows']} gaps={len(feed['gaps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
