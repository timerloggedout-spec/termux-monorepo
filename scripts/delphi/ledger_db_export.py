#!/usr/bin/env python3
"""Read mode: export the Delphi ledger feed FROM the Neon working
database (owner correction, 2026-10-28 — pipelines query the DB;
the feed is an export of database state, not a compute input).

Emits delphi-ledger-feed-db/v1: the delphi-ledger-feed/v1 shape with
events/currents/living served from delphi_ledger_events,
delphi_ledger_current and delphi_living_records; ledger metadata +
invariants come from the registry (ops/delphi/ledgers.json), the same
file the cache collector reads. Differences from the cache feed, by
design: excluded_noise is null (noise is never written to the DB —
it stays a source-partition count), and living records carry
recorded_at instead of the issue's updated_at.

Never fails its caller; no-op (exit 0) without ledger credentials.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


le = _load("ledger_event")
lf = _load("ledger_feed")

EVENTS_Q = """
SELECT jsonb_build_object(
  'ledger_id', ledger_id, 'event_key', event_key,
  'comment_id', comment_id,
  'created_at', to_char(occurred_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
  'marker', marker, 'payload', payload, 'body', body)::text
FROM delphi_ledger_events ORDER BY ledger_id, occurred_at, comment_id;
"""
CURRENT_Q = """
SELECT jsonb_build_object(
  'ledger_id', ledger_id, 'comment_id', comment_id,
  'created_at', to_char(occurred_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
  'payload', payload)::text
FROM delphi_ledger_current ORDER BY ledger_id;
"""
LIVING_Q = """
SELECT jsonb_build_object(
  'record_id', record_id, 'issue_number', issue_number,
  'version_key', version_key,
  'snapshot_at', CASE WHEN snapshot_at IS NULL THEN NULL ELSE
    to_char(snapshot_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') END,
  'recorded_at', to_char(recorded_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
  'body', body)::text
FROM (SELECT DISTINCT ON (record_id) * FROM delphi_living_records
      ORDER BY record_id, recorded_at DESC) latest ORDER BY record_id;
"""


def build_feed(registry: dict, events: list[dict], currents: list[dict],
               living: list[dict]) -> dict:
    by_ledger: dict[str, list[dict]] = {}
    for e in events:
        by_ledger.setdefault(e["ledger_id"], []).append(e)
    cur = {c["ledger_id"]: c for c in currents}
    feed = {"schema": "delphi-ledger-feed-db/v1", "ledgers": [],
            "living_records": [], "invariants": registry.get("invariants"),
            "summary": {"events": 0, "excluded_noise": None}}
    reg_ledgers = {l["id"]: l for l in registry.get("ledgers", [])}
    for lid, led in reg_ledgers.items():
        evs = []
        for e in by_ledger.get(lid, []):
            evs.append({"event_key": e["event_key"], "comment_id": e["comment_id"],
                        "created_at": e["created_at"], "marker": e["marker"],
                        "class": "machine-state" if e["marker"] else "record",
                        "headline": lf.first_line(e["body"], led.get("markers", [])),
                        "payload": e["payload"]})
        c = cur.get(lid)
        feed["ledgers"].append({
            "id": lid, "title": led.get("title"), "issue": led.get("issue"),
            "kind": led.get("kind"), "semantics": led.get("semantics"),
            "derivation": led.get("derivation"), "state_rule": led.get("state_rule"),
            "events": evs,
            "current": ({"comment_id": c["comment_id"], "created_at": c["created_at"],
                         "payload": c["payload"]} if c else None),
            "excluded_noise": None})
        feed["summary"]["events"] += len(evs)
    by_issue = {r["issue_number"]: r for r in living}
    for led in registry.get("ledgers", []):
        if led.get("kind") != "living-body":
            continue
        r = by_issue.get(led["issue"])
        if r is None:
            continue
        body = r["body"]
        first = (body.splitlines() or [""])[0].strip()
        feed["living_records"].append({
            "id": led["id"], "title": led.get("title"), "issue": led["issue"],
            "kind": led["kind"], "semantics": led.get("semantics"),
            "state_rule": led.get("state_rule"), "marker": led.get("marker"),
            "assigned_marker": led.get("assigned_marker"),
            "body_marker": first if first.startswith("<!--") else None,
            "version_key": r["version_key"], "snapshot_at": r["snapshot_at"],
            "recorded_at": r["recorded_at"], "body": body})
    return feed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", default="ops/delphi/ledgers.json")
    ap.add_argument("--out", default="apps/help-wanted-dashboard/data/delphi-ledger-feed-db.json")
    ap.add_argument("--strict", action="store_true")
    ns = ap.parse_args(argv)
    try:
        url = le.resolve_url()
        if not url:
            print("::notice title=delphi-ledger-db-export::no LANE_EVENTS_DATABASE_URL "
                  "or NEON_API_KEY; skipping (no-op)")
            return 0
        def rows(q):
            out = le.psql(url, ["-At", "-c", q]).strip()
            return [json.loads(l) for l in out.splitlines() if l.strip()]
        registry = json.loads(Path(ns.registry).read_text())
        feed = build_feed(registry, rows(EVENTS_Q), rows(CURRENT_Q), rows(LIVING_Q))
        Path(ns.out).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.out).write_text(json.dumps(feed, indent=1, sort_keys=True) + "\n")
        print(f"::notice title=delphi-ledger-db-export::wrote {ns.out} "
              f"({feed['summary']['events']} events from Neon)")
        return 0
    except Exception as exc:  # never fail the caller
        print(f"::warning title=delphi-ledger-db-export::{type(exc).__name__}: {str(exc)[:300]}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    sys.exit(main())
