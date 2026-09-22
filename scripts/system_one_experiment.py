#!/usr/bin/env python3
"""Run bounded System One decision-engine experiments."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DecisionReceipt:
    schema_version: str
    experiment_id: str
    cohort_id: str
    lane_id: str
    engine: str
    policy_version: str
    status: str
    decision: dict[str, Any]
    confidence: float | None
    latency_ms: float
    failure_class: str | None = None


def deterministic_decision(state: dict[str, Any]) -> dict[str, Any]:
    """Transparent control policy; deliberately non-semantic."""
    body = str(state.get("body", "")).lower()
    if any(word in body for word in ("cancel", "outage", "blocked", "critical")):
        return {"route": "escalate", "confidence": 0.99}
    if any(word in body for word in ("refund", "invoice", "payment")):
        return {"route": "billing", "confidence": 0.99}
    return {"route": "general", "confidence": 0.99}


def run_laya_stub() -> dict[str, Any]:
    completed = subprocess.run(
        ["python3", str(ROOT / "scripts/laya_decision_stub.py"), "--json"],
        cwd=ROOT, check=False, capture_output=True, text=True, timeout=30,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "laya stub failed")
    return json.loads(completed.stdout)


def normalize_laya(raw: dict[str, Any]) -> dict[str, Any]:
    answer = raw.get("answers", {}).get("department", {})
    confidence = answer.get("confidence")
    return {
        "route": answer.get("choice") or "unknown",
        "confidence": float(confidence) if confidence is not None else None,
        "raw": raw,
    }


def run_lane(
    lane_id: str, engine: str, policy_version: str, state: dict[str, Any],
    experiment_id: str, cohort_id: str,
) -> DecisionReceipt:
    started = time.perf_counter()
    try:
        if engine == "deterministic":
            decision = deterministic_decision(state)
        elif engine == "laya":
            decision = normalize_laya(run_laya_stub())
        elif engine == "jev":
            return DecisionReceipt(
                "system-one.v1", experiment_id, cohort_id, lane_id, engine,
                policy_version, "UNAVAILABLE", {}, None,
                (time.perf_counter() - started) * 1000, "ENGINE_UNAVAILABLE",
            )
        else:
            raise ValueError(f"unknown engine: {engine}")
        return DecisionReceipt(
            "system-one.v1", experiment_id, cohort_id, lane_id, engine,
            policy_version, "OK", decision, decision.get("confidence"),
            (time.perf_counter() - started) * 1000,
        )
    except subprocess.TimeoutExpired:
        return DecisionReceipt(
            "system-one.v1", experiment_id, cohort_id, lane_id, engine,
            policy_version, "FAILED", {}, None,
            (time.perf_counter() - started) * 1000, "ENGINE_ERROR",
        )
    except (OSError, RuntimeError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return DecisionReceipt(
            "system-one.v1", experiment_id, cohort_id, lane_id, engine,
            policy_version, "FAILED", {"error": str(exc)}, None,
            (time.perf_counter() - started) * 1000, "ENGINE_ERROR",
        )


def run_experiment(cohort_id: str, state: dict[str, Any]) -> list[DecisionReceipt]:
    experiment_id = f"system-one:{cohort_id}"
    lanes = [
        ("A", "deterministic", "M0-control"),
        ("B", "laya", "M1-fast-gate"),
        ("C", "jev", "M1-fast-gate"),
    ]
    return [
        run_lane(lane, engine, policy, state, experiment_id, cohort_id)
        for lane, engine, policy in lanes
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", default="local-smoke")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()
    state = {
        "subject": "Duplicate charge on invoice #4411",
        "body": "We were billed twice. Please refund or we will cancel.",
    }
    payload = "\n".join(
        json.dumps(asdict(r), sort_keys=True)
        for r in run_experiment(args.cohort, state)
    ) + "\n"
    if args.output == "-":
        print(payload, end="")
    else:
        Path(args.output).write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
