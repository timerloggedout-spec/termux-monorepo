#!/usr/bin/env python3
"""Static contract checks for the Tribute dashboard control surface."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "apps/help-wanted-dashboard"
HTML = DASHBOARD / "index.html"
NAV = DASHBOARD / "site-nav.js"
VERSIONING = DASHBOARD / "versioning.js"
MATRIX = DASHBOARD / "matrix.html"
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
    if not NAV.is_file():
        raise SystemExit("shared site-nav.js is missing")
    nav = NAV.read_text(encoding="utf-8")
    versioning = VERSIONING.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    required_nav = ('["Tribute", tribute, "tribute"]', '["Lane matrix", origin + "/matrix/", "matrix"]', '["Version comparison", tribute + "versioning.html", "versioning"]')
    missing_nav = [item for item in required_nav if item not in nav]
    if missing_nav:
        raise SystemExit("shared navigation is missing required destinations: " + ", ".join(missing_nav))
    if 'new URL("./site-nav.js", window.location.href)' not in versioning:
        raise SystemExit("dashboard versioning module does not load shared navigation")
    if 'src="./site-nav.js"' not in matrix:
        raise SystemExit("matrix page does not load shared navigation")
    if 'origin + "/tribute/"' not in nav:
        raise SystemExit("shared navigation does not use the canonical Tribute route")
    if "var previewMatch = path.match" not in nav or "/previews/" not in nav:
        raise SystemExit("shared navigation does not preserve the preview route context")
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
        # help_wanted_status.py deliberately emits history_complete=False with an
        # explicit history_coverage statement until sweep-accountability backfill
        # lands; accept that honest partial claim, reject a silent one.
        if not ctl.get("history_complete") and not ctl.get("history_coverage"):
            raise SystemExit("status snapshot does not assert complete lane history or declare its coverage")
        if not ctl.get("history_complete"):
            print("notice: lane history declared partial: " + str(ctl.get("history_coverage")))
        if not isinstance(data.get("evolution"), list):
            raise SystemExit("status snapshot evolution is not a list")
    print("Tribute dashboard control-surface and shared-navigation contract: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
