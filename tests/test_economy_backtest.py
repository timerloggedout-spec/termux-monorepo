"""Deterministic economy backtest contract tests."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.model_selection_market.economy_backtest import (
    run_backtest, run_matrix, write_immutable,
)


def manifest(seed=41):
    return {
        "schema_version": 1,
        "scenario_id": "fixture-economy",
        "seed": seed,
        "horizon_rounds": 4,
        "reward_units": 10,
        "participants": [
            {"participant_id": "a-origin", "success_probability_bps": 0,
             "initial_balance": 11, "origin_id": None},
            {"participant_id": "b-derivative", "success_probability_bps": 10000,
             "initial_balance": 3, "origin_id": "a-origin"},
            {"participant_id": "c-worker", "success_probability_bps": 7500,
             "initial_balance": 5, "origin_id": None},
        ],
        "policy": {
            "policy_id": "baseline", "cull_after_misses": 1,
            "pool_distribution_bps": 5000, "royalty_rate_bps": 2500,
        },
    }


class EconomyBacktestTests(unittest.TestCase):
    def test_replay_is_byte_deterministic_for_same_manifest(self):
        first = run_backtest(manifest())
        second = run_backtest(manifest())
        self.assertEqual(first, second)
        self.assertEqual(first["result"]["result_digest"], second["result"]["result_digest"])

    def test_cull_keeps_origin_royalty_payable_separate_from_pool(self):
        result = run_backtest(manifest())["result"]
        metrics = result["metrics"]
        self.assertEqual(metrics["culled_participants"], 1)
        self.assertGreater(metrics["pool_inflow_units"], 0)
        self.assertGreater(metrics["royalty_payable_units"], 0)
        self.assertEqual(result["royalty_payable_by_origin"]["a-origin"], 8)
        self.assertEqual(metrics["conservation_residual_units"], 0)
        cull = next(event for event in result["events"] if event["type"] == "cull")
        self.assertEqual(cull["payload"]["culled_participant"], "a-origin")
        self.assertEqual(cull["payload"]["pool_destination"], "promotions-incentives-bonuses")

    def test_run_identity_binds_exact_implementation_commit(self):
        first = run_backtest(manifest(), code_commit_sha="a" * 40)
        second = run_backtest(manifest(), code_commit_sha="b" * 40)
        self.assertNotEqual(first["result"]["run_id"], second["result"]["run_id"])
        self.assertEqual(first["result"]["implementation_commit"], "a" * 40)

    def test_pool_distribution_conserves_units(self):
        result = run_backtest(manifest())["result"]
        metrics = result["metrics"]
        self.assertGreater(metrics["pool_distributed_units"], 0)
        self.assertGreaterEqual(metrics["pool_remainder_units"], 0)
        self.assertEqual(
            metrics["initial_units"] + metrics["issued_units"],
            metrics["participant_balance_units"]
            + metrics["pool_remainder_units"]
            + metrics["royalty_payable_units"],
        )

    def test_matrix_compares_policy_variants_over_same_seed_set(self):
        base = manifest()
        policies = [
            {"policy_id": "baseline-0bp", "cull_after_misses": 1,
             "pool_distribution_bps": 5000, "royalty_rate_bps": 0},
            {"policy_id": "royalty-250bp", "cull_after_misses": 1,
             "pool_distribution_bps": 5000, "royalty_rate_bps": 250},
            {"policy_id": "royalty-500bp", "cull_after_misses": 2,
             "pool_distribution_bps": 7500, "royalty_rate_bps": 500},
        ]
        first = run_matrix(base, policies, [11, 22, 33])
        second = run_matrix(base, policies, [11, 22, 33])
        self.assertEqual(first, second)
        self.assertEqual(len(first["runs"]), 9)
        self.assertEqual(first["summary"]["baseline-0bp"]["replications"], 3)
        self.assertIn("confidence_intervals_95", first["summary"]["baseline-0bp"])
        self.assertEqual(
            first["runs"][0]["run_manifest"]["source"]["digest"],
            first["runs"][1]["run_manifest"]["source"]["digest"],
        )
        self.assertEqual(first["verdict"], "exploratory_synthetic")

    def test_matrix_rejects_duplicate_policy_ids_and_seeds(self):
        policies = [dict(manifest()["policy"]), dict(manifest()["policy"])]
        with self.assertRaises(ValueError):
            run_matrix(manifest(), policies, [1, 2])
        with self.assertRaises(ValueError):
            run_matrix(manifest(), [manifest()["policy"]], [1, 1])

    def test_manifest_rejects_duplicate_participants_and_bool_amounts(self):
        value = manifest()
        value["participants"].append(dict(value["participants"][0]))
        with self.assertRaises(ValueError):
            run_backtest(value)
        value = manifest()
        value["reward_units"] = True
        with self.assertRaises(ValueError):
            run_backtest(value)

    def test_immutable_artifact_store_accepts_identical_and_rejects_changed_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            write_immutable(path, {"run_id": "one", "value": 1})
            write_immutable(path, {"run_id": "one", "value": 1})
            with self.assertRaises(ValueError):
                write_immutable(path, {"run_id": "one", "value": 2})
            self.assertEqual(json.loads(path.read_text()), {"run_id": "one", "value": 1})


if __name__ == "__main__":
    unittest.main()
