"""Admitted -> dispatch executor (#5176).

Converts filings in state {swarm-admitted AND dispatch-queued AND
unclaimed} into {producer claim + build-dispatch fire}.

The executor consumes admitted state ONLY. It never re-evaluates
`deferred-by-tier` filings (admission drain = #4977 Fix 3b) and never
implements the drain. Where the legs meet (a filing admitted, then
deferred), admission's state machine governs; the executor acts only
on the admitted snapshot at its run.

Gates, all fail-closed (a HOLD names its cause; nothing fires on an
unknown):
  1. eligibility — labels {swarm-admitted, dispatch-queued} present,
     `dispatch-claimed` absent. `dispatch-escalated` does NOT exclude:
     escalation means "unclaimed too long" and the executor IS the
     remedy. The claim (comment + label) is the exactly-once mutex.
  2. arm selection — #5151 registry + census feed: eligible arms in
     registry order, free-tier before credit-funded; quota-terminal
     arms skipped for the arm-day; if no generic arm is eligible the
     Gemini arm is the fallback of record and the fire is stamped
     `constrained-arm` (never a preference).
  3. quota gate — per-arm budgets read from the registry's Cadence
     LEDGER (#5152) mirror + the census feed's quota_terminal flags.
     Draws come from the usage record when present; an absent or
     stale usage record means `quota_unknown` -> HOLD (the #5160
     addendum: until #5113 T2 publishes the ledger read contract,
     ledger reads are unavailable; do not invent a metering leg).
  4. pre-flight — standing fleet law (lineage corrected c.6825944343:
     documented quota state from 2026-10-20 + tiers verified
     2026-10-30; #1884 = allocation layer, NOT the origin). Every
     metered dispatch carries a live bucket-total headroom read
     {bucket, source, ts, headroom} in its stamp; lane-local draw
     counts are INVALID as a headroom source. For the Gemini class
     the pre-flight of record is fleet-draw coverage + last
     quota_terminal + reset window, COVERAGE-STAMPED, UPPER-BOUND
     only (QDesk #5152 c.6825931792): unstamped coverage -> HOLD,
     upper-bound headroom < 1 -> HOLD. A discovered 429 is a
     pre-flight defect datum, NOT a probe verdict.
  5. census freshness — a census older than CENSUS_MAX_AGE_HOURS
     makes eligibility unknown -> HOLD `census_stale`.

One conversion per run by default (max_conversions=1): minimal blast
radius, one auditable stamp set per run. The workflow raises
max_conversions only on a QDesk decision.

Every fire carries the full DoE dispatch stamp set (schema
dispatch-executor/stamp-v1). Escalation draws stamp
quota_class=escalation and require an explicit escalation-class
filing (label `escalation-class`); the executor never spends the
escalation slice on its own motion. Primary reads spendable-primary
only.

Usage:
  python3 scripts/ops/dispatch_executor.py decide \
      --filings filings.json --arms ops/dispatch/build-arms.json \
      --census ops/que/feeds/arm-census.json \
      [--usage ops/quota/quota-usage.json] [--now 2026-11-12T15:00:00Z] \
      [--max-conversions 1] [--out decisions.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

SCHEMA = "dispatch-executor/stamp-v1"
CENSUS_MAX_AGE_HOURS = 48
USAGE_MAX_AGE_HOURS = 48
CLAIM_MARKER = "PRODUCER CLAIM"
STAMP_MARKER = "DISPATCH-EXECUTOR STAMP"
HOLD_MARKER = "DISPATCH-EXECUTOR HOLD"

REQUIRED_STAMP_FIELDS = (
    "schema", "instance_key", "arm_instance_key", "model", "model_version",
    "dispatch_id", "timestamp", "entry", "task_ref", "trigger",
    "set_index", "cumulative_n", "selection_reason", "outcome", "usage",
    "route_id", "quota_class", "preflight",
)


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _age_hours(generated_at: str, now: datetime) -> float:
    return (now - _parse_ts(generated_at)).total_seconds() / 3600.0


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def eligible_filings(filings: list[dict]) -> list[dict]:
    """Admitted + queued + unclaimed, oldest first.

    `deferred-by-tier` filings never carry swarm-admitted in the
    admitted snapshot, so they are excluded by the label test itself;
    the executor never re-evaluates them.
    """
    out = []
    for f in filings:
        labels = {str(label) for label in f.get("labels", [])}
        if "swarm-admitted" not in labels:
            continue
        if "dispatch-queued" not in labels:
            continue
        if "dispatch-claimed" in labels:
            continue
        out.append(f)
    return sorted(out, key=lambda f: f["number"])


def census_eligible_arms(registry: dict, census: dict, now: datetime) -> tuple[list[dict], str | None]:
    """Return (eligible arms, hold reason or None).

    Eligible = registry status eligible AND census verdict passed AND
    not quota-terminal for the arm-day. The census feed is the
    eligibility record of #5151; a stale census makes eligibility
    unknown -> HOLD.
    """
    generated_at = census.get("generated_at")
    if not generated_at:
        return [], "census_unstamped"
    if _age_hours(generated_at, now) > CENSUS_MAX_AGE_HOURS:
        return [], "census_stale"
    census_by_id = {a["arm_id"]: a for a in census.get("arms", [])}
    eligible = []
    for arm in registry.get("arms", []):
        if not arm.get("selectable", False):
            continue
        if arm.get("status") != "eligible":
            continue
        row = census_by_id.get(arm["arm_id"])
        # Census verdict vocabulary of record (#5151 run 43045718809):
        # gemini-cli carries "eligible", generic arms carry "passed".
        if row is None or row.get("verdict") not in ("passed", "eligible"):
            continue
        qt = row.get("quota_terminal") or {}
        if qt.get("terminal") and qt.get("date") == now.date().isoformat():
            continue
        eligible.append(arm)
    return eligible, None


def order_arms(arms: list[dict]) -> list[dict]:
    """Registry order, free-tier before credit-funded (per #5151 selection_rule)."""
    def key(arm: dict) -> tuple[int, int]:
        budget = arm.get("budget") or {}
        funded = 1 if budget.get("class") == "credit-funded" else 0
        return (funded, registry_index(arm))
    return sorted(arms, key=key)


_REGISTRY_ORDER: dict[str, int] = {}


def registry_index(arm: dict) -> int:
    return _REGISTRY_ORDER.get(arm["arm_id"], 0)


def draws_today(usage: dict | None, arm_id: str, now: datetime) -> int | None:
    """Draws recorded for this arm-day, or None when unknown.

    The usage record is the Cadence draw surface when present; an
    absent record is UNKNOWN (not zero) -- lane-local counts are an
    invalid headroom source and a missing record must HOLD, never
    be read as "no draws".
    """
    if usage is None:
        return None
    arms = (usage.get("arms") or {}).get(arm_id) or {}
    day = arms.get(now.date().isoformat())
    if day is None:
        return None
    return int(day.get("draws", 0))


def quota_headroom(arm: dict, usage: dict | None, now: datetime,
                   quota_class: str) -> tuple[int | None, str | None]:
    """(headroom, hold reason). Primary reads spendable-primary only."""
    budget = arm.get("budget") or {}
    if quota_class == "escalation":
        total = budget.get("reserved_escalation")
    else:
        total = budget.get("spendable_primary", budget.get("daily_total"))
    if total is None:
        return None, "quota_unbudgeted"
    draws = draws_today(usage, arm["arm_id"], now)
    if draws is None:
        return None, "quota_unknown"
    return int(total) - draws, None


def preflight(arm: dict, usage: dict | None, now: datetime,
              headroom: int) -> tuple[dict | None, str | None]:
    """Live bucket-total headroom read for the stamp, or a HOLD reason.

    Gemini class: the pre-flight of record is fleet-draw coverage +
    last quota_terminal + reset window, coverage-stamped, UPPER-BOUND
    only. Unstamped coverage -> HOLD; upper-bound headroom < 1 -> HOLD.
    Other arms: the quota-gate read IS the live read (registry budget
    mirror + recorded draws); unknown draws already HOLDs upstream.
    """
    provider = (arm.get("endpoint") or {}).get("provider")
    if provider == "google" and arm.get("harness") == "run-gemini-cli":
        coverage = (usage or {}).get("coverage") or {}
        if not coverage.get("complete"):
            return None, "preflight_coverage_unstamped"
        last_terminal = coverage.get("last_quota_terminal")
        if last_terminal and last_terminal[:10] == now.date().isoformat():
            return None, "preflight_quota_terminal_today"
        if headroom < 1:
            return None, "preflight_headroom_zero"
        return {
            "bucket": "gemini-api-free",
            "source": "fleet-draw-coverage",
            "ts": now.isoformat().replace("+00:00", "Z"),
            "headroom": headroom,
            "headroom_kind": "upper_bound_only",
            "coverage_stamp": coverage.get("stamped_at"),
            "reset_window": "midnight PT",
        }, None
    return {
        "bucket": f"{arm['arm_id']}-free-tier",
        "source": "registry-budget-mirror+recorded-draws",
        "ts": now.isoformat().replace("+00:00", "Z"),
        "headroom": headroom,
        "headroom_kind": "recorded_draws",
        "reset_window": "daily",
    }, None


def build_stamp(filing: dict, arm: dict, quota_class: str,
                preflight_read: dict, run_id: str, now: datetime,
                cumulative_n: int, constrained: bool,
                workflow_ref: str, workflow_sha: str,
                script_sha: str) -> dict:
    """The full DoE dispatch stamp set for one fire."""
    stamp = {
        "schema": SCHEMA,
        "instance_key": {
            "system_prompt_ref": workflow_ref,
            "system_prompt_sha256": workflow_sha,
            "tools_ref": "scripts/ops/dispatch_executor.py",
            "tools_sha256": script_sha,
            "role": "dispatch-executor",
            "moniker": "fleet-dispatch-executor",
            "context": "admitted-dispatch-executor #5176",
        },
        "arm_instance_key": {
            "arm_id": arm["arm_id"],
            "model": arm.get("model"),
            "route_id": (arm.get("endpoint") or {}).get("route_id"),
            "harness": arm.get("harness"),
            "harness_ref": arm.get("harness_ref"),
        },
        "model": arm.get("model"),
        "model_version": arm.get("model_version"),
        "dispatch_id": f"executor-{run_id}-{filing['number']}",
        "timestamp": now.isoformat().replace("+00:00", "Z"),
        "entry": "admitted-dispatch-executor",
        "task_ref": f"#{filing['number']}",
        "trigger": "dispatch-executor",
        "set_index": 1,
        "cumulative_n": cumulative_n,
        "selection_reason": (
            "constrained-arm: sole eligible arm (census of record)"
            if constrained else "executor-rotation: registry order, free-tier first"
        ),
        "outcome": "fired",
        "usage": {"quota_class": quota_class},
        "route_id": (arm.get("endpoint") or {}).get("route_id"),
        "quota_class": quota_class,
        "preflight": preflight_read,
    }
    return stamp


def claim_body(filing: dict, arm: dict, stamp: dict) -> str:
    """Claim comment per scripts/dispatch/claim_task.py convention:
    marker + stamp, applied together with the `dispatch-claimed`
    label in one motion."""
    return (
        f"[MUSEai]@{{role:{{dispatch-executor}}}} {CLAIM_MARKER} — dispatch "
        f"executor claim on #{filing['number']}\n\n"
        f"- arm: {arm['arm_id']} ({arm.get('model')}) — {stamp['selection_reason']}\n"
        f"- quota_class: {stamp['quota_class']}\n"
        f"- pre-flight: {stamp['preflight']['bucket']} headroom "
        f"{stamp['preflight']['headroom']} ({stamp['preflight']['headroom_kind']}) "
        f"@ {stamp['preflight']['ts']}\n"
        f"- dispatch_id: {stamp['dispatch_id']}\n\n"
        "State: `dispatch-queued` -> `dispatch-claimed` (label applied "
        "with this claim). Execution underway; the build-dispatch fire "
        "follows this claim.\n\n"
        f"<!-- {STAMP_MARKER}:v1 -->\n"
        "```json\n" + json.dumps(stamp, indent=2, sort_keys=True) + "\n```"
    )


def decide(filings: list[dict], registry: dict, census: dict,
           usage: dict | None, now: datetime, run_id: str,
           max_conversions: int = 1, workflow_ref: str = "",
           workflow_sha: str = "", script_sha: str = "") -> dict:
    """Decide the executor's actions for one run. Pure + deterministic."""
    global _REGISTRY_ORDER
    _REGISTRY_ORDER = {a["arm_id"]: i for i, a in enumerate(registry.get("arms", []))}
    decisions: list[dict] = []
    eligible = eligible_filings(filings)
    arms, census_hold = census_eligible_arms(registry, census, now)
    ordered = order_arms(arms)
    generic = [a for a in ordered if a["arm_id"] != "gemini-cli"]
    gemini = [a for a in ordered if a["arm_id"] == "gemini-cli"]
    converted = 0
    for filing in eligible:
        if converted >= max_conversions:
            decisions.append({
                "issue": filing["number"], "action": "hold",
                "hold_reason": "max_conversions_reached",
            })
            continue
        if census_hold:
            decisions.append({
                "issue": filing["number"], "action": "hold",
                "hold_reason": census_hold,
            })
            continue
        quota_class = (
            "escalation" if "escalation-class" in {str(x) for x in filing.get("labels", [])}
            else "primary"
        )
        arm_holds: list[dict] = []
        for arm in generic + gemini:
            constrained = arm["arm_id"] == "gemini-cli"
            headroom, q_hold = quota_headroom(arm, usage, now, quota_class)
            if q_hold:
                arm_holds.append({"arm": arm["arm_id"], "hold_reason": q_hold})
                continue
            if headroom is not None and headroom < 1:
                # Quota-terminal for the arm-day: rotate, never backoff-burn.
                arm_holds.append({"arm": arm["arm_id"], "hold_reason": "quota_terminal"})
                continue
            pf, pf_hold = preflight(arm, usage, now, headroom)
            if pf_hold:
                arm_holds.append({"arm": arm["arm_id"], "hold_reason": pf_hold})
                continue
            stamp = build_stamp(
                filing, arm, quota_class, pf, run_id, now,
                cumulative_n=converted + 1, constrained=constrained,
                workflow_ref=workflow_ref, workflow_sha=workflow_sha,
                script_sha=script_sha,
            )
            decisions.append({
                "issue": filing["number"], "action": "fire",
                "arm": arm["arm_id"], "quota_class": quota_class,
                "constrained_arm": constrained,
                "stamp": stamp, "claim_body": claim_body(filing, arm, stamp),
            })
            converted += 1
            break
        else:
            # No arm fired: exactly one HOLD per filing, naming every
            # arm's cause (rotation attempted, none cleared its gate).
            decisions.append({
                "issue": filing["number"], "action": "hold",
                "hold_reason": "no_arm_cleared_gate",
                "arm_holds": arm_holds or [{"arm": None, "hold_reason": "no_eligible_arm"}],
            })
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "eligible_count": len(eligible),
        "decisions": decisions,
    }


def _load(path: str | None) -> dict | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    decide_p = sub.add_parser("decide", help="decide one executor run")
    decide_p.add_argument("--filings", required=True)
    decide_p.add_argument("--arms", required=True)
    decide_p.add_argument("--census", required=True)
    decide_p.add_argument("--usage")
    decide_p.add_argument("--now")
    decide_p.add_argument("--run-id", default="local")
    decide_p.add_argument("--max-conversions", type=int, default=1)
    decide_p.add_argument("--workflow-ref", default=".github/workflows/dispatch-executor.yml")
    decide_p.add_argument("--workflow-sha", default="")
    decide_p.add_argument("--script-sha", default="")
    decide_p.add_argument("--out")
    args = parser.parse_args(argv)

    now = _parse_ts(args.now) if args.now else datetime.now(timezone.utc)
    filings = _load(args.filings)
    registry = _load(args.arms)
    census = _load(args.census)
    usage = _load(args.usage)
    result = decide(
        filings, registry, census, usage, now, args.run_id,
        max_conversions=args.max_conversions,
        workflow_ref=args.workflow_ref,
        workflow_sha=args.workflow_sha, script_sha=args.script_sha,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
