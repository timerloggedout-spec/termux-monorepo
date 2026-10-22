#!/usr/bin/env python3
"""Read-only, non-authoritative paper CSV view over MSM MarketGraph snapshots."""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, TextIO

PAPER_ONLY_NOTE = "PAPER ONLY — observational snapshot; no spendable balance or real settlement"
FIELDS = [
    "paper_only", "record_type", "actor_id", "actor_class", "entry_id",
    "subject_kind", "subject_id", "model", "task", "units", "unit_kind",
    "status", "prediction", "role", "card_id", "card_owner", "card_share",
    "artifact_path", "opt_script_path", "offer_to", "offer_at", "note",
    "balance", "reserved", "available", "source_event_count", "source_digest",
    "reservation_id", "reservation_owner", "reservation_status", "reservation_kind",
    "csv_version", "event_id", "event_type", "event_correlation", "provenance", "reference",
]


def _safe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value[:1] in ("\t", "\r", "\n") or value.lstrip()[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def _records(value: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{name} must be a list of objects")
    return value


def _amount(value: Any, name: str, *, integer: bool = False) -> None:
    if isinstance(value, bool) or type(value) not in ((int,) if integer else (int, float)):
        raise ValueError(f"{name} must be a {'non-negative integer' if integer else 'finite number'}")
    if (integer and value > 2**63 - 1) or value < 0:
        raise ValueError(f"{name} must be a {'non-negative integer' if integer else 'finite number'}")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name} must be a {'non-negative integer' if integer else 'finite number'}")


def _accounting_rows(accounting: Any) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(accounting, dict) or type(accounting.get("schema_version")) is not int or accounting.get("schema_version") != 1 or accounting.get("asset") != "paper_point":
        raise ValueError("paper_accounting must be schema_version 1 paper_point")
    count, digest = accounting.get("event_count"), accounting.get("source_digest")
    _amount(count, "event_count", integer=True)
    if not isinstance(digest, str) or not digest:
        raise ValueError("source_digest must be a non-empty string")
    accounts = _records(accounting.get("accounts"), "accounts")
    reservations = _records(accounting.get("reservations"), "reservations")
    owners: dict[str, dict[str, Any]] = {}
    rows = []
    for a in accounts:
        owner = a.get("owner")
        if not isinstance(owner, str) or not owner or owner in owners:
            raise ValueError("account owners must be unique non-empty strings")
        for key in ("balance", "reserved", "available"):
            _amount(a.get(key), f"account {key}", integer=True)
        if a["reserved"] > a["balance"] or a["available"] != a["balance"] - a["reserved"]:
            raise ValueError("account balance/reserved/available are inconsistent")
        owners[owner] = a
        rows.append({"record_type": "account", "reservation_owner": owner,
                     "balance": a["balance"], "reserved": a["reserved"], "available": a["available"],
                     "source_event_count": count, "source_digest": digest})
    ids = set()
    active: dict[str, int] = {owner: 0 for owner in owners}
    operations = set()
    for r in reservations:
        rid, owner = r.get("reservation_id"), r.get("owner")
        if not isinstance(rid, str) or not rid or rid in ids or owner not in owners:
            raise ValueError("reservation ids must be unique and owners must reference accounts")
        ids.add(rid)
        _amount(r.get("units"), "reservation units", integer=True)
        if r["units"] <= 0 or r.get("status") not in ("reserved", "settled", "released"):
            raise ValueError("invalid reservation units or status")
        if r.get("status") == "reserved": active[owner] += r["units"]
        if r.get("kind") == "bet":
            op = (owner, r.get("entry_id"))
            if not r.get("entry_id") or op in operations: raise ValueError("duplicate bet reservation operation")
            operations.add(op)
        rows.append({"record_type": "reservation", "units": r["units"], "unit_kind": "paper_point",
                     "reservation_id": rid, "reservation_owner": owner, "reservation_status": r["status"],
                     "reservation_kind": r.get("kind", ""), "entry_id": r.get("entry_id", ""),
                     "card_id": r.get("card_id", ""), "offer_to": r.get("to_owner", r.get("recipient", "")),
                     "source_event_count": count, "source_digest": digest})
    events = _records(accounting.get("events"), "events")
    try:
        from .accounting import digest as event_digest, replay
    except ImportError:
        from accounting import digest as event_digest, replay
    if count != len(events) or digest != event_digest(events): raise ValueError("event history count/digest mismatch")
    # Use the production reducer as the authority for event schema and derived state.
    try:
        from .market import MarketGraph
    except ImportError:
        from market import MarketGraph
    graph = MarketGraph()
    state = graph._reduce(events)
    if state["accounts"] != {owner: a["balance"] for owner, a in owners.items()}:
        raise ValueError("account balances do not match event history")
    if state["reservations"] != {r["reservation_id"]: r for r in reservations}:
        raise ValueError("reservations do not match event history")
    for owner, a in owners.items():
        if a["reserved"] != active[owner]: raise ValueError("account reserved amount does not equal active holds")
    event_ids = set()
    for event in events:
        if not isinstance(event.get("event_id"), str) or not event.get("event_id") or event["event_id"] in event_ids or not isinstance(event.get("type"), str):
            raise ValueError("event rows require event_id and type")
        event_ids.add(event["event_id"])
        rows.append({"record_type": "event", "event_id": event["event_id"], "event_type": event["type"],
                     "event_correlation": event.get("correlation_id", event["event_id"]),
                     "provenance": json.dumps(event.get("provenance", event.get("payload", {}).get("provenance", "")), sort_keys=True, separators=(",", ":")),
                     "reference": event.get("reference", event.get("payload", {}).get("provenance", {}).get("reference", event.get("payload", {}).get("reference", ""))), "source_event_count": count, "source_digest": digest})
    return rows, {f"{r.get('owner')}\0{r.get('entry_id')}": r for r in reservations if r.get("kind") == "bet"}


def project_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot root must be a JSON object")
    if type(snapshot.get("schema_version")) is not int or snapshot.get("schema_version") != 1 or snapshot.get("policy") != "observational_until_promote":
        raise ValueError("expected an observational MSM MarketGraph v1 snapshot")
    card_records = _records(snapshot.get("cards"), "cards")
    bets = _records(snapshot.get("bets"), "bets")
    rows: list[dict[str, Any]] = []
    cards = {str(c.get("card_id", "")): c for c in card_records}
    if len(cards) != len(card_records):
        raise ValueError("duplicate card_id in snapshot")
    accounting = snapshot.get("paper_accounting")
    extra: list[dict[str, Any]] = []
    reservations: dict[str, dict[str, Any]] = {}
    metadata: dict[str, Any] = {}
    if accounting is not None:
        extra, reservations = _accounting_rows(accounting)
        metadata = {"source_event_count": accounting["event_count"], "source_digest": accounting["source_digest"]}
    for bet in bets:
        subject, stake = bet.get("subject"), bet.get("stake")
        if not isinstance(subject, dict) or not isinstance(stake, dict):
            raise ValueError("each bet needs subject and stake objects")
        units = stake.get("units")
        try:
            valid = type(units) in (int, float) and math.isfinite(units) and units > 0
        except OverflowError:
            valid = False
        kind = stake.get("unit_kind")
        if kind == "paper_point":
            if type(units) is not int or units <= 0:
                raise ValueError("paper_point stake must be a positive integer")
            key = f"{bet.get('actor_id')}\0{bet.get('entry_id')}"
            r = reservations.get(key)
            if not r or r.get("units") != units or r.get("owner") != bet.get("actor_id"):
                raise ValueError("paper_point stake must correlate to a matching reservation")
        elif not valid or kind not in ("observational", "soft_quota_token"):
            raise ValueError("stake must use finite positive paper units")
        card = cards.get(str(bet.get("card_id") or ""), {})
        sid, skind = str(subject.get("id", "")), subject.get("kind", "")
        linked_key = f"{bet.get('actor_id')}\0{bet.get('entry_id')}"
        linked = reservations.get(linked_key) if kind == "paper_point" else None
        rows.append({"record_type": "stake", "actor_id": bet.get("actor_id", ""), "actor_class": bet.get("actor_class", ""), "entry_id": bet.get("entry_id", ""),
                     "subject_kind": skind, "subject_id": sid, "model": sid if skind == "model" else "", "task": sid if skind == "job" else "",
                     "units": units, "unit_kind": kind, "status": bet.get("status", ""), "prediction": bet.get("prediction", ""),
                     "role": subject.get("role", "") or card.get("role", ""), "card_id": bet.get("card_id", ""), "card_owner": card.get("owner", ""),
                     "card_share": card.get("share", ""), "artifact_path": card.get("artifact_path", ""), "opt_script_path": card.get("opt_script_path", ""), "reservation_id": linked.get("reservation_id", "") if linked else "", **metadata})
    for card in cards.values():
        common = {"card_id": card.get("card_id", ""), "card_owner": card.get("owner", ""), "card_share": card.get("share", ""),
                  "role": card.get("role", ""), "artifact_path": card.get("artifact_path", ""), "opt_script_path": card.get("opt_script_path", ""), **metadata}
        rows.append({"record_type": "card", **common})
        for trade in _records(card.get("trade_log", []), "trade_log"):
            if trade.get("action") == "offer":
                rows.append({"record_type": "offer", **common, "actor_id": trade.get("from", card.get("owner", "")), "offer_to": trade.get("to", ""),
                             "offer_at": trade.get("at", ""), "note": "Offer is observational; no transfer or settlement"})
    rows.extend(extra)
    for row in rows:
        row["paper_only"] = PAPER_ONLY_NOTE
        row["csv_version"] = 1
    return rows


def _write_rows(rows: list[dict[str, Any]], destination: TextIO) -> int:
    writer = csv.DictWriter(destination, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: _safe(row.get(k, "")) for k in FIELDS})
    return len(rows)


