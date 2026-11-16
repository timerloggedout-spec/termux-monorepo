#!/usr/bin/env python3
"""Create append-only accountability receipts for historical/future sweeps.

Stdlib only. Existing immutable receipts are never overwritten.
"""
from __future__ import annotations
import argparse, hashlib, json, os, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "sweep.accountability.v1"
DEFAULT_OUT = "docs/ops/generated/sweep-ledger"

def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def make_receipt(args: argparse.Namespace) -> dict[str, Any]:
    started = args.started_at or now()
    completed = args.completed_at or now()
    findings = json.loads(args.findings)
    actions = json.loads(args.actions)
    effects = json.loads(args.effects)
    sources = json.loads(args.sources)
    provenance = json.loads(args.provenance)
    scope = {
        "repository": args.repository, "ref": args.ref, "from": args.from_time,
        "to": args.to_time, "query": args.query, "cursor": args.cursor, "sources": sources,
    }
    input_snapshot = {"scope": scope, "sources": sources, "query": args.query, "cursor": args.cursor}
    return {
        "schema_version": SCHEMA_VERSION,
        "sweep_id": args.sweep_id or str(uuid.uuid4()),
        "parent_sweep_id": args.parent_sweep_id,
        "sweep_version": args.sweep_version,
        "iteration": args.iteration,
        "mode": args.mode,
        "scope": scope,
        "started_at": started,
        "completed_at": completed,
        "status": args.status,
        "coverage": {
            "state": args.coverage, "observed": args.observed, "expected": args.expected,
            "next_cursor": args.next_cursor, "reason": args.coverage_reason,
        },
        "provenance": {**provenance, "input_sha256": sha256_json(input_snapshot)},
        "findings": findings, "actions": actions, "effects": effects,
        "errors": json.loads(args.errors),
        "next": {
            "sweep_version": args.next_sweep_version or args.sweep_version,
            "iteration": args.iteration + 1,
            "cursor": args.next_cursor,
            "start": args.to_time or completed,
        },
    }

def write_receipt(receipt: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    day = receipt["started_at"][:10]
    sweep_id = receipt["sweep_id"]
    immutable = out_dir / f"{sweep_id}.json"
    if immutable.exists():
        raise FileExistsError(f"refusing to overwrite receipt: {immutable}")
    line = json.dumps(receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    with (out_dir / f"{day}.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    immutable.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return immutable

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repository", required=True)
    ap.add_argument("--sweep-version", default="v1")
    ap.add_argument("--iteration", type=int, default=0)
    ap.add_argument("--mode", choices=("HISTORICAL","CONTINUOUS","RECONCILIATION","CORRECTION"), required=True)
    ap.add_argument("--status", choices=("RUNNING","SUCCESS","PARTIAL","FAILED","CANCELLED","NOOP"), default="SUCCESS")
    ap.add_argument("--coverage", choices=("COMPLETE","PARTIAL","UNKNOWN"), default="UNKNOWN")
    ap.add_argument("--observed", type=int, default=0)
    ap.add_argument("--expected", type=int)
    ap.add_argument("--ref")
    ap.add_argument("--from", dest="from_time")
    ap.add_argument("--to", dest="to_time")
    ap.add_argument("--query", default="")
    ap.add_argument("--cursor")
    ap.add_argument("--next-cursor")
    ap.add_argument("--coverage-reason")
    ap.add_argument("--parent-sweep-id")
    ap.add_argument("--next-sweep-version")
    ap.add_argument("--sweep-id")
    ap.add_argument("--sources", default="[]")
    ap.add_argument("--provenance", default="{}")
    ap.add_argument("--findings", default="[]")
    ap.add_argument("--actions", default="[]")
    ap.add_argument("--effects", default="[]")
    ap.add_argument("--errors", default="[]")
    ap.add_argument("--started-at")
    ap.add_argument("--completed-at")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    args = ap.parse_args()
    receipt = make_receipt(args)
    path = write_receipt(receipt, Path(args.out_dir))
    print(json.dumps({"receipt": str(path), "sweep_id": receipt["sweep_id"], "schema_version": SCHEMA_VERSION}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
