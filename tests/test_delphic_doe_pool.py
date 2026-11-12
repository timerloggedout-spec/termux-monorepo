import unittest

from scripts.delphic_doe_pool import build_candidate_packet


def candidate(pid="p1", provider="alpha", fit=0.9, reliability=0.8, **overrides):
    row = {
        "participant_id": pid,
        "instance": {
            "provider": provider, "model": "model-x@1", "endpoint": "https://example.invalid",
            "protocol": "https-json", "account_scope": "participant:p1",
            "system_prompt_sha256": "a" * 64, "tools_sha256": "b" * 64,
            "role": "researcher", "moniker": pid, "context": "doe",
            "instance_key": (provider[0] * 64),
        },
        "route_verified": True, "health": "healthy", "capacity": "available",
        "quota_state": "available", "quota_class": "free",
        "action_classes": ["research"], "available_tools": ["python"],
        "context_class": "public", "task_fit_score": fit,
        "verified_reliability": reliability,
    }
    row.update(overrides)
    return row


TASK = {"task_id": "task-1", "action_class": "research",
        "required_tools": ["python"], "context_class": "public"}


class CandidatePacketTests(unittest.TestCase):
    def test_selects_best_configured_instance_and_is_read_only(self):
        result = build_candidate_packet(TASK, [candidate(), candidate("p2", "beta", 0.95, 0.7)])
        self.assertEqual(result["selected"]["provider"], "beta")
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["wallet_mutation_authorized"])
        self.assertEqual(len(result["input_digest"]), 64)

    def test_quota_terminal_and_unissued_identity_are_excluded(self):
        dead = candidate("p1", "alpha", quota_state="terminal")
        unissued = candidate("p2", "beta")
        unissued["participant_id"] = None
        result = build_candidate_packet(TASK, [dead, unissued])
        self.assertIsNone(result["selected"])
        self.assertEqual(result["status"], "HELD_NO_ELIGIBLE_INSTANCE")
        self.assertEqual(len(result["excluded"]), 2)

    def test_previous_provider_is_deprioritized_on_equal_score(self):
        result = build_candidate_packet(TASK, [candidate(), candidate("p2", "beta")],
                                        previous_provider="alpha")
        self.assertEqual(result["selected"]["provider"], "beta")

    def test_context_and_tools_are_hard_gates(self):
        bad = candidate("p1", "alpha", context_class="restricted", available_tools=[])
        result = build_candidate_packet(TASK, [bad])
        self.assertIsNone(result["selected"])
        self.assertIn("context_class_mismatch", result["excluded"][0]["reasons"])
        self.assertIn("required_tools_unavailable", result["excluded"][0]["reasons"])

    def test_missing_task_identity_rejected(self):
        with self.assertRaises(ValueError):
            build_candidate_packet({}, [])


if __name__ == "__main__":
    unittest.main()
