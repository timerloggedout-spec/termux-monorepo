import json
import unittest
from pathlib import Path

from scripts.pcdoe.shadow_prioritizer import evaluate_snapshot

ROOT = Path(__file__).resolve().parents[2]
CATALOG = json.loads((ROOT / "docs/ops/pcdoe/PRIORITIZATION-POLICIES.json").read_text())
SNAPSHOT = json.loads((ROOT / "tests/pcdoe/fixtures/shadow-snapshot.json").read_text())


class ShadowPrioritizerTests(unittest.TestCase):
    def test_all_six_treatments_return_recommendations_only(self):
        result = evaluate_snapshot(CATALOG, SNAPSHOT)
        self.assertEqual(len(result["policies"]), 6)
        self.assertTrue(result["recommendations_only"])
        self.assertEqual(result["side_effects"], [])
        for policy in result["policies"]:
            self.assertTrue(policy["recommendation_only"])
            self.assertEqual(len(policy["recommendations"]), 4)
            self.assertEqual(
                {item["task_id"] for item in policy["recommendations"]},
                {item["task_id"] for item in SNAPSHOT["tasks"]},
            )

    def test_policy_results_are_deterministic_for_frozen_snapshot(self):
        first = evaluate_snapshot(CATALOG, SNAPSHOT)
        second = evaluate_snapshot(CATALOG, SNAPSHOT)
        for left, right in zip(first["policies"], second["policies"]):
            self.assertEqual(
                [(x["task_id"], x["rank"], x["score"]) for x in left["recommendations"]],
                [(x["task_id"], x["rank"], x["score"]) for x in right["recommendations"]],
            )
            self.assertEqual(left["policy_sha256"], right["policy_sha256"])

    def test_unknown_and_high_risk_tasks_are_ineligible(self):
        result = evaluate_snapshot(CATALOG, SNAPSHOT)
        for policy in result["policies"]:
            rows = {item["task_id"]: item for item in policy["recommendations"]}
            self.assertFalse(rows["task-unknown-risk"]["eligible"])
            self.assertFalse(rows["task-high-risk"]["eligible"])
            self.assertIn("risk_unknown_or_above_snapshot_limit", rows["task-high-risk"]["eligibility_reason"])


    def test_catalog_weights_drive_policy_scores(self):
        policy = next(p for p in CATALOG["policies"] if p["treatment_type"] == "balanced")
        task = SNAPSHOT["tasks"][0]
        baseline = evaluate_snapshot({"policies": [policy]}, dict(SNAPSHOT, tasks=[task]))
        changed = json.loads(json.dumps(policy))
        changed["factors"][0]["weight"] = 0.9
        changed["factors"][1]["weight"] = 0.01
        changed["factors"][2]["weight"] = 0.01
        changed["factors"][3]["weight"] = 0.01
        changed["factors"][4]["weight"] = 0.01
        changed["factors"][5]["weight"] = 0.01
        altered = evaluate_snapshot({"policies": [changed]}, dict(SNAPSHOT, tasks=[task]))
        self.assertNotEqual(
            baseline["policies"][0]["recommendations"][0]["score"],
            altered["policies"][0]["recommendations"][0]["score"],
        )

    def test_unknown_factors_reduce_confidence_without_becoming_zero_inputs(self):
        result = evaluate_snapshot(CATALOG, SNAPSHOT)
        balanced = next(p for p in result["policies"] if p["policy_id"] == "priority-balanced")
        row = next(x for x in balanced["recommendations"] if x["task_id"] == "task-unknown-risk")
        self.assertIn("dependency_unlock", row["unknown_inputs"])
        self.assertIn("blocked_time_reduction", row["unknown_inputs"])
        self.assertLess(row["confidence"], 1.0)
        self.assertIsNone(row["components"]["dependency_unlock"])

    def test_all_missing_policy_factors_produce_unknown_score(self):
        task = {"task_id": "task-empty", "risk": 0.1}
        result = evaluate_snapshot(CATALOG, dict(SNAPSHOT, tasks=[task]))
        for policy in result["policies"]:
            if policy["policy_id"] != "priority-incumbent":
                self.assertIsNone(policy["recommendations"][0]["score"])
                self.assertEqual(policy["recommendations"][0]["confidence"], 0.0)

    def test_live_snapshot_mode_is_rejected(self):
        live = dict(SNAPSHOT, mode="live")
        with self.assertRaisesRegex(ValueError, "read_only_shadow"):
            evaluate_snapshot(CATALOG, live)

    def test_duplicate_task_ids_are_rejected(self):
        duplicate = dict(SNAPSHOT, tasks=SNAPSHOT["tasks"] + [dict(SNAPSHOT["tasks"][0])])
        with self.assertRaisesRegex(ValueError, "unique"):
            evaluate_snapshot(CATALOG, duplicate)


if __name__ == "__main__":
    unittest.main()
