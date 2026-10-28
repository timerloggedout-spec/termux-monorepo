#!/usr/bin/env python3
"""Delphi continuous-ledger feed collector — schema delphi-ledger-feed/v1.

Reads a cache directory (issues.json + comments.json in GitHub API
shape, ledgers.json copied from ops/delphi/) and emits the feed the
dashboard renders: every registered continuous ledger (contract:
docs/ops/DELPHI-LEDGER-STORE.md) as an append-only event stream plus
its folded current state, and every registered living record as its
current body with a hash version key.

Honesty rules: a ledger whose issue is missing from the cache is a
hard refusal (no partial feed); a comment is an event iff it starts
with one of the ledger's markers or with '[MUSEai]@' (signed append);
all other comments are counted as excluded noise, never carried;
snapshot payloads are carried verbatim from the newest marker comment
(the gate's own latest_json rule) — this collector folds nothing and
recomputes no EWMA, Elo or score.

Usage: ledger_feed.py --cache DIR --out FEED.json
The cache is produced by ledger_fetch.py (Actions) or any
authenticated GitHub client.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "delphi-ledger-feed/v1"
JSON_BLOCK = re.compile(r"```json\n(.*?)\n```", re.S)
SNAPSHOT_AT = re.compile(r"Snapshot\s+(\d{4}-\d{2}-\d{2}T[0-9:]+Z)")


def event_key(ledger_id: str, comment_id: int) -> str:
    """Mirror idempotency key: one row/event per source comment."""
    return hashlib.sha256(f"{ledger_id}|{comment_id}".encode()).hexdigest()


def marker_of(body: str, markers: list[str]) -> str | None:
    for m in markers:
        if body.startswith(m):
            return m
    return None


def payload_of(body: str) -> dict | None:
    m = JSON_BLOCK.search(body or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def first_line(body: str, markers: list[str]) -> str:
    lines = [ln.strip() for ln in (body or "").splitlines()]
    lines = [ln for ln in lines if ln and ln not in markers]
    return lines[0][:200] if lines else ""


def collect(cache: Path) -> dict:
    needed = ["issues.json", "comments.json", "ledgers.json"]
    missing = [n for n in needed if not (cache / n).exists()]
    if missing:
        raise SystemExit(f"partial cache refused: missing {', '.join(missing)}")
    issues = {i["number"]: i for i in json.loads((cache / "issues.json").read_text())}
    comments = json.loads((cache / "comments.json").read_text())
    registry = json.loads((cache / "ledgers.json").read_text())

    # Partition each issue's comments across its ledgers exactly once:
    # a marker match claims the comment for that ledger (registry order);
    # an unmarked signed append goes to the issue's first ledger.
    claims: dict[tuple[int, int], str] = {}
    for led in registry.get("ledgers", []):
        for c in comments.get(str(led["issue"]), []):
            k = (led["issue"], c["id"])
            if k not in claims and marker_of(c.get("body") or "", led["markers"]):
                claims[k] = led["id"]
    first_of_issue: dict[int, str] = {}
    for led in registry.get("ledgers", []):
        first_of_issue.setdefault(led["issue"], led["id"])
    noise_of_issue: dict[int, int] = {}
    for led in registry.get("ledgers", []):
        num = led["issue"]
        for c in comments.get(str(num), []):
            k = (num, c["id"])
            if k in claims:
                continue
            if (c.get("body") or "").startswith("[MUSEai]@"):
                claims[k] = first_of_issue[num]
            elif led["id"] == first_of_issue[num]:
                noise_of_issue[num] = noise_of_issue.get(num, 0) + 1

    feed: dict = {"schema": SCHEMA, "ledgers": [], "living_records": [],
                  "summary": {"events": 0, "excluded_noise": 0}}
    for led in registry.get("ledgers", []):
        num = led["issue"]
        if num not in issues or str(num) not in comments:
            raise SystemExit(
                f"partial cache refused: ledger {led['id']} issue #{num} absent")
        events, current = [], None
        noise = noise_of_issue.get(num, 0) if led["id"] == first_of_issue[num] else 0
        seen_keys = set()
        for c in sorted(comments[str(num)], key=lambda c: (c["created_at"], c["id"])):
            if claims.get((num, c["id"])) != led["id"]:
                continue
            body = c.get("body") or ""
            mark = marker_of(body, led["markers"])
            key = event_key(led["id"], c["id"])
            if key in seen_keys:  # idempotent re-delivery: one event per comment
                continue
            seen_keys.add(key)
            ev = {"event_key": key, "comment_id": c["id"],
                  "created_at": c["created_at"], "marker": mark,
                  "headline": first_line(body, led["markers"]),
                  "payload": payload_of(body)}
            events.append(ev)
            if led["kind"] == "snapshot-comments" and mark is not None \
                    and ev["payload"] is not None:
                current = {"comment_id": c["id"], "created_at": c["created_at"],
                           "payload": ev["payload"]}
        feed["ledgers"].append({
            "id": led["id"], "title": led["title"], "issue": num,
            "kind": led["kind"], "semantics": led["semantics"],
            "state_rule": led["state_rule"], "events": events,
            "current": current, "excluded_noise": noise})
        feed["summary"]["events"] += len(events)
        feed["summary"]["excluded_noise"] += noise

    for rec in registry.get("living_records", []):
        num = rec["issue"]
        if num not in issues:
            raise SystemExit(
                f"partial cache refused: living record {rec['id']} issue #{num} absent")
        body = issues[num].get("body") or ""
        m = SNAPSHOT_AT.search(body)
        feed["living_records"].append({
            "id": rec["id"], "title": rec["title"], "issue": num,
            "kind": rec["kind"], "semantics": rec["semantics"],
            "state_rule": rec["state_rule"],
            "version_key": hashlib.sha256(body.encode()).hexdigest(),
            "snapshot_at": m.group(1) if m else None,
            "updated_at": issues[num].get("updated_at"), "body": body})
    return feed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    feed = collect(Path(args.cache))
    Path(args.out).write_text(json.dumps(feed, indent=1) + "\n")
    print(f"{feed['schema']}: {len(feed['ledgers'])} ledgers, "
          f"{feed['summary']['events']} events, "
          f"{len(feed['living_records'])} living records, "
          f"{feed['summary']['excluded_noise']} noise comments excluded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
