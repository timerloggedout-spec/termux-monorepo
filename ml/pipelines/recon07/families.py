"""Family locks. EXTRACT never means overwrite a peer branch."""
from __future__ import annotations

WHOLESALE_ML = frozenset({432, 549, 601, 682, 746, 787, 817})
MINESWEEPER = frozenset({65, 140, 481, 630, 672, 680, 750, 1151, 1182, 1185, 1186})
STAGING_ONLY = frozenset({48, 788})
NEED_EVIDENCE_SLICES = frozenset({806, 809})
EVIDENCE_INCIDENTS = frozenset({1023, 1024, 1025, 1026})


def family_of(number: int) -> str:
    if number in WHOLESALE_ML:
        return "wholesale-ml"
    if number in MINESWEEPER:
        return "minesweeper"
    if number in STAGING_ONLY:
        return "staging-only"
    if number in NEED_EVIDENCE_SLICES:
        return "need-evidence-slice"
    if number in EVIDENCE_INCIDENTS:
        return "actions-incident"
    return "unscoped"


def forbidden_actions(number: int) -> tuple[str, ...]:
    family = family_of(number)
    if family == "wholesale-ml":
        return ("wholesale-merge", "force-push-master")
    if family == "minesweeper":
        return ("overwrite-peer", "auto-promote", "force-push-master")
    if family == "staging-only":
        return ("retarget-master", "wholesale-merge")
    if family == "need-evidence-slice":
        return ("promote-without-dual-gate",)
    if family == "actions-incident":
        return ("treat-as-promote-gate",)
    return ("force-push-master",)
