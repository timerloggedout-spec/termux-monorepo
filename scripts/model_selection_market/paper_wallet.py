#!/usr/bin/env python3
"""MSM-012: read-only paper CSV view over an MSM market snapshot (not a wallet)."""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
from pathlib import Path
from typing import Any, TextIO

PAPER_ONLY_NOTE = "PAPER ONLY — observational snapshot; no spendable balance or real settlement"
FIELDS = [
    "paper_only", "record_type", "actor_id", "actor_class", "entry_id",
    "subject_kind", "subject_id", "model", "task", "units", "unit_kind",
    "status", "prediction", "role", "card_id", "card_owner", "card_share",
    "artifact_path", "opt_script_path", "offer_to", "offer_at", "note",
    "accounting_version", "balance", "reserved", "available", "event_ref", "reservation_ref", "journal_head", "account",
]


def _safe(value: Any) -> Any:
    """Neutralize spreadsheet formulas, including whitespace-prefixed ones."""
    if not isinstance(value, str):
        return value
    if value[:1] in ("\t", "\r", "\n") or value.lstrip()[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def _records(value: Any, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ValueError(f"{name} must be a list of objects")
    return value


def project_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate and project MSM records without establishing new authority."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot root must be a JSON object")
    if type(snapshot.get("schema_version")) is not int or snapshot.get("schema_version") != 1 or snapshot.get("policy") != "observational_until_promote":
        raise ValueError("expected an observational MSM MarketGraph v1 snapshot")
    card_records = _records(snapshot.get("cards"), "cards")
    bets = _records(snapshot.get("bets"), "bets")
    rows: list[dict[str, Any]] = []
    cards = {str(card.get("card_id", "")): card for card in card_records}
    if len(cards) != len(card_records):
        raise ValueError("duplicate card_id in snapshot")
    for bet in bets:
        subject, stake = bet.get("subject"), bet.get("stake")
        if not isinstance(subject, dict) or not isinstance(stake, dict):
            raise ValueError("each bet needs subject and stake objects")
        units = stake.get("units")
        try:
            valid_units = type(units) in (int, float) and math.isfinite(units) and units > 0
        except OverflowError:
            valid_units = False
        if not valid_units or stake.get("unit_kind") not in ("observational", "soft_quota_token"):
            raise ValueError("stake must use finite positive paper units")
        card = cards.get(str(bet.get("card_id") or ""), {})
        subject_id = str(subject.get("id", ""))
        kind = subject.get("kind", "")
        rows.append({
            "record_type": "stake", "actor_id": bet.get("actor_id", ""),
            "actor_class": bet.get("actor_class", ""), "entry_id": bet.get("entry_id", ""),
            "subject_kind": kind, "subject_id": subject_id,
            "model": subject_id if kind == "model" else "",
            "task": subject_id if kind == "job" else "",
            "units": units, "unit_kind": stake["unit_kind"],
            "status": bet.get("status", ""), "prediction": bet.get("prediction", ""),
            "role": subject.get("role", "") or card.get("role", ""),
            "card_id": bet.get("card_id", ""), "card_owner": card.get("owner", ""),
            "card_share": card.get("share", ""), "artifact_path": card.get("artifact_path", ""),
            "opt_script_path": card.get("opt_script_path", ""),
        })
    for card in cards.values():
        trades = _records(card.get("trade_log", []), "trade_log")
        common = {"actor_id": card.get("owner", ""), "card_id": card.get("card_id", ""), "card_owner": card.get("owner", ""),
                  "card_share": card.get("share", ""), "role": card.get("role", ""),
                  "artifact_path": card.get("artifact_path", ""), "opt_script_path": card.get("opt_script_path", "")}
        rows.append({"record_type": "card", **common})
        for trade in trades:
            if trade.get("action") == "offer":
                rows.append({"record_type": "offer", **common,
                             "actor_id": trade.get("from", card.get("owner", "")),
                             "offer_to": trade.get("to", ""), "offer_at": trade.get("at", ""),
                             "note": "Offer is observational; no transfer or settlement"})
    accounting = snapshot.get("accounting", {})
    if accounting:
        if type(accounting.get("schema_version")) is not int or accounting.get("schema_version") != 1 or not isinstance(accounting.get("accounts"), dict):
            raise ValueError("invalid authoritative accounting snapshot")
        head = accounting.get("head", "")
        reservations = accounting.get("reservations", {})
        if not isinstance(reservations, dict) or any(not isinstance(r, dict) or not isinstance(r.get("owner"), str) or type(r.get("amount")) is not int or r["amount"] <= 0 or not isinstance(r.get("market_ref"), str) for r in reservations.values()):
            raise ValueError("invalid authoritative reservations")
        events = accounting.get('events', [])
        if not isinstance(events, list) or any(not isinstance(e, dict) or type(e.get('version')) is not int or e['version'] != 1 or not isinstance(e.get('hash'), str) or len(e['hash']) != 64 for e in events):
            raise ValueError('invalid authoritative journal events')
        if events and (not isinstance(head, str) or head != events[-1]['hash']):
            raise ValueError('accounting head does not match journal')
        for owner, account in sorted(accounting['accounts'].items()):
            if not isinstance(account, dict) or any(type(account.get(k)) is not int or account[k] < 0 for k in ('balance','reserved','available')) or account['reserved'] > account['balance'] or account['balance']-account['reserved'] != account['available']:
                raise ValueError('invalid accounting account invariant')
            rows.append({'record_type':'account','actor_id':owner,'account':owner,'accounting_version':1,
                         'balance':account['balance'],'reserved':account['reserved'],'available':account['available'],
                         'journal_head':head,'event_ref':head,
                         'reservation_ref':','.join(sorted(rid for rid,r in reservations.items() if r.get('owner')==owner))})
        for row in rows:
            account = accounting["accounts"].get(row.get("actor_id", ""))
            if account and row.get('record_type') != 'account':
                row.update(accounting_version=1, balance=account["balance"], reserved=account["reserved"], available=account["available"], journal_head=head)
            row["event_ref"] = head
            row["journal_head"] = head
            if row['record_type'] == 'account':
                continue
            reference = ('bet:' + row['entry_id']) if row.get('entry_id') else ('offer:' + row['card_id'] + ':' + row['offer_at']) if row['record_type'] == 'offer' else None
            row["reservation_ref"] = ','.join(sorted(rid for rid, r in reservations.items() if reference and r['market_ref'] == reference))
            for event in events:
                wrapper = event.get('record', {})
                record = wrapper.get('record', {}) if isinstance(wrapper, dict) else {}
                if (row['record_type'] == 'stake' and event.get('type') == 'market_bet' and record.get('entry_id') == row.get('entry_id')) or (row['record_type'] == 'card' and event.get('type') == 'market_card' and record.get('card_id') == row.get('card_id')) or (row['record_type'] == 'offer' and event.get('type') == 'market_offer' and record.get('card_id') == row.get('card_id') and wrapper.get('offer', {}).get('at') == row.get('offer_at')):
                    row['event_ref'] = event['hash']
    for row in rows:
        row["paper_only"] = PAPER_ONLY_NOTE
    return rows


def _write_rows(rows: list[dict[str, Any]], destination: TextIO) -> int:
    writer = csv.DictWriter(destination, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: _safe(row.get(key, "")) for key in FIELDS})
    return len(rows)


