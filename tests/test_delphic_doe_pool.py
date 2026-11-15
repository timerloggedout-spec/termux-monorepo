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


    def test_missing_context_evidence_is_not_a_match(self):
        bad = candidate("p1", "alpha")
        del bad["context_class"]
        result = build_candidate_packet(TASK, [bad])
        self.assertIsNone(result["selected"])
        self.assertIn("context_class_evidence_missing", result["excluded"][0]["reasons"])

    def test_malformed_tool_evidence_is_excluded_without_aborting(self):
        malformed = candidate("p1", "alpha", available_tools={"python": True})
        valid = candidate("p2", "beta")
        result = build_candidate_packet(TASK, [malformed, valid])
        self.assertEqual(result["selected"]["provider"], "beta")
        self.assertIn("available_tools_evidence_invalid", result["excluded"][0]["reasons"])

    def test_missing_or_invalid_ranking_evidence_is_not_zero_filled(self):
        missing = candidate("p1", "alpha")
        missing.pop("task_fit_score")
        invalid = candidate("p2", "beta", fit=float("nan"))
        result = build_candidate_packet(TASK, [missing, invalid])
        self.assertIsNone(result["selected"])
        reasons = [r for item in result["excluded"] for r in item["reasons"]]
        self.assertIn("task_fit_score_missing_or_invalid", reasons)

    def test_rotation_parameter_is_bound_into_digest_and_provenance(self):
        first = build_candidate_packet(TASK, [candidate()], previous_provider="alpha")
        second = build_candidate_packet(TASK, [candidate()], previous_provider="beta")
        self.assertNotEqual(first["input_digest"], second["input_digest"])
        self.assertEqual(first["selection_provenance"]["previous_provider"], "alpha")


    def test_empty_participant_identity_is_excluded(self):
        bad = candidate("p1", "alpha")
        bad["participant_id"] = ""
        result = build_candidate_packet(TASK, [bad])
        self.assertIsNone(result["selected"])
        self.assertIn("participant_identity_not_issued", result["excluded"][0]["reasons"])

    def test_malformed_task_action_class_is_rejected(self):
        with self.assertRaises(ValueError):
            build_candidate_packet({**TASK, "action_class": ["research"]}, [candidate()])

    def test_rotation_provenance_only_marks_an_equal_score_tiebreak(self):
        tied = build_candidate_packet(
            TASK, [candidate("p1", "alpha"), candidate("p2", "beta")],
            previous_provider="alpha",
        )
        higher = build_candidate_packet(
            TASK, [candidate("p1", "alpha", 0.5), candidate("p2", "beta", 0.95)],
            previous_provider="alpha",
        )
        self.assertTrue(tied["selection_provenance"]["rotation_applied"])
        self.assertFalse(higher["selection_provenance"]["rotation_applied"])

    def test_candidate_schema_declares_selection_provenance(self):
        from pathlib import Path
        schema = (Path(__file__).resolve().parents[1] /
                  "docs" / "schemas" / "delphic-doe-task-candidate.yaml").read_text()
        self.assertIn("selection_provenance", schema)
        self.assertIn("rotation_applied", schema)


if __name__ == "__main__":
    unittest.main()
