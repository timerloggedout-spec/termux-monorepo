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
  sweep  LEDGER --config CONFIG [--wallets WALLETS_JSON]
                [--trigger threshold|settlement|manual]
                [--wallet ID] [--amount N] [--dry-run]
                 — custodial sweeps, paper analogue of the Fireblocks
                   trigger model (6REA7 research annex §4): move a
                   wallet's balance to its pool as a paired
                   `sweep_transferred` event set (debit + credit,
                   hash-chained like every ledger move; modeled on
                   the cull_transferred paired pattern).
                   Triggers: threshold (fold balance > the class
                   threshold in CONFIG ⇒ sweep the excess) ·
                   settlement (full balance, named wallet) · manual
                   (named wallet, named amount or full balance).
                   Threshold VALUES are unruled: CONFIG carries
                   "NOT_ESTABLISHED" per class and the engine NEVER
                   invents a default — an unruled class never fires.
                   Pool mapping: paper:<instance> → its instance pool
                   pool:speculator:<participant slug> (via WALLETS_JSON);
                   fallback pool:other:pooled-buckets.
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

FALLBACK_POOL = "pool:other:pooled-buckets"
SWEEP_REF = {"kind": "sweep",
             "source": "scripts/moneyball/wallet_ledger.py sweep engine",
             "rule": "Fireblocks trigger model, paper analogue (6REA7 "
                     "research annex section 4; moneyball PR #19)"}


def _slug(text):
    import re
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return re.sub(r"-+", "-", s)


def pool_for(wallet_id, wallets_index):
    """Destination pool for a wallet: its instance pool when the
    wallets index (WALLETS.json) maps it, else the pooled-buckets
    fallback. Returns None when the wallet IS a pool."""
    if wallet_id.startswith("pool:"):
        return None
    participant = (wallets_index or {}).get(wallet_id)
    if participant:
        return f"pool:speculator:{_slug(participant)}"
    return FALLBACK_POOL


def plan_sweeps(balances, config, wallets_index, trigger,
                wallet=None, amount=None):
    """Returns (sweeps, notes). Each sweep: {source, pool, amount,
    trigger}. Deterministic from the fold — no discretion."""
    thresholds = (config or {}).get("thresholds") or {}
    default_th = (config or {}).get("default", "NOT_ESTABLISHED")
    sweeps, notes = [], []
    if trigger == "threshold":
        for wid in sorted(balances):
            pool = pool_for(wid, wallets_index)
            if pool is None or balances[wid] <= 0:
                continue
            cls = "speculator" if wid.startswith("paper:") else "other"
            th = thresholds.get(cls, default_th)
            if not isinstance(th, (int, float)):
                notes.append(f"{wid}: threshold {cls} NOT_ESTABLISHED "
                             f"(unruled) — never fires")
                continue
            excess = balances[wid] - th
            if excess > 0:
                sweeps.append({"source": wid, "pool": pool,
                               "amount": excess,
                               "trigger": {"kind": "threshold",
                                           "class": cls,
                                           "threshold": th,
                                           "balance_before":
                                               balances[wid]}})
            else:
                notes.append(f"{wid}: balance {balances[wid]} <= "
                             f"threshold {th} — no sweep")
        return sweeps, notes
    # settlement / manual act on one named wallet
    if not wallet:
        raise ValueError(f"--trigger {trigger} requires --wallet")
    if wallet not in balances:
        raise ValueError(f"wallet {wallet} not in fold")
    pool = pool_for(wallet, wallets_index)
    if pool is None:
        raise ValueError(f"wallet {wallet} is a pool — pools do not "
                         f"sweep to themselves")
    bal = balances[wallet]
    amt = bal if amount is None else amount
    if amt <= 0:
        notes.append(f"{wallet}: balance {bal} — nothing to sweep")
        return sweeps, notes
    if amt > bal:
        raise ValueError(f"amount {amt} exceeds balance {bal} for "
                         f"{wallet} (fail-closed)")
    trig = {"kind": trigger, "balance_before": bal}
    if trigger == "manual":
        trig["op"] = "custodian manual op"
    sweeps.append({"source": wallet, "pool": pool, "amount": amt,
                   "trigger": trig})
    return sweeps, notes


def sweep_events(events, sweeps):
    """Build the paired sweep_transferred events (debit + credit)
    continuing the hash chain from the ledger's last receipt."""
    import datetime
    ts = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prev = events[-1]["receipt"]["payload_hash"] if events else \
        "GENESIS"
    seq = len(events)
    _, balances, _ = verify(events)
    out = []
    for sw in sweeps:
        seq += 1
        sweep_id = f"sweep-{seq:04d}"
        for leg, wid, delta in (("debit", sw["source"],
                                 -sw["amount"]),
                                ("credit", sw["pool"], sw["amount"])):
            if leg == "credit":
                seq += 1
            balances[wid] = balances.get(wid, 0) + delta
            ev = {"seq": seq, "ts": ts, "type": "sweep_transferred",
                  "wallet_id": wid, "class": "pool" if
                  wid.startswith("pool:") else "speculator",
                  "kind": "paper|test",
                  "unit": "soft_quota_token (observational)",
                  "delta": delta, "balance_after": balances[wid],
                  "sweep_id": sweep_id, "leg": leg,
                  "trigger": sw["trigger"],
                  "pool_destination": sw["pool"],
                  "source_wallet": sw["source"],
                  "ref": dict(SWEEP_REF)}
            h = payload_hash(ev)
            ev["receipt"] = {"receipt_id": f"wr-{seq:04d}-{h[:12]}",
                             "wallet_id": wid, "event_seq": seq,
                             "payload_hash": h,
                             "prev_receipt_hash": prev}
            prev = h
            out.append(ev)
    return out


def run_sweep(a):
    events = load(a.ledger)
    errs, balances, _ = verify(events)
    if errs:
        print("WALLET LEDGER VERIFY FAILED (pre-sweep):")
        [print(" -", e) for e in errs]
        sys.exit(1)
    config = json.loads(Path(a.config).read_text()) if a.config \
        else {}
    wallets_index = {}
    if a.wallets:
        wj = json.loads(Path(a.wallets).read_text())
        wallets_index = {w["wallet_id"]: w["participant"]
                         for w in wj.get("wallets", [])}
    sweeps, notes = plan_sweeps(balances, config, wallets_index,
                                a.trigger, a.wallet, a.amount)
    result = {"trigger": a.trigger, "planned": sweeps,
              "notes": notes, "appended": 0, "dry_run": a.dry_run}
    if sweeps and not a.dry_run:
        new = sweep_events(events, sweeps)
        errs2, _, _ = verify(events + new)
        if errs2:
            print("SWEEP ABORTED — post-append verify failed:")
            [print(" -", e) for e in errs2]
            sys.exit(1)
        with open(a.ledger, "a") as f:
            for ev in new:
                f.write(json.dumps(ev) + "\n")
        result["appended"] = len(new)
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["verify", "fold", "sweep"])
    ap.add_argument("ledger")
    ap.add_argument("--config")
    ap.add_argument("--wallets")
    ap.add_argument("--trigger",
                    choices=["threshold", "settlement", "manual"],
                    default="threshold")
    ap.add_argument("--wallet")
    ap.add_argument("--amount", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.mode == "sweep":
        sys.exit(run_sweep(a))
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
