#!/usr/bin/env python3
"""Observe admitted and candidate challenge records through public source pages.

The coordinator remains the source of record. This observer is read-only:
it writes coverage and append-only page-hash snapshots, then the workflow
proposes those observations as a refresh PR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "termux-monorepo-challenge-osint/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "replace")


def records_to_watch(coordinator: dict):
    """Yield admitted events and pre-admission candidates as separate kinds."""
    for kind, key in (("event", "events"), ("candidate", "candidate_events")):
        for record in coordinator.get(key, []) or []:
            if isinstance(record, dict):
                yield kind, record


def watch_sources_of(record: dict) -> list[dict]:
    sources = record.get("watch_sources")
    if isinstance(sources, list) and sources:
        out = []
        for source in sources:
            if isinstance(source, str):
                out.append({"label": "source", "url": source})
            elif isinstance(source, dict) and source.get("url"):
                out.append({"label": source.get("label") or "source",
                            "url": source["url"]})
        return out
    url = record.get("official_url")
    return [{"label": "official page", "url": url}] if url else []


def coverage_of(record: dict, record_type: str = "event") -> dict:
    prizes = record.get("prizes") or {}
    tiers = prizes.get("tiers") if isinstance(prizes, dict) else None
    if isinstance(tiers, list):
        tier_count = len(tiers)
    else:
        tier_count = int(bool(tiers))
    prize_status = (prizes.get("status") if isinstance(prizes, dict) else None)
    if not prize_status:
        prize_status = ("ESTABLISHED" if tier_count or
                        (isinstance(prizes, dict) and prizes.get("pool"))
                        else "NOT_ESTABLISHED")

    dates = record.get("dates") or {}
    if isinstance(dates, dict):
        date_count = sum(1 for value in dates.values()
                         if value not in (None, "", "NOT_ESTABLISHED"))
    elif isinstance(dates, list):
        date_count = len(dates)
    else:
        date_count = int(bool(dates))

    constraints = record.get("constraints") or []
    gates = record.get("gates") or []
    rules_count = (len(constraints) if isinstance(constraints, list)
                   else int(bool(constraints)))
    rules_count += (len(gates) if isinstance(gates, list)
                    else int(bool(gates)))
    organizers = record.get("organizers") or []
    if not organizers and record.get("host"):
        organizers = [record["host"]]
    participants = record.get("participants") or []
    projects = record.get("projects") or []
    judges = record.get("judges") or []
    signals = record.get("signals") or {}
    signal_rows = signals.get("snapshots", []) if isinstance(signals, dict) else []
    sources = watch_sources_of(record)

    return {
        "record_type": record_type,
        "status": record.get("status"),
        "organizers": len(organizers) if isinstance(organizers, list) else int(bool(organizers)),
        "dates": date_count,
        "prizes": {"status": prize_status, "tiers": tier_count},
        "rules_constraints": rules_count,
        "our_projects": len(projects) if isinstance(projects, list) else int(bool(projects)),
        "competitor_projects_participants": len(participants) if isinstance(participants, list) else int(bool(participants)),
        "judges": len(judges) if isinstance(judges, list) else int(bool(judges)),
        "signals": len(signal_rows) if isinstance(signal_rows, list) else int(bool(signal_rows)),
        "recruitment": int(bool(record.get("recruitment"))),
        "opportunity_cost": int(bool(record.get("opportunity_cost"))),
        "official_page_watch": bool(sources),
        "page_watch_urls": len(sources),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    ns = parser.parse_args(argv)
    root = Path(ns.root)
    coordinator_path = root / "ops/challenge/coordinator.json"
    osint_dir = root / "ops/challenge/osint"
    osint_dir.mkdir(parents=True, exist_ok=True)

    coordinator = json.loads(coordinator_path.read_text())
    snapshots_path = osint_dir / "snapshots.json"
    snapshots_doc = (json.loads(snapshots_path.read_text())
                     if snapshots_path.exists() else {"snapshots": []})
    snapshots = snapshots_doc.setdefault("snapshots", [])
    observed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    event_matrix = {}
    candidate_matrix = {}
    changed = []
    page_count = 0
    failures = []

    for record_type, record in records_to_watch(coordinator):
        event_id = str(record.get("id") or record.get("slug") or record.get("name") or "")
        if not event_id:
            continue
        matrix = event_matrix if record_type == "event" else candidate_matrix
        matrix[event_id] = coverage_of(record, record_type)

        for source in watch_sources_of(record):
            url = source["url"]
            label = source["label"]
            page_count += 1
            try:
                text = fetch_text(url)
                digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                seen = any(
                    snap.get("event") == event_id
                    and snap.get("url") == url
                    and snap.get("sha256") == digest
                    and snap.get("record_type", "event") == record_type
                    for snap in snapshots
                )
                if not seen:
                    snapshots.append({
                        "event": event_id,
                        "record_type": record_type,
                        "source_label": label,
                        "url": url,
                        "sha256": digest,
                        "fetched_at": observed_at,
                        "excerpt": " ".join(text.split())[:800],
                    })
                    changed.append(f"{record_type}:{event_id}:{label}")
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                failures.append({
                    "record_type": record_type,
                    "event": event_id,
                    "source_label": label,
                    "url": url,
                    "error": type(exc).__name__,
                })
                print(f"::warning title=challenge-osint::{record_type} {event_id} "
                      f"{label}: {type(exc).__name__}")

    coverage = {
        "schema": "challenge-osint-coverage/v1",
        "generated_at": observed_at,
        "summary": {
            "events": len(event_matrix),
            "candidates": len(candidate_matrix),
            "pages_watched": page_count,
            "snapshots_total": len(snapshots),
            "changed_this_run": len(changed),
            "fetch_failures": len(failures),
        },
        "events": event_matrix,
        "candidates": candidate_matrix,
        "fetch_failures": failures,
        "changed_this_run": changed,
    }
    (osint_dir / "coverage.json").write_text(
        json.dumps(coverage, indent=2) + "\n")
    snapshots_doc["snapshots"] = snapshots
    snapshots_path.write_text(json.dumps(snapshots_doc, indent=2) + "\n")
    print(f"::notice title=challenge-osint::events={len(event_matrix)} "
          f"candidates={len(candidate_matrix)} pages={page_count} "
          f"new_snapshots={len(changed)} failures={len(failures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
