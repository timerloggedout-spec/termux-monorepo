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


def touchpoints_of(rows: list[dict]) -> list[dict]:
    """Executed engagement touchpoints across a batch (first-class data).

    Engagement is autonomous (owner correction, 2026-10-28): records
    carry engagement.touchpoints[] = logs of touchpoints that HAPPENED
    ({surface, at, content_ref}). There is no draft/approval state in
    this writer — nothing is gated, held or approved here; a record is
    mirrored as written.
    """
    out = []
    for r in rows:
        rec = json.loads(r["payload"])
        eng = rec.get("engagement") if isinstance(rec, dict) else None
        tps = eng.get("touchpoints") if isinstance(eng, dict) else None
        for t in tps or []:
            if isinstance(t, dict):
                out.append({"event": r["event"], "participant": r["participant"],
                            "surface": t.get("surface"), "at": t.get("at"),
                            "content_ref": t.get("content_ref")})
    return out


def judge_key_for(event_id: str, jkey: str) -> str:
    return hashlib.sha256(f"challenge-judges|{event_id}|{jkey}".encode()).hexdigest()


def snapshot_key_for(kind: str, event_id: str, ekey: str, snap) -> str:
    canon = json.dumps(snap, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(f"{kind}|{event_id}|{ekey}|{canon}".encode()).hexdigest()


def _entity_rows(records, eid, sync_key, kind):
    """Rows for one entity list: entity rows + their snapshot rows."""
    rows, snaps, seen = [], [], set()
    key_field = "participant" if kind == "participant" else "judge"
    for rec in records or []:
        pk = participant_key(rec)
        if pk in seen:
            continue
        seen.add(pk)
        key = event_key(eid, pk) if kind == "participant" else judge_key_for(eid, pk)
        rows.append({"key": key, "sync": sync_key, "event": eid,
                     key_field: pk,
                     "payload": json.dumps(rec, sort_keys=True, default=str)})
        snaps_list = rec.get("snapshots") if isinstance(rec, dict) else None
        for s in snaps_list or []:
            snaps.append({"key": snapshot_key_for(kind, eid, pk, s),
                          "sync": sync_key, "kind": kind, "event": eid,
                          "entity": pk,
                          "snapshot": json.dumps(s, sort_keys=True, default=str)})
    return rows, snaps


def batch_from_source(source: Path, source_ref: str) -> dict:
    """One sync batch: sync row + participant/judge/snapshot rows.

    Counts v2: {"participants": {event: n}, "judges": {event: n},
    "snapshots": total, "touchpoints": total}. The sync row also
    carries the events' core fields (id/name/prizes) for the podium
    join (schema.sql challenge_events_current).
    """
    data = json.loads(source.read_text())
    sync_key = hashlib.sha256(source_ref.encode()).hexdigest()
    p_counts: dict[str, int] = {}
    j_counts: dict[str, int] = {}
    participants, judges, snapshots = [], [], []
    events_core = []
    for ev in data.get("events", []):
        eid = str(ev.get("id") or ev.get("slug") or ev.get("name") or "")
        events_core.append({"id": eid, "name": ev.get("name"),
                            "prizes": ev.get("prizes"),
                            "opportunity_cost": ev.get("opportunity_cost")})
        pr, ps = _entity_rows(ev.get("participants"), eid, sync_key, "participant")
        jr, js = _entity_rows(ev.get("judges"), eid, sync_key, "judge")
        participants += pr
        judges += jr
        snapshots += ps + js
        p_counts[eid] = len(pr)
        j_counts[eid] = len(jr)
    ledger_rows = []
    ledger_path = source.parent / "opportunity_ledger.json"
    if ledger_path.exists():
        for entry in json.loads(ledger_path.read_text()).get("entries", []):
            eid2 = str(entry.get("id") or "")
            ledger_rows.append({
                "key": hashlib.sha256(f"opportunity-ledger|{eid2}".encode()).hexdigest(),
                "sync": sync_key, "entry": eid2,
                "payload": json.dumps(entry, sort_keys=True, default=str)})
    osint_rows = []
    osint_path = source.parent / "osint" / "snapshots.json"
    if osint_path.exists():
        for snap in json.loads(osint_path.read_text()).get("snapshots", []):
            osint_rows.append({
                "key": hashlib.sha256(f"osint-page|{snap.get('event')}|{snap.get('sha256')}".encode()).hexdigest(),
                "sync": sync_key, "event": str(snap.get("event") or ""),
                "payload": json.dumps(snap, sort_keys=True, default=str)})
    counts = {"participants": p_counts, "judges": j_counts, "osint_snapshots": len(osint_rows),
              "snapshots": len(snapshots),
              "touchpoints": len(touchpoints_of(participants)),
              "ledger_entries": len(ledger_rows)}
    sync = {"sync": sync_key, "ref": source_ref,
            "counts": json.dumps(counts, sort_keys=True),
            "events": json.dumps(events_core, sort_keys=True, default=str)}
    return {"sync": sync, "participants": participants,
            "judges": judges, "snapshots": snapshots,
            "ledger": ledger_rows, "osint": osint_rows, "counts": counts}


def recruitment_of(batch: dict) -> list[dict]:
    """Current recruitment state across both entity kinds."""
    out = []
    for kind, rows in (("participant", batch["participants"]),
                       ("judge", batch["judges"])):
        for r in rows:
            rec = json.loads(r["payload"])
            rc = rec.get("recruitment") if isinstance(rec, dict) else None
            if isinstance(rc, dict):
                out.append({"kind": kind, "event": r["event"],
                            "entity": r["participant"] if kind == "participant" else r["judge"],
                            "candidate": rc.get("candidate"),
                            "pipeline_state": rc.get("pipeline_state")})
    return out


def wins_of(batch: dict) -> list[dict]:
    """past_wins[] across both entity kinds (podium inputs)."""
    out = []
    for kind, rows in (("participant", batch["participants"]),
                       ("judge", batch["judges"])):
        for r in rows:
            rec = json.loads(r["payload"])
            for w in (rec.get("past_wins") or []) if isinstance(rec, dict) else []:
                if isinstance(w, dict):
                    out.append({"kind": kind, "event": r["event"],
                                "entity": r["participant"] if kind == "participant" else r["judge"],
                                **{k: w.get(k) for k in ("event", "place", "prize", "project")}})
    return out


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
        lines = [l for l in (res.stderr or "psql failed").strip().splitlines()
                 if "NOTICE:" not in l]
        raise RuntimeError((lines[-1] if lines else "psql failed")[:300])
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
            batch = batch_from_source(Path(ns.source), ns.source_ref)
            print(f"dry-run: sync {batch['sync']['sync'][:12]} "
                  f"ref {ns.source_ref[:12]} counts {batch['counts']} "
                  f"recruitment {len(recruitment_of(batch))} "
                  f"wins {len(wins_of(batch))}")
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
        batch = batch_from_source(Path(ns.source), ns.source_ref)
        sync = batch["sync"]
        args = ["-f", str(SQL_DIR / "insert-sync.sql")]
        for k, v in sync.items():
            args += ["-v", f"{k}={v}"]
        psql(url, args)
        plan = (("insert-participant.sql", batch["participants"]),
                ("insert-judge.sql", batch["judges"]),
                ("insert-snapshot.sql", batch["snapshots"]),
                ("insert-ledger.sql", batch.get("ledger", [])),
                ("insert-osint.sql", batch.get("osint", [])))
        total = 0
        for sqlf, rows in plan:
            for r in rows:
                args = ["-f", str(SQL_DIR / sqlf)]
                for k, v in r.items():
                    args += ["-v", f"{k}={v}"]
                psql(url, args)
                total += 1
        print(f"::notice title=challenge-participants::synced batch {sync['sync'][:12]} "
              f"counts {sync['counts']} ({total} rows, ON CONFLICT DO NOTHING)")
        return 0
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"::warning title=challenge-participants::{type(exc).__name__}: {str(exc)[:300]}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    sys.exit(main())
