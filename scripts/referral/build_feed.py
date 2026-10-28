#!/usr/bin/env python3
"""Build the public referral feed from config/referral_programs.json.

One live code per programme (pool order = rotation order); reserve codes
stay unpublished. Output: apps/help-wanted-dashboard/data/referral-feed.json
Feed is consumed by the landing repo's partners grid (Web Design lane).
Stdlib only. Unknown values stay null, never zero.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "config" / "referral_programs.json"
OUT = ROOT / "apps" / "help-wanted-dashboard" / "data" / "referral-feed.json"


def build(reg):
    items = []
    for p in sorted(reg["programs"], key=lambda x: x["priority"]):
        live = next((c for c in p.get("codes", []) if c["status"] == "live"), None)
        reserve = sum(1 for c in p.get("codes", []) if c["status"] == "reserve")
        items.append({
            "id": p["id"],
            "name": p["name"],
            "status": p["status"],
            "mechanic": p["mechanic"],
            "free_no_cc": p["free_no_cc"],
            "visitor_reward": p["visitor_reward"],
            "fleet_replenishment": p["fleet_replenishment"],
            "live_code": live["code"] if live else None,
            "reserve_codes": reserve,
            "link_ref": p.get("link_ref"),
        })
    return {
        "schema": "referral-feed/1",
        "source": "config/referral_programs.json",
        "items": items,
        "rules": reg["rules"],
    }


def main():
    reg = json.loads(SRC.read_text())
    feed = build(reg)
    if "--stdout" in sys.argv:
        print(json.dumps(feed, indent=1, sort_keys=True))
        return
    OUT.write_text(json.dumps(feed, indent=1, sort_keys=True) + "\n")
    print("wrote", OUT, len(feed["items"]), "items")


if __name__ == "__main__":
    main()