def write_csv(snapshot: dict[str, Any], destination: TextIO) -> int:
    return _write_rows(project_snapshot(snapshot), destination)


def parse_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(text.splitlines(keepends=True), strict=True)
    legacy = FIELDS[:22]
    if reader.fieldnames not in (FIELDS, legacy):
        raise ValueError("CSV header does not match paper view schema")
    result = []
    account_owners, reservation_ids = set(), set()
    sources = set()
    event_ids = set()
    rows = []
    for row in reader:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("malformed CSV row")
        if row.get("paper_only") != PAPER_ONLY_NOTE:
            raise ValueError("invalid paper_only label")
        if not legacy and row["csv_version"] != "1": raise ValueError("unsupported CSV version")
        if legacy:
            rows.append(row); result.append(row); continue
        for k in ("balance", "reserved", "available", "source_event_count"):
            if row[k] and (not row[k].isdigit() or int(row[k]) > 2**63 - 1):
                raise ValueError(f"invalid {k} amount/schema value")
        if row["record_type"] not in ("stake", "card", "offer", "account", "reservation", "event"):
            raise ValueError("unknown CSV record_type")
        if row["record_type"] == "account":
            owner = row["reservation_owner"]
            if not owner or owner in account_owners: raise ValueError("duplicate or missing account owner")
            account_owners.add(owner)
            if any(not row[k] for k in ("balance", "reserved", "available", "source_event_count", "source_digest")): raise ValueError("account amounts and source metadata are required")
            balance, reserved, available = (int(row[k]) for k in ("balance", "reserved", "available"))
            if reserved > balance or available != balance - reserved: raise ValueError("inconsistent account amounts")
        if row["record_type"] == "reservation":
            rid = row["reservation_id"]
            if not rid or rid in reservation_ids: raise ValueError("duplicate or missing reservation id")
            reservation_ids.add(rid)
            if not row["reservation_owner"] or row["reservation_status"] not in ("reserved", "settled", "released") or not row["units"] or not row["source_event_count"] or not row["source_digest"]: raise ValueError("invalid or incomplete reservation row")
            if int(row["units"]) <= 0 or int(row["units"]) > 2**63 - 1: raise ValueError("reservation units out of range")
        if row["record_type"] == "event":
            if not row["event_id"] or row["event_id"] in event_ids or not row["event_type"] or not row["source_event_count"] or not row["source_digest"]: raise ValueError("invalid or incomplete event row")
            event_ids.add(row["event_id"])
        if row["unit_kind"] == "paper_point" and row["units"] and (not row["units"].isdigit() or int(row["units"]) <= 0):
            raise ValueError("paper_point units must be a positive integer")
        if row["record_type"] == "stake" and (not row["actor_id"] or not row["entry_id"] or not row["subject_kind"] or not row["subject_id"] or not row["units"] or not row["unit_kind"] or not row["status"]): raise ValueError("incomplete stake row")
        if row["record_type"] in ("account", "reservation", "event"):
            sources.add((row["source_event_count"], row["source_digest"]))
        result.append(row)
    if len(sources) > 1:
        raise ValueError("mismatched source event count/digest across rows")
    if sources:
        if not all(c.isdigit() and d for c, d in sources): raise ValueError("missing source event count/digest")
        count = int(next(iter(sources))[0])
        event_rows = [r for r in result if r["record_type"] == "event"]
        if len(event_rows) != count:
            raise ValueError("event rows do not match source event count")
        account_set = {r["reservation_owner"] for r in result if r["record_type"] == "account"}
        if any(r["reservation_owner"] not in account_set for r in result if r["record_type"] == "reservation"): raise ValueError("reservation owner has no account")
        active = {}
        operations = set()
        for r in result:
            if r["record_type"] == "reservation":
                if r["reservation_kind"] == "bet":
                    key = (r["reservation_owner"], r["entry_id"])
                    if not r["entry_id"] or key in operations: raise ValueError("duplicate bet reservation operation")
                    operations.add(key)
                if r["reservation_status"] == "reserved": active[r["reservation_owner"]] = active.get(r["reservation_owner"], 0) + int(r["units"])
        for r in result:
            if r["record_type"] == "account" and int(r["reserved"]) != active.get(r["reservation_owner"], 0): raise ValueError("account reserved amount does not equal active holds")
    return result


