#!/usr/bin/env python3
"""Cadence tick ledger — HFT-style per-request quota telemetry (QAC-009).

Every GitHub API response already carries x-ratelimit-{limit,used,remaining,
reset} headers: the tick exists on EVERY request instance at zero extra API
cost. Chokepoints (the PAT helper today; app-token minters and workflow
steps by adoption) append one JSONL tick per request:

  {ts, principal, session, method, endpoint, resource,
   limit, used, remaining, reset, status, counted}

`endpoint` is a normalized route class (repo + numeric segments templated).
`used` is the BUCKET's counter at that instant — deltas between consecutive
ticks of one resource measure fleet-wide burn between the two instants,
including consumers that emit no ticks. This tool validates tick files and
summarizes them into the cadence-tick-ledger/v1 feed: per-principal x
per-resource counted calls, per-endpoint counts, per-minute burn series,
and the latest remaining per resource.

Usage:
  cadence_tick_ledger.py check <ticks.jsonl> [...]
  cadence_tick_ledger.py summarize <ticks.jsonl> [...] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "cadence-tick-ledger/v1"
REQUIRED = ("ts", "principal", "method", "endpoint", "resource",
            "limit", "used", "remaining", "reset", "status", "counted")


def validate_tick(tick):
    """Return field-level audit errors for one tick; preserve valid raw evidence."""
    if not isinstance(tick, dict):
        return ["record must be a JSON object"]
    missing = [key for key in REQUIRED if key not in tick]
    if missing:
        return [f"missing fields {missing}"]
    errors = []
    for key in ("ts", "principal", "method", "endpoint"):
        if not isinstance(tick[key], str) or not tick[key].strip():
            errors.append(f"{key} must be a non-empty string")
    if tick.get("resource") is not None and (
            not isinstance(tick["resource"], str) or not tick["resource"].strip()):
        errors.append("resource must be a non-empty string or null")
    if isinstance(tick["ts"], str):
        try:
            parsed = datetime.fromisoformat(tick["ts"].replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("ts must include a timezone")
        except ValueError:
            errors.append("ts must be an ISO-8601 timestamp")
    for key in ("limit", "used", "remaining", "reset", "status"):
        value = tick[key]
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{key} must be an integer")
        elif value < 0:
            errors.append(f"{key} must be non-negative")
    if isinstance(tick["counted"], bool) is False:
        errors.append("counted must be a boolean")
    if all(isinstance(tick[k], int) and not isinstance(tick[k], bool)
           for k in ("limit", "used", "remaining")):
        if tick["remaining"] > tick["limit"]:
            errors.append("remaining exceeds limit")
    if "session" in tick and tick["session"] is not None and not isinstance(tick["session"], str):
        errors.append("session must be a string or null")
    return errors


def load_ticks(paths):
    """Read + audit tick files. Returns (valid_ticks, errors)."""
    ticks, errors, seen = [], [], set()
    for path in paths:
        for lineno, line in enumerate(Path(path).read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                tick = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{lineno}: invalid JSON: {exc}")
                continue
            problems = validate_tick(tick)
            if problems:
                errors.extend(f"{path}:{lineno}: {problem}" for problem in problems)
                continue
            identity = tuple(tick.get(k) for k in (
                "ts", "principal", "session", "method", "endpoint", "resource",
                "limit", "used", "remaining", "reset", "status", "counted"))
            if identity in seen:
                errors.append(f"{path}:{lineno}: duplicate/replayed tick identity")
                continue
            seen.add(identity)
            ticks.append(tick)
    ticks.sort(key=lambda t: t["ts"])
    return ticks, errors


def summarize(ticks):
    counted = [t for t in ticks if t["counted"]]
    by_principal_resource = Counter(
        (t["principal"], t["resource"] or "unknown") for t in counted)
    by_endpoint = Counter(t["endpoint"] for t in counted)
    per_minute = Counter(t["ts"][:16] for t in counted)
    latest = {}
    for t in ticks:
        if t["resource"] and t["remaining"] is not None:
            latest[t["resource"]] = {"remaining": t["remaining"],
                                     "limit": t["limit"], "used": t["used"],
                                     "reset": t["reset"], "at": t["ts"]}
    return {
        "schema": SCHEMA,
        "ticks_total": len(ticks),
        "ticks_counted": len(counted),
        "window": {"first": ticks[0]["ts"] if ticks else None,
                   "last": ticks[-1]["ts"] if ticks else None},
        "counted_by_principal_resource": [
            {"principal": p, "resource": r, "calls": n}
            for (p, r), n in sorted(by_principal_resource.items())],
        "counted_by_endpoint": [
            {"endpoint": e, "calls": n}
            for e, n in by_endpoint.most_common()],
        "burn_per_minute": [
            {"minute": m, "counted_calls": per_minute[m]}
            for m in sorted(per_minute)],
        "latest_remaining_by_resource": latest,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "summarize"):
        p = sub.add_parser(name)
        p.add_argument("files", nargs="+")
        if name == "summarize":
            p.add_argument("--out")
    args = ap.parse_args(argv)
    ticks, errors = load_ticks(args.files)
    for e in errors:
        print(f"ERROR {e}", file=sys.stderr)
    if args.cmd == "check":
        if errors:
            return 1
        print(json.dumps({"ok": True, "ticks": len(ticks)}))
        return 0
    feed = summarize(ticks)
    text = json.dumps(feed, indent=1, sort_keys=True)
    if getattr(args, "out", None):
        Path(args.out).write_text(text + "\n")
    print(text)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
