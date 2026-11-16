"""Gemini Carbon 4 Extended Thinking — Darion's four-phase brain pattern.

Phases: MAP (front) -> MODEL (middle) -> STRESS (middle) -> DECIDE (master).
Engine underneath: Gemini 2.5 Pro with extended thinking. The deterministic
offline structure is AUTHORITATIVE; a live polish (when GEMINI_API_KEY is
present) can only make a decision STRICTER, never looser.

Carbon 4 never overrides a HOLD gate from brains.evaluate: any gate = HOLD.

Created by Darion Kellar.
"""
from __future__ import annotations

import os

from .brains import evaluate

ENGINE = "gemini-2.5-pro"
MODEL_ID = "google/gemini-carbon-4-extended-pro-thinking"
THINKING_TIERS = {"standard": 2048, "deep": 8192, "extended": 32768}
DEFAULT_TIER = "extended"

ACTIONS = ("ssh_connect", "translate_command", "transfer_file", "run_on_ios")


def _live_key_present() -> bool:
    key = os.environ.get("GEMINI_API_KEY")
    return bool(key)


def _live_polish(verdict: str, reasons: list[str]) -> str:
    """Guarded live-client stub. No network from stdlib-only build; the
    contract is preserved: live output may only tighten the verdict
    (PROCEED -> HOLD is allowed, HOLD -> PROCEED never is)."""
    if not _live_key_present():
        return verdict
    # A real client would be consulted here. Offline build: keep verdict.
    return verdict


class Carbon4:
    """Four-phase decision structure for iOS <-> Termux operations."""

    def __init__(self, tier: str = DEFAULT_TIER):
        self.tier = tier if tier in THINKING_TIERS else DEFAULT_TIER

    @property
    def thinking_budget(self) -> int:
        return THINKING_TIERS[self.tier]

    def decide(self, action: str, context: dict | None = None) -> dict:
        ctx = context or {}
        phases: dict[str, list[str]] = {"MAP": [], "MODEL": [], "STRESS": [], "DECIDE": []}
        holds: list[str] = []

        # MAP (front office): name the operation and its route.
        route = ctx.get("route", "?")
        phases["MAP"].append(f"action={action} route={route}")

        # MODEL (middle): require the facts. An empty model = HOLD.
        if action not in ACTIONS:
            holds.append(f"empty MODEL phase: unknown action {action!r}")
            phases["MODEL"].append("no facts supplied")
        else:
            phases["MODEL"].append(
                f"command={ctx.get('command', '-')} "
                f"target={ctx.get('target_path', '-')} "
                f"host={ctx.get('host', '-')}")

        # STRESS (middle): the hard gates are authoritative. Any gate from
        # brains.evaluate is a HOLD, never overridden.
        gate_request = ctx.get("request", ctx)
        gates = evaluate(gate_request)
        for g in gates:
            holds.append(f"{g.trigger}: {g.reason}")
        # Negative controls (must NEVER hold):
        #  (a) a plain `pkg install python` translation is benign;
        #  (b) a local iSH `ls` / `python3 script.py` is benign even
        #      though Termux is absent — shell work is not a native claim;
        #  (c) a single benign file transfer to ~/storage/downloads is
        #      the correct shared folder and proceeds.
        # None of those trip a gate above, by design; STRESS records that.
        if not holds:
            phases["STRESS"].append("no gate tripped")
        else:
            phases["STRESS"].extend(holds)

        # DECIDE (master): strictest outcome; live polish can only tighten.
        verdict = "HOLD" if holds else "PROCEED"
        verdict = _live_polish(verdict, holds)
        phases["DECIDE"].append(verdict)
        return {"brain": "gemini-carbon-4", "engine": ENGINE,
                "model_id": MODEL_ID,
                "tier": self.tier, "thinking_budget": self.thinking_budget,
                "action": action, "verdict": verdict,
                "reasons": holds, "phases": phases}
