#!/usr/bin/env python3
"""Project invocation observations into the public Free-Tier Value Board.

This is a strict projection, not an upstream evidence validator. Incomplete
observations remain coverage rows. Counterfactual value is calculated with
decimal arithmetic and is never represented as actual provider spend.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
from typing import Any

SCHEMA = "3l0.free-tier-use-value.v1"
VALUE_QUANTUM = Decimal("0.0000000001")
GATES = {
    "validation_status": "VALIDATED",
    "basksweep_status": "PASS",
    "publication_status": "PUBLIC_SAFE",
}


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant: {value}")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal,
                      parse_constant=_reject_constant)


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    rows = []
    if not path.exists():
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        item = json.loads(line, parse_float=Decimal, parse_constant=_reject_constant)
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


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def decimal_rate(value: Any) -> Decimal | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return rate if rate.is_finite() and rate >= 0 else None


def exact_price(pricing: list[dict[str, Any]], canonical_model_id: str,
                pricing_id: str) -> tuple[Decimal, Decimal] | None:
    matches = [p for p in pricing
               if p.get("canonical_model_id") == canonical_model_id
               and p.get("pricing_id") == pricing_id]
    # Ambiguous price identities are not resolved by row order.
    if len(matches) != 1:
        return None
    input_rate = decimal_rate(matches[0].get("input_usd_per_million"))
    output_rate = decimal_rate(matches[0].get("output_usd_per_million"))
    if input_rate is None or output_rate is None:
        return None
    return input_rate, output_rate


def safe_session(row: dict[str, Any], pricing: list[dict[str, Any]]) -> dict[str, Any] | None:
    if any(row.get(key) != expected for key, expected in GATES.items()):
        return None
    required_strings = ("call_uid", "run_id", "repository", "provider", "model_id",
                        "model_version_pin", "canonical_model_id", "pricing_id")
    if any(not nonempty_string(row.get(key)) for key in required_strings):
        return None
    if not nonnegative_int(row.get("run_attempt")) or row["run_attempt"] < 1:
        return None
    if not nonnegative_int(row.get("tokens_in")) or not nonnegative_int(row.get("tokens_out")):
        return None
    if row.get("outcome_status") not in ("SUCCESS", "SUCCEEDED"):
        return None
    if row.get("billing_status") != "VERIFIED_NO_COST":
        return None

    rates = exact_price(pricing, row["canonical_model_id"], row["pricing_id"])
    if rates is None:
        return None
    input_rate, output_rate = rates

    actual_cost = row.get("cost_usd")
    if actual_cost is not None:
        actual_cost_decimal = decimal_rate(actual_cost)
        if actual_cost_decimal is None or actual_cost_decimal != 0:
            return None

    # Decimal avoids binary-float drift. Quantize only once, at the published
    # display precision; ROUND_HALF_UP is explicit and deterministic.
    with localcontext() as ctx:
        ctx.prec = 50
        paid_equivalent = (
            Decimal(row["tokens_in"]) * input_rate
            + Decimal(row["tokens_out"]) * output_rate
        ) / Decimal(1_000_000)
        paid_equivalent = paid_equivalent.quantize(VALUE_QUANTUM, rounding=ROUND_HALF_UP)

    return {
        "session_label": row.get("session_label") or row["call_uid"],
        "run_uid": f"gha:{row['repository']}:{row['run_id']}:{row['run_attempt']}",
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
        "billing_status": row["billing_status"],
        "cost_usd": actual_cost,
        "paid_equivalent_usd": float(paid_equivalent),
        "pricing_id": row["pricing_id"],
        "source_sha": row.get("source_sha") or row.get("head_sha"),
        "source_run_attempt": f"{row['run_id']}:{row['run_attempt']}",
        "observed_at": row.get("timestamp"),
        "evidence_url": row.get("evidence_url"),
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"unsupported JSON value: {type(value).__name__}")


def build(root: Path, observations_path: Path, source_sha: str | None) -> dict[str, Any]:
    board_path = root / "apps/tribute-dashboard/data/free-tier-value.json"
    board = read_json(board_path, {})
    if board.get("schema") != SCHEMA:
        raise ValueError("unexpected board schema")
    source_rows = read_ndjson(observations_path)
    pricing = board.get("pricing", [])
    if not isinstance(pricing, list) or any(not isinstance(p, dict) for p in pricing):
        raise ValueError("board pricing must be a list of objects")

    sessions, coverage = [], []
    seen: set[tuple[str, str, str, str]] = set()
    for row in source_rows:
        run_id, attempt = row.get("run_id"), row.get("run_attempt")
        repository = row.get("repository")
        request_id = row.get("request_id")
        call_uid = row.get("call_uid")
        identity_atom = call_uid or request_id
        identity = (str(repository), str(run_id), str(attempt), str(identity_atom or ""))
        reason = "missing_call_identity"
        if identity in seen:
            reason = "duplicate_call_identity"
        else:
            seen.add(identity)
            if nonempty_string(call_uid):
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
        "publication_policy": "all three validation/Basksweep/publication gates plus exact call, run-attempt, pinned model, token and unambiguous pricing identities and verified no-cost evidence",
        "value_precision_usd": "0.0000000001",
        "value_rounding": "ROUND_HALF_UP",
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
    output.write_text(json.dumps(result, indent=2, sort_keys=False, default=_json_default) + "\\n",
                      encoding="utf-8")
    print(json.dumps(result["source_manifest"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
