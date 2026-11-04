#!/usr/bin/env python3
"""DoE oversight fold feed — roster/state rows for the pool:doe:*
slice of the site wallet ledger (Admin Desk Plane 6; Desk operates,
DoE holds oversight semantics, Speculators-build stewards the ledger).

States are FOLDS over ledger events, never free fields:
  PROVISIONED            — wallet_provisioned seen (sole entry)
  PARTICIPATION_ELIGIBLE — latest participation_set state wins
                           (PARTICIPATION_ELIGIBLE entry / PROVISIONED
                           revocation; unresolvable countersigns are
                           the oversight leg's to flag — the fold
                           reports the recorded state + its ref)
  ante state             — open ante_drawn events (drawn, unsettled)
                           per pool, from the Plane-6 vocabulary

Reading rules (DoE-ruled): absent `depth` reads as depth 1; the 4
grandfathered non-doe pools are out of this slice by construction.

Vintage stamps: ledger_head_seq = the ledger's last seq folded;
feed_as_of_seq = the same number (this feed is generated from the
head) — the C-A attribution pair {ledger head · feed as-of}.

Usage:
  doe_oversight_feed.py LEDGER [--out FEED.json]
Prints the feed JSON to stdout when --out is omitted.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wallet_ledger import load, verify, ante_review  # noqa: E402


def build_feed(events):
    errs, balances, _ = verify(events)
    if errs:
        raise SystemExit("ledger verify failed; feed not generated: "
                         + "; ".join(errs[:5]))
    head = events[-1]["seq"] if events else 0
    rows = {}
    order = []
    open_antes = {}
    settled_draws = set()
    draw_by_receipt = {}
    for ev in events:
        wid = ev.get("wallet_id", "")
        if ev.get("type") == "wallet_provisioned" \
                and wid.startswith("pool:doe:"):
            rows[wid] = {
                "wallet_id": wid,
                "entity_ref": ev.get("entity_ref"),
                "display": ev.get("display"),
                "depth": ev.get("depth", 1),
                "parent_entity": ev.get("parent_entity"),
                "parent_wallet": ev.get("parent_wallet"),
                "state": "PROVISIONED",
                "participation_ref": None,
                "balance": balances.get(wid, 0),
                "members": ev.get("members"),
                "provisioned_seq": ev["seq"],
                "last_event_seq": ev["seq"],
                "open_antes": [],
            }
            order.append(wid)
        elif wid in rows:
            rows[wid]["last_event_seq"] = ev["seq"]
            if ev.get("type") == "participation_set":
                # latest wins; delta is always 0 (no economic fact)
                rows[wid]["state"] = ev.get("state", "PROVISIONED")
                rows[wid]["participation_ref"] = (
                    ev.get("ref") or {}).get("source")
            elif ev.get("type") == "ante_drawn":
                draw_by_receipt[ev["receipt"]["receipt_id"]] = wid
                open_antes.setdefault(wid, []).append({
                    "seq": ev["seq"],
                    "receipt_id": ev["receipt"]["receipt_id"],
                    "amount": ev.get("amount"),
                    "task": (ev.get("ref") or {}).get("task"),
                    "state_vintage_seq": ev.get("state_vintage_seq"),
                })
            elif ev.get("type") == "ante_settled":
                draw_ref = (ev.get("ref") or {}).get("draw")
                if draw_ref in draw_by_receipt:
                    settled_draws.add(draw_ref)
    for wid, draws in open_antes.items():
        rows[wid]["open_antes"] = [
            d for d in draws
            if d["receipt_id"] not in settled_draws]
    return {
        "schema": "doe-oversight-feed/v1",
        "slice": "pool:doe:*",
        "ledger_head_seq": head,
        "feed_as_of_seq": head,
        "pool_count": len(order),
        "reading_rules": {
            "absent_depth": "reads as depth 1 (DoE C-B reading rule)",
            "states": "folds over ledger events, never free fields",
            "balances": "fold-derived (verify-checked at generation)",
        },
        "ante_review_flags": ante_review(events),
        "rows": [rows[w] for w in order],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--out")
    ap.add_argument("--mirror-out",
                    help="second output path written byte-identical "
                         "(dashboard mirror, QUE-feed pattern)")
    a = ap.parse_args()
    feed = build_feed(load(a.ledger))
    text = json.dumps(feed, indent=1, sort_keys=True)
    if a.out:
        Path(a.out).write_text(text + "\n")
        print(f"doe-oversight feed: {feed['pool_count']} rows, "
              f"head {feed['ledger_head_seq']}, "
              f"as-of {feed['feed_as_of_seq']} -> {a.out}")
    if a.mirror_out:
        Path(a.mirror_out).write_text(text + "\n")
        print(f"mirror (byte-identical) -> {a.mirror_out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
