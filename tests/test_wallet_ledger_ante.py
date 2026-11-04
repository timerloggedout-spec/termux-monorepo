"""Plane-6 ante/participation vocabulary on the site wallet ledger
(DoE vocabulary amendment 2026-11-04): participation_set creates no
economic fact; ante_drawn is the pool's obligation (clause (e)
permits rule-cited negative balances); ante_review flags INVALID
draws without refusing history."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _wl():
    spec = importlib.util.spec_from_file_location(
        "wallet_ledger", ROOT / "scripts/moneyball/wallet_ledger.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _chain(wl, evs):
    prev = "GENESIS"
    for ev in evs:
        h = wl.payload_hash(ev)
        ev["receipt"] = {"receipt_id": f"wr-{ev['seq']:04d}-{h[:12]}",
                         "wallet_id": ev["wallet_id"],
                         "event_seq": ev["seq"], "payload_hash": h,
                         "prev_receipt_hash": prev}
        prev = h
    return evs


def _fixture(wl, rule=True, vintage=True):
    evs = [
        {"seq": 1, "ts": "2026-11-04T00:00:00Z",
         "type": "wallet_provisioned",
         "wallet_id": "pool:doe:doe-expert", "class": "pool",
         "delta": 0, "balance_after": 0,
         "ref": {"kind": "pool_provisioning_program"}},
        {"seq": 2, "ts": "2026-11-04T00:01:00Z",
         "type": "participation_set",
         "wallet_id": "pool:doe:doe-expert", "class": "pool",
         "delta": 0, "balance_after": 0,
         "state": "PARTICIPATION_ELIGIBLE",
         "ref": {"kind": "participation_countersign",
                 "source": "doe-countersign-fixture-001"}},
        {"seq": 3, "ts": "2026-11-04T00:02:00Z",
         "type": "ante_drawn", "wallet_id": "pool:doe:doe-expert",
         "class": "pool", "delta": -25, "balance_after": -25,
         "actor": "desk-que", "amount": 25,
         "ref": {"kind": "ante", "task": "que-fixture-task-1"}},
        {"seq": 4, "ts": "2026-11-04T00:03:00Z",
         "type": "ante_settled", "wallet_id": "pool:doe:doe-expert",
         "class": "pool", "delta": 25, "balance_after": 0,
         "ref": {"kind": "ante_settlement",
                 "resolution": "task-receipt-fixture-001"}},
    ]
    if vintage:
        evs[2]["state_vintage_seq"] = 2
    if rule:
        evs[2]["ref"]["rule"] = "Plane-6 clause (e): ante obligation"
    evs = _chain(wl, evs)
    evs[3]["ref"]["draw"] = evs[2]["receipt"]["receipt_id"]
    # ref.draw entered the payload after chaining seq 3 only; seq 4's
    # hash covers its own payload as built above (draw set pre-chain
    # in real appends) — rebuild seq 4 receipt honestly:
    evs[3].pop("receipt")
    h = wl.payload_hash(evs[3])
    evs[3]["receipt"] = {
        "receipt_id": f"wr-0004-{h[:12]}",
        "wallet_id": evs[3]["wallet_id"], "event_seq": 4,
        "payload_hash": h,
        "prev_receipt_hash": evs[2]["receipt"]["payload_hash"]}
    return evs


def test_valid_ante_cycle_verifies():
    wl = _wl()
    evs = _fixture(wl)
    errs, balances, _ = wl.verify(evs)
    assert errs == []
    assert balances["pool:doe:doe-expert"] == 0
    assert wl.ante_review(evs) == []


def test_ruleless_negative_draw_is_invalid_and_errors():
    wl = _wl()
    evs = _fixture(wl, rule=False)
    errs, _, _ = wl.verify(evs)
    assert any("negative balance" in e for e in errs)
    clauses = {f["clause"] for f in wl.ante_review(evs)}
    assert "(e)" in clauses


def test_missing_vintage_flags_clause_a():
    wl = _wl()
    evs = _fixture(wl, vintage=False)
    clauses = {f["clause"] for f in wl.ante_review(evs)}
    assert "(a)" in clauses


def test_participation_set_moves_no_value():
    wl = _wl()
    evs = _fixture(wl)
    _, balances, _ = wl.verify(evs[:2])
    assert balances["pool:doe:doe-expert"] == 0
    assert evs[1]["delta"] == 0
