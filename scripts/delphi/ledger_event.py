#!/usr/bin/env python3
"""Mirror Delphi continuous-ledger events to Neon Postgres. Never fails
its caller (the scripts/ops/lane_event.py pattern).

Design: docs/ops/DELPHI-LEDGER-STORE.md (slice 2). The GitHub issue
comments stay the system of record; this writer mirrors the SAME rows
the feed collector derives, with the SAME idempotency key
(event_key = sha256(ledger_id|comment_id)), into the append-only tables
of ops/delphi-ledger/schema.sql. Inserts are ON CONFLICT DO NOTHING —
a re-sync of the same cache inserts zero new rows.

Credential resolution (names only; values never printed):
  1. LANE_EVENTS_DATABASE_URL — a Postgres connection string, or
  2. NEON_API_KEY — finds the existing Neon project "lane-events"
     (created by the lane-events writer; this writer never creates one).
  Neither set -> prints a ::notice and exits 0 (no-op).

Input: the collector cache (--cache DIR, as produced by
ledger_fetch.py). Commands: sync (default), schema, count.
--dry-run prints the row set instead of touching a database.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL_DIR = HERE.parent.parent / "ops" / "delphi-ledger"
NEON_API = "https://console.neon.tech/api/v2"
NEON_PROJECT = os.environ.get("LANE_EVENTS_NEON_PROJECT", "lane-events")

_spec = importlib.util.spec_from_file_location("ledger_feed", HERE / "ledger_feed.py")
ledger_feed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ledger_feed)


def rows_from_cache(cache: Path) -> tuple[list[dict], list[dict]]:
    """Flatten a collector cache into (event rows, living rows).

    Reuses ledger_feed.collect so the mirror can never diverge from
    the feed: same partition, same keys, same current-state inputs.
    Bodies come from the cache (the feed carries payloads, not bodies).
    """
    feed = ledger_feed.collect(cache)
    comments = json.loads((cache / "comments.json").read_text())
    issues = {i["number"]: i for i in json.loads((cache / "issues.json").read_text())}
    events = []
    for led in feed["ledgers"]:
        cmap = {c["id"]: c for c in comments[str(led["issue"])]}
        for ev in led["events"]:
            body = cmap[ev["comment_id"]].get("body") or ""
            events.append({
                "key": ev["event_key"], "ledger": led["id"],
                "issue": str(led["issue"]), "comment": str(ev["comment_id"]),
                "marker": ev["marker"] or "",
                "payload": json.dumps(ev["payload"]) if ev["payload"] is not None else "",
                "body": body, "occurred": ev["created_at"]})
    living = []
    for rec in feed["living_records"]:
        body = issues[rec["issue"]].get("body") or ""
        sha = hashlib.sha256(body.encode()).hexdigest()
        living.append({
            "vkey": hashlib.sha256(f"{rec['issue']}|{sha}".encode()).hexdigest(),
            "record": rec["id"], "issue": str(rec["issue"]), "sha": sha,
            "snapshot": rec["snapshot_at"] or "", "body": body})
    return events, living


def _neon(method: str, path: str, key: str) -> dict:
    req = urllib.request.Request(NEON_API + path, method=method, headers={
        "Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"{}")


def resolve_url() -> str | None:
    url = os.environ.get("LANE_EVENTS_DATABASE_URL", "").strip()
    if url:
        return url
    key = os.environ.get("NEON_API_KEY", "").strip()
    if not key:
        return None
    projects = _neon("GET", f"/projects?search={NEON_PROJECT}&limit=50", key).get("projects", [])
    proj = next((p for p in projects if p.get("name") == NEON_PROJECT), None)
    if proj is None:
        return None  # lane-events writer owns project creation; mirror is a guest
    pid = proj["id"]
    branches = _neon("GET", f"/projects/{pid}/branches", key).get("branches", [])
    default = next((b for b in branches if b.get("default")), branches[0] if branches else {})
    roles = _neon("GET", f"/projects/{pid}/branches/{default['id']}/roles", key).get("roles", [])
    role = next((r["name"] for r in roles if not r.get("protected")), "neondb_owner")
    q = f"/projects/{pid}/connection_uri?database_name=neondb&role_name={role}&branch_id={default['id']}"
    return _neon("GET", q, key)["uri"]


def psql(url: str, args: list[str]) -> str:
    env = dict(os.environ, PGCONNECT_TIMEOUT="15")
    res = subprocess.run(["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1", *args],
                         capture_output=True, text=True, env=env, timeout=120)
    if res.returncode != 0:
        lines = [l for l in (res.stderr or "psql failed").strip().splitlines()
                 if "NOTICE:" not in l]
        raise RuntimeError((lines[-1] if lines else "psql failed")[:300])
    return res.stdout


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", default="sync",
                    choices=("sync", "schema", "count"))
    ap.add_argument("--cache", default=".ledger-cache")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero on errors (tests only)")
    ns = ap.parse_args(argv)
    try:
        if ns.dry_run:
            events, living = rows_from_cache(Path(ns.cache))
            print(f"dry-run: {len(events)} event rows, {len(living)} living rows")
            for r in events:
                print(f"  event {r['ledger']} #{r['issue']} comment {r['comment']} key {r['key'][:12]}")
            for r in living:
                print(f"  living {r['record']} #{r['issue']} vkey {r['vkey'][:12]}")
            return 0
        url = resolve_url()
        if not url:
            print("::notice title=delphi-ledger::no LANE_EVENTS_DATABASE_URL or NEON_API_KEY "
                  "(or no lane-events Neon project); skipping (no-op)")
            return 0
        psql(url, ["-f", str(SQL_DIR / "schema.sql")])
        if ns.command == "schema":
            print("::notice title=delphi-ledger::schema applied")
            return 0
        if ns.command == "count":
            n = psql(url, ["-At", "-c", "SELECT count(*) FROM delphi_ledger_events"]).strip()
            m = psql(url, ["-At", "-c", "SELECT count(*) FROM delphi_living_records"]).strip()
            print(f"::notice title=delphi-ledger count::events={n} living={m}")
            return 0
        events, living = rows_from_cache(Path(ns.cache))
        for r in events:
            args = ["-f", str(SQL_DIR / "insert-event.sql")]
            for k, v in r.items():
                args += ["-v", f"{k}={v}"]
            psql(url, args)
        for r in living:
            args = ["-f", str(SQL_DIR / "insert-living.sql")]
            for k, v in r.items():
                args += ["-v", f"{k}={v}"]
            psql(url, args)
        print(f"::notice title=delphi-ledger::synced {len(events)} event(s), "
              f"{len(living)} living record(s) (ON CONFLICT DO NOTHING)")
        return 0
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError, SystemExit) as exc:
        print(f"::warning title=delphi-ledger::{type(exc).__name__}: {str(exc)[:300]}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    sys.exit(main())
