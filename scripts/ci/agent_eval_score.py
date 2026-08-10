#!/usr/bin/env python3
"""Agent eval matrix v0 — empty commits, merge complexity, optional Oracle hooks.

Emits JSONL lines for docs/ops/eval/points.jsonl or stdout for GHA.

Usage:
  python3 scripts/ci/agent_eval_score.py empty-commit --role jules --context-key pr-126-x --pr 126 --sha abc
  python3 scripts/ci/agent_eval_score.py pr-landed --role jules --pr 126 --files 8 --additions 200 --deletions 40 --band High
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone

P_EMPTY = 3
P_FIX_REVIEWER = 2
P_FIX_AUTHOR = 1
P_BAD_REVIEW = 2
P_SEC = {"medium": 3, "high": 5, "critical": 8}
BAND_MULT = {"P0": 1.5, "High": 1.2, "Medium": 1.0, "Backlog": 0.7}


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit(role: str, context_key: str, metric: str, delta: float, **extra) -> dict:
    row = {
        "ts": ts(),
        "role": role,
        "context_key": context_key or "",
        "metric": metric,
        "delta": delta,
        **extra,
    }
    print(json.dumps(row, separators=(",", ":")))
    return row


def cmd_empty_commit(args: argparse.Namespace) -> None:
    emit(
        args.role,
        args.context_key,
        "empty_commit",
        -P_EMPTY,
        pr=args.pr,
        sha=args.sha or "",
        note="zero-diff head after claimed fix",
    )


def cmd_pr_landed(args: argparse.Namespace) -> None:
    complexity = math.log2(1 + max(0, args.files)) + math.log2(
        1 + max(0, args.additions) + max(0, args.deletions)
    ) / 2.0
    mult = BAND_MULT.get(args.band, 1.0)
    p_merge = max(1, min(10, round(complexity * mult)))
    if args.oracle_boost is not None:
        # oracle_boost in [0,1] from mean(shockwave,nexus)/100
        boost = max(0.0, min(1.0, args.oracle_boost))
        p_merge = max(1, min(10, round(p_merge * (0.75 + 0.5 * boost))))
    emit(
        args.role,
        args.context_key,
        "pr_landed",
        float(p_merge),
        pr=args.pr,
        files=args.files,
        additions=args.additions,
        deletions=args.deletions,
        band=args.band,
        complexity=round(complexity, 3),
    )


def cmd_review_fix(args: argparse.Namespace) -> None:
    if args.accepted:
        emit(args.reviewer_role, args.context_key, "review_fix_accepted", float(P_FIX_REVIEWER), pr=args.pr)
        emit(args.role, args.context_key, "review_fix_accepted", float(-P_FIX_AUTHOR), pr=args.pr)
    else:
        emit(args.reviewer_role, args.context_key, "review_fix_rejected", float(-P_BAD_REVIEW), pr=args.pr)


def main() -> int:
    p = argparse.ArgumentParser(description="Agent eval matrix v0")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("empty-commit")
    e.add_argument("--role", required=True)
    e.add_argument("--context-key", default="")
    e.add_argument("--pr", type=int, default=0)
    e.add_argument("--sha", default="")
    e.set_defaults(func=cmd_empty_commit)

    m = sub.add_parser("pr-landed")
    m.add_argument("--role", required=True)
    m.add_argument("--context-key", default="")
    m.add_argument("--pr", type=int, default=0)
    m.add_argument("--files", type=int, default=1)
    m.add_argument("--additions", type=int, default=0)
    m.add_argument("--deletions", type=int, default=0)
    m.add_argument("--band", default="Medium")
    m.add_argument("--oracle-boost", type=float, default=None)
    m.set_defaults(func=cmd_pr_landed)

    r = sub.add_parser("review-fix")
    r.add_argument("--role", required=True, help="author role")
    r.add_argument("--reviewer-role", required=True)
    r.add_argument("--context-key", default="")
    r.add_argument("--pr", type=int, default=0)
    r.add_argument("--accepted", action="store_true")
    r.set_defaults(func=cmd_review_fix)

    args = p.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
