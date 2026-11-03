#!/usr/bin/env python3
"""Build the public referral feed from config/referral_programs.json.

One live code per programme (pool order = rotation order); reserve codes
stay unpublished. Output: apps/tribute-dashboard/data/referral-feed.json
Feed is consumed by the landing repo's partners grid (Web Design lane).
Stdlib only. Unknown values stay null, never zero.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "config" / "referral_programs.json"
OUT = ROOT / "apps" / "tribute-dashboard" / "data" / "referral-feed.json"


STATE_MAP = {
    "active_codes": "live",
    "active_link": "live",
    "code_pending": "exhausted",
    "pending_identity": "pending",
    "no_public_programme": "pending",
    "programme_verified_not_enrolled": "pending",
}


def viz_state(p):
    """Visualization state {live|pending|not-established|exhausted}.

    Derived, never hand-set: an all-exhausted code pool is exhausted even
    if the registry status lags; a live link whose offer itself is
    NOT ESTABLISHED renders not-established; Hark renders pending with
    its pending_identity detail until main stamps the resolution.
    """
    codes = p.get("codes", [])
    if codes and all(c["status"] == "exhausted" for c in codes):
        return "exhausted"
    if p["id"] == "neon":
        return "not-established"
    return STATE_MAP.get(p["status"], "pending")


def build(reg):
    items = []
    for p in sorted(reg["programs"], key=lambda x: x["priority"]):
        live = next((c for c in p.get("codes", []) if c["status"] == "live"), None)
        cell_b = next((c for c in p.get("codes", []) if c["status"] == "live_cell_b"), None)
        reserve = sum(1 for c in p.get("codes", []) if c["status"] == "reserve")
        pool = None
        if p.get("codes"):
            pool = {
                "live": sum(1 for c in p["codes"] if c["status"] in ("live", "live_cell_b")),
                "reserve": reserve,
                "exhausted": sum(1 for c in p["codes"] if c["status"] == "exhausted"),
            }
        item = {
            "id": p["id"],
            "name": p["name"],
            "status": p["status"],
            "mechanic": p["mechanic"],
            "free_no_cc": p["free_no_cc"],
            "visitor_reward": p["visitor_reward"],
            "fleet_replenishment": p["fleet_replenishment"],
            "live_code": live["code"] if live else None,
            "cell_b_code": cell_b["code"] if cell_b else None,
            "reserve_codes": reserve,
            "link_ref": p.get("link_ref"),
            "link": p.get("link"),
            "badge_svg": p.get("badge_svg"),
            "state": viz_state(p),
            "state_detail": p["status"],
            "pool_health": pool,
            "rotation_events": [e for e in reg.get("rotation_log", [])
                                if e.get("programme") == p["id"] or e.get("program") == p["id"]],
        }
        # Accrued value: carried ONLY where a programme surface establishes
        # it in the registry; absent otherwise, never estimated.
        if p.get("accrued_value") is not None:
            item["accrued_value"] = p["accrued_value"]
        items.append(item)
    return {
        "schema": "referral-feed/1",
        "source": "config/referral_programs.json",
        "items": items,
        "channels": reg.get("channels", []),
        "ab_test": reg.get("ab_test"),
        "rules": reg["rules"],
        "rotation_log": reg.get("rotation_log", []),
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
