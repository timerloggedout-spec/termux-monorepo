#!/usr/bin/env python3
"""Unit tests for GitHub App fleet telemetry."""
import json
import pathlib
import unittest
from unittest.mock import patch

from github_app_telemetry import ROOT, build_telemetry

REGISTRY = json.loads((ROOT / "ops/github-apps/registry.json").read_text())


class TelemetryTests(unittest.TestCase):
    def test_registry_permissions_are_derived_from_manifest_ssot(self):
        app = build_telemetry(REGISTRY)["apps"][0]
        manifest = json.loads((ROOT / REGISTRY["apps"][0]["manifest_path"]).read_text())
        self.assertEqual(app["declared_permissions"], manifest["default_permissions"])
        self.assertEqual(app["declared_events"], manifest["default_events"])
        self.assertEqual(app["evidence"]["manifest"], "checked_in_declaration")
        self.assertEqual(app["evidence"]["live_permissions"], "not_observed")

    def test_registry_contains_four_non_provisioned_role_slots(self):
        result = build_telemetry(REGISTRY)
        self.assertEqual(len(result["planned_roles"]), 4)
        self.assertTrue(all(
            role["status"] == "owner_reported_in_flight_unverified"
            for role in result["planned_roles"]
        ))
        self.assertEqual(len(result["apps"]), 1)

    def test_duplicate_slug_is_rejected(self):
        registry = dict(REGISTRY)
        registry["apps"] = REGISTRY["apps"] + [dict(REGISTRY["apps"][0])]
        with self.assertRaisesRegex(ValueError, "unique"):
            build_telemetry(registry)

    def test_manifest_permission_values_are_validated(self):
        with patch("github_app_telemetry._load_manifest",
                   side_effect=ValueError("termux-fleet-collector: invalid manifest permission value")):
            with self.assertRaisesRegex(ValueError, "invalid manifest permission"):
                build_telemetry(REGISTRY)

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
