#!/usr/bin/env python3
"""Build the public Hackathon Desk challenge projection.

Source of truth: ops/challenge/coordinator.json
Public contract: challenge-public-feed/v1
The output is a strict allowlist. Internal estimates, opportunity-cost data,
project records, credentials, and arbitrary extension fields never cross the
browser boundary.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA = "challenge-public-feed/v1"
SOURCE = "ops/challenge/coordinator.json"
FORBIDDEN_KEYS = {"metrics_internal", "win_probability"}
DATE_FIELDS = (
    "announced", "reg_open", "reg_close", "build_start", "build_end",
    "submissions_open", "deadline", "judging_end", "winners_at",
)


def _scalar(value):
    return value if value is None or isinstance(value, (str, int, float, bool)) else None


def _https(value):
    if not isinstance(value, str):
        return None
    parsed = urlparse(value)
    return value if parsed.scheme == "https" and parsed.netloc else None


def _pick_scalars(record, fields):
    if not isinstance(record, dict):
        return {}
    return {key: _scalar(record[key]) for key in fields
            if key in record and _scalar(record[key]) is not None}


def _date(value):
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return None
    return _pick_scalars(value, ("at", "tz", "source"))


def _dates(value):
    if not isinstance(value, dict):
        return {}
    return {key: _date(value[key]) for key in DATE_FIELDS if key in value}


def _organizers(value):
    if not isinstance(value, list):
        return []
    rows = []
    for item in value:
        if not isinstance(item, dict):
            continue
        row = _pick_scalars(item, ("name", "role", "fetched_at"))
        url = _https(item.get("source_url"))
        if url:
            row["source_url"] = url
        if row:
            rows.append(row)
    return rows


def _gates(value):
    if not isinstance(value, list):
        return []
    return [_pick_scalars(item, ("id", "label", "blocks", "status"))
            for item in value if isinstance(item, dict)]


def _prizes(value):
    if not isinstance(value, dict):
        return None
    out = _pick_scalars(value, ("status", "pool"))
    tiers = []
    for item in value.get("tiers", []):
        if not isinstance(item, dict):
            continue
        row = _pick_scalars(item, ("place", "award"))
        url = _https(item.get("source_url"))
        if url:
            row["source_url"] = url
        if row:
            tiers.append(row)
    out["tiers"] = tiers
    return out


def _state_record(value, fields):
    if not isinstance(value, dict):
        return None
    return _pick_scalars(value, fields)


def _event(record):
    if not isinstance(record, dict):
        raise ValueError("each coordinator event must be an object")
    out = _pick_scalars(
        record, ("id", "name", "host", "platform", "status")
    )
    official_url = _https(record.get("official_url"))
    if official_url:
        out["official_url"] = official_url

    platforms = record.get("also_platforms")
    if isinstance(platforms, list):
        out["also_platforms"] = [v for v in platforms if isinstance(v, str)]

    organizers = _organizers(record.get("organizers"))
    if organizers:
        out["organizers"] = organizers

    dates = _dates(record.get("dates"))
    if dates:
        out["dates"] = dates

    constraints = record.get("constraints")
    if isinstance(constraints, list):
        out["constraints"] = [v for v in constraints if isinstance(v, str)]

    gates = _gates(record.get("gates"))
    if gates:
        out["gates"] = gates

    prizes = _prizes(record.get("prizes"))
    if prizes is not None:
        out["prizes"] = prizes

    registration = _state_record(record.get("registration"), ("state",))
    if registration is not None:
        out["registration"] = registration

    submission = _state_record(record.get("submission"), ("state", "at"))
    if submission is not None:
        out["submission"] = submission
    return out


def _assert_public(value):
    if isinstance(value, dict):
        leaked = FORBIDDEN_KEYS.intersection(value)
        if leaked:
            raise ValueError(f"forbidden internal field in public projection: {sorted(leaked)}")
        for child in value.values():
            _assert_public(child)
    elif isinstance(value, list):
        for child in value:
            _assert_public(child)


def build_feed(root: Path) -> dict:
    source = root / SOURCE
    try:
        coordinator = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read coordinator source: {exc}") from exc
    if not isinstance(coordinator, dict) or coordinator.get("schema_version") != 1:
        raise ValueError("unsupported coordinator schema_version; expected 1")
    events = coordinator.get("events")
    if not isinstance(events, list):
        raise ValueError("coordinator events must be a list")

    feed = {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": SOURCE,
        "coordinator_schema_version": 1,
        "events": [_event(event) for event in events],
    }
    _assert_public(feed)
    return feed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    feed = build_feed(Path(args.root))
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(f"wrote {output} ({len(feed['events'])} public events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
