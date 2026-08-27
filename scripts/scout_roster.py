#!/usr/bin/env python3
"""Build a dynamic Scout roster from provider-model catalog evidence.

Scout discovers candidates; it does not grant routing authority. Provider/model
identities come from the observed catalog instead of a hard-coded candidate list.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ELIGIBLE_ACCESS = {"free_zero_price", "free_trial"}


def classify(row: dict) -> str:
    if row.get("access_classification") in ELIGIBLE_ACCESS:
        return "candidate"
    if row.get("pricing_classification") == "free_zero_price" or row.get("free_suffix"):
        return "candidate"
    return "observed"


def build(document: dict) -> dict:
    roster = []
    for row in document.get("models", []):
        provider = row.get("provider")
        model = row.get("id")
        if not provider or not model:
            continue
        roster.append({
            "provider": provider,
            "model": model,
            "name": row.get("name"),
            "status": classify(row),
            "pricing_classification": row.get("pricing_classification", "unknown"),
            "access_classification": row.get("access_classification", "unknown"),
            "access_source": row.get("access_source"),
            "observed_at": document.get("observed_at"),
            "context_length": row.get("context_length"),
            "max_output_tokens": row.get("max_output_tokens"),
            "raw_source": row.get("raw_source"),
        })
    roster.sort(key=lambda x: (x["status"] != "candidate", x["provider"], x["model"]))
    return {
        "schema": "agent-scout-roster/v1",
        "observed_at": document.get("observed_at"),
        "source_schema": document.get("schema"),
        "policy": "observe_only",
        "candidates": roster,
        "errors": document.get("errors", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = build(source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    candidates = sum(1 for row in result["candidates"] if row["status"] == "candidate")
    print(f"scout_models={len(result['candidates'])} candidates={candidates} errors={len(result['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
