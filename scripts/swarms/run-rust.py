#!/usr/bin/env python3
"""Bounded swarms-rs worker runner; offline unless --execute is passed."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.swarms_rust_adapter import run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", help="Explicit configured hub route; no paid default")
    parser.add_argument("--max-loops", type=int, default=1, help="Workflow passes, 1–3")
    parser.add_argument("--number-agents", type=int, default=2, help="1 or 2")
    parser.add_argument("--max-tokens", type=int, default=8192, help="Per-request output token limit")
    parser.add_argument("--timeout-seconds", type=int, default=120, help="Whole-workflow deadline")
    parser.add_argument("--binary", help="Installed trusted worker executable (or SWARMS_RS_BINARY)")
    parser.add_argument("--execute", action="store_true", help="Opt in to hub model calls")
    args = parser.parse_args()
    try:
        result = run({"task": args.task, "model": args.model,
                      "max_loops": args.max_loops, "number_agents": args.number_agents,
                      "execute": args.execute}, binary=args.binary,
                     max_tokens=args.max_tokens, timeout_seconds=args.timeout_seconds)
    except Exception as exc:
        print(json.dumps({"status": "error", "backend": "swarms-rs", "error": str(exc)}))
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