def write_csv(snapshot: dict[str, Any], destination: TextIO) -> int:
    return _write_rows(project_snapshot(snapshot), destination)


def validate_csv(source: TextIO, snapshot: dict[str, Any]) -> bool:
    """Compare the entire deterministic projection, not a caller-edited head field."""
    expected = io.StringIO()
    write_csv(snapshot, expected)
    return source.read() == expected.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="project a market snapshot to paper CSV")
    export.add_argument("snapshot", type=Path, help="JSON MarketGraph snapshot")
    export.add_argument("output", type=Path, help="CSV output path, or - for stdout")
    view = sub.add_parser("view", help="display a paper CSV projection")
    view.add_argument("csv_file", type=Path)
    view.add_argument("--journal", type=Path, help="reject stale/edited CSV against the authoritative MSM-005 journal")
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
            # Validate everything before truncating an existing output file.
            rows = project_snapshot(snapshot)
            if str(args.output) == "-":
                _write_rows(rows, sys.stdout)
            else:
                with args.output.open("w", encoding="utf-8", newline="") as destination:
                    _write_rows(rows, destination)
        else:
            with args.csv_file.open("r", encoding="utf-8", newline="") as source:
                if args.journal:
                    from .market import MarketGraph
                    if not validate_csv(source, MarketGraph(journal=str(args.journal)).snapshot()):
                        raise ValueError("CSV is stale or edited; rebuild from the authoritative journal")
                    source.seek(0)
                sys.stdout.write(source.read())
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
