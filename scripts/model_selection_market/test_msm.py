#!/usr/bin/env python3
"""stdlib unittest for model_selection_market — no network."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.model_selection_market.bootstrap import bootstrap_equal_weights, load_static_free_seed
from scripts.model_selection_market.catalog_join import join_catalog, normalize_catalog_models
from scripts.model_selection_market.dspy_doe import DoeArm, DspyDoeStub
from scripts.model_selection_market.ledger import LedgerSample, PerformanceLedger
from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard
from scripts.model_selection_market.router_peer import observe_peers_for_role, peers_as_router_pairs
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
        self.assertEqual(s.cohort_summary()["policy"], "consideration_only")

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


class TestCatalogJoin(unittest.TestCase):
    def test_normalize_ids_envelope(self) -> None:
        raw = {"ids": ["stealth/ox-alpha", "paid/model"], "models": [{"id": "qwen/qwen3-coder:free"}]}
        m = normalize_catalog_models(raw)
        self.assertIn("stealth/ox-alpha", m)
        self.assertIn("qwen/qwen3-coder:free", m)
        self.assertNotIn("paid/model", m)  # no :free / zero meta

    def test_join_static_and_dict(self) -> None:
        t = join_catalog(
            catalog_dict={"ids": ["nvidia/nemotron-nano-9b-v2:free"]},
            include_or_snapshot=False,
        )
        self.assertTrue(t["join"]["observe_only"])
        self.assertFalse(t["join"]["weight_promote"])
        self.assertGreaterEqual(t["join"]["joined_count"], 1)
        # all weights still 1.0
        for models in t["roles"].values():
            for meta in models.values():
                self.assertEqual(meta["weight"], 1.0)

    def test_rejects_paid_in_join(self) -> None:
        t = join_catalog(
            catalog_dict={"models": {"openai/gpt-paid": {"free": False, "roles": ["triage"]}}},
            include_static=False,
            include_or_snapshot=False,
        )
        self.assertEqual(t["join"]["joined_count"], 0)


class TestRouterPeer(unittest.TestCase):
    def test_observe_peers(self) -> None:
        obs = observe_peers_for_role(role="triage", k=3)
        self.assertEqual(obs["policy"], "observe_only")
        self.assertFalse(obs["weight_promote"])
        self.assertGreaterEqual(len(obs["peers"]), 1)
        for p in obs["peers"]:
            self.assertEqual(p["weight"], 1.0)
            self.assertEqual(p["weight_policy"], "observe_only_until_promote")

    def test_pairs_shape(self) -> None:
        obs = observe_peers_for_role(role="review", k=2)
        pairs = peers_as_router_pairs(obs)
        self.assertIsInstance(pairs, list)
        if pairs:
            self.assertEqual(len(pairs[0]), 2)

    def test_ledger_overlay_still_observe(self) -> None:
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
            obs = observe_peers_for_role(role="triage", ledger_path=path, k=5)
            self.assertFalse(obs["weight_promote"])
            # promote_eligible may be False (n=1 < 2)
            for p in obs["peers"]:
                self.assertEqual(p["weight"], 1.0)


if __name__ == "__main__":
    unittest.main()
