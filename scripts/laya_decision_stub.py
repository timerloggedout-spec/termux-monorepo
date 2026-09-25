#!/usr/bin/env python3
"""Thin Laya-shaped decision stub for monorepo integration tests.

Canonical upstream: https://github.com/NandhaKishorM/laya
Does not require the `laya` package. When installed, --live uses Router.predict;
otherwise deterministic offline mocks (CI-safe, no weight download).

See refTemplates/16_Org_Phased/laya/
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def mock_predict(state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    """Deterministic offline stand-in aligned with upstream answer shapes."""
    answers: dict[str, Any] = {}
    for key, q in questions.items():
        qtype = (q or {}).get("type", "noul")
        if qtype == "choice":
            criteria = list(((q or {}).get("criteria") or {}).keys()) or ["unknown"]
            pick = criteria[0]
            dist = {c: (0.7 if c == pick else 0.3 / max(len(criteria) - 1, 1)) for c in criteria}
            answers[key] = {
                "choice": pick,
                "distribution": dist,
                "confidence": 0.7,
            }
        elif qtype == "score":
            levels = (q or {}).get("criteria") or ["low", "medium", "high"]
            mid = float(len(levels) // 2)
            answers[key] = {"score": mid, "confidence": 0.6}
        else:
            answers[key] = {"noul": 0.5, "confidence": 0.5}
    return {
        "answers": answers,
        "routing": {"model": "mock", "reason": "offline stub; install laya for live"},
        "mode": "mock",
    }


def live_predict(state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    try:
        from laya import Router  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            f"laya package not installed: {exc}\n"
            "pip install laya  # from https://github.com/NandhaKishorM/laya"
        ) from exc
    router = Router(preload=False)
    return router.predict(state, questions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Use installed laya package")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    state = {
        "subject": "Duplicate charge on invoice #4411",
        "body": "We were billed twice. Please refund or we will cancel.",
    }
    questions = {
        "department": {
            "type": "choice",
            "instructions": "Which department should handle this request?",
            "criteria": {
                "billing": "invoices, payments, refunds",
                "technical": "bugs, outages",
                "sales": "pricing, contracts",
                "other": "everything else",
            },
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is this request?",
            "criteria": ["not urgent", "soon", "critical deadline or blocking issue"],
        },
        "churn_risk": {
            "type": "noul",
            "instructions": "Does the user threaten to cancel or leave?",
        },
    }

    result = live_predict(state, questions) if args.live else mock_predict(state, questions)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
        print("OK: laya decision stub (mock)" if not args.live else "OK: laya live predict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
