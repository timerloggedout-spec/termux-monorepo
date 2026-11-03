#!/usr/bin/env python3
"""Project invocation observations into the public Free-Tier Value Board.

This is a strict projection, not a validator of upstream Basksweep evidence.
Only rows carrying every publication gate and exact call/model/token identity
are published as sessions. All other observations remain coverage/withheld
metadata; missing values are never coerced to zero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "3l0.free-tier-use-value.v1"
GATES = {
    "validation_status": "VALIDATED",
    "basksweep_status": "PASS",
    "publication_status": "PUBLIC_SAFE",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"observation line {number} must be an object")
        rows.append(item)
    return rows


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def safe_session(row: dict[str, Any], pricing: list[dict[str, Any]]) -> dict[str, Any] | None:
    if any(row.get(key) != expected for key, expected in GATES.items()):
        return None
    required = ("call_uid", "run_id", "run_attempt", "provider", "model_id",
                "model_version_pin", "tokens_in", "tokens_out", "outcome_status")
    if any(row.get(key) in (None, "") for key in required):
        return None
    if not nonnegative_int(row["tokens_in"]) or not nonnegative_int(row["tokens_out"]):
        return None
    if row["outcome_status"] not in ("SUCCESS", "SUCCEEDED"):
        return None
    if row.get("billing_status") != "VERIFIED_NO_COST":
        return None
    price = next((p for p in pricing
                  if p.get("canonical_model_id") == row.get("canonical_model_id")
                  and p.get("pricing_id") == row.get("pricing_id")), None)
    if price is None:
        return None
    input_rate = price.get("input_usd_per_million")
    output_rate = price.get("output_usd_per_million")
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) or v < 0 for v in (input_rate, output_rate)):
        return None
    paid_equivalent = (
        row["tokens_in"] * input_rate + row["tokens_out"] * output_rate
    ) / 1_000_000
    actual_cost = row.get("cost_usd")
    if actual_cost is not None and (isinstance(actual_cost, bool) or not isinstance(actual_cost, (int, float)) or not math.isfinite(actual_cost) or actual_cost < 0):
        return None
    if actual_cost is not None and actual_cost != 0:
        return None
    return {
        "session_label": row.get("session_label") or row["call_uid"],
        "run_uid": f"gha:{row.get('repository', '')}:{row['run_id']}:{row['run_attempt']}",
        "call_uid": row["call_uid"],
        "provider": row["provider"],
        "model_id": row["model_id"],
        "model_version_pin": row["model_version_pin"],
        "input_tokens": row["tokens_in"],
        "output_tokens": row["tokens_out"],
        "outcome_status": row["outcome_status"],
        "validation_status": row["validation_status"],
        "basksweep_status": row["basksweep_status"],
        "publication_status": row["publication_status"],
        "billing_status": row.get("billing_status", "UNKNOWN"),
        "cost_usd": row.get("cost_usd"),
        "paid_equivalent_usd": round(paid_equivalent, 10),
        "pricing_id": row["pricing_id"],
        "source_sha": row.get("source_sha") or row.get("head_sha"),
        "source_run_attempt": f"{row['run_id']}:{row['run_attempt']}",
        "observed_at": row.get("timestamp"),
        "evidence_url": row.get("evidence_url"),
    }


def build(root: Path, observations_path: Path, source_sha: str | None) -> dict[str, Any]:
    board_path = root / "apps/tribute-dashboard/data/free-tier-value.json"
    board = read_json(board_path, {})
    if board.get("schema") != SCHEMA:
        raise ValueError("unexpected board schema")
    source_rows = read_ndjson(observations_path)
    pricing = board.get("pricing", [])
    sessions, coverage = [], []
    seen = set()
    for row in source_rows:
        run_id, attempt = row.get("run_id"), row.get("run_attempt")
        request_id = row.get("request_id")
        call_uid = row.get("call_uid")
        identity = (str(run_id), str(attempt), str(call_uid or request_id or ""))
        reason = "missing_call_identity"
        if identity in seen:
            reason = "duplicate_call_identity"
        else:
            seen.add(identity)
            if call_uid:
                session = safe_session(row, pricing)
                if session:
                    sessions.append(session)
                    reason = "published"
                else:
                    reason = "publication_gates_or_exact_model_pricing_or_verified_no_cost_not_established"
        coverage.append({
            "run_id": run_id,
            "run_attempt": attempt,
            "provider": row.get("provider"),
            "model_id": row.get("requested_model") or row.get("model_id"),
            "response_model": row.get("response_model"),
            "role": row.get("role"),
            "source_sha": row.get("head_sha") or row.get("source_sha"),
            "tokens_in": row.get("tokens_in"),
            "tokens_out": row.get("tokens_out"),
            "actual_cost_usd": row.get("cost_usd"),
            "native_quota_unit": "requests",
            "native_quota_value": row.get("requests_used"),
            "evidence_status": reason,
            "instance_status": "NOT_ESTABLISHED",
            "model_version_status": "NOT_ESTABLISHED" if not row.get("model_version_pin") else "ESTABLISHED",
        })
    board["sessions"] = sessions
    board["coverage"] = coverage
    board["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    board["source_sha"] = source_sha
    board["source_manifest"] = {
        "observations_path": str(observations_path),
        "observations_sha256": sha256_file(observations_path) if observations_path.exists() else None,
        "observation_count": len(source_rows),
        "published_session_count": len(sessions),
        "withheld_count": len(coverage) - len(sessions),
        "publication_policy": "all three validation/Basksweep/publication gates plus exact call, run-attempt, pinned model, token and pricing identities",
    }
    return board


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--source-sha", default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    result = build(args.root, args.observations, args.source_sha)
    output = args.out or args.root / "apps/tribute-dashboard/data/free-tier-value.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps(result["source_manifest"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
