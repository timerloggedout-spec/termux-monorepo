#!/usr/bin/env python3
"""nc-1 evaluator — scores notation-drift detector arms on the gold corpus.

Arms (DESIGN #2865): L3-only (GitHub-surface units), L2-only (chat
units), L3+L2 (union), FULL (union flags => L1 validation queue; only
L1-confirmed flags count, so FULL precision/recall stay PENDING_L1
here — the queue is emitted for main/doe-expert adjudication).

Detector of record for run-001 = reference implementation of the
pre-registered metric: flag iff prose_ratio > tau (tau from
records/TAU-AMENDMENT.md, set pre-scoring). Tier-1 L3/L2 builds plug
in later by replacing `reference_flags` with their flag files
(same {unit_id: bool} shape) — responses/cost accounting unchanged.

Cost model: tokens_scanned = corpus tokens the arm reads; FULL adds
L1 re-read of flagged units only (classifier-first cascade).
chat_noise_events: this harness performs no chat or GitHub writes —
0 by construction.

Usage: nc1_evaluator.py <units.jsonl> <tau> [out.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nc1_features import features  # noqa: E402

ARMS = {"L3-only": {"github"}, "L2-only": {"chat"},
        "L3+L2": {"github", "chat"}, "FULL": {"github", "chat"}}


def score(units, flags, surfaces):
    sub = [u for u in units if u["surface"] in surfaces]
    tp = sum(1 for u in sub if flags[u["unit_id"]] and u["label"] == "drift")
    fp = sum(1 for u in sub if flags[u["unit_id"]] and u["label"] == "compliant")
    fn = sum(1 for u in sub if not flags[u["unit_id"]] and u["label"] == "drift")
    scanned = sum(u["_tokens"] for u in sub)
    return {"units": len(sub), "tp": tp, "fp": fp, "fn": fn,
            "precision": round(tp / (tp + fp), 4) if tp + fp else None,
            "recall": round(tp / (tp + fn), 4) if tp + fn else None,
            "tokens_scanned": scanned,
            "tokens_per_confirmed_drift": round(scanned / tp, 1) if tp else None}


def main(argv):
    units = [json.loads(l) for l in Path(argv[1]).read_text().splitlines() if l.strip()]
    tau = float(argv[2])
    feat = {}
    for u in units:
        f = features(u["text"])
        u["_tokens"] = f["tokens"]
        feat[u["unit_id"]] = f
    flags = {u["unit_id"]: feat[u["unit_id"]]["prose_ratio"] > tau for u in units}
    arms = {name: score(units, flags, s) for name, s in ARMS.items()
            if name != "FULL"}
    union = arms["L3+L2"]
    l1_queue = [{"unit_id": u["unit_id"], "surface": u["surface"],
                 "gold_label": u["label"], **feat[u["unit_id"]]}
                for u in units if flags[u["unit_id"]]]
    full = dict(union)
    full.update({"precision": "PENDING_L1", "recall": "PENDING_L1",
                 "l1_queue_units": len(l1_queue),
                 "l1_reread_tokens": sum(feat[q["unit_id"]]["tokens"] for q in l1_queue),
                 "tokens_scanned": union["tokens_scanned"]})
    arms["FULL"] = full
    # cull pricing (DESIGN): price each layer on the FULL population —
    # layers cover disjoint surfaces, so removal = scoring the full set
    # with only the remaining layer's flags (recall drops by the removed
    # layer's unique coverage), against the token saving.
    full_recall = union["recall"]
    cull = {}
    for layer, rest_surfaces in (("L3", {"chat"}), ("L2", {"github"})):
        sub = [u for u in units if u["surface"] in rest_surfaces]
        tp_rest = sum(1 for u in sub if flags[u["unit_id"]] and u["label"] == "drift")
        fn_rest = sum(1 for u in units if u["label"] == "drift") - tp_rest
        recall_rest = round(tp_rest / (tp_rest + fn_rest), 4)
        toks_rest = sum(u["_tokens"] for u in sub)
        cull[layer] = {"recall_cost_if_removed": round(full_recall - recall_rest, 4),
                       "token_saving_frac": round(1 - toks_rest / union["tokens_scanned"], 4),
                       "culled_by_rule": (full_recall - recall_rest) < 0.03
                       and (1 - toks_rest / union["tokens_scanned"]) > 0.25}
    out = {"campaign": "nc-1-notation-compliance", "run": "run-001",
           "detector": "reference_core (prose_ratio > tau); Tier-1 flags plug-in pending",
           "tau": tau, "corpus_units": len(units),
           "features": feat, "arms": arms, "cull_analysis": cull,
           "l1_queue": l1_queue, "chat_noise_events": 0}
    text = json.dumps(out, indent=1)
    if len(argv) > 3:
        Path(argv[3]).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
