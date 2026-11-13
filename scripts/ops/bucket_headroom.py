#!/usr/bin/env python3
"""Bucket-headroom watcher (QUE #5230): scheduled /rate_limit reads,
derived-threshold projection, standing-issue page, ledger-side record.

Cadence ruling of record (#5219 c.6823803635, QDesk acceptance
c.6823811148):

- Thresholds are DERIVED from live /rate_limit responses at poll time
  (limit / remaining / reset read in the same response). There is no
  hardcoded remaining-count threshold anywhere in this module: a bucket
  pages only when its own observed burn rate projects exhaustion
  BEFORE its own reset time (or it is already at zero).
- Poll floor 5 minutes for any fixed-interval leg (the workflow runs
  every 10 minutes, inside the floor and on the fleet cadence norm).
- GitHub-independence split: the watcher is Actions-hosted, but the
  RECORD is ledger-side -- state transitions emit
  ``que-governor-event/v1`` rows with ``kind: headroom_alert`` into
  ``ops/que/events/governor-events-<date>.jsonl`` (batch-published by
  commit; the QUE collector folds, as with every governor batch). The
  standing issue is the page surface, never the record of record.
- Buckets: PAT core, the per-repo GITHUB_TOKEN class (observable), the
  Swarm mint path (the Swarm installation bucket read through a freshly
  minted token), and every fleet GitHub App installation enumerated
  from ops/github-apps/PROCESS.json. Apps without an Actions-side
  SEC-03 mint copy in this repo are reported unreadable with a named
  reason -- never silently skipped.

Subcommands:
  collect   env-token /rate_limit reads -> reads.json (IO leg)
  evaluate  pure projection/transition logic (fixtures-testable):
            reads + PROCESS.json + previous feed -> feed + events +
            page plan. No network, no subprocess.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

FEED_SCHEMA = "bucket-headroom/v1"
EVENT_SCHEMA = "que-governor-event/v1"
ACTOR = "actions/bucket-headroom-watcher"
REPO_PATH = "/repos/timerloggedout-spec/termux-monorepo"

# App slugs whose SEC-03 mint copies (vars/secrets) exist in THIS repo
# today, so the workflow carries a mint step for them. Pinned against
# the workflow by tests/test_bucket_headroom_workflow.py. Every other
# enumerated app is reported unreadable (sec03_unprovisioned) until the
# provisioning lane lands its copy -- a named gap, not a silent skip.
MINTABLE_APP_SLUGS = (
    "termux-fleet-swarm",
    "termux-fleet-collector",
    "termux-fleet-crossreference",
)

# Token env var -> (bucket id, kind, source) for the collect leg.
TOKEN_BUCKETS = (
    ("HEADROOM_PAT_TOKEN", "pat-core", "pat", "pat-secret"),
    ("HEADROOM_GITHUB_TOKEN", "github-token", "github_token", "workflow-github-token"),
    ("HEADROOM_SWARM_TOKEN", "app-termux-fleet-swarm", "app_installation", "swarm-mint"),
    ("HEADROOM_COLLECTOR_TOKEN", "app-termux-fleet-collector", "app_installation", "sec03-mint"),
    ("HEADROOM_CROSSREFERENCE_TOKEN", "app-termux-fleet-crossreference", "app_installation", "sec03-mint"),
)


def iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def enumerate_apps(process_doc) -> list:
    """Walk PROCESS.json for {app_id:int, slug:str} records; dedupe by
    app_id, first occurrence wins. Returns [{bucket, app_id, slug}]."""
    found = {}

    def walk(node):
        if isinstance(node, dict):
            app_id = node.get("app_id")
            slug = node.get("slug")
            if isinstance(app_id, int) and isinstance(slug, str) and slug:
                found.setdefault(app_id, {"bucket": f"app-{slug}", "app_id": app_id, "slug": slug})
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(process_doc)
    return [found[k] for k in sorted(found)]


def normalize_rate_limit(payload, bucket, kind, source, read_ts) -> dict:
    """Normalize a /rate_limit response's resources.core into a read."""
    core = payload["resources"]["core"]
    return {
        "bucket": bucket,
        "kind": kind,
        "source": source,
        "limit": int(core["limit"]),
        "used": int(core["used"]),
        "remaining": int(core["remaining"]),
        "reset": int(core["reset"]),
        "read_ts": int(read_ts),
        "read_at": iso(read_ts),
    }


