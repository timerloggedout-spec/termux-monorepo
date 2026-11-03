#!/usr/bin/env python3
"""Pure, evidence-preserving reconciliation of provider snapshots and events.

Input is normalized JSON with snapshots, events, and coverage rows. This module
does not poll providers or mutate a ledger. Only exact, established events in a
complete, same-scope interval enter the comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "provider-consumption-reconciliation/v1"
KEY_FIELDS = ("provider", "scope", "resource", "unit", "reset_epoch")


def timestamp(value, label):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}: timestamp must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label}: invalid timestamp {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label}: timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: expected a numeric value")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label}: expected a finite non-negative value")
    return value


def identity(row, label):
    for field in KEY_FIELDS:
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}: {field} must be a non-empty string")


def fingerprint(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def source_refs(*rows):
    refs = []
    for row in rows:
        if not row:
            continue
        ref = row.get("source_ref") or row.get("event_id") or row.get("snapshot_id")
        if ref and ref not in refs:
            refs.append(ref)
    return refs


def finding(kind, key, interval, reason, rows=(), **values):
    sources = source_refs(*rows)
    identity_value = {"schema": SCHEMA, "kind": kind, "key": key,
                      "interval": interval, "sources": sources}
    return {
        "finding_id": "PCR-" + fingerprint(identity_value)[:20],
        "kind": kind, "key": key, "interval": interval,
        "reason": reason, "source_refs": sources, **values,
    }


def reconcile(document, *, now=None, stale_after_seconds=None):
    """Return deterministic findings from normalized snapshots/events/coverage."""
    if not isinstance(document, dict):
        raise ValueError("input must be a JSON object")
    snapshots = document.get("snapshots", [])
    events = document.get("events", [])
    coverage = document.get("coverage", [])
    if not all(isinstance(x, list) for x in (snapshots, events, coverage)):
        raise ValueError("snapshots, events, and coverage must be arrays")
    if stale_after_seconds is not None and (
            isinstance(stale_after_seconds, bool) or
            not isinstance(stale_after_seconds, (int, float)) or
            stale_after_seconds < 0):
        raise ValueError("stale_after_seconds must be a non-negative number")

    now_dt = timestamp(now, "now") if now else datetime.now(timezone.utc)
    parsed_snapshots = []
    for index, row in enumerate(snapshots):
        label = f"snapshots[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{label}: expected an object")
        identity(row, label)
        row = dict(row)
        row["_at"] = timestamp(row.get("observed_at"), label + ".observed_at")
        row["_used"] = number(row.get("used"), label + ".used")
        parsed_snapshots.append(row)

    parsed_events, event_ids = [], {}
    for index, row in enumerate(events):
        label = f"events[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{label}: expected an object")
        identity(row, label)
        row = dict(row)
        event_id = row.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError(f"{label}: event_id must be a non-empty stable source identity")
        row["_at"] = timestamp(row.get("occurred_at"), label + ".occurred_at")
        if row.get("match") == "exact" and row.get("status") == "established":
            row["_value"] = number(row.get("usage_value"), label + ".usage_value")
        replay_fingerprint = fingerprint(
            {k: v for k, v in row.items() if not k.startswith("_")})
        if event_id in event_ids:
            if event_ids[event_id] != replay_fingerprint:
                raise ValueError(f"{label}: conflicting replay for event_id {event_id!r}")
            continue
        event_ids[event_id] = replay_fingerprint
        parsed_events.append(row)

    parsed_coverage = []
    for index, row in enumerate(coverage):
        label = f"coverage[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{label}: expected an object")
        identity(row, label)
        row = dict(row)
        row["_start"] = timestamp(row.get("window_start"), label + ".window_start")
        row["_end"] = timestamp(row.get("window_end"), label + ".window_end")
        if row["_end"] <= row["_start"]:
            raise ValueError(f"{label}: window_end must be after window_start")
        if row.get("coverage_status") not in ("complete", "partial", "unknown"):
            raise ValueError(f"{label}: invalid coverage_status")
        parsed_coverage.append(row)

    # Preserve separate provider/account/resource/unit series.
    groups = {}
    for row in parsed_snapshots:
        group_key = (row["provider"], row["scope"], row["resource"], row["unit"])
        groups.setdefault(group_key, []).append(row)

    findings = []
    for _, rows in sorted(groups.items()):
        rows.sort(key=lambda item: item["_at"])
        if len(rows) == 1:
            row = rows[0]
            key = {field: row[field] for field in KEY_FIELDS}
            interval = {"start": None, "end": row["observed_at"]}
            findings.append(finding(
                "missing_baseline", key, interval,
                "Only one provider snapshot exists; no delta can be computed.", (row,)))
            continue

        for previous, current in zip(rows, rows[1:]):
            key = {field: current[field] for field in KEY_FIELDS}
            interval = {"start": previous["observed_at"],
                        "end": current["observed_at"]}
            pair = (previous, current)
            start, end = previous["_at"], current["_at"]

            if current["reset_epoch"] != previous["reset_epoch"]:
                findings.append(finding(
                    "reset_boundary", key, interval,
                    "Provider reset epoch changed; do not subtract across the boundary.", pair))
                continue
            if end <= start:
                findings.append(finding(
                    "scope_mismatch", key, interval,
                    "Snapshot timestamps are not strictly increasing.", pair))
                continue
            if stale_after_seconds is not None:
                age = (now_dt - current["_at"]).total_seconds()
                if age > stale_after_seconds:
                    findings.append(finding(
                        "stale_reading", key, interval,
                        "Latest snapshot exceeds the configured freshness budget.",
                        pair, age_seconds=age))
                    continue
            if current["_used"] < previous["_used"]:
                findings.append(finding(
                    "counter_regression", key, interval,
                    "Counter decreased without a reset-epoch change.", pair))
                continue

            delta = current["_used"] - previous["_used"]
            candidates = [c for c in parsed_coverage
                          if c["provider"] == current["provider"]
                          and c["resource"] == current["resource"]
                          and c["_start"] == start and c["_end"] == end]
            exact_coverage = [c for c in candidates
                              if all(c[field] == current[field] for field in KEY_FIELDS)]
            if not exact_coverage:
                kind = "scope_mismatch" if candidates else "missing_events"
                reason = ("Coverage exists for the interval but scope, unit, or reset epoch differs."
                          if candidates else "No event-coverage assertion matches this exact snapshot interval.")
                findings.append(finding(kind, key, interval, reason, pair + tuple(candidates)))
                continue
            coverage_row = exact_coverage[-1]
            if coverage_row["coverage_status"] != "complete":
                findings.append(finding(
                    "incomplete_event_coverage", key, interval,
                    "Event coverage is partial or unknown; residual is not attributable.",
                    pair + (coverage_row,), coverage_status=coverage_row["coverage_status"],
                    observed_delta=delta))
                continue

            interval_events = [e for e in parsed_events
                               if e["provider"] == current["provider"]
                               and e["scope"] == current["scope"]
                               and e["resource"] == current["resource"]
                               and e["unit"] == current["unit"]
                               and start < e["_at"] <= end]
            mismatched = [e for e in interval_events
                          if e["reset_epoch"] != current["reset_epoch"]]
            if mismatched:
                findings.append(finding(
                    "scope_mismatch", key, interval,
                    "Events in the interval carry a different account scope, unit, or reset epoch.",
                    pair + (coverage_row,) + tuple(mismatched)))
                continue

            established = [e for e in interval_events
                           if e.get("match") == "exact" and e.get("status") == "established"]
            activity = [e for e in interval_events
                        if e.get("match") == "activity-proxy" or e.get("status") == "activity-only"]
            attributed = sum(e["_value"] for e in established)
            residual = delta - attributed
            lineage = pair + (coverage_row,) + tuple(established) + tuple(activity)
            values = {"observed_delta": delta, "attributed_total": attributed,
                      "residual": residual, "activity_events_excluded": len(activity),
                      "coverage_status": "complete"}
            if math.isclose(residual, 0.0, rel_tol=0.0, abs_tol=1e-9):
                kind, reason = "reconciled", "Provider snapshot delta equals established event usage."
            elif residual > 0:
                kind, reason = "positive_residual", "Provider consumption exceeds attributed events; residual remains unallocated."
            else:
                kind, reason = "negative_residual", "Attributed events exceed provider consumption; investigate duplicate or mismatched evidence."
            findings.append(finding(kind, key, interval, reason, lineage, **values))

    return {
        "schema": SCHEMA, "findings": findings,
        "summary": {
            "findings": len(findings),
            "reconciled": sum(row["kind"] == "reconciled" for row in findings),
            "gaps": sum(row["kind"] != "reconciled" for row in findings),
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="normalized JSON document")
    parser.add_argument("--output", help="write JSON findings to this path")
    parser.add_argument("--now", help="timezone-aware ISO-8601 timestamp for deterministic freshness checks")
    parser.add_argument("--stale-after-seconds", type=float)
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = reconcile(document, now=args.now,
                           stale_after_seconds=args.stale_after_seconds)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
