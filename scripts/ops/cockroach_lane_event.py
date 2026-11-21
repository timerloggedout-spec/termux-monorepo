#!/usr/bin/env python3
"""Append canonical lane events to an optional CockroachDB continuity projection.

Credential: COCKROACH_DATABASE_URL (PostgreSQL wire-protocol URI).
The writer reuses lane_event.py normalization and event-key identity.
Credentials stay in the process environment; connection passwords are moved
from the URI into PGPASSWORD before psql starts.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit, urlunsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SQL_DIR = ROOT / "ops" / "cockroachdb"
sys.path.insert(0, str(HERE))
from lane_event import FIELDS, load_events, normalize  # noqa: E402


def resolve_url() -> str | None:
    return os.environ.get("COCKROACH_DATABASE_URL", "").strip() or None


def connection_parts(url: str) -> tuple[str, dict[str, str]]:
    parsed = urlsplit(url)
    if parsed.scheme not in ("postgres", "postgresql") or not parsed.hostname:
        raise ValueError("COCKROACH_DATABASE_URL must be a PostgreSQL-wire URI")
    sslmode = parse_qs(parsed.query).get("sslmode", [""])[0].lower()
    test_insecure = (
        sslmode == "disable"
        and os.environ.get("CI", "").lower() == "true"
        and os.environ.get("COCKROACH_ALLOW_INSECURE_TEST") == "1"
    )
    if sslmode not in ("verify-full", "verify-ca") and not test_insecure:
        raise ValueError("CockroachDB connections require sslmode=verify-full or verify-ca")
    netloc = parsed.hostname
    if ":" in netloc and not netloc.startswith("["):
        netloc = f"[{netloc}]"
    if parsed.port:
        netloc += f":{parsed.port}"
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}"
    safe_url = urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    env: dict[str, str] = {"PGCONNECT_TIMEOUT": "15", "PGAPPNAME": "termux-cockroach-lane-events"}
    if parsed.password:
        env["PGPASSWORD"] = unquote(parsed.password)
    return safe_url, env


def psql(url: str, args: list[str]) -> str:
    safe_url, connection_env = connection_parts(url)
    env = dict(os.environ)
    env.update(connection_env)
    for attempt in range(5):
        result = subprocess.run(
            ["psql", safe_url, "-X", "-q", "-v", "ON_ERROR_STOP=1", *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # CockroachDB SERIALIZABLE transactions surface retryable conflicts as SQLSTATE 40001.
        if "40001" not in (result.stderr or "") or attempt == 4:
            raise RuntimeError(f"psql exited with status {result.returncode}")
        time.sleep(0.05 * (2 ** attempt))
    raise RuntimeError("psql retry budget exhausted")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", nargs="?", default="record", choices=("record", "count", "schema"))
    for field in FIELDS:
        ap.add_argument(f"--{field.replace('_', '-')}", dest=field, default="")
    ap.add_argument("--payload", default="")
    ap.add_argument("--events-file", default="")
    ap.add_argument("--strict", action="store_true", help="return non-zero when the sink is unavailable")
    return ap


def main(argv: list[str] | None = None) -> int:
    ns = parser().parse_args(argv)
    try:
        url = resolve_url()
        if not url:
            print("::notice title=cockroach-lane-events::COCKROACH_DATABASE_URL absent; projection skipped")
            return 1 if ns.strict else 0
        if ns.command == "schema":
            psql(url, ["-f", str(SQL_DIR / "lane-events-schema.sql")])
            print("::notice title=cockroach-lane-events::schema applied")
            return 0
        if ns.command == "count":
            count = psql(url, ["-At", "-c", "SELECT count(*) FROM lane_events"])
            print(f"COCKROACHDB_COUNT rows={count}")
            return 0
        events = load_events(ns)
        for raw in events:
            event = normalize(raw)
            args: list[str] = ["-f", str(SQL_DIR / "lane-events-insert.sql")]
            for key, value in event.items():
                args.extend(["-v", f"{key}={value}"])
            psql(url, args)
        print(f"::notice title=cockroach-lane-events::recorded {len(events)} event(s)")
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"::warning title=cockroach-lane-events::{type(exc).__name__}: {exc}")
        return 1 if ns.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
