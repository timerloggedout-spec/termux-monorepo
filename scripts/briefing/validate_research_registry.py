#!/usr/bin/env python3
"""Validate research-lane registry records with only Python stdlib dependencies."""

from __future__ import annotations
import json, sys
from pathlib import Path

REQUIRED = {
    "resource_id", "project", "canonical_source", "source_type",
    "observed_at", "evidence_status", "horizon", "confidence", "decision_status",
}
HORIZONS = {"H0", "H1", "H2", "H3"}
EVIDENCE = {"confirmed", "research", "attributed", "signal", "speculative", "disputed"}
DECISIONS = {"WATCH", "INVESTIGATE", "PROTOTYPE", "ADOPT", "REJECT", "HOLD"}

def validate(record: dict) -> list[str]:
    errors = [f"missing: {k}" for k in sorted(REQUIRED - record.keys())]
    if "horizon" in record and record["horizon"] not in HORIZONS:
        errors.append("invalid horizon")
    if "evidence_status" in record and record["evidence_status"] not in EVIDENCE:
        errors.append("invalid evidence_status")
    if "decision_status" in record and record["decision_status"] not in DECISIONS:
        errors.append("invalid decision_status")
    if "canonical_source" in record and not str(record["canonical_source"]).startswith(("https://", "git://", "file://")):
        errors.append("canonical_source must be an inspectable URI")
    return errors

def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print("usage: validate_research_registry.py RECORD.json [...]", file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"{path}: read/parse error: {exc}", file=sys.stderr)
            failed = True
            continue
        errors = validate(record)
        if errors:
            failed = True
            print(f"{path}: " + "; ".join(errors), file=sys.stderr)
        else:
            print(f"{path}: OK")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
