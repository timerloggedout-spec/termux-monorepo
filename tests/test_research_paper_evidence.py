"""Rebuildable fake paper evidence using the canonical MSM-005 journal and CSV view."""
import csv
import io
import json
import os
from pathlib import Path

from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard
from scripts.model_selection_market.paper_wallet import FIELDS, parse_csv, write_csv


PROVENANCE = {
    "issuer": "offline-fixture",
    "source": "synthetic",
    "reference": "nonredeemable paper evidence; no production wallet",
}


def test_four_scope_lifecycle_has_one_authority_and_rebuildable_csv(tmp_path):
    journal = tmp_path / "market.jsonl"
    graph = MarketGraph(event_path=str(journal))
    graph.open_account("fixture-owner", event_id="open-owner", provenance=PROVENANCE)
    graph.open_account("fixture-peer", event_id="open-peer", provenance=PROVENANCE)
    graph.issue_points("fixture-owner", 100, event_id="issue-owner", provenance=PROVENANCE)

    for actor, subject_kind, subject_id, terminal in (
        ("itself", "model", "fixture/self", "settle"),
        ("others", "model", "fixture/peer", "cancelled"),
        ("job", "job", "fixture-job", "unresolved"),
    ):
        reservation_id = "fixture-" + actor
        bet = BetEntry(actor_class=actor, actor_id="fixture-owner", subject_kind=subject_kind,
                       subject_id=subject_id, unit_kind="paper_point", units=10)
        graph.reserve_bet(bet, event_id="reserve-" + actor, reservation_id=reservation_id)
        if terminal == "settle":
            graph.settle(reservation_id, event_id="settle-" + actor, recipient="fixture-peer")
        else:
            graph.release(reservation_id, event_id="release-" + actor, reason=terminal)

    card = graph.add_card(TradingCard(role="fixture-review", owner="fixture-owner"))
    snapshot = graph.snapshot()
    rebuilt = MarketGraph(event_path=str(journal)).snapshot()
    assert snapshot == rebuilt
    assert any(row["card_id"] == card["card_id"] for row in snapshot["cards"])
    accounts = snapshot["paper_accounting"]["accounts"]
    assert sum(row["balance"] for row in accounts) == 100
    assert all(row["reserved"] == 0 for row in accounts)
    assert {row["status"] for row in snapshot["paper_accounting"]["reservations"]} == {"settled", "released"}

    projection = io.StringIO(newline="")
    write_csv(snapshot, projection)
    replayed_projection = io.StringIO(newline="")
    write_csv(rebuilt, replayed_projection)
    assert projection.getvalue() == replayed_projection.getvalue()
    parsed = parse_csv(projection.getvalue())
    assert {row["record_type"] for row in parsed} >= {"account", "reservation", "event", "card"}
    assert "PAPER ONLY" in projection.getvalue()

    destination = os.environ.get("RESEARCH_PAPER_EVIDENCE_DIR")
    if destination:
        directory = Path(destination)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "paper-market-fixture.jsonl").write_text(journal.read_text())
        (directory / "paper-market-snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
        (directory / "paper-market-projection.csv").write_text(projection.getvalue())


def test_csv_view_rejects_edits_against_authoritative_journal(tmp_path, capsys):
    import pytest
    from scripts.model_selection_market.paper_wallet import main

    journal = tmp_path / "market.jsonl"
    graph = MarketGraph(event_path=str(journal))
    graph.open_account("owner", event_id="open-owner", provenance=PROVENANCE)
    graph.issue_points("owner", 10, event_id="issue-owner", provenance=PROVENANCE)
    output = io.StringIO(newline="")
    write_csv(graph.snapshot(), output)
    source = tmp_path / "projection.csv"
    source.write_text(output.getvalue())

    assert main(["view", str(source), "--events", str(journal)]) == 0
    assert capsys.readouterr().out == output.getvalue()
    assert parse_csv(output.getvalue())

    rows = list(csv.DictReader(io.StringIO(output.getvalue(), newline="")))
    account = next(row for row in rows if row["record_type"] == "account")
    account["balance"] = "99"
    account["available"] = "99"
    tampered = io.StringIO(newline="")
    writer = csv.DictWriter(tampered, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    source.write_text(tampered.getvalue())

    with pytest.raises(SystemExit):
        main(["view", str(source), "--events", str(journal)])
    owner = next(row for row in graph.accounting_snapshot()["accounts"] if row["owner"] == "owner")
    assert owner["balance"] == 10
