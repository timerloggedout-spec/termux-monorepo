#!/usr/bin/env python3
"""Quota gate for AI Studio Delphi rounds (ai-studio-mesh, both legs).

[MUSEai]@{role:{google-ai-studio}}

Pure-stdlib, deterministic. Decides ALLOW / DEFER for one panel run
against the model's verified free-tier daily budget and a JSONL usage
ledger (one JSON object per completed run: {"ts": <iso8601 UTC>,
"model": "<model-id>"}). Budgets are provisioning facts, verified
firsthand on the owner's AI Studio rate-limit page 2026-10-30
(docs/proposals/passes/ai-studio-delphi-panel/evidence.json); a model
with no verified budget DEFERs (unknown is not unlimited).

Smooth-flow rule (owner, 2026-10-29): pace consumption to the
replenishment rate - a run is allowed only while today's count is
below the model's RPD budget; DEFER is fail-soft (exit 3), the
trigger holds in the mesh Queue/D1 leg and drains after the daily
reset (RPD budgets replenish at day boundary UTC).

CLI:
  quota_gate.py check <model-id> <ledger.jsonl> [--now <iso8601>]
    exit 0 ALLOW / exit 3 DEFER, prints one JSON decision line.
  quota_gate.py budgets
    prints the verified budget table as JSON.
"""
import json
import sys
from datetime import datetime, timezone

# model-id -> verified free-tier requests/day (RPD). Source:
# AI Studio rate-limit page, Free tier, project LLM-cnxns,
# inspected 2026-10-30. Paid-labelled and 0/0 models are listed
# with budget 0 on purpose: known-paid is a DEFER, never an ALLOW.
BUDGETS_RPD = {
    "gemini-3.8-flash": 20,
    "gemini-3.8-flash-tts": 10,
    "gemini-3.8-flash-lite-tts": 10,
    "gemini-robotics-er-2-preview": 20,
    # Known Paid / 0-0 on the free tier (2026-10-30 snapshot):
    "gemini-4-argon": 0,
    "gemini-3-flash-preview": 0,
    "antigravity-preview-09-2026": 0,
    "deep-research-preview-04-2026": 0,
    "deep-research-max-preview-04-2026": 0,
    "lyria-3-pro-preview": 0,
    "lyria-3-clip-preview": 0,
}

# Models confirmed present with free-tier limits on the rate-limit
# page but whose exact RPD was not captured in the 2026-10-30
# inspection: DEFER with reason budget_unverified until a fresh
# inspection stamps the number (evidence before allowance).
BUDGET_UNVERIFIED = {
    "gemini-3.1-pro-preview",
    "gemini-3.5-live-translate-preview",
    "gemini-3.1-flash-live-preview",
    "gemini-3.1-flash-tts-preview",
    "gemini-2.5-pro-preview-tts",
    "gemini-2.5-flash-preview-tts",
    "gemini-robotics-er-2-streaming-preview",
}


def _day(ts):
    return ts.astimezone(timezone.utc).strftime("%Y-%m-%d")


def count_today(ledger_rows, model, now):
    today = _day(now)
    n = 0
    for row in ledger_rows:
        if row.get("model") != model:
            continue
        ts = row.get("ts", "")
        try:
            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if _day(when) == today:
            n += 1
    return n


def decide(model, ledger_rows, now=None):
    """Return a decision dict: {decision, model, used_today,
    budget_rpd, reason}. decision is ALLOW or DEFER."""
    now = now or datetime.now(timezone.utc)
    if model in BUDGET_UNVERIFIED:
        return {"decision": "DEFER", "model": model,
                "used_today": count_today(ledger_rows, model, now),
                "budget_rpd": None, "reason": "budget_unverified"}
    if model not in BUDGETS_RPD:
        return {"decision": "DEFER", "model": model,
                "used_today": count_today(ledger_rows, model, now),
                "budget_rpd": None, "reason": "model_unknown"}
    budget = BUDGETS_RPD[model]
    used = count_today(ledger_rows, model, now)
    if budget <= 0:
        return {"decision": "DEFER", "model": model,
                "used_today": used, "budget_rpd": budget,
                "reason": "paid_or_zero_budget"}
    if used >= budget:
        return {"decision": "DEFER", "model": model,
                "used_today": used, "budget_rpd": budget,
                "reason": "rpd_exhausted"}
    return {"decision": "ALLOW", "model": model,
            "used_today": used, "budget_rpd": budget,
            "reason": "within_budget"}


def load_ledger(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        rows = []
    return rows


def main(argv):
    if len(argv) >= 2 and argv[1] == "budgets":
        print(json.dumps({"budgets_rpd": BUDGETS_RPD,
                          "budget_unverified": sorted(BUDGET_UNVERIFIED)},
                         indent=1, sort_keys=True))
        return 0
    if len(argv) >= 4 and argv[1] == "check":
        model, ledger_path = argv[2], argv[3]
        now = None
        if "--now" in argv:
            now = datetime.fromisoformat(
                argv[argv.index("--now") + 1].replace("Z", "+00:00"))
        decision = decide(model, load_ledger(ledger_path), now)
        print(json.dumps(decision, sort_keys=True))
        return 0 if decision["decision"] == "ALLOW" else 3
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
