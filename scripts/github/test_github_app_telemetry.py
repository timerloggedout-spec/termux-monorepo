#!/usr/bin/env python3
"""Unit tests for GitHub App fleet telemetry."""
import json
import pathlib
import unittest
from unittest.mock import patch
from github_app_telemetry import build_telemetry

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = json.loads((ROOT / "ops/github-apps/registry.json").read_text())


class TelemetryTests(unittest.TestCase):
    def test_registry_is_declaration_not_live_proof(self):
        app = build_telemetry(REGISTRY)["apps"][0]
        self.assertEqual(app["slug"], "termux-fleet-collector")
        self.assertEqual(app["evidence"]["live_permissions"], "not_observed")
        self.assertEqual(app["evidence"]["live_installation"], "not_observed")

    def test_duplicate_slug_is_rejected(self):
        registry = dict(REGISTRY)
        registry["apps"] = REGISTRY["apps"] + [dict(REGISTRY["apps"][0])]
        with self.assertRaisesRegex(ValueError, "unique"):
            build_telemetry(registry)

    def test_invalid_permission_value_is_rejected(self):
        registry = json.loads(json.dumps(REGISTRY))
        registry["apps"][0]["declared_permissions"]["contents"] = "owner"
        with self.assertRaisesRegex(ValueError, "invalid declared permission"):
            build_telemetry(registry)

    @patch("github_app_telemetry.request_json")
    def test_live_probe_is_redacted(self, request_json):
        request_json.side_effect = [
            (200, {"resources": {"core": {"limit": 5000, "remaining": 4999, "reset": 123}}}),
            (200, {"repositories": [{"full_name": "timerloggedout-spec/termux-monorepo"}]}),
        ]
        result = build_telemetry(REGISTRY, token="ephemeral-test-value")
        app = result["apps"][0]
        self.assertEqual(app["evidence"]["rate_limit"], "observed")
        self.assertEqual(app["evidence"]["repository_scope"], "observed")
        self.assertEqual(app["rate_limit"]["remaining"], 4999)
        self.assertNotIn("ephemeral-test-value", json.dumps(result))

    @patch("github_app_telemetry.request_json")
    def test_failed_probe_is_not_success(self, request_json):
        request_json.side_effect = [(403, {}), (403, {})]
        app = build_telemetry(REGISTRY, token="ephemeral-value")["apps"][0]
        self.assertEqual(app["evidence"]["rate_limit"], "probe_failed_http_403")
        self.assertEqual(app["evidence"]["repository_scope"], "probe_failed_http_403")
        self.assertNotIn("observed_repository_scope", app)


if __name__ == "__main__":
    unittest.main()
