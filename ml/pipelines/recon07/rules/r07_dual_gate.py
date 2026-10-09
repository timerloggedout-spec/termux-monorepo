"""Promote requires dual-gate on this SHA. Review bots are non-gate."""
from __future__ import annotations

from ml.pipelines.recon07.types import Finding

RULE_ID = "R07"
NON_GATES = ("vercel", "copilot", "coderabbit", "qodo", "devin", "gitlab")


def evaluate(ctx: dict[str, object]) -> Finding:
    gates = ctx.get("gates") if isinstance(ctx.get("gates"), dict) else {}
    named = gates or {}
    if not named:
        return Finding(RULE_ID, True, "no candidate gates in this recon context")
    ok = named.get("repo-gate") == "success" and named.get("termux-smoke") == "success"
    if any(named.get(name) == "success" for name in NON_GATES) and not ok:
        ok = False
    return Finding(RULE_ID, ok, "repo-gate and termux-smoke are the only promote pair")
