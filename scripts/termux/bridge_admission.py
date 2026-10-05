#!/usr/bin/env python3
"""Classify the Termux bridge manifest without printing secrets or endpoints."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("endpoint", "port", "ssh_user", "expires_at")


def classify(manifest: dict, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    status = manifest.get("status")
    missing = [key for key in REQUIRED if not manifest.get(key)]
    expired = False
    port_ok = False
    expires_at = manifest.get("expires_at")
    if expires_at:
        try:
            expires = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            expired = expires <= now
        except ValueError:
            missing.append("expires_at")
    port = manifest.get("port")
    try:
        port_ok = port is not None and 1 <= int(port) <= 65535
    except (TypeError, ValueError):
        port_ok = False
    admitted = status == "active" and not missing and not expired and port_ok
    if admitted:
        reason = "admitted"
    elif status != "active":
        reason = "status_not_active"
    elif missing:
        reason = "incomplete"
    elif expired:
        reason = "expired"
    else:
        reason = "port_out_of_range"
    return {
        "admitted": admitted,
        "reason": reason,
        "status": status,
        "missing": missing,
        "expired": expired,
        "stale_reason": manifest.get("stale_reason"),
    }


def write_receipt(path: Path, manifest: dict, verdict: dict, meta: dict) -> None:
    payload = {
        "schema_version": 1,
        "run_id": meta.get("run_id"),
        "run_attempt": meta.get("run_attempt"),
        "sha": meta.get("sha"),
        "ref": meta.get("ref"),
        "event_name": meta.get("event_name"),
        "bridge": {
            "status": manifest.get("status"),
            "port": manifest.get("port"),
            "expires_at": manifest.get("expires_at"),
            "stale_reason": manifest.get("stale_reason"),
        },
        "checks": [verdict],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--skip-file", default="deepcli-bridge-skip")
    parser.add_argument("--event-name", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-attempt", default="")
    parser.add_argument("--sha", default="")
    parser.add_argument("--ref", default="")
    args = parser.parse_args(argv)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    verdict = classify(manifest)
    write_receipt(
        Path(args.receipt),
        manifest,
        verdict,
        {
            "run_id": args.run_id,
            "run_attempt": args.run_attempt,
            "sha": args.sha,
            "ref": args.ref,
            "event_name": args.event_name,
        },
    )
    if verdict["admitted"]:
        print(f"bridge admission admitted status={verdict['status']}")
        return 0
    message = (
        "ACCESS/ADMISSION FAILURE: "
        f"reason={verdict['reason']} status={verdict['status']!r} "
        f"missing={verdict['missing']}"
    )
    Path(args.skip_file).write_text(message + "\n", encoding="utf-8")
    if args.event_name == "workflow_dispatch":
        print(f"::error::{message}")
        return 1
    print(f"::warning::{message}; SSH dispatch skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
