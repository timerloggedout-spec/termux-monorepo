#!/usr/bin/env python3
"""Speculators strategy registry — multiple token strategies, one table.

Source of record: timerloggedout-spec/speculators_fork (fork of
vllm-project/speculators) @ c13304cf3ec2, filed under
termux-monorepo issue #195 (Evaluations: "Multiple Token
Strategies Implementations").

Every strategy here is a speculative-decoding token strategy:
a draft side proposes tokens, the verifier (target) model checks
them in one forward pass, and accepted tokens are guaranteed to
match verifier-only decoding (lossless). `baseline` is the
verifier-only control arm — no drafting — against which speedup
is measured.

Fork-module paths and drafting modes are read from the fork tree
itself (src/speculators/models/<name>, docs/user_guide/algorithms/
<name>.md, src/speculators/proposals/greedy.py); a strategy whose
fork module disappears fails the registry test in
tests/test_speculators.py rather than drifting silently.
"""
from __future__ import annotations

FORK_REPO = "timerloggedout-spec/speculators_fork"
FORK_REF = "c13304cf3ec212171c7ad536f18698a7c67f18a8"

STRATEGIES: dict[str, dict] = {
    "baseline": {
        "name": "Baseline (verifier only)",
        "fork_module": None,
        "fork_docs": None,
        "drafting_mode": "none",
        "draft_side": "none — verifier generates every token",
        "lossless": True,
        "notes": "Control arm. Speedup denominator for every "
                 "speculative cell.",
    },
    "eagle3": {
        "name": "EAGLE-3",
        "fork_module": "src/speculators/models/eagle3",
        "fork_docs": "docs/user_guide/algorithms/eagle3.md",
        "drafting_mode": "sequential",
        "draft_side": "draft model conditioned on auxiliary hidden "
                      "states from multiple verifier layers",
        "lossless": True,
        "notes": "Sequential per-token drafting; the reference "
                 "speculator family in the fork.",
    },
    "peagle": {
        "name": "P-EAGLE",
        "fork_module": "src/speculators/models/peagle",
        "fork_docs": "docs/user_guide/algorithms/peagle.md",
        "drafting_mode": "parallel",
        "draft_side": "parallel multi-token prediction via "
                      "Conditional-On-Distribution (COD) sampling",
        "lossless": True,
        "notes": "Extends EAGLE-3; predicts multiple tokens in a "
                 "single forward pass, cutting drafting latency.",
    },
    "dflash": {
        "name": "DFlash",
        "fork_module": "src/speculators/models/dflash",
        "fork_docs": "docs/user_guide/algorithms/dflash.md",
        "drafting_mode": "anchored-block",
        "draft_side": "anchored-block drafting from auxiliary "
                      "hidden states of multiple verifier layers; "
                      "sliding-window attention on draft layers "
                      "by default",
        "lossless": True,
        "notes": "Block drafting; CLI carries block size and max "
                 "anchors options in the fork.",
    },
    "dspark": {
        "name": "DSpark",
        "fork_module": "src/speculators/models/dspark",
        "fork_docs": "docs/user_guide/algorithms/dspark.md",
        "drafting_mode": "anchored-block+markov+confidence",
        "draft_side": "DFlash anchored-block drafting + Markov "
                      "head (each draft position conditioned on "
                      "the previous in-block token) + confidence "
                      "head (per-position acceptance probability)",
        "lossless": True,
        "notes": "Checkpoints can warm-start from DFlash "
                 "checkpoints.",
    },
    "mtp": {
        "name": "MTP finetuning",
        "fork_module": "src/speculators/models/mtp",
        "fork_docs": "docs/user_guide/algorithms/mtp.md",
        "drafting_mode": "native-heads",
        "draft_side": "the verifier's own native Multi-Token "
                      "Prediction heads, finetuned on domain data "
                      "(FastMTP approach)",
        "lossless": True,
        "notes": "No separate draft model; head is small "
                 "(~100M-400M params) and trains on pre-extracted "
                 "hidden states without loading the full verifier.",
    },
}


def strategy_ids() -> list[str]:
    """Deterministic (sorted) strategy id list."""
    return sorted(STRATEGIES)


def speculative_ids() -> list[str]:
    """All strategies except the verifier-only control arm."""
    return [s for s in strategy_ids() if s != "baseline"]