def _same_path(source: Path, output: Path) -> bool:
    resolved = source.resolve()
    targets = (source, Path(str(source) + ".lock"), resolved, Path(str(resolved) + ".lock"))
    for target in targets:
        try:
            if output.resolve() == target.resolve() or (output.exists() and target.exists() and os.path.samefile(output, target)):
                return True
        except OSError:
            continue
    return False


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as f:
            temp = Path(f.name); f.write(content); f.flush(); os.fsync(f.fileno())
        os.replace(temp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(dir_fd)
        finally: os.close(dir_fd)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def _render(snapshot: dict[str, Any]) -> str:
    import io
    out = io.StringIO(newline="")
    write_csv(snapshot, out)
    return out.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="project a market snapshot to paper CSV")
    export.add_argument("snapshot", type=Path); export.add_argument("output", type=Path)
    events = sub.add_parser("export-events", help="replay an event log and export its canonical paper CSV")
    events.add_argument("event_log", type=Path); events.add_argument("output", type=Path)
    view = sub.add_parser("view", help="validate and display a paper CSV projection")
    view.add_argument("csv_file", type=Path); view.add_argument("--events", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            if _same_path(args.snapshot, args.output): raise ValueError("output must not overwrite snapshot input or its lock")
            snapshot = json.loads(args.snapshot.read_text(encoding="utf-8")); text = _render(snapshot)
            if str(args.output) == "-": sys.stdout.write(text)
            else: _atomic_write(args.output, text)
        elif args.command == "export-events":
            if _same_path(args.event_log, args.output): raise ValueError("output must not overwrite event log or its lock")
            if not args.event_log.exists(): raise ValueError("event log does not exist")
            try:
                from .market import MarketGraph
            except ImportError:
                from market import MarketGraph
            graph = MarketGraph(event_path=str(args.event_log)); text = _render(graph.snapshot())
            if str(args.output) == "-": sys.stdout.write(text)
            else: _atomic_write(args.output, text)
        else:
            text = args.csv_file.read_text(encoding="utf-8")
            parse_csv(text)
            if args.events:
                if not args.events.exists(): raise ValueError("event log does not exist")
                try:
                    from .market import MarketGraph
                except ImportError:
                    from market import MarketGraph
                canonical = _render(MarketGraph(event_path=str(args.events)).snapshot())
                if text != canonical: raise ValueError("CSV view is stale or tampered relative to event log")
            sys.stdout.write(text)
    except (ValueError, OSError, json.JSONDecodeError, csv.Error) as exc:
        parser.error(str(exc))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
