#!/usr/bin/env python3
"""nc-1 wave-2 flags producer: score corpus units with the v2 features
(claim<->ref adjacency + symbol-function) and emit evaluator --flags
JSONL rows {unit_id, layer, drift, borderline, score, tokens_scanned,
adj_refs, connective_per_100w}. Layer := L2 for chat stratum, L3 else.
The operator set is loaded from linguist-panel-feed/v1 at runtime
(--feed PATH or $LINGUIST_PANEL_FEED); it is never hard-coded.

Usage: flags_v2.py UNITS.jsonl --feed FEED.json [-o OUT.jsonl]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compliance_scorer import load_operator_set, score_v2  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("units")
    ap.add_argument("--feed", default=os.environ.get("LINGUIST_PANEL_FEED"))
    ap.add_argument("-o", "--out")
    args = ap.parse_args()
    if not args.feed:
        print("::error::--feed or $LINGUIST_PANEL_FEED required (operator set "
              "is registry-derived, never hard-coded)", file=sys.stderr)
        return 2
    ops = load_operator_set(args.feed)
    rows = []
    with open(args.units) as fh:
        for line in fh:
            if not line.strip():
                continue
            u = json.loads(line)
            r = score_v2(u.get("text") or "", ops)
            rows.append({
                "unit_id": u["unit_id"],
                "layer": "L2" if u.get("stratum") == "chat" else "L3",
                "drift": r["verdict_v2"] == "prose",
                "borderline": r["verdict_v2"] == "borderline",
                "score": r["score_v2"],
                "tokens_scanned": r["words"],
                "adj_refs": r["adj_refs"],
                "connective_per_100w": r["connective_per_100w"],
            })
    out = open(args.out, "w") if args.out else sys.stdout
    for r in rows:
        out.write(json.dumps(r) + "\n")
    if args.out:
        out.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
