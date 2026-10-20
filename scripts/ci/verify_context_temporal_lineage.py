#!/usr/bin/env python3
"""Validate monotonic historical context-relationship temporal lineage."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: lineage record must be an object")
        rows.append(value)
    return rows


def validate(lineage_path: Path, manifest_path: Path) -> dict:
    rows = load_jsonl(lineage_path)
    if not rows:
        raise ValueError("temporal lineage is empty")

    starts = []
    observed = []
    snapshots = set()

    for index, row in enumerate(rows, 1):
        if row.get("schema") != "context-relationship-temporal/v1":
            raise ValueError(f"record {index}: unexpected schema")
        if row.get("event") != "OBSERVED":
            raise ValueError(f"record {index}: unexpected event")
        if row.get("source_ref") != "master":
            raise ValueError(f"record {index}: source_ref must remain master")

        window = row.get("history_window") or {}
        start = window.get("start_page")
        next_page = window.get("next_start_page")
        if not isinstance(start, int) or start < 1:
            raise ValueError(f"record {index}: invalid start_page")
        if next_page is not None and (not isinstance(next_page, int) or next_page <= start):
            raise ValueError(f"record {index}: next_start_page must advance beyond start_page")

        snapshot = row.get("snapshot_id")
        if not isinstance(snapshot, str) or not snapshot or snapshot in snapshots:
            raise ValueError(f"record {index}: missing or duplicate snapshot_id")
        snapshots.add(snapshot)

        source_sha = row.get("source_sha")
        if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
            raise ValueError(f"record {index}: source_sha must be a 40-character SHA")

        timestamp = row.get("observed_at")
        if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
            raise ValueError(f"record {index}: observed_at must be UTC ISO text")

        starts.append((start, next_page))
        observed.append(timestamp)

    for previous, current in zip(starts, starts[1:]):
        previous_next = previous[1]
        current_start = current[0]
        if previous_next is None:
            raise ValueError("lineage continues after a complete event")
        if current_start != previous_next:
            raise ValueError(
                f"history window discontinuity: previous next_start_page={previous_next}, "
                f"current start_page={current_start}"
            )

    if observed != sorted(observed):
        raise ValueError("lineage observed_at timestamps are not monotonic")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_window = manifest.get("history_window") or {}
    last_start, last_next = starts[-1]
    if manifest_window.get("start_page") != last_start:
        raise ValueError("manifest start_page disagrees with latest lineage event")
    if manifest_window.get("next_start_page") != last_next:
        raise ValueError("manifest next_start_page disagrees with latest lineage event")
    if manifest.get("latest_observed_at") != observed[-1]:
        raise ValueError("manifest latest_observed_at disagrees with latest lineage event")

    return {
        "status": "VALIDATED",
        "records": len(rows),
        "first_start_page": starts[0][0],
        "last_start_page": last_start,
        "next_start_page": last_next,
        "latest_observed_at": observed[-1],
        "snapshot_count": len(snapshots),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lineage", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.lineage, args.manifest)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
