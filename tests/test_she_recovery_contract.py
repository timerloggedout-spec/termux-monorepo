"""Regression guard for the master-alignment recovery of SHE P0.8-P0.13."""
from __future__ import annotations

from unittest import TestCase

import she
from she import Attestation, EvidenceLedger, EvolutionPlan, LearningRecord, PromotionDecision, ReplayVerdict
from she.verify import DUAL_GATES


class SHERecoveryContractTests(TestCase):
    def test_public_api_contains_recovered_layers(self) -> None:
        for symbol in (
            Attestation,
            EvidenceLedger,
            EvolutionPlan,
            LearningRecord,
            PromotionDecision,
            ReplayVerdict,
        ):
            self.assertIsNotNone(symbol)
        self.assertEqual(she.__version__, "0.14.0")

    def test_dual_gate_invariant_remains_public(self) -> None:
        self.assertEqual(DUAL_GATES, {"repo-gate", "termux-smoke"})

    def test_recovered_planners_are_observer_only(self) -> None:
        self.assertFalse(she.live_learn_enabled())
        self.assertFalse(she.live_evolve_enabled())
        self.assertFalse(she.live_promote_enabled())
        self.assertFalse(she.live_ledger_enabled())
        self.assertFalse(she.live_attest_enabled())
        self.assertFalse(she.live_replay_enabled())


if __name__ == "__main__":
    import unittest

    unittest.main()
