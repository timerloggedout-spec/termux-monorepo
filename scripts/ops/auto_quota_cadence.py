#!/usr/bin/env python3
"""autoQuotaCadence: deterministic DoE endpoint-pool generation + cadence derivation.

QUE #5160. Pure derivation over files already in the checkout -- no model
inference, no live provider calls, no metering, no new cron/ledger/registry/
poller/router (clause 4 + Cadence review c.6802642639).

Inputs
------
- ``ops/dispatch/build-arms.json`` (``build-arms/v1``): the arm registry.
- ``ops/que/feeds/arm-census.json`` (``arm-census/v1``): eligibility census.
- ``ops/quota/registry.json`` (``quota.registry.v2``): entitlement/observation
  evidence per service record.
- ``--snapshot`` (optional, ``ledger-snapshot/v1``): a *published* ledger
  snapshot carrying per-arm draws + coverage + budgets incl. explicit
  ``{reset_window, reset_tz}``. See ``docs/ops/LEDGER-SNAPSHOT-CONTRACT.md``.

Gap 1 (Cadence review c.6802642639, QDesk addendum c.6802661589): the #5152
ledger read contract {store, fields, freshness} is UNPUBLISHED until #5113
T2 publishes it. Until then the snapshot input is ABSENT by definition and
this derivation treats ledger reads as UNAVAILABLE: every arm defers on
``quota_unknown`` and the pool is empty with named reasons. The derivation
never invents a metering leg in Actions -- unknown/stale quota means defer
(clause 4), never a zero or a guess.

Gap 2 (same review): budget records carry reset only as prose today. This
derivation reads ``{reset_window, reset_tz}`` ONLY from a published snapshot's
budgets; the registry's prose ``reset`` field is cited as an evidence
reference and is NEVER parsed into a window (QUOTA-RESET-CONTRACT boundary:
observe, never infer a reset from the calendar). Absent a snapshot the reset
is stamped UNKNOWN.

Outputs
-------
- ``--out``: ``pool-cadence/v1`` feed (``ops/que/feeds/pool-cadence.json``):
  per-arm eligibility + cadence decisions + rotation order + source SHAs.
- ``--usage-out``: the executor's ``--usage`` record shape
  (``{arms: {arm_id: {date: {draws}}}, coverage: {...}, budgets: {...}}``),
  populated ONLY from a published snapshot; empty + coverage-incomplete
  when the snapshot is absent/stale. The dispatch executor
  (``scripts/ops/dispatch_executor.py``) consumes it verbatim.

Per-arm gate (clause 3) -- an arm is dispatchable only when ALL hold:
exact invoke route; current census pass from the relevant environment;
entitlement record in the quota registry; usable quota headroom with source
+ observation time + reset window/tz; no duplicate route_id. Anything else
defers with a named reason; a listing, a ``/v1/models`` hit, a sandbox-only
success, or a bare 429 never proves entitlement/headroom.

Gemini participates on the SAME gate as every other arm (clause 5): no
fallback-of-record, no precedence, no hard dependency. The pool generation
itself succeeds with zero eligible arms and with Gemini unavailable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

SCHEMA = "pool-cadence/v1"
SNAPSHOT_SCHEMA = "ledger-snapshot/v1"
CENSUS_MAX_AGE_HOURS = 48
SNAPSHOT_MAX_AGE_SECONDS = 3600
ELIGIBLE_VERDICTS = ("passed", "eligible")


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _registry_record_id(arm: dict) -> str | None:
    """Registry record id named by the arm's quota_metric_source, or None.

    The source string names e.g. ``ops/quota/registry.json record
    gemini.api_free``; the token after ``record `` is the id. A source that
    names no record yields None (entitlement unprovable -> defer).
    """
    source = ((arm.get("budget") or {}).get("quota_metric_source") or "")
    marker = "record "
    # rfind, not find: the Gemini source mentions "budget record of record"
    # before naming its registry record; the LAST "record " names the id.
    idx = source.rfind(marker)
    if idx < 0:
        return None
    token = source[idx + len(marker):].strip().split()[0].strip(",;")
    return token or None


def _snapshot_fresh(snapshot: dict, now: datetime) -> tuple[bool, str]:
    generated = snapshot.get("generated_at")
    if not generated:
        return False, "snapshot_unstamped"
    try:
        age = (now - _parse_ts(generated)).total_seconds()
    except ValueError:
        return False, "snapshot_unstamped"
    if age < 0:
        return False, "snapshot_from_future"
    if age > SNAPSHOT_MAX_AGE_SECONDS:
        return False, "snapshot_stale"
    return True, ""


def _budget_total(budget: dict, quota_class: str = "primary") -> int | None:
    if quota_class == "escalation":
        total = budget.get("reserved_escalation")
    else:
        total = budget.get("spendable_primary", budget.get("daily_total"))
    return None if total is None else int(total)


def derive(
    arms_doc: dict,
    census_doc: dict,
    registry_doc: dict,
    snapshot: dict | None,
    previous: dict | None,
    now: datetime,
) -> dict:
    """Derive the pool + cadence decisions. Pure; no I/O, no inference."""
    arms = arms_doc.get("arms", [])
    census_rows = {r.get("arm_id"): r for r in census_doc.get("arms", [])}
    services = {s.get("id"): s for s in registry_doc.get("services", [])}

    census_generated = census_doc.get("generated_at")
    try:
        census_age_h = (
            (now - _parse_ts(census_generated)).total_seconds() / 3600
            if census_generated
            else None
        )
    except ValueError:
        census_age_h = None
    census_fresh = census_age_h is not None and 0 <= census_age_h <= CENSUS_MAX_AGE_HOURS
    # Availability environment: a census with a run_id is Actions evidence;
    # without one its provenance is unknown (sandbox-only is NOT admission).
    availability_env = "actions" if census_doc.get("run_id") else "unknown"

    if snapshot is None:
        ledger_read = {
            "status": "unavailable",
            "contract": SNAPSHOT_SCHEMA,
            "reason": "ledger_snapshot_absent",
            "note": "Read contract unpublished until #5113 T2 publishes "
            "{store, fields, freshness} (Cadence c.6802642639 gap 1); "
            "ledger reads treated as UNAVAILABLE, arms defer on "
            "quota_unknown. No metering invented in Actions.",
        }
        snapshot_fresh = False
    else:
        snapshot_fresh, reason = _snapshot_fresh(snapshot, now)
        ledger_read = {
            "status": "available" if snapshot_fresh else "unavailable",
            "contract": SNAPSHOT_SCHEMA,
            "reason": None if snapshot_fresh else reason,
            "snapshot_generated_at": snapshot.get("generated_at"),
        }
    snap_arms = (snapshot or {}).get("arms", {}) if snapshot_fresh else {}
    snap_coverage = (snapshot or {}).get("coverage", {}) if snapshot_fresh else {}
    snap_budgets = (snapshot or {}).get("budgets", {}) if snapshot_fresh else {}

    seen_routes: set[str] = set()
    arm_rows: list[dict] = []
    for arm in arms:
        arm_id = arm["arm_id"]
        reasons: list[str] = []
        endpoint = arm.get("endpoint") or {}
        budget = arm.get("budget") or {}

        # 1. exact invoke route (url or a named harness with a ref).
        route_id = endpoint.get("route_id")
        has_route = bool(endpoint.get("url")) or bool(
            arm.get("harness") and arm.get("harness_ref")
        )
        if not has_route:
            reasons.append("route_dead")
        if route_id:
            if route_id in seen_routes:
                reasons.append("duplicate_route")
            else:
                seen_routes.add(route_id)

        # 2. census: current pass from the relevant environment.
        row = census_rows.get(arm_id)
        if row is None:
            reasons.append("census_missing")
        elif row.get("verdict") not in ELIGIBLE_VERDICTS:
            reasons.append("census_not_passed")
        elif not census_fresh:
            reasons.append("census_stale")
        elif (row.get("quota_terminal") or {}).get("terminal") and (
            row.get("quota_terminal") or {}
        ).get("date") == now.date().isoformat():
            reasons.append("quota_terminal_today")
        if availability_env == "unknown":
            reasons.append("availability_env_unknown")

        # 3. entitlement: a named registry record must exist.
        record_id = _registry_record_id(arm)
        record = services.get(record_id) if record_id else None
        if record is None:
            reasons.append("entitlement_unknown")

        # 4. quota headroom: snapshot-only, never invented.
        headroom: int | None = None
        reset_window: str | None = None
        reset_tz: str | None = None
        snap_budget = snap_budgets.get(arm_id) or {}
        if snap_budget:
            reset_window = snap_budget.get("reset_window")
            reset_tz = snap_budget.get("reset_tz")
        total = _budget_total(budget)
        if total is None:
            reasons.append("quota_unbudgeted")
        elif not snapshot_fresh:
            reasons.append("quota_unknown")
        else:
            day = (snap_arms.get(arm_id) or {}).get(now.date().isoformat())
            if day is None:
                reasons.append("quota_unknown")
            else:
                headroom = total - int(day.get("draws", 0))
                if headroom < 1:
                    reasons.append("quota_exhausted")
        if reset_window is None:
            reasons.append("reset_window_unknown")
        if reset_tz is None:
            reasons.append("reset_tz_unknown")

        status = "eligible" if not reasons else "deferred"
        arm_rows.append(
            {
                "arm_id": arm_id,
                "status": status,
                "defer_reasons": reasons,
                "headroom": headroom,
                "reset_window": reset_window or "unknown",
                "reset_tz": reset_tz or "unknown",
                "availability_env": availability_env,
                "route_id": route_id,
                "registry_record": record_id,
                "census_verdict": (row or {}).get("verdict"),
            }
        )

    eligible = [r for r in arm_rows if r["status"] == "eligible"]

    # Rotation: registry order, free-tier before credit-funded; avoid a
    # consecutive same-arm selection when the previous feed names one.
    def _order_key(row: dict) -> tuple[int, int]:
        arm = next(a for a in arms if a["arm_id"] == row["arm_id"])
        funded = 1 if ((arm.get("budget") or {}).get("class") == "credit-funded") else 0
        return (funded, arms.index(arm))

    order = [r["arm_id"] for r in sorted(eligible, key=_order_key)]
    last_selected = (previous or {}).get("rotation", {}).get("last_selected_arm")
    if last_selected in order and len(order) > 1:
        order.remove(last_selected)
        order.append(last_selected)

    usage_arms: dict = {}
    for arm_id, days in snap_arms.items():
        usage_arms[arm_id] = days
    usage_record = {
        "arms": usage_arms,
        "coverage": {
            "complete": bool(snap_coverage.get("complete")),
            "stamped_at": snap_coverage.get("stamped_at"),
            "last_quota_terminal": snap_coverage.get("last_quota_terminal"),
        },
        "budgets": snap_budgets,
    }

    return {
        "schema": SCHEMA,
        "generated_at": _fmt(now),
        "ledger_read": ledger_read,
        "census": {
            "generated_at": census_generated,
            "fresh": census_fresh,
            "max_age_hours": CENSUS_MAX_AGE_HOURS,
            "availability_env": availability_env,
        },
        "arms": arm_rows,
        "pool": {
            "eligible": order,
            "deferred": [r["arm_id"] for r in arm_rows if r["status"] == "deferred"],
            "eligible_count": len(order),
        },
        "rotation": {
            "order": order,
            "last_selected_arm": last_selected,
        },
        "usage_record": usage_record,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="autoQuotaCadence derivation")
    parser.add_argument("--arms", required=True)
    parser.add_argument("--census", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--snapshot", default=None)
    parser.add_argument("--previous", default=None)
    parser.add_argument("--now", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--usage-out", required=True)
    args = parser.parse_args(argv)

    with open(args.arms) as fh:
        arms_doc = json.load(fh)
    with open(args.census) as fh:
        census_doc = json.load(fh)
    with open(args.registry) as fh:
        registry_doc = json.load(fh)
    snapshot = None
    snapshot_sha = None
    if args.snapshot:
        with open(args.snapshot) as fh:
            snapshot = json.load(fh)
        if snapshot.get("schema") != SNAPSHOT_SCHEMA:
            print(
                f"snapshot schema must be {SNAPSHOT_SCHEMA}, "
                f"got {snapshot.get('schema')!r}",
                file=sys.stderr,
            )
            return 2
        snapshot_sha = _sha256_file(args.snapshot)
    previous = None
    if args.previous:
        with open(args.previous) as fh:
            previous = json.load(fh)

    now = _parse_ts(args.now)
    feed = derive(arms_doc, census_doc, registry_doc, snapshot, previous, now)
    feed["sources"] = {
        "arms": args.arms,
        "arms_sha256": _sha256_file(args.arms),
        "census": args.census,
        "census_sha256": _sha256_file(args.census),
        "registry": args.registry,
        "registry_sha256": _sha256_file(args.registry),
        "snapshot": args.snapshot,
        "snapshot_sha256": snapshot_sha,
    }
    with open(args.out, "w") as fh:
        json.dump(feed, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(args.usage_out, "w") as fh:
        json.dump(feed["usage_record"], fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(
        f"pool-cadence: {feed['pool']['eligible_count']} eligible / "
        f"{len(feed['pool']['deferred'])} deferred; "
        f"ledger_read={feed['ledger_read']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
