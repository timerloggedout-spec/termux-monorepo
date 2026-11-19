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
