#!/usr/bin/env python3
"""MoneyBall site wallet ledger (wallet-ledger/v1) — fold + verify.

Ledger of record: ops/agentic-gambling/site/wallet-ledger.jsonl
(append-only; DESIGN §4.2 in timerloggedout-spec/moneyball/docs/DESIGN.md).
Balances are a derived fold of events, never a stored field; each
event's balance_after is a claim this tool recomputes. Receipts are
hash-chained: payload_hash = sha256(canonical event JSON sans
receipt), prev_receipt_hash links the chain.

Modes:
  verify LEDGER  — chain integrity, fold == balance_after claims,
                   genesis equality across site wallets; exit 1 on gap
  fold   LEDGER  — print derived balances as JSON
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

def load(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]

def payload_hash(ev):
    body = {k: v for k, v in ev.items() if k != "receipt"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def verify(events):
    errs, balances, genesis, prev = [], {}, {}, "GENESIS"
    for i, ev in enumerate(events, 1):
        if ev.get("seq") != i:
            errs.append(f"seq gap at line {i}: seq={ev.get('seq')}")
        rc = ev.get("receipt") or {}
        h = payload_hash(ev)
        if rc.get("payload_hash") != h:
            errs.append(f"seq {i}: payload_hash mismatch")
        if rc.get("prev_receipt_hash") != prev:
            errs.append(f"seq {i}: chain break (prev_receipt_hash)")
        prev = h
        wid = ev.get("wallet_id")
        balances[wid] = balances.get(wid, 0) + ev.get("delta", 0)
        if ev.get("balance_after") != balances[wid]:
            errs.append(f"seq {i}: balance_after {ev.get('balance_after')} != fold {balances[wid]} for {wid}")
        if balances[wid] < 0:
            errs.append(f"seq {i}: negative balance for {wid}")
        if ev.get("type") == "faucet_issued" and (ev.get("ref") or {}).get("kind") == "genesis_ruling":
            genesis[wid] = ev["delta"]
    if genesis:
        amounts = set(genesis.values())
        if len(amounts) != 1:
            errs.append(f"genesis NOT equal across wallets: {genesis}")
    return errs, balances, genesis

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["verify", "fold"])
    ap.add_argument("ledger")
    a = ap.parse_args()
    events = load(a.ledger)
    errs, balances, genesis = verify(events)
    if a.mode == "fold":
        print(json.dumps(balances, indent=1, sort_keys=True))
    if errs:
        print("WALLET LEDGER VERIFY FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
    print(f"wallet-ledger ok: {len(events)} events, {len(balances)} wallets, "
          f"genesis equal x{len(genesis)} @ {next(iter(set(genesis.values())), 0)} soft_quota_token, chain intact")

if __name__ == "__main__":
    main()