def project(prev, cur):
    """Burn-rate projection from two reads of one bucket.

    Returns None when no projection is possible (no previous read, a
    reset-window change, no elapsed time, or remaining did not drop).
    The page condition is derived entirely from the reads: projected
    used at reset exceeds the bucket's own live limit, i.e. projected
    exhaustion lands before the bucket's own reset time.
    """
    if prev is None:
        return None
    if int(prev["reset"]) != int(cur["reset"]):
        return None  # window rolled over; this read is the new baseline
    dt = int(cur["read_ts"]) - int(prev["read_ts"])
    if dt <= 0:
        return None
    burned = int(prev["remaining"]) - int(cur["remaining"])
    if burned <= 0:
        return None
    rate_per_sec = burned / dt
    seconds_to_reset = max(int(cur["reset"]) - int(cur["read_ts"]), 0)
    projected_used = int(cur["used"]) + rate_per_sec * seconds_to_reset
    return {
        "rate_per_min": round(rate_per_sec * 60, 3),
        "projected_used_at_reset": round(projected_used, 1),
        "projected_exhaustion_at": iso(int(cur["read_ts"]) + int(cur["remaining"] / rate_per_sec)) if rate_per_sec > 0 else None,
        "crosses": projected_used > int(cur["limit"]),
    }


def _event(ts, bucket_row, verdict, detail, session):
    return {
        "schema": EVENT_SCHEMA,
        "ts": iso(ts),
        "kind": "headroom_alert",
        "actor": ACTOR,
        "session": session,
        "path": "/rate_limit",
        "chain": None,
        "verdict": verdict,
        "detail": detail,
        "source": "record",
    }


def evaluate(reads, apps, previous_feed, now_ts, drill=False, session="local"):
    """Pure evaluation. reads: list of read dicts (normalize_rate_limit
    shape) possibly including explicit {bucket, unreadable_reason}
    entries. Returns (feed, events, page_plan)."""
    read_by_bucket = {r["bucket"]: r for r in reads}
    prev_buckets = {}
    if previous_feed:
        prev_buckets = {b["bucket"]: b for b in previous_feed.get("buckets", [])}

    # Full bucket universe: base buckets + every enumerated app.
    universe = [
        {"bucket": "pat-core", "kind": "pat"},
        {"bucket": "github-token", "kind": "github_token"},
    ]
    for app in apps:
        universe.append({"bucket": app["bucket"], "kind": "app_installation",
                         "app_id": app["app_id"], "slug": app["slug"]})

    events = []
    rows = []
    raised, cleared = [], []

    def transition(row, prev_state, new_state, detail):
        if prev_state == new_state:
            return
        if new_state == "alert":
            events.append(_event(now_ts, row, "alert", detail, session))
            raised.append(row["bucket"])
        elif prev_state == "alert" and new_state == "ok":
            events.append(_event(now_ts, row, "recovered", detail, session))
            cleared.append(row["bucket"])

    for spec in universe:
        bucket = spec["bucket"]
        prev_row = prev_buckets.get(bucket, {})
        prev_state = prev_row.get("state", "ok")
        read = read_by_bucket.get(bucket)
        row = dict(spec)
        if read is None or "unreadable_reason" in (read or {}):
            reason = (read or {}).get("unreadable_reason")
            if reason is None:
                reason = ("sec03_unprovisioned" if spec["kind"] == "app_installation"
                          and spec.get("slug") not in MINTABLE_APP_SLUGS
                          else "no_read_supplied")
            # Typed headroom (Cadence countersign #5152 c.6842945679):
            # an unread bucket is headroom kind=unknown, value null --
            # never an invented number. The unknown episode continues
            # across polls until a read or a probe conversion ends it.
            episode = prev_row.get("probe_episode") or {
                "episode_id": f"{bucket}@unknown-{int(now_ts)}", "probed": False}
            row.update({"state": "unreadable", "unreadable_reason": reason,
                        "read": None, "projection": None,
                        "headroom": {"kind": "unknown", "value": None,
                                     "unit": "requests", "as_of": iso(now_ts),
                                     "valid_until": None},
                        "probe_episode": episode})
            rows.append(row)
            continue
        prev_read = prev_row.get("read")
        proj = project(prev_read, read)
        exhausted = int(read["remaining"]) <= 0
        crosses = bool(proj and proj["crosses"])
        new_state = "alert" if (exhausted or crosses) else "ok"
        # An authoritative /rate_limit read is headroom kind=exact
        # (post-draw), valid until the bucket's own reset.
        row.update({"state": new_state, "read": read, "projection": proj,
                    "headroom": {"kind": "exact", "value": int(read["remaining"]),
                                 "unit": "requests", "as_of": read["read_at"],
                                 "valid_until": iso(read["reset"])},
                    "probe_episode": {"episode_id": f"{bucket}@{read['read_at']}",
                                      "probed": False}})
        detail = {
            "bucket": bucket,
            "limit": read["limit"],
            "remaining": read["remaining"],
            "reset": iso(read["reset"]),
            "rate_per_min": proj["rate_per_min"] if proj else None,
            "projected_used": proj["projected_used_at_reset"] if proj else None,
            "threshold": read["limit"],
            "exhausted": exhausted,
        }
        transition(row, prev_state, new_state, detail)
        rows.append(row)

    if drill:
        row, drill_events = _drill_row(now_ts, prev_buckets.get("synthetic-drill", {}), session)
        rows.append(row)
        events.extend(drill_events)
        if drill_events:
            raised.append("synthetic-drill")

    # Carry rows for buckets outside this watcher's read universe
    # (provider-arm buckets whose state arrives via record-probe):
    # a watcher cycle must never erase probe-measured state.
    universe = {r["bucket"] for r in rows}
    for prev_row in prev_buckets.values():
        if prev_row.get("bucket") and prev_row["bucket"] not in universe:
            rows.append(prev_row)

    feed = {
        "schema": FEED_SCHEMA,
        "generated_at": iso(now_ts),
        "poll_interval_min": 10,
        "buckets": rows,
        "alerting": sorted(r["bucket"] for r in rows if r["state"] == "alert"),
    }
    page_plan = {
        "action": "create_or_update" if (raised or cleared) else "none",
        "raised": raised,
        "cleared": cleared,
        "synthetic": bool(drill and raised),
    }
    return feed, events, page_plan


