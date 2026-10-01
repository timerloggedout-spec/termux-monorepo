#!/usr/bin/env python3
"""Static contract checks for the Help-Wanted dashboard control surface."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "apps/help-wanted-dashboard/index.html"
SNAPSHOT = ROOT / "apps/help-wanted-dashboard/data/status.json"

REQUIRED_HTML = (
    "Control surface",
    "Lane evolution",
    "Publication lanes",
    "control_surface",
    "evolution",
    "source_sha",
)

def main() -> int:
    html = HTML.read_text(encoding="utf-8")
    missing = [x for x in REQUIRED_HTML if x not in html]
    if missing:
        raise SystemExit("missing dashboard contract markers: " + ", ".join(missing))
    if SNAPSHOT.exists():
        data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        ctl = data.get("control_surface") or {}
        if ctl.get("schema_version") != "help-wanted.control-surface.v2":
            raise SystemExit("status snapshot is missing control-surface.v2")
        if not ctl.get("source_sha"):
            raise SystemExit("status snapshot is missing source_sha")
        if not ctl.get("history_complete"):
            raise SystemExit("status snapshot does not assert complete lane history")
        if not isinstance(data.get("evolution"), list):
            raise SystemExit("status snapshot evolution is not a list")
    print("help-wanted dashboard control-surface contract: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
