from __future__ import annotations

import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.provider_checklist import (  # noqa: E402
    enqueue,
    initial_state,
    load_state,
    next_provider,
    save_state,
    select,
    transition,
)
from core.provider_registry import all_providers, get_provider  # noqa: E402


class ProviderRegistryTests(unittest.TestCase):
    def test_catalog_is_curated_and_non_secret(self):
        catalog = all_providers()
        self.assertEqual(
            [provider.provider_id for provider in catalog],
            ["deepseek", "mistral", "gemini", "claude", "colab"],
        )
        for provider in catalog:
            descriptor_keys = set(provider.__dict__)
            self.assertFalse(
                descriptor_keys & {"cookie", "cookies", "token", "tokens", "session_id", "authorization", "waf"}
            )
            self.assertNotIn("=", provider.manual_command or "")
        self.assertEqual(get_provider("DeepSeek").provider_id, "deepseek")


class ProviderChecklistTests(unittest.TestCase):
    def test_selection_skip_and_retry_preserve_order(self):
        payload = initial_state()
        select(payload, ("mistral", "deepseek", "claude"))
        self.assertEqual(payload["selected"], ["mistral", "deepseek", "claude"])

        transition(payload, "mistral", "skipped", reason="Later")
        self.assertEqual(payload["providers"]["mistral"]["state"], "skipped")
        self.assertEqual(next_provider(payload)["provider_id"], "deepseek")

        enqueue(payload, "mistral")
        self.assertEqual(payload["providers"]["mistral"]["state"], "selected")
        self.assertEqual(payload["selected"], ["mistral", "deepseek", "claude"])

    def test_account_route_and_completion_are_resumable(self):
        payload = initial_state()
        select(payload, ("deepseek",))
        transition(payload, "deepseek", "needs_account")
        self.assertEqual(next_provider(payload)["state"], "needs_account")

        enqueue(payload, "deepseek")
        transition(payload, "deepseek", "connecting", account="primary")
        transition(payload, "deepseek", "connected")
        entry = payload["providers"]["deepseek"]
        self.assertEqual(entry["account"], "primary")
        self.assertEqual(entry["attempts"], 1)
        self.assertEqual(entry["state"], "connected")

    def test_invalid_transition_is_rejected(self):
        payload = initial_state()
        with self.assertRaisesRegex(ValueError, "Cannot transition"):
            transition(payload, "deepseek", "connected")

    def test_non_secret_state_is_persisted_with_restrictive_permissions(self):
        payload = initial_state()
        select(payload, ("deepseek", "mistral"))
        transition(payload, "deepseek", "connecting", account="primary")
        transition(payload, "deepseek", "connected")

        with tempfile.TemporaryDirectory() as temp_dir:
            path = save_state(payload, temp_dir)
            raw = path.read_text(encoding="utf-8").lower()
            for prohibited in ("cookie", "token", "session_id", "authorization", "waf"):
                self.assertNotIn(prohibited, raw)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            loaded = load_state(temp_dir)
            self.assertEqual(loaded["providers"]["deepseek"]["state"], "connected")
            self.assertEqual(loaded["providers"]["deepseek"]["account"], "primary")


if __name__ == "__main__":
    unittest.main()