def _drill_row(now_ts, prev_row, session):
    """Stamped synthetic crossing (done-evidence drill): a fabricated
    bucket whose two reads project exhaustion well before reset.
    Never mixed into the real bucket universe; flagged synthetic."""
    limit, reset = 5000, int(now_ts) + 3600
    prev = {"bucket": "synthetic-drill", "kind": "drill", "source": "synthetic",
            "limit": limit, "used": 1000, "remaining": 4000,
            "reset": reset, "read_ts": int(now_ts) - 600, "read_at": iso(now_ts - 600)}
    cur = {"bucket": "synthetic-drill", "kind": "drill", "source": "synthetic",
           "limit": limit, "used": 4000, "remaining": 1000,
           "reset": reset, "read_ts": int(now_ts), "read_at": iso(now_ts)}
    proj = project(prev, cur)
    row = {"bucket": "synthetic-drill", "kind": "drill", "synthetic": True,
           "state": "alert" if proj and proj["crosses"] else "ok",
           "read": cur, "projection": proj,
           "headroom": {"kind": "exact", "value": 1000, "unit": "requests",
                        "as_of": cur["read_at"], "valid_until": iso(reset)},
           "probe_episode": {"episode_id": f"synthetic-drill@{cur['read_at']}",
                             "probed": False}}
    events = []
    if row["state"] == "alert" and prev_row.get("state") != "alert":
        events.append(_event(now_ts, row, "alert", {
            "bucket": "synthetic-drill", "limit": limit, "remaining": 1000,
            "reset": iso(reset), "rate_per_min": proj["rate_per_min"],
            "projected_used": proj["projected_used_at_reset"],
            "threshold": limit, "exhausted": False, "synthetic_test": True,
        }, session))
    return row, events


PROBE_SCHEMA = "quota-probe-event/v1"  # field set per Cadence countersign
PROBE_OUTCOMES = ("success", "quota_terminal", "transient_rate_limit",
                  "auth_error", "route_error", "inconclusive")


def probe_headroom(outcome, *, token_draw=None, authoritative_remaining=None,
                   quota_dimension=None, reset_at=None, observed_at):
    """Typed headroom for a probe outcome (countersign section 3).
    A successful probe does NOT yield exact headroom unless an
    authoritative remaining value came with it: success alone proves
    only that the probe draw itself was available at observed_at."""
    if outcome == "success" and authoritative_remaining is not None:
        return {"kind": "exact", "value": authoritative_remaining,
                "unit": "requests", "as_of": observed_at,
                "valid_until": reset_at}
    if outcome == "success":
        return {"kind": "lower_bound", "value": token_draw,
                "unit": "requests", "as_of": observed_at,
                "valid_until": None}  # same-decide-cycle evidence only
    if outcome == "quota_terminal" and quota_dimension:
        return {"kind": "zero_until_reset", "value": 0,
                "unit": "requests", "as_of": observed_at,
                "valid_until": reset_at}
    return {"kind": "unknown", "value": None, "unit": "requests",
            "as_of": observed_at, "valid_until": None}


