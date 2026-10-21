#!/usr/bin/env python3
"""Bounded Swarms workflow runner; offline dry-run unless --execute is passed."""
import argparse
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT)
from src.swarms_adapter import run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", help="Explicit model identifier (no paid default)")
    parser.add_argument("--max-loops", type=int, default=1)
    parser.add_argument("--number-agents", type=int, default=2)
    parser.add_argument("--execute", action="store_true", help="Opt in to model calls through llm_api_hub")
    args = parser.parse_args()
    try:
        result = run({"task": args.task, "model": args.model, "max_loops": args.max_loops,
                      "number_agents": args.number_agents, "execute": args.execute})
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2
    print(json.dumps(result, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
