#!/usr/bin/env python3
"""Speculators paper|test wallets — provisioning + verification.

Wallet invariant (ops/agentic-gambling/lane.json component
`wallets-participant`, owner 2026-11-01): every participant has
a wallet — universal, required-by-design. The speculator
(Speculators) is a concrete participant implementation whose
records/wallets/standing stay distinct from the gambler class
(lane.json naming-collapse scope note), so this campaign keeps
its own wallet ledger: experiments/speculators/token-strategies/
WALLETS.json, keyed by configured instance (instance_key from
PLAN.json — one wallet per cell instance, never per bare model).

Paper|test: these wallets are paper/test provisioning — the
seed substrate is observational soft_quota_token (lane.json);
genesis balance is 0 and no real value moves. Provisioning is
the act of record: a participant without a wallet record here
is unprovisioned, whatever its PLAN row says.

Culling wallet waterfall (owner rule 2026-11-01/02; PRs #3747,
#3748): cull -> the culled participant's wallet balance
transfers to the pooled buckets (promotions / incentives /
bonuses) — culling never destroys wallet value; the cull record
itself names {culled_participant, wallet_balance_at_cull,
pool_destination}. A culled participant's residual/royalty
stream is explicitly NOT folded by the waterfall (separate
owner question, PR #3747) — paper wallets carry no such stream.

Modes:
  provision  PLAN.json -> WALLETS.json (deterministic genesis
             ledger; refuses to overwrite an existing ledger —
             balances are state, not plan output)
  verify     PLAN.json + WALLETS.json -> every planned instance
             provisioned exactly once, every wallet carrying
             the waterfall; exit 1 naming the gap otherwise
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

POOL_DESTINATION = "pooled-buckets (promotions/incentives/bonuses)"
WATERFALL = {
    "on_cull": "wallet balance transfers to pool_destination — "
               "culling never destroys wallet value",
    "cull_record_names": ["culled_participant",
                          "wallet_balance_at_cull",
                          "pool_destination"],
    "pool_destination": POOL_DESTINATION,
    "residual_stream": "NOT folded (separate owner question, "
                       "PR #3747); paper wallets carry none",
}


def build_ledger(plan: dict) -> dict:
    instances: dict[str, dict] = {}
    for row in plan["rows"]:
        inst = row["instance"]
        instances[inst["instance_key"]] = {
            "participant": inst["model"],
            "cell_first_run": row["run_id"],
            "factors": row["factors"],
        }
    wallets = []
    for key in sorted(instances):
        inst = instances[key]
        wallets.append({
            "wallet_id": f"paper:{key[:16]}",
            "participant": inst["participant"],
            "instance_key": key,
            "factors": inst["factors"],
            "kind": "paper|test",
            "unit": "soft_quota_token (observational)",
            "balance": 0,
            "status": "provisioned",
            "cull_waterfall": WATERFALL,
        })
    return {
        "schema": "speculators-wallets/v1",
        "campaign_id": plan["campaign_id"],
        "kind": "paper|test",
        "rule": "wallet invariant (ops/agentic-gambling/lane.json "
                "wallets-participant): every participant has a "
                "wallet; speculator wallets stay distinct from "
                "the gambler class at record level",
        "pool_destination": POOL_DESTINATION,
        "wallets": wallets,
    }


def verify(campaign_dir: Path) -> list[str]:
    plan = json.loads((campaign_dir / "PLAN.json").read_text())
    ledger = json.loads((campaign_dir / "WALLETS.json").read_text())
    planned = {r["instance"]["instance_key"] for r in plan["rows"]}
    gaps = []
    seen: dict[str, int] = {}
    for w in ledger["wallets"]:
        seen[w["instance_key"]] = seen.get(w["instance_key"], 0) + 1
        if w.get("kind") != "paper|test":
            gaps.append(f"{w['wallet_id']}: kind != paper|test")
        wf = w.get("cull_waterfall") or {}
        if wf.get("pool_destination") != POOL_DESTINATION:
            gaps.append(f"{w['wallet_id']}: waterfall pool mismatch")
        if wf.get("cull_record_names") != WATERFALL[
                "cull_record_names"]:
            gaps.append(f"{w['wallet_id']}: cull record names gap")
    for key in sorted(planned):
        if seen.get(key, 0) != 1:
            gaps.append(f"instance {key[:12]}: "
                        f"{seen.get(key, 0)} wallets (want 1)")
    for key in sorted(seen):
        if key not in planned:
            gaps.append(f"wallet for unplanned instance {key[:12]}")
    return gaps


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["provision", "verify"])
    ap.add_argument("campaign_dir", type=Path)
    args = ap.parse_args()
    if args.mode == "provision":
        out = args.campaign_dir / "WALLETS.json"
        if out.exists():
            print("refused: WALLETS.json exists (balances are "
                  "state, not plan output)")
            return 1
        plan = json.loads(
            (args.campaign_dir / "PLAN.json").read_text())
        out.write_text(json.dumps(build_ledger(plan), indent=1,
                                  sort_keys=True) + "\n")
        print(f"provisioned {len(build_ledger(plan)['wallets'])} "
              f"paper|test wallets -> {out}")
        return 0
    gaps = verify(args.campaign_dir)
    if gaps:
        print("UNPROVISIONED / DRIFT:")
        for g in gaps:
            print(" -", g)
        return 1
    print("verify: all planned instances provisioned exactly "
          "once, waterfall intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
