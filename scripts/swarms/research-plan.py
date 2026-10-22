#!/usr/bin/env python3
"""Emit an offline, bounded research plan; this tool never executes a lane."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "integrations/swarms/research-lanes.json"
MAX_TASK_LENGTH = 500


def build_plan(lane: str, task: str) -> dict:
    if lane not in {"parity", "research", "wallets"}:
        raise ValueError("lane must be parity, research, or wallets")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be nonblank")
    if len(task) > MAX_TASK_LENGTH:
        raise ValueError(f"task must be at most {MAX_TASK_LENGTH} characters")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entry = registry["lanes"][lane]
    return {
        "schema_version": 1,
        "status": "planned",
        "lane": lane,
        "task": task.strip(),
        "sources": entry["sources"],
        "market_contract": registry["market_contract"],
        "market_policy": registry["market_policy"],
        "evidence_requirements": entry["evidence"],
        "execution": "not_performed",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", required=True, choices=("parity", "research", "wallets"))
    parser.add_argument("--task", required=True, help=f"nonblank, at most {MAX_TASK_LENGTH} characters")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.lane, args.task)
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
