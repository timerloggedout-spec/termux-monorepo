#!/usr/bin/env python3
"""stdlib unittest for model_selection_market — no network."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.model_selection_market.bootstrap import bootstrap_equal_weights, load_static_free_seed
from scripts.model_selection_market.dspy_doe import DoeArm, DspyDoeStub
from scripts.model_selection_market.ledger import LedgerSample, PerformanceLedger
from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard
from scripts.model_selection_market.selector import SelectionMode, select_models


class TestBootstrap(unittest.TestCase):
    def test_equal_weights(self) -> None:
        t = bootstrap_equal_weights()
        self.assertEqual(t["policy"], "equal_weight_bootstrap")
        self.assertGreater(t["model_count"], 0)
        for role, models in t["roles"].items():
            for mid, meta in models.items():
                self.assertEqual(meta["weight"], 1.0)
                self.assertEqual(meta["confidence"], 0.0)
                self.assertTrue(meta["free"])

    def test_rejects_non_free(self) -> None:
        seed = load_static_free_seed()
        seed["paid/model"] = {"roles": ["triage"], "free": False}
        t = bootstrap_equal_weights(seed)
        self.assertIn("paid/model", t["skipped_non_free"])


class TestLedger(unittest.TestCase):
    def test_append_and_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "led.jsonl"
            L = PerformanceLedger(path)
            L.append(
                LedgerSample(
                    role="triage",
                    model_id="stealth/ox-alpha",
                    dimensions={"correctness_gate_pass": True},
                )
            )
            agg = L.aggregate()
            self.assertEqual(agg["sample_count"], 1)
            self.assertEqual(agg["aggregates"]["triage"]["stealth/ox-alpha"]["weight"], 1.0)
            self.assertEqual(agg["aggregates"]["triage"]["stealth/ox-alpha"]["weight_policy"], "observe_only_until_promote")


class TestSelector(unittest.TestCase):
    def test_series(self) -> None:
        r = select_models(role="triage", mode=SelectionMode.SERIES)
        self.assertEqual(r["mode"], "series")
        self.assertIsNotNone(r["chosen"])

    def test_parallel(self) -> None:
        r = select_models(role="review", mode="parallel", k=2)
        self.assertEqual(r["mode"], "parallel")
        self.assertLessEqual(len(r["chosen_set"]), 2)

    def test_concurrent(self) -> None:
        r = select_models(mode="concurrent")
        self.assertEqual(r["mode"], "concurrent")
        self.assertIn("triage", r["chosen_by_role"])


class TestDspy(unittest.TestCase):
    def test_arms(self) -> None:
        s = DspyDoeStub()
        s.run_arm(DoeArm(arm_id="A", signature="x"))
        self.assertTrue(s.cohort_summary()["not_default_router"] if False else s.cohort_summary()["policy"] == "consideration_only")

    def test_rejects_paid_arm(self) -> None:
        s = DspyDoeStub()
        with self.assertRaises(ValueError):
            s.run_arm(DoeArm(arm_id="X", signature="y", free_only=False))


class TestMarket(unittest.TestCase):
    def test_card_and_bet(self) -> None:
        g = MarketGraph()
        c = TradingCard(role="invoke", owner="gemma")
        d = g.add_card(c)
        self.assertIn("card_id", d)
        b = g.place_bet(
            BetEntry(actor_class="itself", subject_kind="model", subject_id="google/gemma-3-12b-it:free", role="invoke")
        )
        self.assertEqual(b["status"], "open")
        snap = g.snapshot()
        self.assertGreaterEqual(len(snap["edges"]), 2)


if __name__ == "__main__":
    unittest.main()
