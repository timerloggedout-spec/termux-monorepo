"""Regressions from independent code review of the paper accounting slice."""
import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from scripts.model_selection_market import accounting
from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard

PROV = {"issuer": "fixture", "source": "synthetic", "reference": "review"}


class TestReviewRegressions(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "market.jsonl"
        self.graph = MarketGraph(event_path=self.path)
        self.graph.open_account("alice", event_id="open", provenance=PROV)

    def test_ephemeral_mutations_preserve_observational_bets_and_offers(self):
        graph = MarketGraph()
        card = TradingCard(role="review", owner="alice")
        graph.add_card(card)
        card.offer_trade("bob")
        graph.cards[card.card_id()]["trade_log"] = card.trade_log
        graph.place_bet(BetEntry(actor_class="others", subject_kind="model", subject_id="legacy"))
        graph.open_account("alice", event_id="open", provenance=PROV)
        graph.issue_points("alice", 5, event_id="issue", provenance=PROV)
        snapshot = graph.snapshot()
        self.assertEqual(len(snapshot["bets"]), 1)
        self.assertEqual(snapshot["cards"][0]["trade_log"][0]["to"], "bob")

    def test_snapshots_keep_writer_locked_through_projection(self):
        for method in (self.graph.snapshot, self.graph.accounting_snapshot):
            started, completed = threading.Event(), threading.Event()
            failures = []
            def write():
                started.set()
                try:
                    self.graph.issue_points("alice", 1, event_id="writer-" + method.__name__, provenance=PROV)
                except BaseException as exc:
                    failures.append(exc)
                finally:
                    completed.set()
            writer = threading.Thread(target=write)
            original = self.graph._accounting_view
            def project():
                writer.start()
                self.assertTrue(started.wait(2))
                self.assertFalse(completed.wait(0.03), "writer interleaved with projection")
                return original()
            try:
                with mock.patch.object(self.graph, "_accounting_view", side_effect=project):
                    method()
            finally:
                writer.join(3)
            self.assertFalse(writer.is_alive())
            self.assertFalse(failures)
            self.assertTrue(completed.is_set())

    def test_retry_reestablishes_durability_after_uncertain_fsync(self):
        real_sync = accounting.os.fsync
        with mock.patch.object(accounting.os, "fsync", side_effect=OSError("uncertain sync")):
            with self.assertRaises(OSError):
                self.graph.issue_points("alice", 5, event_id="issue", provenance=PROV)
        with mock.patch.object(accounting.os, "fsync", wraps=real_sync) as sync:
            self.graph.issue_points("alice", 5, event_id="issue", provenance=PROV)
            self.assertGreaterEqual(sync.call_count, 2)
        self.assertEqual(self.graph.accounting_snapshot()["accounts"][0]["balance"], 5)

    def test_replay_rejects_forged_identity_and_unfunded_paper_bet_event(self):
        self.graph.issue_points("alice", 5, event_id="issue", provenance=PROV)
        self.graph.reserve_bet(BetEntry(actor_class="itself", subject_kind="model", subject_id="m",
                                       actor_id="alice", unit_kind="paper_point", units=2),
                               event_id="reserve", reservation_id="r")
        events = [json.loads(line) for line in self.path.read_text().splitlines()]
        for corruption in ("identity", "empty", "paper-without-reserve"):
            modified = copy.deepcopy(events)
            if corruption == "identity":
                modified[-1]["payload"]["bet"]["entry_id"] = "forged"
                modified[-1]["payload"]["reservation"]["entry_id"] = "forged"
            elif corruption == "empty":
                modified[-1]["payload"] = {"reservation": {}}
            else:
                modified[-1]["type"] = "bet"
                modified[-1]["payload"] = {"bet": modified[-1]["payload"]["bet"]}
            self.path.write_text("".join(accounting.canonical(event) + "\n" for event in modified))
            with self.subTest(corruption=corruption), self.assertRaises(ValueError):
                MarketGraph(event_path=self.path)


if __name__ == "__main__":
    unittest.main()
