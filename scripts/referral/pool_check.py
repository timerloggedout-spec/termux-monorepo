#!/usr/bin/env python3
"""Referral pool watchdog.

Reads config/referral_programs.json and reports, per code programme, how
many unpublished spare codes remain. A live programme with 0 spares is one
exhaustion away from a dead public code — that state is detectable from
the registry alone, so this check is fully automated (weekly workflow
opens/updates a `referral:pool-low` issue).

Exit 0 = every live code programme has >= its rotation.pool_target spares.
Exit 1 = at least one alert. JSON report on stdout either way.
Stdlib only.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "config" / "referral_programs.json"


def main():
    reg = json.loads(SRC.read_text())
    report, alerts = [], []
    for p in reg["programs"]:
        codes = p.get("codes", [])
        if not codes:
            continue
        spares = sum(1 for c in codes if c["status"] == "reserve")
        target = p.get("rotation", {}).get("pool_target", 1)
        row = {"program": p["id"], "status": p["status"], "spares": spares,
               "pool_target": target,
               "live": [c["code"] for c in codes if c["status"].startswith("live")]}
        if p["status"].startswith("active") and spares < target:
            row["alert"] = "pool_below_target"
            alerts.append(p["id"])
        report.append(row)
    print(json.dumps({"programs": report, "alerts": alerts}, indent=1))
    return 1 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
