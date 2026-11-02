#!/usr/bin/env python3
"""VM workspace backup events -> Telemetry MEASUREMENT records.

Owner direction 2026-11-01: backup events become telemetry measurement
records {state_hash, export_id, publish_commit (backup repo), relay_commit
(monorepo), at}, joined to the monorepo commit stream by hash + time so
backup state is correlatable with the commit stream like every other
plane.

Source of record = Tracking lane's feed `ops/tracking/backup-relays.jsonl`
(backup-state/v1; the dashboard render source — telemetry READS it as
intake, never forks its numbers). Output = append-only
`ops/telemetry/backup-measurements.jsonl` (schema backup-measurement/v1),
immutable intake per DoE rule 8: idempotent on evidence_hash (sha256 of
the canonical source line); existing records are never rewritten.

relay_commit resolution: the monorepo commit that appended the source
line (commits API, path-filtered, oldest-append order). Resolved once,
then carried in the record forever. When the API is unavailable the
record ships with relay_commit = null + join state noted, and a later
run back-resolves it by APPENDING nothing — resolution only happens for
records not yet emitted (immutability wins over completeness).

Usage: backup_events.py --relays ops/tracking/backup-relays.jsonl
         --out ops/telemetry/backup-measurements.jsonl
         --receipt ops/telemetry/backup-measurements-receipt.json
         [--relay-map relay_map.json]   # {line_index: relay_sha}
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

SCHEMA = "backup-measurement/v1"
REPO = "timerloggedout-spec/termux-monorepo"
RELAYS_PATH = "ops/tracking/backup-relays.jsonl"


def evidence_hash(line: str) -> str:
    return hashlib.sha256(line.strip().encode("utf-8")).hexdigest()


def resolve_relay_map(token: str) -> dict:
    """{line_index: relay_commit_sha} from the commits that touched the
    relays file, oldest first (each append commit adds its line)."""
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/commits?path={RELAYS_PATH}&per_page=100",
        method="GET")
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.build_opener().open(req, timeout=60) as resp:
        commits = json.loads(resp.read())
    out = {}
    for i, c in enumerate(reversed(commits)):
        out[i] = c["sha"]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relays", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--relay-map")
    ap.add_argument("--mode", default="live", choices=["live", "backfill"])
    args = ap.parse_args()

    lines = [l for l in open(args.relays, encoding="utf-8").read().splitlines()
             if l.strip()]
    existing = []
    if os.path.exists(args.out):
        existing = [json.loads(l) for l in open(args.out, encoding="utf-8")
                    if l.strip()]
    have = {r["evidence_hash"] for r in existing}

    relay_map = {}
    if args.relay_map:
        relay_map = {int(k): v for k, v in
                     json.load(open(args.relay_map)).items()}
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
        if token:
            try:
                relay_map = resolve_relay_map(token)
            except Exception:
                relay_map = {}

    new = []
    for i, line in enumerate(lines):
        eh = evidence_hash(line)
        if eh in have:
            continue
        src = json.loads(line)
        rec = {
            "schema": SCHEMA,
            "kind": src.get("kind"),
            "at": src.get("at"),
            "state_hash": src.get("state_hash"),
            "export_id": src.get("export_id"),
            "publish_commit": src.get("publish_commit"),
            "publish_repo": ("timerloggedout-spec/muse-vm-workspace-backup"
                             if src.get("publish_commit") else None),
            "relay_commit": relay_map.get(i),
            "relay_repo": REPO,
            "join": {
                "by": "relay_commit (append commit) + at (event time)",
                "relay_resolved": i in relay_map,
                "stream": "monorepo master commits",
            },
            "origin": f"{args.mode}{{backup-events}}",
            "evidence_hash": eh,
        }
        new.append(rec)

    if new:
        with open(args.out, "a", encoding="utf-8") as fh:
            for rec in new:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    total = existing + new
    receipt = {
        "schema": SCHEMA,
        "source_feed": RELAYS_PATH,
        "source_owner": "tracking lane (backup-state/v1 render source)",
        "records_total": len(total),
        "records_new": len(new),
        "by_kind": {},
        "relay_resolved": sum(1 for r in total
                              if r["join"]["relay_resolved"]),
        "with_publish_commit": sum(1 for r in total if r["publish_commit"]),
    }
    for r in total:
        receipt["by_kind"][r["kind"]] = receipt["by_kind"].get(r["kind"], 0) + 1
    with open(args.receipt, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
