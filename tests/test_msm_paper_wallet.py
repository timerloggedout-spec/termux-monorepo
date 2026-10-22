import csv
import io
import json
import tempfile
from pathlib import Path
from scripts.model_selection_market.paper_wallet import main
import unittest

from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard
from scripts.model_selection_market.paper_wallet import FIELDS, PAPER_ONLY_NOTE, project_snapshot, write_csv


class TestPaperWallet(unittest.TestCase):
    def snapshot(self):
        graph = MarketGraph()
        card = TradingCard(role="review", owner="=evil", artifact_path="@artifact")
        graph.add_card(card)
        card.offer_trade("+recipient")
        graph.cards[card.card_id()]['trade_log'] = card.trade_log
        graph.place_bet(BetEntry(actor_class="others", subject_kind="model", subject_id="-model", actor_id="@actor", role="review", units=2.5, card_id=card.card_id()))
        graph.place_bet(BetEntry(actor_class="job", subject_kind="job", subject_id="task-17", actor_id="worker", units=1, card_id=card.card_id()))
        return graph.snapshot()

    def test_projects_stakes_cards_and_offers(self):
        rows = project_snapshot(self.snapshot())
        self.assertEqual([r['record_type'] for r in rows], ['stake', 'stake', 'card', 'offer'])
        stake = rows[0]
        self.assertEqual((stake['actor_id'], stake['entry_id'], stake['units'], stake['unit_kind']), ('@actor', stake['entry_id'], 2.5, 'observational'))
        self.assertEqual(stake['model'], '-model')
        self.assertEqual(rows[1]['task'], 'task-17')
        self.assertEqual(rows[-1]['offer_to'], '+recipient')
        self.assertTrue(all(r['paper_only'] == PAPER_ONLY_NOTE for r in rows))

    def test_csv_is_valid_and_formula_fields_are_neutralized(self):
        output = io.StringIO(newline='')
        count = write_csv(self.snapshot(), output)
        self.assertEqual(count, 4)
        parsed = list(csv.DictReader(io.StringIO(output.getvalue(), newline='')))
        self.assertEqual(len(parsed), 4)
        self.assertEqual(parsed[0]['actor_id'], "'@actor")
        self.assertEqual(parsed[0]['model'], "'-model")
        card = next(r for r in parsed if r['record_type'] == 'card')
        self.assertEqual(card['card_owner'], "'=evil")
        self.assertEqual(card['artifact_path'], "'@artifact")
        self.assertEqual(parsed[0]['units'], '2.5')
        self.assertEqual(set(parsed[0]), set(FIELDS))

    def test_whitespace_prefixed_formulas_are_neutralized(self):
        for actor in (" =SUM(1,2)", "\n=1+1", "\t@SUM(1,2)", "  +1", "\r-1"):
            graph = MarketGraph()
            graph.place_bet(BetEntry(actor_class="itself", subject_kind="model", subject_id="m", actor_id=actor))
            output = io.StringIO(newline="")
            write_csv(graph.snapshot(), output)
            rows = list(csv.DictReader(io.StringIO(output.getvalue(), newline="")))
            self.assertEqual(rows[0]["actor_id"], "'" + actor)

    def test_malformed_snapshot_never_writes_output(self):
        mutations = [
            {"cards": [None]}, {"bets": [None]}, {"bets": {}},
            {"bets": [{"subject": {}, "stake": None}]},
            {"cards": [{"card_id": "c", "trade_log": [None]}]},
            {"bets": [{"subject": {}, "stake": {"units": -1, "unit_kind": "observational"}}]},
            {"policy": "live-settlement"},
        ]
        for mutation in mutations:
            snapshot = MarketGraph().snapshot()
            snapshot.update(mutation)
            output = io.StringIO()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                write_csv(snapshot, output)
            self.assertEqual(output.getvalue(), "")

    def test_invalid_cli_input_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            source, destination = Path(directory) / "snapshot.json", Path(directory) / "paper.csv"
            source.write_text(json.dumps({"schema_version": 1, "policy": "observational_until_promote", "cards": [None], "bets": []}))
            destination.write_text("previous CSV remains intact")
            from contextlib import redirect_stderr
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                main(["export", str(source), str(destination)])
            self.assertEqual(raised.exception.code, 2)
            self.assertEqual(destination.read_text(), "previous CSV remains intact")

    def test_invalid_stakes_rejected_without_mutating_market(self):
        for value in (0, -1, float('nan'), float('inf'), True, '1'):
            graph = MarketGraph()
            with self.subTest(value=value), self.assertRaises(ValueError):
                graph.place_bet(BetEntry(actor_class='itself', subject_kind='model', subject_id='x', units=value))
            self.assertEqual(graph.bets, [])


if __name__ == '__main__':
    unittest.main()
