#!/usr/bin/env python3
"""Canny-style completion gate for dual-gate / adaptive-wait.

Pattern from qkal/Canny (Reddit top-20 #19):
  Facts → code (ledger, exit codes, diffs). Only facts hard-block.
  Judgments → decision engine (noul). Engine only advises / relaxes.

Zero runtime deps for the fact path. Optional noul via decision_engines
or any System One–compatible endpoint.

Production use: agent "I am done" claims, PR dual-gate evidence,
adaptive-wait completion. Never YOLO.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

# Fact kinds that can hard-block (deterministic, no engine required)
FACT_KINDS = frozenset(
    {
        "file_changed",
        "command_exit_nonzero",
        "command_failed_repeat",
        "test_failed",
        "secret_detected",
        "diff_empty",
        "check_not_run_since_edit",
    }
)


def evaluate_facts(facts: list[dict[str, Any]]) -> dict[str, Any]:
    """Deterministic fact evaluation. Only facts can hard-block."""
    blocks: list[dict[str, Any]] = []
    for f in facts:
        if not f:
            continue
        kind = f.get("kind")
        if kind not in FACT_KINDS:
            continue
        if kind == "command_exit_nonzero":
            if int(f.get("exit_code") or 0) != 0:
                blocks.append({"kind": kind, "detail": f.get("detail") or f.get("cmd")})
        elif kind == "test_failed":
            blocks.append({"kind": kind, "detail": f.get("detail")})
        elif kind == "command_failed_repeat":
            if int(f.get("count") or 0) >= 2:
                blocks.append({"kind": kind, "detail": f.get("detail")})
        elif kind == "secret_detected":
            blocks.append({"kind": kind, "detail": "redacted"})
        elif kind == "diff_empty":
            if f.get("claimed_done"):
                blocks.append({"kind": kind, "detail": "no diff since claim"})
        elif kind == "check_not_run_since_edit":
            blocks.append({"kind": kind, "detail": f.get("check") or "required check"})
    return {
        "hard_block": bool(blocks),
        "blocks": blocks,
        "fact_count": len(facts),
        "mode": "facts_only",
    }


def mock_noul_advice(claim: str, state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Offline stand-in for engine noul on 'is completion claim supported?'."""
    evidence = (state or {}).get("evidence") or []
    # Single-pass evidence classification with early exit on adverse facts
    adverse = False
    has_positive = False
    for e in evidence:
        if not e:
            continue
        k = e.get("kind")
        if k == "test_failed" or k == "secret_detected" or (k == "command_exit_nonzero" and int(e.get("exit_code") or 0) != 0):
            adverse = True
            break
        if k == "file_changed" or (k == "command_exit_nonzero" and int(e.get("exit_code") or 0) == 0):
            has_positive = True

    supported = has_positive and not adverse
    noul = 0.72 if supported else 0.28
    return {
        "noul": noul,
        "confidence": 0.55,
        "advice": "relax_allowed" if noul >= 0.6 else "hold_for_evidence",
        "mode": "mock_noul",
        "claim_snippet": (claim or "")[:120],
    }


def gate(
    claim: str,
    facts: list[dict[str, Any]] | None = None,
    state: dict[str, Any] | None = None,
    use_noul: bool = True,
) -> dict[str, Any]:
    """Full gate: facts first (hard-block), optional noul advice second."""
    facts = facts or []
    fact_result = evaluate_facts(facts)
    out: dict[str, Any] = {
        "engine_id": "canny_pattern",
        "claim": (claim or "")[:200],
        "hard_block": fact_result["hard_block"],
        "blocks": fact_result["blocks"],
        "ts": int(time.time()),
        "dense_feedback": {
            "ledger_entry": True,
            "fact_block": fact_result["hard_block"],
            "reason": "facts_hard_block" if fact_result["hard_block"] else "facts_clear",
        },
    }
    if fact_result["hard_block"]:
        out["decision"] = "BLOCK"
        out["dense_feedback"]["noul_advice"] = None
        return out

    if use_noul:
        advice = mock_noul_advice(claim, state)
        out["noul_advice"] = advice
        out["dense_feedback"]["noul_advice"] = advice.get("advice")
        out["dense_feedback"]["confidence"] = advice.get("confidence")
        if advice.get("advice") == "hold_for_evidence":
            out["decision"] = "HOLD"
            out["dense_feedback"]["reason"] = "noul_hold"
        else:
            out["decision"] = "ALLOW"
            out["dense_feedback"]["reason"] = "facts_clear_noul_relax"
    else:
        out["decision"] = "ALLOW"
        out["dense_feedback"]["reason"] = "facts_clear_no_noul"
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim", default="I am done; tests passed.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-noul", action="store_true")
    parser.add_argument(
        "--demo-block",
        action="store_true",
        help="Inject a failing test fact for demo",
    )
    args = parser.parse_args()

    facts: list[dict[str, Any]] = []
    if args.demo_block:
        facts.append(
            {
                "kind": "test_failed",
                "detail": "pytest exit 1 on scripts/decision_engines.py",
            }
        )
    else:
        facts.append({"kind": "file_changed", "paths": ["scripts/decision_engines.py"]})
        facts.append({"kind": "command_exit_nonzero", "exit_code": 0, "cmd": "pytest -q"})

    state = {"evidence": facts}
    result = gate(
        claim=args.claim,
        facts=facts,
        state=state,
        use_noul=not args.no_noul,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.json:
        print(
            f"OK: canny_completion_gate decision={result.get('decision')}",
            file=sys.stderr,
        )
    return 1 if result.get("decision") == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
