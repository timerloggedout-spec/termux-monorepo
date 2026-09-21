#!/usr/bin/env python3
"""Decision-engine registry (not LLM provider catalog).

LLM providers live in provider_model_catalog / model_router (OpenRouter, Felo, …).
This registry is for **System-1 / schema decision** engines used as pre-gates
before expensive LLM calls (triage, guardrails, routing).

Primary entry: Laya — https://github.com/NandhaKishorM/laya
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENGINES = {
    "laya": {
        "id": "laya",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "repo": "https://github.com/NandhaKishorM/laya",
        "demo": "https://huggingface.co/spaces/convaiinnovations/laya-demo",
        "weights": "https://huggingface.co/convaiinnovations/laya",
        "product": "https://laya.convaiinnovations.com",
        "install": "pip install laya",
        "primitives": ["choice", "score", "noul"],
        "stub": "scripts/laya_decision_stub.py",
        "slot": "refTemplates/16_Org_Phased/laya",
        "phase": "IMPLEMENTATION",
        "workflows": [
            "pre-LLM triage",
            "guardrails / jailbreak noul",
            "tool/model route choice",
            "help-wanted urgency score",
        ],
        "dense_feedback": [
            "checkpoint",
            "confidence",
            "routing.reason",
            "latency_budget_ms",
        ],
    }
}


def list_engines() -> list[dict]:
    return list(ENGINES.values())


def get_engine(engine_id: str) -> dict | None:
    return ENGINES.get(engine_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--id", default="laya")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.list:
        data = list_engines()
    else:
        data = get_engine(args.id)
        if data is None:
            print(f"unknown engine: {args.id}", file=sys.stderr)
            return 1
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
