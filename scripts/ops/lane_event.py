#!/usr/bin/env python3
"""Write lane_events rows to Neon Postgres. Never fails its caller.

Credentials are never written to stdout/stderr: the env values arrive from
Actions secrets (masked by the runner) and the resolved Neon URI is only
passed to psql as an argument.

Credential resolution (names only; values are never printed):
  1. LANE_EVENTS_DATABASE_URL  - a Postgres connection string, or
  2. NEON_API_KEY              - finds or creates Neon project "lane-events"
                                 (region aws-us-east-2, Realtime-capable) and
                                 resolves its connection string at runtime.
  Neither set -> prints a ::notice and exits 0 (no-op).

Input: one event (CLI flags) or a JSONL file of events (--events-file).
Commands: record (default), count (emit row count as a ::notice), schema.
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
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL_DIR = HERE.parent.parent / "ops" / "lane-events"
NEON_API = "https://console.neon.tech/api/v2"
NEON_PROJECT = os.environ.get("LANE_EVENTS_NEON_PROJECT", "lane-events")
NEON_REGION = os.environ.get("LANE_EVENTS_NEON_REGION", "aws-us-east-2")
MAX_PAYLOAD = 16_000
FIELDS = ("lane", "workflow", "event_type", "repo", "run_id", "run_attempt",
          "subject_url", "phase_id", "conclusion", "head_sha", "occurred_at")


def event_key(ev: dict) -> str:
    subject = ev.get("subject_url") or ev.get("phase_id") or ""
    raw = "|".join(str(ev.get(k) or "") for k in ("lane", "workflow", "run_id", "run_attempt")) + f"|{subject}|{ev.get('event_type') or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def normalize(ev: dict) -> dict:
    out = {k: ("" if ev.get(k) is None else str(ev.get(k))) for k in FIELDS}
    if not out["occurred_at"]:
        out["occurred_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload = ev.get("payload") or {}
    text = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    if len(text) > MAX_PAYLOAD:
        text = json.dumps({"truncated": True, "bytes": len(text)})
    out["payload"] = text
    for req in ("lane", "workflow", "event_type", "repo"):
        if not out[req]:
            raise ValueError(f"event missing {req}")
    if not (out["run_id"] or out["subject_url"] or out["phase_id"]):
        raise ValueError("event needs run_id, subject_url or phase_id")
    out["key"] = event_key(out)
    return out


def _neon(method: str, path: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(NEON_API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Accept": "application/json", "Content-Type": "application/json"})
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
        created = _neon("POST", "/projects", key, {"project": {"name": NEON_PROJECT, "region_id": NEON_REGION}})
        proj = created["project"]
        print(f"::notice title=lane-events::created Neon project {NEON_PROJECT} in {NEON_REGION}")
    print(f"::notice title=lane-events::Neon project {NEON_PROJECT} region={proj.get('region_id')}")
    pid = proj["id"]
    branches = _neon("GET", f"/projects/{pid}/branches", key).get("branches", [])
    default = next((b for b in branches if b.get("default")), branches[0] if branches else {})
    roles = _neon("GET", f"/projects/{pid}/branches/{default['id']}/roles", key).get("roles", [])
    role = next((r["name"] for r in roles if not r.get("protected")), "neondb_owner")
    q = f"/projects/{pid}/connection_uri?database_name=neondb&role_name={role}&branch_id={default['id']}"
    uri = _neon("GET", q, key)["uri"]
    return uri


def psql(url: str, args: list[str], stdin: str | None = None) -> str:
    env = dict(os.environ, PGCONNECT_TIMEOUT="15")
    res = subprocess.run(["psql", url, "-X", "-q", "-v", "ON_ERROR_STOP=1", *args],
                         input=stdin, capture_output=True, text=True, env=env, timeout=120)
    if res.returncode != 0:
        # stderr from psql never contains the password; keep only the first line.
        raise RuntimeError((res.stderr or "psql failed").strip().splitlines()[0][:300])
    return res.stdout


def load_events(ns: argparse.Namespace) -> list[dict]:
    events: list[dict] = []
    if ns.events_file:
        p = Path(ns.events_file)
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    events.append(json.loads(line))
    if ns.event_type and not ns.events_file:
        ev = {k: getattr(ns, k) for k in FIELDS}
        ev["payload"] = json.loads(ns.payload) if ns.payload else {}
        events.append(ev)
    return events


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", nargs="?", default="record", choices=("record", "count", "schema"))
    for f in FIELDS:
        ap.add_argument(f"--{f.replace('_', '-')}", dest=f, default="")
    ap.add_argument("--payload", default="")
    ap.add_argument("--events-file", default="")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on errors (tests only)")
    ns = ap.parse_args(argv)
    try:
        url = resolve_url()
        if not url:
            print("::notice title=lane-events::no LANE_EVENTS_DATABASE_URL or NEON_API_KEY; skipping (no-op)")
            return 0
        psql(url, ["-f", str(SQL_DIR / "schema.sql")])
        if ns.command == "schema":
            print("::notice title=lane-events::schema applied")
            return 0
        if ns.command == "count":
            n = psql(url, ["-At", "-c", "SELECT count(*) FROM lane_events"]).strip()
            by = psql(url, ["-At", "-F", "=", "-c", "SELECT lane, count(*) FROM lane_events GROUP BY 1 ORDER BY 1"]).strip().replace("\n", ", ")
            print(f"::notice title=lane-events count::rows={n} ({by})")
            return 0
        events = [normalize(e) for e in load_events(ns)]
        for ev in events:
            args = ["-f", str(SQL_DIR / "insert.sql")]
            for k, v in ev.items():
                args += ["-v", f"{k}={v}"]
            psql(url, args)
        print(f"::notice title=lane-events::recorded {len(events)} event(s) for {ns.lane or 'events-file'}")
        return 0
    except (urllib.error.URLError, OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"::warning title=lane-events::{type(exc).__name__}: {str(exc)[:300]}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    sys.exit(main())
