#!/usr/bin/env python3
"""CLI for provenance-only ATES outcome receipts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .ates_outcome_receipt import build_outcome_receipt
except ImportError:
    from ates_outcome_receipt import build_outcome_receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-run-id", type=int, required=True)
    parser.add_argument("--source-run-attempt", type=int, required=True)
    parser.add_argument("--source-head-sha", default="")
    parser.add_argument("--source-workflow-name", default="")
    parser.add_argument("--source-conclusion", default="unknown")
    parser.add_argument("--skip-reason", default="metadata_unavailable")
    parser.add_argument("--collection-outcome", default="skipped")
    parser.add_argument("--checkout-outcome", default="skipped")
    parser.add_argument("--task-boundary-outcome", default="skipped")
    args = parser.parse_args()
    receipt = build_outcome_receipt(
        source_run_id=args.source_run_id,
        source_run_attempt=args.source_run_attempt,
        source_head_sha=args.source_head_sha,
        source_workflow_name=args.source_workflow_name,
        source_conclusion=args.source_conclusion,
        skip_reason=args.skip_reason,
        collection_outcome=args.collection_outcome,
        checkout_outcome=args.checkout_outcome,
        task_boundary_outcome=args.task_boundary_outcome,
    )
    Path(args.output).write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
