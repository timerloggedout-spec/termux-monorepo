#!/usr/bin/env python3
"""Thin Laya-shaped decision stub for monorepo integration tests.

Does not require the `laya` package. When `laya` is installed, --live attempts
Router.predict; otherwise uses deterministic offline mocks so CI stays green
without model downloads.

See refTemplates/16_Org_Phased/laya/NOTES.md
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def mock_predict(state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    """Deterministic offline stand-in: preference for first choice / mid score / 0.5 noul."""
    out: dict[str, Any] = {}
    for key, q in questions.items():
        qtype = (q or {}).get("type", "noul")
        if qtype == "choice":
            criteria = list(((q or {}).get("criteria") or {}).keys()) or ["unknown"]
            pick = criteria[0]
            dist = {c: (0.7 if c == pick else 0.3 / max(len(criteria) - 1, 1)) for c in criteria}
            out[key] = {"type": "choice", "value": pick, "distribution": dist, "confidence": 0.7, "mode": "mock"}
        elif qtype == "score":
            levels = (q or {}).get("criteria") or ["low", "medium", "high"]
            mid = len(levels) // 2
            out[key] = {
                "type": "score",
                "value": mid,
                "label": levels[mid] if mid < len(levels) else None,
                "confidence": 0.6,
                "mode": "mock",
            }
        else:
            out[key] = {"type": "noul", "p_true": 0.5, "confidence": 0.5, "mode": "mock"}
    return out


def live_predict(state: dict[str, Any], questions: dict[str, Any]) -> dict[str, Any]:
    try:
        from laya import Router  # type: ignore
    except ImportError as exc:
        raise SystemExit(f"laya package not installed: {exc}") from exc
    router = Router(preload=False)
    return router.predict(state, questions)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Use installed laya package")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    args = parser.parse_args()

    state = {
        "subject": "billing dispute",
        "body": "Charged twice, please refund.",
    }
    questions = {
        "queue": {
            "type": "choice",
            "instructions": "Which queue owns this?",
            "criteria": {
                "billing": "refunds, invoices",
                "infrastructure": "outages",
                "support": "general",
            },
        },
        "urgency": {
            "type": "score",
            "instructions": "Urgency",
            "criteria": ["low", "medium", "high", "critical"],
        },
        "churn": {"type": "noul", "instructions": "Churn threat?"},
    }

    result = live_predict(state, questions) if args.live else mock_predict(state, questions)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
        print("OK: laya decision stub" if not args.live else "OK: laya live predict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
