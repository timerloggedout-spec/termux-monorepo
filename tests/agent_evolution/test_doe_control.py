import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.agent_evolution.doe_control import (  # noqa: E402
    build_confirmation_assignment,
    build_policy_design,
    full_factorial_policy_specs,
    promotion_readiness,
    replay_design,
    validate_confirmation_assignment,
    validate_policy_design,
    _digest,
)
from scripts.agent_evolution.replay_simulator import (
    DiscoveryHistory, DiscoveryNode, ExplorationPolicy, ReplaySimulator,
)


class DoEControlTests(unittest.TestCase):
    def setUp(self):
        self.incumbent = ExplorationPolicy(max_active=2)
        self.factors = {
            "max_active": [1, 2, 4],
            "stop_after_terminal": [False, True],
        }

    def test_factorial_is_unique_and_retains_incumbent(self):
        specs = full_factorial_policy_specs(self.incumbent, self.factors)
        self.assertEqual(len(specs), 6)
        normalized = full_factorial_policy_specs(
            ExplorationPolicy(max_active=2, min_score=0), {"max_active": [2]}
        )
        self.assertEqual(sum(spec["min_score"] == 0.0 for spec in normalized), 1)
        self.assertIn(
            {"max_active": 2, "min_score": None, "stop_after_terminal": False},
            specs,
        )

    def test_design_has_one_incumbent_control(self):
        design = build_policy_design(
            self.incumbent, self.factors, campaign_id="evo-screen-1", seed=17,
        )
        self.assertEqual(sum(arm["role"] == "control" for arm in design["arms"]), 1)
        self.assertEqual(design["execution_plane"], "offline_replay")
        validate_policy_design(design)

    def test_design_rejects_duplicate_reconstructed_policy_identity(self):
        design = build_policy_design(
            ExplorationPolicy(max_active=2, min_score=0),
            {"max_active": [2, 3], "min_score": [0.0]},
            campaign_id="evo-identity-1", seed=19,
        )
        candidate = next(arm for arm in design["arms"] if arm["role"] == "candidate")
        duplicate = dict(candidate)
        duplicate["policy"] = dict(candidate["policy"], min_score=0)
        duplicate["arm_id"] = _digest(duplicate["policy"])
        design["arms"].append(duplicate)
        payload = {key: value for key, value in design.items() if key != "design_id"}
        design["design_id"] = _digest(payload, 40)
        with self.assertRaisesRegex(ValueError, "unique policy identities"):
            validate_policy_design(design)

    def test_design_is_reproducible(self):
        kwargs = dict(campaign_id="evo-screen-1", seed=17)
        first = build_policy_design(self.incumbent, self.factors, **kwargs)
        second = build_policy_design(self.incumbent, self.factors, **kwargs)
        self.assertEqual(first, second)

    def test_factor_validation(self):
        with self.assertRaises(ValueError):
            full_factorial_policy_specs(self.incumbent, {"unknown": [1, 2]})
        with self.assertRaises(ValueError):
            full_factorial_policy_specs(self.incumbent, {"max_active": [1, 1]})
        with self.assertRaises(ValueError):
            full_factorial_policy_specs(self.incumbent, {"max_active": ["2"]})

    def test_replay_uses_same_history_and_emits_lineage(self):
        history = DiscoveryHistory.from_nodes([
            DiscoveryNode("root", None, 1.0),
            DiscoveryNode("leaf", "root", 3.0, terminal=True),
        ])
        design = build_policy_design(
            self.incumbent, {"max_active": [1, 2]},
            campaign_id="evo-replay-1", seed=3,
        )
        rows = replay_design(design, ReplaySimulator(history))
        self.assertEqual(len(rows), len(design["arms"]))
        self.assertTrue(all(row["execution"] == "replay_only" for row in rows))
        self.assertEqual({row["history_nodes"] for row in rows}, {2})
        self.assertTrue(all(row["design_id"] == design["design_id"] for row in rows))

    def test_confirmation_assigns_only_control_and_selected_candidate(self):
        design = build_policy_design(
            self.incumbent, self.factors, campaign_id="evo-screen-1", seed=17,
        )
        candidate = next(a for a in design["arms"] if a["role"] == "candidate")
        kwargs = dict(
            task_blocks={"task-a": "family-a", "task-b": "family-b"},
            seed=23, replicates=2,
        )
        first = build_confirmation_assignment(design, candidate["arm_id"], **kwargs)
        second = build_confirmation_assignment(design, candidate["arm_id"], **kwargs)
        self.assertEqual(first, second)
        assigned = {row["arm_id"] for row in first["assignments"]}
        self.assertEqual(assigned, {design["control_arm_id"], candidate["arm_id"]})
        self.assertEqual(len(first["assignments"]), 2 * 2 * 2)
        validate_confirmation_assignment(first, design)

    def test_confirmation_rejects_incomplete_assignment(self):
        design = build_policy_design(
            self.incumbent, self.factors, campaign_id="evo-screen-1", seed=17,
        )
        candidate = next(a for a in design["arms"] if a["role"] == "candidate")
        confirmation = build_confirmation_assignment(
            design, candidate["arm_id"],
            task_blocks={"task-a": "family-a"}, seed=23,
        )
        broken = dict(confirmation)
        broken["assignments"] = list(confirmation["assignments"][:-1])
        payload = {key: value for key, value in broken.items() if key != "confirmation_id"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        broken["confirmation_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]
        with self.assertRaisesRegex(ValueError, "requires control and candidate"):
            validate_confirmation_assignment(broken, design)

    def test_confirmation_rejects_stale_hash(self):
        design = build_policy_design(
            self.incumbent, self.factors, campaign_id="evo-screen-1", seed=17,
        )
        candidate = next(a for a in design["arms"] if a["role"] == "candidate")
        confirmation = build_confirmation_assignment(
            design, candidate["arm_id"], task_blocks={"task-a": "family-a"}, seed=23,
        )
        confirmation["campaign_id"] = "other-campaign"
        with self.assertRaisesRegex(ValueError, "confirmation_id"):
            validate_confirmation_assignment(confirmation, design)
        payload = {key: value for key, value in confirmation.items() if key != "confirmation_id"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        confirmation["confirmation_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]
        with self.assertRaisesRegex(ValueError, "campaign differs"):
            validate_confirmation_assignment(confirmation, design)

    def test_confirmation_rejects_invalid_replicates_and_empty_blocks(self):
        design = build_policy_design(
            self.incumbent, self.factors, campaign_id="evo-screen-1", seed=17,
        )
        candidate = next(a for a in design["arms"] if a["role"] == "candidate")
        confirmation = build_confirmation_assignment(
            design, candidate["arm_id"], task_blocks={"task-a": "family-a"}, seed=23,
        )
        for value in (True, 0, 1.5, "2"):
            broken = dict(confirmation, replicates=value)
            payload = {key: item for key, item in broken.items() if key != "confirmation_id"}
            canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
            broken["confirmation_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]
            with self.assertRaisesRegex(ValueError, "replicates"):
                validate_confirmation_assignment(broken, design)
        broken = dict(confirmation, task_blocks={})
        payload = {key: item for key, item in broken.items() if key != "confirmation_id"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        broken["confirmation_id"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:40]
        with self.assertRaisesRegex(ValueError, "task_blocks"):
            validate_confirmation_assignment(broken, design)

    def test_promotion_readiness_fails_closed(self):
        receipt = promotion_readiness(
            replay_gain=0.2, minimum_gain=0.1,
            held_out_confirmation_passed=True, task_outcome_verified=True,
            correctness_passed=True, integration_passed=True,
            repo_gate_passed=True, termux_smoke_passed=False,
        )
        self.assertFalse(receipt["ready_for_proposal_review"])
        self.assertEqual(
            receipt["promotion_action"], "external_proposal_and_dual_gate_only"
        )


if __name__ == "__main__":
    unittest.main()
