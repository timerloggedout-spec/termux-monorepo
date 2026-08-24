"""CLI: python -m ops.github_telemetry {collect|reduce|reconcile}."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ops.github_telemetry")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("collect", help="Fetch raw snapshots via gh api (needs token)")
    c.add_argument("--owner", default="timerloggedout-spec")
    c.add_argument("--repo", default="termux-monorepo")
    c.add_argument("--out", type=Path, default=Path("ops/github-telemetry/raw"))
    c.add_argument("--max-runs", type=int, default=50)
    c.add_argument("--workflow", default="", help="Optional workflow file name filter")
    c.add_argument("--with-jobs", action="store_true", help="Fetch jobs for each run")
    c.add_argument("--with-stats", action="store_true")
    c.add_argument("--with-traffic", action="store_true")

    r = sub.add_parser("reduce", help="Reduce raw run/job JSON → derived window stats")
    r.add_argument("--jobs-glob", default="", help="Glob of jobs JSON files")
    r.add_argument("--jobs-file", type=Path, nargs="*", help="Explicit jobs payload paths")
    r.add_argument("--window-label", default="snapshot")
    r.add_argument("--out", type=Path, default=Path("docs/ops/generated"))

    rec = sub.add_parser("reconcile", help="Compare reconstructed rows to UI CSV")
    rec.add_argument("--csv", type=Path, required=True)
    rec.add_argument("--derived", type=Path, required=True, help="JSON from reduce")
    rec.add_argument("--tolerance-pp", type=float, default=2.0)

    args = p.parse_args(argv)
    if args.cmd == "collect":
        from ops.github_telemetry.collect import collect_main

        return collect_main(args)
    if args.cmd == "reduce":
        from ops.github_telemetry.reduce import reduce_main

        return reduce_main(args)
    if args.cmd == "reconcile":
        from ops.github_telemetry.reconcile import reconcile_main

        return reconcile_main(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