def build_probe_event(*, ts, instance_key, provider, account_ref, model,
                      route, bucket_id, quota_dimension, source, probe,
                      outcome, headroom, coverage_scope, prev_hash):
    """One append-only quota_probe metering event (countersign
    sections 1-2): hash-chained, enum outcomes, never an edit."""
    import hashlib
    event = {
        "schema": PROBE_SCHEMA,
        "kind": "quota_probe",
        "event_id": f"probe-{bucket_id}-{ts}-{probe.get('run_id')}",
        "ts": iso(ts),
        "instance_key": instance_key,
        "provider": provider,
        "account_or_project_ref": account_ref,
        "model": model,
        "route": route,
        "bucket_id": bucket_id,
        "quota_dimension": quota_dimension,
        "source": source,
        "probe": probe,
        "outcome": outcome,
        "headroom": headroom,
        "coverage_scope": coverage_scope,
        "prev_hash": prev_hash,
    }
    canonical = json.dumps(event, sort_keys=True).encode("utf-8")
    event["hash"] = hashlib.sha256((prev_hash or "").encode("utf-8")
                                   + canonical).hexdigest()
    return event


def apply_probe(row, event):
    """Consume one quota_probe event against a bucket feed row.
    Returns (new_row, verdict). The event itself is append-only and
    is returned to the caller for ledger append on every verdict
    except a duplicate-probe refusal (a second probe in the same
    unknown episode violates bounded discipline and is not recorded
    as a probe at all).

    Conversion (countersign sections 2-4, 6): only success or an
    identified-dimension quota_terminal converts unknown -> measured;
    the binding is exact-bucket (event bucket_id must equal the row's
    bucket); every presented probe consumes the episode's one probe.
    """
    if event.get("bucket_id") != row.get("bucket"):
        return row, "bucket_mismatch"
    episode = dict(row.get("probe_episode") or
                   {"episode_id": f"{row.get('bucket')}@unknown", "probed": False})
    if episode.get("probed"):
        return row, "refused_duplicate_probe"
    episode["probed"] = True
    new_row = dict(row)
    new_row["probe_episode"] = episode
    headroom = event.get("headroom") or {}
    converts = (
        (event.get("outcome") == "success"
         and headroom.get("kind") in ("exact", "lower_bound"))
        or (event.get("outcome") == "quota_terminal"
            and headroom.get("kind") == "zero_until_reset"
            and event.get("quota_dimension")))
    if (row.get("headroom") or {}).get("kind") == "unknown" and converts:
        new_row["headroom"] = headroom
        new_row["measured"] = {"via": "quota_probe",
                               "event_id": event.get("event_id"),
                               "at": event.get("ts")}
        return new_row, "converted"
    return new_row, "evidence_only"


