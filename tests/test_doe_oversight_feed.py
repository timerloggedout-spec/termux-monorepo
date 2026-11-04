"""doe_oversight_feed: states are folds (Plane-6). Covers the
PROVISIONED entry, the participation_set flip (latest wins), and
open-ante derivation."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _evs(wl):
    evs = [
        {"seq": 1, "ts": "2026-11-04T00:00:00Z",
         "type": "wallet_provisioned", "wallet_id": "pool:doe:x",
         "class": "pool", "pool_class": "doe", "entity_ref": "x",
         "display": "X", "delta": 0, "balance_after": 0, "members": 0,
         "ref": {"kind": "pool_provisioning_program"}},
        {"seq": 2, "ts": "2026-11-04T00:01:00Z",
         "type": "participation_set", "wallet_id": "pool:doe:x",
         "class": "pool", "delta": 0, "balance_after": 0,
         "state": "PARTICIPATION_ELIGIBLE",
         "ref": {"kind": "participation_countersign",
                 "source": "cs-1"}},
        {"seq": 3, "ts": "2026-11-04T00:02:00Z",
         "type": "ante_drawn", "wallet_id": "pool:doe:x",
         "class": "pool", "delta": -10, "balance_after": -10,
         "amount": 10, "state_vintage_seq": 2,
         "ref": {"kind": "ante", "task": "t1", "rule": "clause (e)"}},
    ]
    prev = "GENESIS"
    for ev in evs:
        h = wl.payload_hash(ev)
        ev["receipt"] = {"receipt_id": f"wr-{ev['seq']:04d}-{h[:12]}",
                         "wallet_id": ev["wallet_id"],
                         "event_seq": ev["seq"], "payload_hash": h,
                         "prev_receipt_hash": prev}
        prev = h
    return evs


def test_feed_derives_state_from_fold():
    wl = _mod("wallet_ledger", "scripts/moneyball/wallet_ledger.py")
    feed_mod = _mod("doe_oversight_feed",
                    "scripts/moneyball/doe_oversight_feed.py")
    feed = feed_mod.build_feed(_evs(wl))
    assert feed["ledger_head_seq"] == feed["feed_as_of_seq"] == 3
    (row,) = feed["rows"]
    assert row["state"] == "PARTICIPATION_ELIGIBLE"
    assert row["participation_ref"] == "cs-1"
    assert row["depth"] == 1  # absent depth reads as 1
    assert row["balance"] == -10
    assert len(row["open_antes"]) == 1
    assert feed["ante_review_flags"] == []


def test_feed_ignores_non_doe_pools():
    wl = _mod("wallet_ledger", "scripts/moneyball/wallet_ledger.py")
    feed_mod = _mod("doe_oversight_feed",
                    "scripts/moneyball/doe_oversight_feed.py")
    evs = _evs(wl)
    evs[0]["wallet_id"] = "pool:role:x"
    for ev in evs:
        ev.pop("receipt", None)
    prev = "GENESIS"
    for ev in evs:
        ev["wallet_id"] = "pool:role:x"
        h = wl.payload_hash(ev)
        ev["receipt"] = {"receipt_id": f"wr-{ev['seq']:04d}-{h[:12]}",
                         "wallet_id": ev["wallet_id"],
                         "event_seq": ev["seq"], "payload_hash": h,
                         "prev_receipt_hash": prev}
        prev = h
    feed = feed_mod.build_feed(evs)
    assert feed["rows"] == [] and feed["pool_count"] == 0
