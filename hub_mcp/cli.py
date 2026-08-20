"""Command-line entrypoint for one structured Termux hub job."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .protocol import JobValidationError
from .runner import execute_payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Execute one validated Termux hub job")
    parser.add_argument("job", type=Path, help="Path to a JSON job envelope")
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path.cwd(),
        help="Monorepo root; defaults to the current working directory",
    )
    parser.add_argument(
        "--state-directory",
        type=Path,
        default=Path(".hub_mcp/state"),
        help="Untracked local replay-state directory",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = json.loads(args.job.read_text(encoding="utf-8"))
        result = execute_payload(payload, args.repository, args.state_directory)
    except (OSError, json.JSONDecodeError, JobValidationError) as exc:
        print(json.dumps({"success": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
