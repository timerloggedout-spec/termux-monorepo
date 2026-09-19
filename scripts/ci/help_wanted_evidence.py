#!/usr/bin/env python3
"""Append-only evidence receipts for help-wanted Oversight execute arm.

Does NOT grant MoneyBall admission. Writes evaluation-cohort evidence only.
See docs/ops/HELP-WANTED-EVIDENCE-FEED.md.

Usage:
  python3 scripts/ci/help_wanted_evidence.py \\
    --kind claim --issue https://github.com/o/r/issues/1 --ok true \\
    --extra '{"comment_url":"..."}'
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, help="claim | upstream_pr | fallback | notice | scout_bench")
    ap.add_argument("--issue", default="", help="issue URL or owner/repo#n")
    ap.add_argument("--ok", default="true", choices=("true", "false"))
    ap.add_argument("--pr-url", default="")
    ap.add_argument("--run-url", default="")
    ap.add_argument("--score", default="", help="optional CPPH score")
    ap.add_argument("--extra", default="{}", help="JSON object of extra fields")
    ap.add_argument(
        "--out-dir",
        default="docs/ops/generated/help-wanted-evidence",
        help="directory for dated JSONL",
    )
    args = ap.parse_args()

    try:
        extra = json.loads(args.extra or "{}")
        if not isinstance(extra, dict):
            extra = {}
    except json.JSONDecodeError:
        extra = {}

    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    receipt = {
        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "kind": args.kind,
        "issue": args.issue,
        "ok": args.ok == "true",
        "pr_url": args.pr_url or None,
        "run_url": args.run_url or os.environ.get("GITHUB_RUN_URL") or None,
        "score": float(args.score) if args.score else None,
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "workflow": os.environ.get("GITHUB_WORKFLOW"),
        "actor": os.environ.get("GITHUB_ACTOR"),
        "sha": os.environ.get("GITHUB_SHA"),
        "lane": "help-wanted",
        "scout": "oversight",
        "delivery": "upstream-pr-primary",
        **extra,
    }
    # drop nulls for thinner lines
    receipt = {k: v for k, v in receipt.items() if v is not None}

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{day}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, separators=(",", ":")) + "\n")

    # rolling latest pointer (single object, last write wins)
    latest = out / "latest.json"
    latest.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"wrote": str(path), "receipt": receipt}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
