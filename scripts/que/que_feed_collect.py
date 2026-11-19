#!/usr/bin/env python3
"""QUE feed collector — the producer for the desk surface.

One cycle:
  1. census the Actions queue (queued + in_progress + the
     latest completed page) through the REST API;
  2. classify every run by QUE tier (dispatch-tiers.json:
     first pattern match wins on the workflow name,
     case-insensitive substring; default tier 4);
  3. write the desk feeds under ops/que/feeds/:
       queue-by-tier.json    (que.queue-by-tier/v1)
       priority-windows.json (que.priority-windows/v1)
       governor.json         (que.governor/v1)
  4. diff the census against the previous cycle's state and
     append transition events to ops/que/events/<day>.jsonl
     — the T1 measurement plane; repo snapshots are the
     store of record (QUE.md).

Stdlib only. Auth: GH_TOKEN env (the workflow mints a Termux
Fleet Swarm App installation token; the app identity is what
lets the feed commits trigger downstream consumers).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_ranking  # noqa: E402  (QUE #5283 ranking method of record)

REPO = "timerloggedout-spec/termux-monorepo"
API = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[2]
FEEDS = ROOT / "ops" / "que" / "feeds"
EVENTS = ROOT / "ops" / "que" / "events"
WEDGED_DAYS = 7
EXCLUSIONS = ROOT / "ops" / "queue" / "exclusions.json"
# Declared cadences for per-source freshness (#5546 gate 1):
# (path, cadence_min, tolerance_min, timestamp field). cadence None
# ⇒ UNVERIFIABLE (source-specific, ¬declared). Freshness of one
# source is never inferred from another that embeds it.
FRESHNESS_SOURCES = {
    "dispatch-state-feed": ("ops/challenge/dispatch-state-feed.json",
                            15, 15, "generated_at"),
    "stall-gap-feed": ("ops/que/feeds/stall-gap-feed.json", 15, 15,
                       "generated_at"),
    "opportunity-priority": ("ops/que/feeds/opportunity-priority.json",
                             720, 0, "generated_at"),
}
QF_CADENCE_MIN, QF_TOLERANCE_MIN = 10, 5


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)


def api(path: str, token: str) -> dict:
    req = urllib.request.Request(API + path, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def census(token: str, status: str, pages: int) -> list[dict]:
    out = []
    for page in range(1, pages + 1):
        data = api(f"/repos/{REPO}/actions/runs?status={status}"
                   f"&per_page=100&page={page}", token)
        runs = data.get("workflow_runs", [])
        out.extend(runs)
        if len(runs) < 100:
            break
    return out


def load_tiers() -> dict:
    return json.loads(
        (ROOT / "ops" / "quota" / "dispatch-tiers.json").read_text())


def classify(workflow_name: str, tiers_doc: dict) -> int:
    """First pattern match wins (tiers in declared order);
    default tier 4 — mirrors queue.dispatch-tiers/v2."""
    name = (workflow_name or "").lower()
    for tier in tiers_doc.get("tiers", []):
        for pat in tier.get("patterns") or []:
            if pat.lower() in name:
                return int(tier["tier"])
    return 4


def classify_basis(workflow_name: str, tiers_doc: dict) -> str:
    """#5546 L6: explicit (a pattern matched) | default-T4 (named
    run, ∅ pattern ⇒ default tier 4) | unmatched (∅ workflow name ⇒
    unclassifiable)."""
    name = (workflow_name or "").strip().lower()
    if not name:
        return "unmatched"
    for tier in tiers_doc.get("tiers", []):
        for pat in tier.get("patterns") or []:
            if pat.lower() in name:
                return "explicit"
    return "default-T4"


def tier_basis(queued, in_progress, tiers_doc, wedged_n, excluded_n=0):
    """Actions-run population only (¬combined with dispatch issues)."""
    out = {"population": "actions-runs (queued ∧ in_progress)",
           "explicit": {"1": 0, "2": 0, "3": 0, "4": 0},
           "explicit_total": 0, "default_t4": 0, "unmatched": 0,
           "ancient_excluded": wedged_n,
           "operator_excluded": excluded_n}
    for run in list(queued) + list(in_progress):
        basis = classify_basis(run.get("name"), tiers_doc)
        if basis == "explicit":
            out["explicit"][str(classify(run["name"], tiers_doc))] += 1
            out["explicit_total"] += 1
        elif basis == "default-T4":
            out["default_t4"] += 1
        else:
            out["unmatched"] += 1
    return out


def load_exclusions(path: Path | None = None) -> dict:
    """{run_id: row} under permanent exclusion (queue.exclusions/v1)."""
    p = path or EXCLUSIONS
    try:
        doc = json.loads(p.read_text())
    except (OSError, ValueError):
        return {}
    return {int(r["run_id"]): r for r in doc.get("runs", [])
            if r.get("run_id")}


def split_excluded(runs, excluded):
    keep, dropped = [], []
    for run in runs:
        (dropped if run.get("id") in excluded else keep).append(run)
    return keep, dropped


def _age_min(ts, at):
    when = task_ranking.parse_iso(ts) if isinstance(ts, str) else None
    if when is None:
        return None
    return round((at - when).total_seconds() / 60.0, 1)


def _health(age, cadence, tol):
    if age is None:
        return "UNVERIFIABLE"
    if cadence is None:
        return "UNVERIFIABLE"
    return "FRESH" if age <= cadence + tol else "STALE"


def source_freshness(at, prev_watermark=None, root: Path | None = None):
    """que.source-freshness/v1 (#5546 gate 1): F(x) per source.
    HEALTH(x) := FRESH iff age ≤ cadence + tolerance; else STALE |
    MISSING | UNVERIFIABLE."""
    base = root or ROOT
    sha = os.environ.get("GITHUB_SHA")
    run_id = os.environ.get("GITHUB_RUN_ID")
    gap = _age_min(prev_watermark, at)
    sources = {"que-feed-collect": {
        "source_ref": "ops/que/feeds/que-queue-feed.json",
        "generated_at": iso(at), "observed_at": iso(at),
        "expected_cadence_min": QF_CADENCE_MIN,
        "tolerance_min": QF_TOLERANCE_MIN,
        "previous_cycle_at": prev_watermark,
        "cycle_gap_min": gap,
        "health": _health(gap, QF_CADENCE_MIN, QF_TOLERANCE_MIN)
        if gap is not None else "UNVERIFIABLE",
        "health_basis": "gap since previous cycle watermark",
        "sha": sha, "run_id": run_id}}
    for key, (rel, cadence, tol, field) in FRESHNESS_SOURCES.items():
        path = base / rel
        rec = {"source_ref": rel, "observed_at": iso(at),
               "expected_cadence_min": cadence, "tolerance_min": tol,
               "sha": sha}
        if not path.exists():
            rec.update({"generated_at": None, "age_min": None,
                        "health": "MISSING"})
        else:
            try:
                ts = json.loads(path.read_text()).get(field)
            except ValueError:
                ts = None
            age = _age_min(ts, at)
            rec.update({"generated_at": ts, "age_min": age,
                        "health": _health(age, cadence, tol)})
        sources[key] = rec
    latest = None
    for b in sorted((base / "ops" / "que" / "events").glob(
            "governor-events-*.jsonl")):
        for line in b.read_text().splitlines():
            try:
                ts = json.loads(line).get("ts") if line.strip() else None
            except ValueError:
                ts = None
            when = task_ranking.parse_iso(ts) if ts else None
            if when and (latest is None or when > latest):
                latest = when
    sources["governor-events"] = {
        "source_ref": "ops/que/events/governor-events-*.jsonl",
        "observed_at": iso(at),
        "generated_at": iso(latest) if latest else None,
        "age_min": _age_min(iso(latest), at) if latest else None,
        "expected_cadence_min": None, "tolerance_min": None,
        "health": "UNVERIFIABLE" if latest else "MISSING",
        "health_basis": "emitter cadence ¬declared (source-specific)",
        "sha": sha}
    counts = {}
    for rec in sources.values():
        counts[rec["health"]] = counts.get(rec["health"], 0) + 1
    return {"schema": "que.source-freshness/v1", "generated_at": iso(at),
            "rule": "FRESH iff age ≤ cadence + tolerance; freshness(x) "
                    "¬inferred from freshness(y)",
            "counts": counts, "sources": sources}


CLAIM_UNMATCHED_ENTRIES = (None, "", "Other")


def claim_tier_basis(row: dict) -> str:
    """Dispatch-issue population (¬combined with Actions runs):
    unmatched (∅ registry entry resolves) | default (entry named,
    ∅ timebox ⇒ BASE default: tier index 0 ∧ ∅ nearest_wall) |
    explicit (timebox-derived tier). Rule inferred from the
    watchdog's feed_row fields."""
    if row.get("entry") in CLAIM_UNMATCHED_ENTRIES:
        return "unmatched"
    tier = row.get("tier") or {}
    if not tier or ((tier.get("index") or 0) == 0
                    and not row.get("nearest_wall")):
        return "default"
    return "explicit"


def tier_feed(queued, in_progress, tiers_doc, at):
    tiers = {str(i): {"tier": i, "queued": 0, "in_progress": 0,
                      "oldest_queued_at": None,
                      "by_workflow_queued": {}}
             for i in (1, 2, 3, 4)}
    wedged, unmapped = [], []
    cutoff = at - timedelta(days=WEDGED_DAYS)
    for run in queued:
        created = parse_iso(run["created_at"])
        rec = {"id": run["id"], "workflow": run["name"],
               "created_at": run["created_at"],
               "url": run["html_url"]}
        if created < cutoff:
            wedged.append(rec)
            continue
        t = tiers[str(classify(run["name"], tiers_doc))]
        t["queued"] += 1
        t["by_workflow_queued"][run["name"]] = \
            t["by_workflow_queued"].get(run["name"], 0) + 1
        if t["oldest_queued_at"] is None or \
                run["created_at"] < t["oldest_queued_at"]:
            t["oldest_queued_at"] = run["created_at"]
    for run in in_progress:
        tiers[str(classify(run["name"], tiers_doc))]["in_progress"] += 1
    return {"schema": "que.queue-by-tier/v1", "generated_at": iso(at),
            "repo": REPO, "tiers": tiers,
            "totals": {"queued": sum(t["queued"] for t in tiers.values()),
                       "in_progress": sum(t["in_progress"]
                                          for t in tiers.values())},
            "wedged_ancient": wedged,
            "wedged_excluded_from_counts": True,
            "tier_basis": tier_basis(
                [r for r in queued if parse_iso(r["created_at"]) >= cutoff],
                in_progress, tiers_doc, len(wedged))}


def priority_feed(tiers_doc, at):
    stanza = tiers_doc.get("priority_window")
    if not stanza:
        return {"schema": "que.priority-windows/v1",
                "generated_at": iso(at), "windows": [],
                "source": "ops/quota/dispatch-tiers.json carries no "
                          "priority_window stanza yet (PR #4740)"}
    windows = []
    for w in stanza if isinstance(stanza, list) else [stanza]:
        until = w.get("until")
        state = "unknown"
        if until:
            state = "active" if parse_iso(until) > at else "closed"
        windows.append({**w, "state": state})
    return {"schema": "que.priority-windows/v1",
            "generated_at": iso(at), "windows": windows,
            "source": "ops/quota/dispatch-tiers.json priority_window"}


def queue_feed(queued, in_progress, tiers_doc, at):
    """que-queue-feed/v1 — the producer-of-record feed for the
    Desk surface (Desk-upgrade LEG 1): run-queue state by tier
    + dispatch claims (the measurement plane's record), folded
    live at publish from the dispatch machinery's own feed.
    Published as a byte-identical pair: canonical
    ops/que/feeds/que-queue-feed.json + the dashboard mirror."""
    body = tier_feed(queued, in_progress, tiers_doc, at)
    claims = {"source": "ops/challenge/dispatch-state-feed.json",
              "source_schema": None, "source_generated_at": None,
              "counts": {}, "active_claims": [], "ranking": None}
    src = ROOT / "ops" / "challenge" / "dispatch-state-feed.json"
    if src.exists():
        d = json.loads(src.read_text())
        claims["source_schema"] = d.get("schema")
        claims["source_generated_at"] = d.get("generated_at")
        claims["counts"] = d.get("counts", {})
        # QUE #5283: fold the ranking through (score + rank per claim,
        # claim order + delta from the producer's ranking block).
        # A pre-#5283 source feed carries no ranking: re-derive it
        # from the rows under the same method so the fold never
        # publishes an unranked cycle.
        ranking = d.get("ranking")
        rows = d.get("dispatches", [])
        # 2026-11-18 fix: the re-derive path ranked a copy ∧ folded the
        # raw rows ⇒ 17 claims ∧ 0 scored. Fold the annotated rows
        # whenever any row lacks a numeric score.
        score_basis = "producer"
        if rows and (ranking is None or any(
                not isinstance(r.get("score"), (int, float))
                for r in rows)):
            rows, derived = task_ranking.rank_dispatches(rows)
            ranking = ranking or derived
            score_basis = "fold-derived (que-task-rank/v1)"
        claims["ranking"] = ranking
        claims["score_basis"] = score_basis
        basis_counts = {"explicit": 0, "default": 0, "unmatched": 0}
        for disp in rows:
            if disp.get("claim"):
                basis = claim_tier_basis(disp)
                basis_counts[basis] += 1
                claims["active_claims"].append({
                    "issue": disp.get("issue"),
                    "entry": disp.get("entry"),
                    "title": disp.get("title"),
                    "state": disp.get("state"),
                    "score": disp.get("score"),
                    "score_components": disp.get("components"),
                    "rank": disp.get("rank"),
                    "rank_method": task_ranking.METHOD,
                    "tier": disp.get("tier"),
                    "tier_basis": basis,
                    "claim": disp["claim"]})
        claims["scored"] = sum(
            1 for c in claims["active_claims"]
            if isinstance(c.get("score"), (int, float)))
        claims["tier_basis"] = {
            "population": "dispatch-issues (active claims)",
            **basis_counts}
    return {"schema": "que-queue-feed/v1", "generated_at": iso(at),
            "provenance": {
                "producer": "optimizations-assurance (QUE lead) "
                            "via que-feed-collect",
                "design_input": "Stagefoil — the desk-flow "
                                "template brand (Registry "
                                "issuance PR #4817) — "
                                "agent-browser-clerk pattern "
                                "(D2 candidate B learnings); the "
                                "Desk as interactive-flow + "
                                "routing template, agent-operated",
                "cadence": "*/10 (que-feed-collect)"},
            "queue": {"tiers": body["tiers"],
                      "totals": body["totals"],
                      "wedged_ancient": body["wedged_ancient"],
                      "tier_basis": body["tier_basis"]},
            "dispatch_claims": claims}


def governor_feed(token, at):
    def search_count(q):
        data = api("/search/issues?q=" + urllib.parse.quote(q), token)
        return data.get("total_count")
    day = (at - timedelta(days=1)).strftime("%Y-%m-%d")
    deferred_24h = search_count(
        f"repo:{REPO} label:deferred-by-tier updated:>={day}")
    deferred_open = search_count(
        f"repo:{REPO} label:deferred-by-tier state:open")
    # FREEZE (Desk, 2026-11-04 — the governing note; the two
    # intervening rulings are VOID): the four-feed collector
    # design governs whole — this feed IS the governor plane
    # (admission census + flow-governor state). Cadence's leg
    # is the EMITTER only: que-governor-event/v1 batches land
    # at ops/que/events/governor-events-<date>.jsonl and fold
    # verbatim here; the first batch flips the state
    # NOT_ESTABLISHED → populated (leg ② completion, tracked
    # by the Desk). No seam note acts without FREEZE-LIFT.
    flow = {"state": "NOT_ESTABLISHED",
            "gap": "no governor-event batch has landed yet; "
                   "Cadence's T1 emitter drops "
                   "que-governor-event/v1 batches at "
                   "ops/que/events/governor-events-<date>.jsonl"}
    batches = sorted(EVENTS.glob("governor-events-*.jsonl"))
    if batches:
        total, by_kind, latest = 0, {}, None
        for b in batches:
            for line in b.read_text().splitlines():
                if not line.strip():
                    continue
                total += 1
                try:
                    e = json.loads(line)
                    kind = e.get("kind") or e.get("event") \
                        or "unspecified"
                    ts = e.get("ts")
                    if ts:
                        # batches mix offset forms (-08:00 and
                        # Z); compare instants, not strings
                        try:
                            inst = datetime.fromisoformat(
                                ts.replace("Z", "+00:00"))
                            if latest is None or inst > latest[0]:
                                latest = (inst, ts)
                        except ValueError:
                            pass
                except ValueError:
                    kind = "unparseable"
                by_kind[kind] = by_kind.get(kind, 0) + 1
        flow = {"state": "populated",
                "event_shape": "que-governor-event/v1 (folded "
                               "verbatim; counts only)",
                "batches": [b.name for b in batches],
                "events_total": total, "by_kind": by_kind,
                "latest_event_at": latest[1] if latest else None}
    return {
        "schema": "que.governor/v1", "generated_at": iso(at),
        "admission": {
            "thresholds": {"tier4_defers_at_queued": 400,
                           "tier3_defers_at_queued": 800,
                           "tiers_never_deferred": [1, 2]},
            "deferral_stamped_issues_24h": deferred_24h,
            "deferral_stamped_open": deferred_open,
            "source": "swarm-admission stamps (deferred-by-tier label)"},
        "flow_governor": flow}


def transitions(state, queued, in_progress, completed, tiers_doc, at):
    """Diff the census against the previous cycle state;
    returns (events, new_state)."""
    prev = state.get("active", {})
    current, events = {}, []

    def rec(run, status):
        return {"status": status, "workflow": run["name"],
                "tier": classify(run["name"], tiers_doc),
                "created_at": run["created_at"],
                "run_started_at": run.get("run_started_at")}

    def emit(kind, run_id, r, extra=None):
        e = {"at": iso(at), "run_id": run_id,
             "workflow": r["workflow"], "tier": r["tier"],
             "event": kind}
        if extra:
            e.update(extra)
        events.append(e)

    for run in queued:
        r = rec(run, "queued")
        current[str(run["id"])] = r
        if str(run["id"]) not in prev:
            emit("queued", run["id"], r)
    for run in in_progress:
        r = rec(run, "in_progress")
        current[str(run["id"])] = r
        p = prev.get(str(run["id"]))
        if p is None:
            emit("queued", run["id"], r)
            emit("started", run["id"], r, _wait(r))
        elif p["status"] == "queued":
            emit("started", run["id"], r, _wait(r))
    done_ids = set()
    for run in completed:
        rid = str(run["id"])
        done_ids.add(rid)
        if rid in prev or rid in current:
            r = rec(run, "completed")
            kind = "cancelled" if run.get("conclusion") == "cancelled" \
                else "completed"
            emit(kind, run["id"], r,
                 {"conclusion": run.get("conclusion")})
            current.pop(rid, None)
    for rid, p in prev.items():
        if rid not in current and rid not in done_ids:
            emit("vanished", int(rid), p,
                 {"note": "left the census without a completed "
                          "record (gap class for the ≤1% measure)"})
    return events, {"watermark": iso(at), "active": current}


def _wait(r):
    if r.get("run_started_at") and r.get("created_at"):
        s = (parse_iso(r["run_started_at"])
             - parse_iso(r["created_at"])).total_seconds()
        return {"queue_wait_s": int(s)}
    return {}


def mark_opportunity_staleness(at: datetime, feed_path: Path | None = None) -> bool | None:
    """Registry-feed freshness (2026-11-15): the opportunity-priority
    feed is regenerated by opportunity-cycle; this 10-minute producer
    only flips its `stale` flag once `fresh_until` passes, so a reader
    never trusts a >12h feed silently. Writes only on change."""
    path = feed_path or (FEEDS / "opportunity-priority.json")
    if not path.exists():
        return None
    try:
        doc = json.loads(path.read_text())
    except ValueError:
        return None
    try:
        until = doc.get("fresh_until")
        if until:
            until_dt = parse_iso(until)
        else:
            until_dt = parse_iso(doc["generated_at"]) + timedelta(
                hours=float(doc.get("stale_after_hours", 12)))
    except (KeyError, TypeError, ValueError):
        return None
    stale = at > until_dt
    if doc.get("stale") != stale:
        doc["stale"] = stale
        doc["stale_checked_at"] = iso(at)
        path.write_text(json.dumps(doc, indent=2) + "\n")
    return stale


def main() -> int:
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("GH_TOKEN required", file=sys.stderr)
        return 2
    at = now()
    tiers_doc = load_tiers()
    queued = census(token, "queued", 25)
    in_progress = census(token, "in_progress", 5)
    completed = census(token, "completed", 1)
    excluded = load_exclusions()
    queued, dropped_q = split_excluded(queued, excluded)
    in_progress, dropped_p = split_excluded(in_progress, excluded)
    operator_excluded = [{"id": r["id"], "workflow": r.get("name"),
                          "class": excluded[r["id"]].get("class")}
                         for r in dropped_q + dropped_p]
    FEEDS.mkdir(parents=True, exist_ok=True)
    EVENTS.mkdir(parents=True, exist_ok=True)
    dash = ROOT / "apps" / "tribute-dashboard" / "data"
    dash.mkdir(parents=True, exist_ok=True)

    def publish(name, obj, alias=None):
        """Canonical at ops/que/feeds/ + a byte-identical
        mirror in the dashboard data dir (the board seam,
        confirmed by the Desk 2026-11-04). Two feeds also
        mirror under a que- prefixed alias — the names the
        QUE page fetches (Desk gap report, #4824 section)."""
        data = json.dumps(obj, indent=1) + "\n"
        (FEEDS / name).write_text(data)
        (dash / name).write_text(data)
        if alias:
            (dash / alias).write_text(data)

    state_path = FEEDS / "state.json"
    state = json.loads(state_path.read_text()) \
        if state_path.exists() else {}
    freshness = source_freshness(at, state.get("watermark"))
    tf = tier_feed(queued, in_progress, tiers_doc, at)
    tf["operator_excluded"] = operator_excluded
    tf["tier_basis"]["operator_excluded"] = len(operator_excluded)
    publish("queue-by-tier.json", tf)
    qf = queue_feed(queued, in_progress, tiers_doc, at)
    qf["queue"]["operator_excluded"] = operator_excluded
    qf["queue"]["tier_basis"]["operator_excluded"] = len(operator_excluded)
    qf["source_freshness"] = freshness
    publish("que-queue-feed.json", qf)
    (FEEDS / "source-freshness.json").write_text(
        json.dumps(freshness, indent=1) + "\n")
    publish("priority-windows.json", priority_feed(tiers_doc, at),
            alias="que-priority-windows.json")
    publish("governor.json", governor_feed(token, at),
            alias="que-governor.json")
    # Excluded ghosts leave the differ state once, with an explicit
    # `excluded` event (¬ a false `vanished` gap row).
    excl_events = []
    for rid in [k for k in state.get("active", {}) if int(k) in excluded]:
        p = state["active"].pop(rid)
        excl_events.append({"at": iso(at), "run_id": int(rid),
                            "workflow": p.get("workflow"),
                            "tier": p.get("tier"), "event": "excluded",
                            "note": "ops/queue/exclusions.json"})
    events, new_state = transitions(
        state, queued, in_progress, completed, tiers_doc, at)
    events = excl_events + events
    if events:
        day_file = EVENTS / f"{at.strftime('%Y-%m-%d')}.jsonl"
        with day_file.open("a") as fh:
            for e in events:
                fh.write(json.dumps(e) + "\n")
    state_path.write_text(json.dumps(new_state, indent=1) + "\n")
    opp_stale = mark_opportunity_staleness(at)
    if opp_stale:
        print("::warning title=opportunity-priority::stale (>12h) — opportunity-cycle overdue")
    stale = [k for k, v in freshness["sources"].items()
             if v["health"] in ("STALE", "MISSING")]
    for k in stale:
        print(f"::warning title=que-freshness::{k} "
              f"{freshness['sources'][k]['health']}")
    print(f"cycle ok: queued={len(queued)} "
          f"in_progress={len(in_progress)} events={len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