def _get_rate_limit(token):
    req = urllib.request.Request(
        "https://api.github.com/rate_limit",
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "termux-monorepo-bucket-headroom"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def collect(env, now_ts):
    """IO leg: one /rate_limit read per token env present. A mintable
    app whose token env is absent is recorded as an explicit unreadable
    entry; tokens are never printed or stored."""
    reads = []
    for env_name, bucket, kind, source in TOKEN_BUCKETS:
        token = env.get(env_name)
        if not token:
            if kind == "app_installation":
                reads.append({"bucket": bucket, "unreadable_reason": "mint_unavailable"})
            continue
        payload = _get_rate_limit(token)
        reads.append(normalize_rate_limit(payload, bucket, kind, source, now_ts))
    return reads


def _load_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_collect = sub.add_parser("collect")
    p_collect.add_argument("--out", required=True)

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--reads", required=True)
    p_eval.add_argument("--process", required=True, help="ops/github-apps/PROCESS.json")
    p_eval.add_argument("--previous", help="previous bucket-headroom feed (state)")
    p_eval.add_argument("--feed-out", required=True)
    p_eval.add_argument("--events-out", required=True)
    p_eval.add_argument("--page-out", required=True)
    p_eval.add_argument("--events-dir", help="append events to governor-events-<date>.jsonl here")
    p_eval.add_argument("--drill", action="store_true")
    p_eval.add_argument("--session", default="local")
    p_eval.add_argument("--now", type=int, help="epoch override (tests)")

    p_probe = sub.add_parser("record-probe")
    p_probe.add_argument("--feed", required=True)
    p_probe.add_argument("--probe", required=True, help="probe-result JSON")
    p_probe.add_argument("--ledger", required=True,
                         help="append-only quota_probe ledger (jsonl)")
    p_probe.add_argument("--feed-out", required=True)
    p_probe.add_argument("--now", type=int, help="epoch override (tests)")

    args = parser.parse_args(argv)
    now_ts = int(args.now) if getattr(args, "now", None) else int(time.time())

    if args.cmd == "collect":
        reads = collect(os.environ, now_ts)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump({"reads": reads}, fh, indent=1)
        print(f"collect: {len(reads)} bucket entries")
        return 0

    if args.cmd == "record-probe":
        feed = _load_json(args.feed)
        probe = _load_json(args.probe)
        if feed is None or probe is None:
            print("record-probe: feed/probe unreadable", file=sys.stderr)
            return 2
        if probe.get("outcome") not in PROBE_OUTCOMES:
            print(f"record-probe: outcome not in enum: {probe.get('outcome')}",
                  file=sys.stderr)
            return 2
        rows = feed.get("buckets", [])
        row = next((r for r in rows if r.get("bucket") == probe.get("bucket_id")), None)
        if row is None:
            # A provider-arm bucket enters the feed through its
            # first probe (the watcher's read universe is the
            # GitHub-API buckets; arm buckets are carried, never
            # erased, once present — see evaluate()).
            row = {"bucket": probe.get("bucket_id"), "kind": "provider-arm",
                   "state": "unreadable", "read": None, "projection": None,
                   "headroom": {"kind": "unknown", "value": None,
                                "unit": "requests", "as_of": iso(now_ts),
                                "valid_until": None},
                   "probe_episode": {
                       "episode_id": f"{probe.get('bucket_id')}@unknown-{int(now_ts)}",
                       "probed": False}}
            rows.append(row)
            feed["buckets"] = rows
        prev_hash = None
        if os.path.exists(args.ledger):
            with open(args.ledger, encoding="utf-8") as fh:
                lines = [ln for ln in fh if ln.strip()]
            if lines:
                prev_hash = json.loads(lines[-1]).get("hash")
        source = probe.get("source") or {}
        observed_at = source.get("observed_at") or iso(now_ts)
        headroom = probe_headroom(
            probe["outcome"],
            token_draw=(probe.get("probe") or {}).get("token_draw"),
            authoritative_remaining=probe.get("authoritative_remaining"),
            quota_dimension=probe.get("quota_dimension"),
            reset_at=probe.get("reset_at"), observed_at=observed_at)
        event = build_probe_event(
            ts=now_ts, instance_key=probe.get("instance_key"),
            provider=probe.get("provider"),
            account_ref=probe.get("account_or_project_ref"),
            model=probe.get("model"), route=probe.get("route"),
            bucket_id=probe.get("bucket_id"),
            quota_dimension=probe.get("quota_dimension"),
            source=source, probe=probe.get("probe") or {},
            outcome=probe["outcome"], headroom=headroom,
            coverage_scope=probe.get("coverage_scope"),
            prev_hash=prev_hash)
        new_row, verdict = apply_probe(row, event)
        if verdict not in ("refused_duplicate_probe", "bucket_mismatch"):
            with open(args.ledger, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event) + "\n")
        rows[rows.index(row)] = new_row
        with open(args.feed_out, "w", encoding="utf-8") as fh:
            json.dump(feed, fh, indent=1)
        print(f"record-probe: {probe.get('bucket_id')} -> {verdict} "
              f"(headroom kind={headroom['kind']})")
        return 0

    reads_doc = _load_json(args.reads) or {}
    reads = reads_doc.get("reads", reads_doc if isinstance(reads_doc, list) else [])
    process_doc = _load_json(args.process)
    if process_doc is None:
        print(f"evaluate: PROCESS file unreadable: {args.process}", file=sys.stderr)
        return 2
    apps = enumerate_apps(process_doc)
    previous_feed = _load_json(args.previous)
    feed, events, page_plan = evaluate(reads, apps, previous_feed, now_ts,
                                       drill=args.drill, session=args.session)
    with open(args.feed_out, "w", encoding="utf-8") as fh:
        json.dump(feed, fh, indent=1)
    with open(args.events_out, "w", encoding="utf-8") as fh:
        for event in events:
            fh.write(json.dumps(event) + "\n")
    with open(args.page_out, "w", encoding="utf-8") as fh:
        json.dump(page_plan, fh, indent=1)
    if args.events_dir and events:
        os.makedirs(args.events_dir, exist_ok=True)
        batch = os.path.join(args.events_dir,
                             f"governor-events-{iso(now_ts)[:10]}.jsonl")
        with open(batch, "a", encoding="utf-8") as fh:
            for event in events:
                fh.write(json.dumps(event) + "\n")
        print(f"evaluate: appended {len(events)} headroom_alert event(s) to {batch}")
    print(f"evaluate: {len(feed['buckets'])} buckets, "
          f"alerting={feed['alerting']}, page={page_plan['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
