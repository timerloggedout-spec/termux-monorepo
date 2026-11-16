#!/usr/bin/env python3
"""Unified CLI: python3 -m scripts.model_selection_market.cli <cmd>"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow `python3 scripts/model_selection_market/cli.py` from repo root
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.model_selection_market.bootstrap import bootstrap_equal_weights  # noqa: E402
from scripts.model_selection_market.dspy_doe import DoeArm, DspyDoeStub  # noqa: E402
from scripts.model_selection_market.ledger import LedgerSample, PerformanceLedger  # noqa: E402
from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard  # noqa: E402
from scripts.model_selection_market.selector import select_models  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="model-selection-market")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("bootstrap", help="MSM-001 equal-weight table")
    led = sub.add_parser("ledger-demo", help="MSM-002 append demo sample + aggregate")
    led.add_argument("--path", type=Path, default=None)
    sel = sub.add_parser("select", help="MSM-003 select")
    sel.add_argument("--role", default="triage")
    sel.add_argument("--mode", default="series", choices=["series", "parallel", "concurrent"])
    sel.add_argument("-k", type=int, default=3)
    sub.add_parser("dspy-demo", help="MSM-004 A/B/C/D stub arms")
    sub.add_parser("market-demo", help="MSM-005 card + bet snapshot")
    sub.add_parser("all-demo", help="run all demos once")

    args = p.parse_args(argv)
    out: dict = {}

    if args.cmd == "bootstrap":
        out = bootstrap_equal_weights()
    elif args.cmd == "ledger-demo":
        L = PerformanceLedger(args.path)
        L.append(
            LedgerSample(
                role="triage",
                model_id="stealth/ox-alpha",
                dimensions={"correctness_gate_pass": True, "resource_cost": 1},
            )
        )
        out = L.aggregate()
    elif args.cmd == "select":
        out = select_models(role=args.role, mode=args.mode, k=args.k)
    elif args.cmd == "dspy-demo":
        stub = DspyDoeStub()
        for aid, sig in [("A", "v1"), ("B", "v2"), ("C", "cot"), ("D", "short")]:
            stub.run_arm(DoeArm(arm_id=aid, signature=sig))
        out = {"runs": stub.runs, "summary": stub.cohort_summary()}
    elif args.cmd == "market-demo":
        g = MarketGraph()
        c = TradingCard(role="review", owner="qwen-coder-card")
        g.add_card(c)
        g.place_bet(
            BetEntry(
                actor_class="job",
                subject_kind="job",
                subject_id="help-wanted",
                role="review",
                card_id=c.card_id(),
            )
        )
        out = g.snapshot()
    elif args.cmd == "all-demo":
        out = {
            "bootstrap_model_count": bootstrap_equal_weights()["model_count"],
            "select_series": select_models(mode="series"),
            "select_parallel": select_models(mode="parallel", k=2),
            "select_concurrent": select_models(mode="concurrent"),
            "dspy": DspyDoeStub().cohort_summary(),
            "market_edges": MarketGraph().snapshot()["edges"],
        }
        stub = DspyDoeStub()
        stub.run_arm(DoeArm(arm_id="A", signature="demo"))
        out["dspy"] = stub.cohort_summary()
        g = MarketGraph()
        g.add_card(TradingCard(role="triage", owner="demo"))
        out["market_edges"] = g.snapshot()["edges"]

    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
