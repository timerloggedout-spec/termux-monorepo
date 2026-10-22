"""Rebuildable fake paper evidence, using the same MSM-005 journal and MSM-012 CSV."""
import io
import json
import os
from pathlib import Path

from scripts.model_selection_market.market import MarketGraph, BetEntry, TradingCard
from scripts.model_selection_market.paper_wallet import write_csv


def test_four_scope_lifecycle_has_one_authority_and_rebuildable_csv(tmp_path):
    journal = tmp_path / "market.jsonl"
    graph = MarketGraph(journal=str(journal))
    graph.issue_paper_points("fixture-issue", "fixture-owner", 100, "deterministic offline fixture; nonredeemable paper points")
    for actor, subject_kind, subject_id, terminal in (
        ("itself", "model", "fixture/self", "settle"),
        ("others", "model", "fixture/peer", "release"),
        ("job", "job", "fixture-job", "void"),
    ):
        bet = graph.place_bet(BetEntry(actor_class=actor, actor_id="fixture-owner", subject_kind=subject_kind, subject_id=subject_id))
        reservation = "fixture-" + actor
        graph.reserve_bet("reserve-" + actor, reservation, "fixture-owner", 10, bet["entry_id"])
        if terminal == "settle":
            graph.settle("settle-self", reservation, "fixture-peer")
        elif terminal == "release":
            graph.release("release-peer", reservation)
        else:
            graph.void("void-job", reservation)
    card = graph.add_card(TradingCard(role="fixture-review", owner="fixture-owner"))
    offer = graph.offer_trade("fixture-offer", card["card_id"], "fixture-peer", at="2026-10-22T00:00:00+00:00")
    graph.reserve_offer("reserve-offer", "fixture-offer-reservation", "fixture-owner", 10, card["card_id"], offer["at"])
    graph.settle("settle-offer", "fixture-offer-reservation", "fixture-peer")
    snapshot = graph.snapshot()
    rebuilt = MarketGraph(journal=str(journal)).snapshot()
    assert snapshot == rebuilt
    accounts = snapshot["accounting"]["accounts"]
    assert sum(row["balance"] for row in accounts.values()) == 100
    assert all(row["reserved"] == 0 for row in accounts.values())
    csv = io.StringIO()
    write_csv(snapshot, csv)
    replayed = io.StringIO()
    write_csv(rebuilt, replayed)
    assert csv.getvalue() == replayed.getvalue()
    assert "PAPER ONLY" in csv.getvalue()
    destination = os.environ.get("RESEARCH_PAPER_EVIDENCE_DIR")
    if destination:
        directory = Path(destination)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "paper-market-fixture.jsonl").write_text(journal.read_text())
        (directory / "paper-market-snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
        (directory / "paper-market-projection.csv").write_text(csv.getvalue())


def test_csv_view_rejects_edits_against_authoritative_journal(tmp_path, capsys):
    from scripts.model_selection_market.paper_wallet import main, validate_csv
    import pytest
    journal = tmp_path / 'market.jsonl'
    graph = MarketGraph(journal=str(journal))
    graph.issue_paper_points('issue', 'owner', 10, 'fixture issuance')
    output = io.StringIO()
    write_csv(graph.snapshot(), output)
    source = tmp_path / 'projection.csv'
    source.write_text(output.getvalue())
    assert main(['view', str(source), '--journal', str(journal)]) == 0
    assert capsys.readouterr().out == output.getvalue()
    assert validate_csv(io.StringIO(output.getvalue()), graph.snapshot())
    source.write_text(output.getvalue().replace(',10,0,10,', ',99,0,99,'))
    with pytest.raises(SystemExit): main(['view', str(source), '--journal', str(journal)])
    assert graph.accounting_snapshot()['accounts']['owner']['balance'] == 10
