#!/usr/bin/env python3
"""Build/extend the telemetry feed-history series.

One row per committed snapshot of the telemetry-viz feed
(apps/tribute-dashboard/data/telemetry-feed.json, schema
telemetry-viz-feed/v1): the feed's generated_at plus its golden
counters, verbatim. The series exists so the telemetry page can
render a feed-history trend (chart standard) — pages consume
committed files only, so the history must be a committed file.

Backfill provenance: the first two rows were derived 2026-11-02
from the feed file's own git history (Slice 1 commit 3c66e869fc,
generated 2026-10-30T06:22:26Z; Slice 2 commit 667e16d4ab,
generated 2026-10-30T07:47:32Z, the current feed). Both snapshots
carry identical golden counters — the trend is flat across the
feed's whole committed history, and the feed has not refreshed
since 2026-10-30. Appending is one run of this script per feed
refresh; wire it next to the surface-feeds collector when that
cadence is set.

Usage: telemetry_feed_series.py [feed.json] [series.jsonl]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEED = ROOT / "apps" / "tribute-dashboard" / "data" / "telemetry-feed.json"
SERIES = ROOT / "apps" / "tribute-dashboard" / "data" / "telemetry-feed-series.jsonl"
FIELDS = ("receipts_total", "actioned", "skipped",
          "quota_readings_total", "workflow_runs_observed",
          "actions_failure_rate")


def row_of(feed):
    golden = (feed.get("data") or {}).get("golden") or {}
    row = {"generated_at": feed.get("generated_at"), "state": feed.get("state", "unknown"), "freshness": feed.get("freshness", "unknown"), "sources": feed.get("sources", [])}
    for f in FIELDS:
        row[f] = golden.get(f)
    return row


def build(feed_path=FEED, series_path=SERIES):
    feed = json.loads(Path(feed_path).read_text())
    rows = []
    if Path(series_path).exists():
        rows = [json.loads(l) for l in
                Path(series_path).read_text().splitlines() if l.strip()]
    new = row_of(feed)
    if new["generated_at"] and all(
            r["generated_at"] != new["generated_at"] for r in rows):
        rows.append(new)
        rows.sort(key=lambda r: r["generated_at"])
    return rows


def main():
    feed_path = sys.argv[1] if len(sys.argv) > 1 else FEED
    series_path = sys.argv[2] if len(sys.argv) > 2 else SERIES
    rows = build(feed_path, series_path)
    Path(series_path).write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n"
                for r in rows))
    print(f"{series_path}: {len(rows)} snapshot(s)")


if __name__ == "__main__":
    main()
