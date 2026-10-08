"""MLP-KEEP-006 recon ledger. Stdlib unittest. No network."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from ml.pipelines.recon.budget import disposition, over_advisory
from ml.pipelines.recon.catalog import CONTRACT_VERSION, RECORDED_TIP
from ml.pipelines.recon.peers import is_protected, is_staging_only, is_wholesale, retarget_allowed
from ml.pipelines.recon.receipt import build_receipt
from ml.pipelines.recon.sha import same_commit, tip_relation
from ml.pipelines.recon.version_audit import mismatch, package_version
from ml.pipelines.recon.vocab import assert_lane

ROOT = Path(__file__).resolve().parent

class TipTests(unittest.TestCase):
    def test_prefix_matches_full_sha(self) -> None:
        full = "8424a50c" + "ab" * 16
        self.assertTrue(same_commit("8424a50c", full))

    def test_recorded_tip_drifts_from_live_master(self) -> None:
        self.assertEqual(tip_relation(RECORDED_TIP, "000c9391ebdb4dec"), "drift")

    def test_short_prefix_is_not_a_match(self) -> None:
        self.assertFalse(same_commit("8424a5", "8424a50cdeadbeef"))

    def test_empty_is_not_a_match(self) -> None:
        self.assertFalse(same_commit("", "000c9391ebdb4dec"))

class VersionTests(unittest.TestCase):
    def test_version_file_is_contract(self) -> None:
        self.assertEqual(package_version(ROOT), CONTRACT_VERSION)

    def test_historical_hardcode_was_a_mismatch(self) -> None:
        self.assertTrue(mismatch("0.5.0", CONTRACT_VERSION))

    def test_init_now_tracks_the_file(self) -> None:
        from ml.pipelines import __version__
        self.assertEqual(__version__, package_version(ROOT))
        self.assertFalse(mismatch(__version__, CONTRACT_VERSION))

class PeerTests(unittest.TestCase):
    def test_minesweeper_peers_stay_protected(self) -> None:
        for number in (65, 630, 680, 884, 1151, 1169, 1171):
            self.assertTrue(is_protected(number), number)

    def test_wholesale_ml_family_blocked(self) -> None:
        for number in (432, 549, 601, 682, 746, 787, 817):
            self.assertTrue(is_wholesale(number), number)

    def test_staging_prs_are_not_retargeted_to_master(self) -> None:
        self.assertTrue(is_staging_only(48))
        self.assertTrue(is_staging_only(788))
        self.assertFalse(retarget_allowed(48, "master"))
        self.assertFalse(retarget_allowed(788, "master"))
        self.assertTrue(retarget_allowed(48, "master-staging"))

class BudgetTests(unittest.TestCase):
    def test_zero_files_supersede(self) -> None:
        self.assertEqual(disposition(0, bot=False), "SUPERSEDE")

    def test_bot_over_threshold_is_extract(self) -> None:
        self.assertEqual(disposition(41, bot=True), "EXTRACT")

    def test_human_slice_stays_candidate_even_near_the_window(self) -> None:
        self.assertEqual(disposition(90, bot=False), "CANDIDATE")
        self.assertFalse(over_advisory(90))
        self.assertTrue(over_advisory(101))

    def test_negative_rejected(self) -> None:
        with self.assertRaises(ValueError):
            disposition(-1, bot=False)

class VocabTests(unittest.TestCase):
    def test_invalid_parking_rejected(self) -> None:
        for lane in ("HOLD", "WAIT", "OBSERVE"):
            with self.assertRaises(ValueError):
                assert_lane(lane)

    def test_vocab_v2_accepted(self) -> None:
        for lane in ("EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"):
            self.assertEqual(assert_lane(lane), lane)

class ReceiptTests(unittest.TestCase):
    def test_receipt_records_drift_and_no_secrets(self) -> None:
        receipt = build_receipt(init_version="0.6.0")
        self.assertEqual(receipt["tip_relation"], "drift")
        self.assertEqual(receipt["live_master_class"], "sweep-receipt")
        self.assertFalse(receipt["live_matches_dual_gate"])
        self.assertEqual(receipt["dual_gate"]["repo-gate"], "success")
        self.assertEqual(receipt["dual_gate"]["termux-smoke"], "success")
        self.assertEqual(receipt["secrets"], "names-only")
        blob = json.dumps(receipt).lower()
        self.assertNotIn("ghp_", blob)
        self.assertNotIn("token", blob)
        lanes = {row["lane"] for row in receipt["next_actions"]}
        self.assertTrue(lanes <= {"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"})

    def test_fixture_is_not_a_session_snapshot(self) -> None:
        fixture = ROOT / "fixtures" / "recon_20261008.json"
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(payload["kind"], "mlp-keep-006-recon")
        self.assertFalse(fixture.name.startswith("session_"))

    def test_cli_registers_recon_without_importing_it(self) -> None:
        text = (ROOT / "cli.py").read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("recon")', text)
        self.assertIn("def cmd_recon", text)

if __name__ == "__main__":
    unittest.main()
