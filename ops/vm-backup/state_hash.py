#!/usr/bin/env python3
"""Cheap T0 state fingerprint for the vm-backup cadence hook.

Stat-only (path + size + mtime, no content reads; runs in well under a
second on this VM). Compares the fingerprint against the marker written
by the last successful export:

  exit 0  state unchanged since last export
  exit 3  state changed (or no marker yet) — an export is due

`--write` records the current fingerprint as the marker.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_vm_workspace import t0_state_hash  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=str(Path.home()))
    ap.add_argument("--marker", default=None,
                    help="default <home>/workspace/vm-backup/.last-export-state")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    home = Path(args.home)
    marker = Path(args.marker) if args.marker else \
        home / "workspace/vm-backup/.last-export-state"
    current = t0_state_hash(home)
    print(current)
    if args.write:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(current + "\n")
        return 0
    if marker.is_file() and marker.read_text().strip() == current:
        return 0
    return 3


if __name__ == "__main__":
    sys.exit(main())
