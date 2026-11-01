#!/usr/bin/env python3
"""Contract tests for the Gemini Interactions adapter (no network calls)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "server" / "gemini_interactions.py"
SPEC = importlib.util.spec_from_file_location("gemini_interactions", MODULE)
assert SPEC and SPEC.loader
gemini_interactions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gemini_interactions)


class GeminiInteractionsContractTests(unittest.TestCase):
    def test_build_payload_uses_interactions_shape(self) -> None:
        payload = gemini_interactions.build_payload({
            "model": "gemini-interactions/gemini-flash-latest",
            "messages": [
                {"role": "system", "content": "You are a reviewer."},
                {"role": "user", "content": "Review this change."},
            ],
            "store": True,
            "previous_interaction_id": "previous-123",
            "max_tokens": 512,
            "thinking_level": "low",
            "labels": {"lane": "review"},
        })

        self.assertEqual(payload["model"], "gemini-flash-latest")
        self.assertEqual(payload["previous_interaction_id"], "previous-123")
        self.assertTrue(payload["store"])
        self.assertEqual(payload["generation_config"]["max_output_tokens"], 512)
        self.assertEqual(payload["generation_config"]["thinking_level"], "low")
        self.assertEqual(payload["system_instruction"], "You are a reviewer.")
        self.assertEqual(payload["labels"], {"lane": "review"})
        self.assertEqual(payload["input"][0]["type"], "user_input")

    def test_previous_interaction_requires_storage(self) -> None:
        with self.assertRaises(ValueError):
            gemini_interactions.build_payload({
                "messages": [{"role": "user", "content": "continue"}],
                "store": False,
                "previous_interaction_id": "previous-123",
            })

    def test_normalize_response_preserves_interaction_identity_and_usage(self) -> None:
        response = gemini_interactions.normalize_response({
            "id": "interaction-123",
            "object": "interaction",
            "status": "completed",
            "steps": [{
                "type": "model_output",
                "content": [{"type": "text", "text": "hello"}],
            }],
            "usage": {
                "total_input_tokens": 11,
                "total_output_tokens": 7,
                "total_tokens": 18,
            },
        }, "gemini-interactions/gemini-flash-latest")

        self.assertEqual(response["choices"][0]["message"]["content"], "hello")
        self.assertEqual(response["usage"]["total_tokens"], 18)
        self.assertEqual(
            response["provider_metadata"]["interaction_id"],
            "interaction-123",
        )


if __name__ == "__main__":
    unittest.main()
