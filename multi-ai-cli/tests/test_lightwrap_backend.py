from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backends.lightwrap import LightwrapBackend, LightwrapError  # noqa: E402


class LightwrapBackendTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.runner = Path(self.temp_dir.name) / "lightwrap.mjs"
        self.runner.write_text("// test runner placeholder\n", encoding="utf-8")
        self.backend = LightwrapBackend(
            provider="deepseek",
            account="primary",
            profile_root=Path(self.temp_dir.name) / "profiles",
            runner_path=self.runner,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _completed(self, payload: dict, returncode: int = 0):
        return Mock(returncode=returncode, stdout=json.dumps(payload) + "\n", stderr="")

    def test_capabilities_are_parsed_without_browser_output(self):
        payload = {
            "action": "capabilities",
            "provider": "deepseek",
            "allow_send_after_probe": True,
            "status": {"observed_state": "send-ready"},
        }
        with patch("backends.lightwrap.subprocess.run", return_value=self._completed(payload)) as runner:
            result = self.backend.capabilities()
            available = self.backend.is_available()
        self.assertEqual(result["provider"], "deepseek")
        self.assertTrue(available)
        self.assertIn("--action", runner.call_args.args[0])

    def test_send_returns_only_normalized_text(self):
        payload = {"action": "send", "provider": "deepseek", "observed_state": "completed", "text": "normalized reply"}
        with patch("backends.lightwrap.subprocess.run", return_value=self._completed(payload)):
            self.assertEqual(self.backend.send_message("test prompt", []), "normalized reply")

    def test_runner_error_is_raised_without_raw_output(self):
        payload = {"action": "probe", "provider": "deepseek", "observed_state": "error", "error": "selector drift"}
        with patch("backends.lightwrap.subprocess.run", return_value=self._completed(payload, returncode=2)):
            with self.assertRaisesRegex(LightwrapError, "selector drift"):
                self.backend.probe()

    def test_invalid_runner_output_is_rejected(self):
        completed = Mock(returncode=0, stdout="non-json diagnostic output\n", stderr="")
        with patch("backends.lightwrap.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(LightwrapError, "invalid normalized output"):
                self.backend.capabilities()


    def test_local_profile_configuration_is_non_secret_and_private(self):
        path = self.backend.configure_profile(
            url="https://example.invalid/chat",
            input_mode="textarea",
            input_selectors=("textarea#prompt",),
            submit_selectors=("button#send",),
            response_selectors=("article.answer:last-child",),
            ready_selectors=("textarea#prompt",),
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["state"], "probe-required")
        self.assertTrue(payload["allow_send_after_probe"])
        serialized = json.dumps(payload).lower()
        self.assertNotIn("cookie", serialized)
        self.assertNotIn("token", serialized)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
