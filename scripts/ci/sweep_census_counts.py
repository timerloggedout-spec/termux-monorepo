#!/usr/bin/env python3
"""Count census JSON pages written by sweep-accountability historical mode."""
import json
import pathlib
import sys

def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/ops/generated/sweep-ledger/census")
    for name in ("pulls", "issues", "workflow-runs"):
        raw = root.joinpath(name + ".json").read_text(encoding="utf-8")
        try:
            pages = json.loads(raw)
            if isinstance(pages, list) and pages and isinstance(pages[0], list):
                count = sum(len(x) for x in pages)
            elif isinstance(pages, list):
                count = len(pages)
            else:
                count = 0
        except Exception:
            count = -1
        print(name, count)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
