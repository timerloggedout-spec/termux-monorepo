#!/usr/bin/env python3
"""Mirror challenge participants to Neon Postgres. Never fails its
caller (the scripts/ops/lane_event.py pattern).

Design: docs/ops/CHALLENGE-PARTICIPANT-MIRROR.md. Source of truth =
ops/challenge/coordinator.json, events[].participants[] (absent =
empty; the field lands with the challenge lane's schema extension).
Each sync is one batch keyed sha256(source_ref) where source_ref is
the git SHA of coordinator.json (GITHUB_SHA in Actions); participant
rows key sha256('challenge-participants'|event_id|participant_key),
inserts ON CONFLICT DO NOTHING — a re-sync of the same source inserts
zero new rows. participants_current = newest batch (schema.sql).

Credential resolution (names only; values never printed): as
ledger_event.py — LANE_EVENTS_DATABASE_URL, else NEON_API_KEY against
the existing "lane-events" Neon project (never creates one). Neither
-> ::notice + exit 0 (no-op).

Commands: sync (default), schema, count. --dry-run prints the batch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL_DIR = HERE.parent.parent / "ops" / "challenge-participants"
NEON_API = "https://console.neon.tech/api/v2"
NEON_PROJECT = os.environ.get("LANE_EVENTS_NEON_PROJECT", "lane-events")
IDENTITY_FIELDS = ("id", "handle", "username", "name", "url")


def participant_key(record) -> str:
    if isinstance(record, dict):
        for f in IDENTITY_FIELDS:
            v = record.get(f)
            if isinstance(v, str) and v.strip():
                return v.strip()
        canon = json.dumps(record, sort_keys=True, separators=(",", ":"))
    else:
        canon = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)
        if isinstance(record, str) and record.strip():
            return record.strip()
    return hashlib.sha256(canon.encode()).hexdigest()


def event_key(event_id: str, pkey: str) -> str:
    return hashlib.sha256(f"challenge-participants|{event_id}|{pkey}".encode()).hexdigest()


def batch_from_source(source: Path, source_ref: str) -> tuple[dict, list[dict]]:
    data = json.loads(source.read_text())
    sync_key = hashlib.sha256(source_ref.encode()).hexdigest()
    counts: dict[str, int] = {}
    rows: list[dict] = []
    for ev in data.get("events", []):
        eid = str(ev.get("id") or ev.get("slug") or ev.get("name") or "")
        parts = ev.get("participants") or []
        counts[eid] = len(parts)
        seen = set()
        for rec in parts:
            pk = participant_key(rec)
            if pk in seen:  # duplicate listing in source = one row
                counts[eid] -= 1
                continue
            seen.add(pk)
            rows.append({"key": event_key(eid, pk), "sync": sync_key,
                         "event": eid, "participant": pk,
                         "payload": json.dumps(rec, sort_keys=True, default=str)})
    return {"sync": sync_key, "ref": source_ref,
            "counts": json.dumps(counts, sort_keys=True)}, rows


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
        return None
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
        raise RuntimeError((res.stderr or "psql failed").strip().splitlines()[0][:300])
    return res.stdout


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", default="sync",
                    choices=("sync", "schema", "count"))
    ap.add_argument("--source", default="ops/challenge/coordinator.json")
    ap.add_argument("--source-ref", default=os.environ.get("GITHUB_SHA", "working-tree"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ns = ap.parse_args(argv)
    try:
        if ns.dry_run:
            sync, rows = batch_from_source(Path(ns.source), ns.source_ref)
            counts = json.loads(sync["counts"])
            print(f"dry-run: sync {sync['sync'][:12]} ref {sync['ref'][:12]} "
                  f"counts {counts} rows {len(rows)}")
            return 0
        url = resolve_url()
        if not url:
            print("::notice title=challenge-participants::no LANE_EVENTS_DATABASE_URL "
                  "or NEON_API_KEY (or no lane-events Neon project); skipping (no-op)")
            return 0
        psql(url, ["-f", str(SQL_DIR / "schema.sql")])
        if ns.command == "schema":
            print("::notice title=challenge-participants::schema applied")
            return 0
        if ns.command == "count":
            out = psql(url, ["-At", "-c",
                             "SELECT counts::text FROM participant_syncs "
                             "ORDER BY synced_at DESC, sync_key DESC LIMIT 1"]).strip()
            print(f"::notice title=challenge-participants count::"
                  f"latest sync counts {out or 'no syncs yet'}")
            return 0
        sync, rows = batch_from_source(Path(ns.source), ns.source_ref)
        args = ["-f", str(SQL_DIR / "insert-sync.sql")]
        for k, v in sync.items():
            args += ["-v", f"{k}={v}"]
        psql(url, args)
        for r in rows:
            args = ["-f", str(SQL_DIR / "insert-participant.sql")]
            for k, v in r.items():
                args += ["-v", f"{k}={v}"]
            psql(url, args)
        print(f"::notice title=challenge-participants::synced batch {sync['sync'][:12]} "
              f"counts {sync['counts']} ({len(rows)} rows, ON CONFLICT DO NOTHING)")
        return 0
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"::warning title=challenge-participants::{type(exc).__name__}: {str(exc)[:300]}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    sys.exit(main())
