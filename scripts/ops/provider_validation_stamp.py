#!/usr/bin/env python3
"""Emit per-provider no-cost validation receipts through the canonical Swarm stamp fan-out."""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


def build_stamp(receipt: dict, *, run_id: str, run_attempt: str, run_url: str, experiment_label: str) -> dict:
    if receipt.get("schema") != "provider-inference-validation/v1":
        raise ValueError("invalid_receipt_schema")
    provider = receipt.get("provider")
    if not isinstance(provider, str) or not provider:
        raise ValueError("receipt_provider_missing")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}", experiment_label):
        raise ValueError("experiment_label_invalid")
    if receipt.get("experiment_label") != experiment_label:
        raise ValueError("receipt_experiment_label_mismatch")
    if not isinstance(receipt.get("observed_at"), str) or not receipt["observed_at"]:
        raise ValueError("receipt_timestamp_missing")
    status = receipt.get("validation_status")
    outcome_status = {
        "inference_validated": "completed",
        "failed": "failed",
        "deferred": "deferred",
    }.get(status)
    if outcome_status is None:
        raise ValueError("receipt_validation_status_invalid")
    no_cost = receipt.get("no_cost_verified") is True
    confirmed = True if status == "inference_validated" else (False if status == "failed" else None)
    model = receipt.get("model")
    diagnosis = str(receipt.get("diagnosis") or "").replace("\\n", " ")[:240]
    return {
        "dispatch_id": f"provider-validation-{run_id}-{run_attempt}-{provider}",
        "ts": receipt.get("observed_at"),
        "task_class": "inference-probe",
        "entry": "5454",
        "trigger": "workflow_dispatch",
        "provider": provider,
        "model": model,
        "role": "validator",
        "moniker": "optimizations-assurance",
        "context": f"QUE #5454 free-only provider validation; experiment={experiment_label}",
        "run": {"workflow": "provider-inference-validation.yml", "run_id": run_id, "session_id": None},
        "outcome": {
            "status": outcome_status,
            "summary": f"{status}; inference={receipt.get('inference_status')}; diagnosis={diagnosis}",
            "artifact": run_url,
            "gate_call": "catalog-verified-free-only" if no_cost else "no-cost-not-established",
            "confirmed": confirmed,
        },
        "quota": {"pool": receipt.get("pool_id") or provider,
                  "cost_class": "free-tier" if no_cost else "not_established", "slice": None},
        "usage": {"status": "not_established", "value": None, "unit": None, "source": None,
                  "latency_ms": receipt.get("latency_ms"), "retries": 0},
        "arm_state": "live" if status == "inference_validated" else ("degraded" if status == "failed" else "unknown"),
        "selection": {"scout": "provider-inference-validation", "manager": "QUE",
                      "request": "5454", "arm": provider,
                      "basis": "current Actions no-cost invocation receipt",
                      "talent_class": "native-provider", "exploration": False},
        "origin": "live",
    }


def dispatch_stamp(stamp: dict, *, repository: str, token: str, opener=urllib.request.urlopen) -> int:
    url = f"https://api.github.com/repos/{repository}/actions/workflows/dispatch-stamp-fanout.yml/dispatches"
    payload = json.dumps({"ref": "master", "inputs": {"stamp": json.dumps(stamp), "phase": "dispatch"}}).encode()
    request = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    })
    try:
        with opener(request, timeout=20) as response:
            return int(getattr(response, "status", 204))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"stamp_dispatch_http_{exc.code}") from None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts-dir", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--experiment-label", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    token = os.environ.get("GH_TOKEN", "")
    if not args.dry_run and not token:
        parser.error("GH_TOKEN is required unless --dry-run is set")
    paths = sorted(Path(args.receipts_dir).glob("*/receipt.json"))
    if not paths:
        print("no validation receipts found; no stamps emitted")
        return 0
    emitted = 0
    for path in paths:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        stamp = build_stamp(receipt, run_id=args.run_id, run_attempt=args.run_attempt,
                            run_url=args.run_url, experiment_label=args.experiment_label)
        if args.dry_run:
            print(json.dumps(stamp, sort_keys=True))
        else:
            status = dispatch_stamp(stamp, repository=args.repository, token=token)
            if status not in (200, 201, 202, 204):
                raise RuntimeError(f"stamp_dispatch_unexpected_status_{status}")
            print(f"stamped provider={receipt['provider']} status={receipt['validation_status']}")
            emitted += 1
            time.sleep(1)
    print(f"provider_validation_stamps_emitted={emitted}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
