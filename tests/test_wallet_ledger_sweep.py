"""Custodial sweeps on the site wallet ledger (wallet_ledger.py
mode 'sweep') — Fireblocks trigger model, paper analogue (6REA7
research annex section 4). Thresholds are config, never invented:
NOT_ESTABLISHED classes never fire."""
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


def _ledger(wl, tmp_path, balance=1000):
    evs = [{"seq": 1, "ts": "2026-11-03T00:00:00Z",
            "type": "wallet_provisioned", "wallet_id": "paper:abc",
            "class": "speculator", "delta": 0, "balance_after": 0,
            "ref": {"kind": "provisioning_record", "source": "test"}},
           {"seq": 2, "ts": "2026-11-03T00:01:00Z",
            "type": "wallet_provisioned",
            "wallet_id": "pool:speculator:abc-instance",
            "class": "pool", "delta": 0, "balance_after": 0,
            "ref": {"kind": "pool_creation"}},
           {"seq": 3, "ts": "2026-11-03T00:02:00Z",
            "type": "faucet_issued", "wallet_id": "paper:abc",
            "class": "speculator", "delta": balance,
            "balance_after": balance,
            "ref": {"kind": "genesis_ruling", "rule": "test"}}]
    prev = "GENESIS"
    for ev in evs:
        h = wl.payload_hash(ev)
        ev["receipt"] = {"receipt_id": f"wr-{ev['seq']:04d}-{h[:12]}",
                         "wallet_id": ev["wallet_id"],
                         "event_seq": ev["seq"], "payload_hash": h,
                         "prev_receipt_hash": prev}
        prev = h
    p = tmp_path / "ledger.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in evs) + "\n")
    return p


IDX = {"paper:abc": "abc-instance"}


def test_threshold_fires_on_excess(tmp_path):
    wl = _wl()
    p = _ledger(wl, tmp_path)
    sweeps, _ = wl.plan_sweeps({"paper:abc": 1000},
                               {"thresholds": {"speculator": 250}},
                               IDX, "threshold")
    assert len(sweeps) == 1 and sweeps[0]["amount"] == 750
    assert sweeps[0]["pool"] == "pool:speculator:abc-instance"
    new = wl.sweep_events(wl.load(p), sweeps)
    assert [e["type"] for e in new] == ["sweep_transferred"] * 2
    assert [e["delta"] for e in new] == [-750, 750]
    errs, balances, _ = wl.verify(wl.load(p) + new)
    assert errs == [] and balances["paper:abc"] == 250
    assert balances["pool:speculator:abc-instance"] == 750


def test_threshold_not_established_never_fires():
    wl = _wl()
    sweeps, notes = wl.plan_sweeps(
        {"paper:abc": 1000},
        {"thresholds": {"speculator": "NOT_ESTABLISHED"},
         "default": "NOT_ESTABLISHED"}, IDX, "threshold")
    assert sweeps == []
    assert any("NOT_ESTABLISHED" in n for n in notes)


def test_settlement_sweeps_full_and_manual_validates(tmp_path):
    wl = _wl()
    sweeps, _ = wl.plan_sweeps({"paper:abc": 1000}, {}, IDX,
                               "settlement", wallet="paper:abc")
    assert sweeps[0]["amount"] == 1000
    try:
        wl.plan_sweeps({"paper:abc": 100}, {}, IDX, "manual",
                       wallet="paper:abc", amount=500)
        raise AssertionError("over-balance manual sweep not rejected")
    except ValueError:
        pass


def test_live_config_is_unruled():
    cfg = json.loads((ROOT / "ops/agentic-gambling/site"
                      / "sweep-thresholds.json").read_text())
    assert cfg["default"] == "NOT_ESTABLISHED"
    assert all(v == "NOT_ESTABLISHED"
               for v in cfg["thresholds"].values())
