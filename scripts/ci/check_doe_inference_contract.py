#!/usr/bin/env python3
"""Fail on drift in the DoE-governed inference allocation contract."""
from __future__ import annotations
import json
import sys
from pathlib import Path

def validate_fee_distribution(distribution: dict) -> bool:
    keys = {"doe_pct", "mvt_pct", "ates_pct", "moneyball_pct", "3l0_pct"}
    if not isinstance(distribution, dict) or not keys.issubset(distribution):
        return False
    values = [distribution.get(key) for key in keys]
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in values):
        return False
    return abs(sum(values) - 100.0) < 1e-6 and distribution.get("total_pct") == 100

def validate_contract(feed: dict, design: dict, schema: dict,
                      roster: str, missions: str, gambling: str) -> list[str]:
    errors = []
    rotation = feed.get("dispatch", {}).get("provider_catalog", {}).get("rotation_rule", {})
    rule = str(rotation.get("rule", ""))
    selection = str(rotation.get("selection", ""))
    if "DoE owns allocation" not in rule:
        errors.append("desk feed must declare DoE as allocation/rotation authority")
    if "Scout selects" not in rule and "Scout selects" not in selection:
        errors.append("desk feed must bind Scout to scoped endpoint selection")
    if "no global no-repeat" not in rule.lower():
        errors.append("desk feed must explicitly reject a global no-repeat rule")
    if "no provider takes 2 consecutive" in rule.lower() or "no provider takes 2 consecutive" in selection.lower():
        errors.append("superseded consecutive-provider rule must not be active policy")
    amendment = design.get("owner_amendment", {})
    if "DoE owns inference endpoint allocation" not in amendment.get("authority", ""):
        errors.append("util-1 design must identify DoE authority")
    assignment = design.get("design", {}).get("assignment", "")
    if "DoE owns allocation and rotation" not in assignment or "Scout selects" not in assignment:
        errors.append("util-1 assignment must describe DoE allocation followed by Scout selection")
    window = design.get("design", {}).get("window_rule", "").lower()
    if "descriptive only" not in window:
        errors.append("n>=4 must remain descriptive, not a significance gate")
    if "each inference endpoint" not in amendment.get("endpoint_unit", ""):
        errors.append("endpoint-level independent evaluation must be declared")
    if schema.get("properties", {}).get("authority", {}).get("const") != "doe":
        errors.append("selection receipt schema must make DoE the authority")
    if schema.get("properties", {}).get("selector", {}).get("properties", {}).get("kind", {}).get("const") != "scout":
        errors.append("selection receipt schema must identify Scout as selector")
    fee = schema.get("properties", {}).get("custom_contract", {}).get("properties", {}).get("fee", {})
    if "distribution" not in fee.get("required", []):
        errors.append("custom contract fee must include lane distribution")
    distribution = fee.get("properties", {}).get("distribution", {}).get("properties", {})
    if not all(key in distribution for key in ("doe_pct", "mvt_pct", "ates_pct", "moneyball_pct", "3l0_pct")):
        errors.append("fee distribution must cover DoE, MVT, ATES, MoneyBall and 3L0")
    if "DoE-governed inference selection" not in roster:
        errors.append("Scout roster documentation missing DoE selection contract")
    if "DoE-authorized Scout" not in missions:
        errors.append("Scout missions missing bounded DoE-authorized selection role")
    if "private while the participant remains active" not in gambling:
        errors.append("participant strategy privacy rule missing")
    return errors

def main() -> int:
    root = Path(__file__).resolve().parents[2]
    read = lambda p: (root / p).read_text(encoding="utf-8")
    try:
        feed = json.loads(read("ops/challenge/desk-feed.json"))
        design = json.loads(read("experiments/doe/util-1-provider-rotation/DESIGN.json"))
        schema = json.loads(read("docs/schemas/inference-selection-receipt.schema.json"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CONTRACT_INVALID: {exc}", file=sys.stderr)
        return 2
    errors = validate_contract(
        feed, design, schema,
        read("docs/ops/SCOUT-ROSTER.md"),
        read("docs/ops/SCOUT-MISSIONS.md"),
        read("docs/ops/AGENTIC-GAMBLING-LANE.md"),
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: DoE allocation authority, Scout selection, endpoint gates, receipt and privacy contract agree")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
