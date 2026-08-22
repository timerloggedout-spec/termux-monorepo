from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / ".github" / "agentic" / "recon-intel-policy.json"
PROVIDER_LIBRARY_PATH = ROOT / ".github" / "agentic" / "provider-command-library.json"


class ReconIntelPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        cls.provider_library = json.loads(PROVIDER_LIBRARY_PATH.read_text(encoding="utf-8"))

    def test_declares_a_versioned_read_first_policy(self) -> None:
        self.assertEqual(1, self.policy["schema_version"])
        self.assertEqual("recon-intel-v1", self.policy["policy_version"])
        self.assertFalse(self.policy["discovery"]["allow_scheduled_repository_writes"])
        self.assertEqual(["master"], self.policy["discovery"]["allowed_gitlab_refs"])
        self.assertEqual(15, self.policy["discovery"]["active_pr_schedule_minutes"])

    def test_every_state_has_exactly_one_safe_lane_definition(self) -> None:
        states = self.policy["lease_states"]
        expected = {
            "aligned",
            "github-ahead",
            "gitlab-ahead",
            "diverged",
            "no-common-ancestor",
            "not-configured",
            "external-access-denied",
        }
        self.assertEqual(expected, set(states))
        for state, definition in states.items():
            self.assertIn(definition["lane"], {"github-primary", "gitlab-primary", "hold", "not-configured", "access-denied"}, state)
            self.assertIsInstance(definition["allow_corrective_write_platforms"], list, state)
            self.assertIsInstance(definition["allow_reconciliation_apply"], bool, state)

    def test_hold_and_unknown_states_disable_corrective_writes(self) -> None:
        states = self.policy["lease_states"]
        for state in ("diverged", "no-common-ancestor", "not-configured", "external-access-denied"):
            self.assertEqual([], states[state]["allow_corrective_write_platforms"], state)
            self.assertFalse(states[state]["allow_reconciliation_apply"], state)

    def test_only_gitlab_ahead_can_prepare_reconciliation(self) -> None:
        states = self.policy["lease_states"]
        eligible = {name for name, definition in states.items() if definition["allow_reconciliation_apply"]}
        self.assertEqual({"gitlab-ahead"}, eligible)

    def test_provider_policy_is_deny_by_default_and_matches_known_library_entries(self) -> None:
        providers = self.policy["providers"]
        self.assertEqual({"coderabbit", "jules", "gemini", "qodo", "devin"}, set(providers))
        for provider, definition in providers.items():
            self.assertTrue(definition["requires_current_lease_for_corrective_write"], provider)
            self.assertIsInstance(definition["review_platforms"], list, provider)
            self.assertIsInstance(definition["corrective_write_platforms"], list, provider)
            command_key = definition["provider_command_key"]
            if command_key is not None:
                self.assertIn(command_key, self.provider_library["providers"], provider)

    def test_only_coderabbit_has_a_policy_corrective_write_platform(self) -> None:
        providers = self.policy["providers"]
        allowed = {
            provider: definition["corrective_write_platforms"]
            for provider, definition in providers.items()
            if definition["corrective_write_platforms"]
        }
        self.assertEqual({"coderabbit": ["github"]}, allowed)

    def test_evidence_contract_requires_current_tuple_without_raw_review_content(self) -> None:
        evidence = self.policy["evidence"]
        self.assertTrue(evidence["require_current_github_head_sha"])
        self.assertTrue(evidence["require_policy_version"])
        self.assertTrue(evidence["require_gitlab_sha_for_lease"])
        self.assertTrue(evidence["review_messages_are_data_only"])
        self.assertTrue(evidence["provider_control_notices_are_not_review_evidence"])


if __name__ == "__main__":
    unittest.main()
