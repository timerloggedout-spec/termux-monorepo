#!/usr/bin/env python3
"""Unit tests for GitHub App fleet telemetry."""
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import github_app_telemetry as telemetry
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
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            manifest = root / "invalid-manifest.json"
            manifest.write_text(json.dumps({
                "default_permissions": {"contents": "superuser"},
                "default_events": [],
            }), encoding="utf-8")
            registry = dict(REGISTRY)
            registry["apps"] = [dict(REGISTRY["apps"][0], manifest_path="invalid-manifest.json")]
            with patch.object(telemetry, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "invalid manifest permission value"):
                    build_telemetry(registry)

    def test_missing_manifest_declaration_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "incomplete.json").write_text(
                json.dumps({"default_permissions": {}}), encoding="utf-8"
            )
            registry = dict(REGISTRY)
            registry["apps"] = [dict(REGISTRY["apps"][0], manifest_path="incomplete.json")]
            with patch.object(telemetry, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "must declare"):
                    build_telemetry(registry)

    @patch("github_app_telemetry.request_json")
    def test_live_probe_is_redacted(self, request_json):
        request_json.side_effect = [
            (200, {"resources": {"core": {"limit": 5000, "remaining": 4999, "reset": 123}}}, {}),
            (200, {"repositories": [{"full_name": "timerloggedout-spec/termux-monorepo"}]}, {}),
        ]
        result = build_telemetry(
            REGISTRY, token="ephemeral-test-value", probe_app_slug="termux-fleet-collector"
        )
        app = result["apps"][0]
        self.assertEqual(app["evidence"]["rate_limit"], "observed")
        self.assertEqual(app["evidence"]["repository_scope"], "observed")
        self.assertEqual(app["rate_limit"]["remaining"], 4999)
        self.assertNotIn("ephemeral-test-value", json.dumps(result))

    @patch("github_app_telemetry.request_json")
    def test_failed_probe_is_not_success(self, request_json):
        request_json.side_effect = [(403, {}, {}), (403, {}, {})]
        app = build_telemetry(
            REGISTRY, token="ephemeral-value", probe_app_slug="termux-fleet-collector"
        )["apps"][0]
        self.assertEqual(app["evidence"]["rate_limit"], "probe_failed_http_403")
        self.assertEqual(app["evidence"]["repository_scope"], "probe_failed_http_403")
        self.assertNotIn("observed_repository_scope", app)

    @patch("github_app_telemetry.request_json")
    def test_repository_scope_paginates_all_pages(self, request_json):
        request_json.side_effect = [
            (200, {"repositories": [{"full_name": "org/one"}]},
             {"Link": '<https://api.github.com/installation/repositories?per_page=100&page=2>; rel="next"'}),
            (200, {"repositories": [{"full_name": "org/two"}]}, {}),
        ]
        status, repos = telemetry._installation_repositories("ephemeral")
        self.assertEqual(status, 200)
        self.assertEqual(repos, ["org/one", "org/two"])
        self.assertEqual(request_json.call_count, 2)

    @patch("github_app_telemetry.request_json")
    def test_partial_repository_scope_is_not_observed(self, request_json):
        request_json.side_effect = [
            (200, {"repositories": [{"full_name": "org/one"}]},
             {"Link": '<https://api.github.com/installation/repositories?per_page=100&page=2>; rel="next"'}),
            (403, {}, {}),
        ]
        status, repos = telemetry._installation_repositories("ephemeral")
        self.assertEqual(status, 403)
        self.assertIsNone(repos)

    @patch("github_app_telemetry.request_json")
    def test_probe_updates_only_the_named_app(self, request_json):
        second = dict(REGISTRY["apps"][0], slug="second-app")
        registry = dict(REGISTRY, apps=REGISTRY["apps"] + [second])
        request_json.side_effect = [
            (200, {"resources": {"core": {"limit": 5000, "remaining": 4900, "reset": 123}}}, {}),
            (200, {"repositories": []}, {}),
        ]
        rows = build_telemetry(
            registry, token="ephemeral", probe_app_slug="termux-fleet-collector"
        )["apps"]
        self.assertEqual(rows[0]["evidence"]["rate_limit"], "observed")
        self.assertEqual(rows[1]["evidence"]["rate_limit"], "not_observed")
        self.assertEqual(rows[1]["evidence"]["repository_scope"], "not_observed")

    def test_token_requires_explicit_app_binding(self):
        with self.assertRaisesRegex(ValueError, "probe_app_slug is required"):
            build_telemetry(REGISTRY, token="ephemeral")


    def test_g4_runtime_receipt_contract_accepts_complete_sanitized_receipt(self):
        receipt = {
            "schema_version": 1,
            "receipt_type": "github_app_g4_runtime_receipt",
            "app_slug": "termux-fleet-collector",
            "mint_outcome": "success",
            "rate_limit_before": {"limit": 5000, "remaining": 4990, "reset": 1900000000},
            "rate_limit_after": {"limit": 5000, "remaining": 4984, "reset": 1900000000},
            "api_calls_by_status": {"200": 5, "304": 1},
            "repositories_inspected": 1,
            "workflow": {"run_id": 12345, "attempt": 1, "head_sha": "a" * 40},
            "duration_seconds": 12.5,
            "conclusion": "success",
            "observed_at": "2026-10-30T07:00:00Z",
        }
        self.assertTrue(telemetry.validate_g4_receipt(receipt))

    def test_g4_runtime_receipt_rejects_missing_contract_fields(self):
        receipt = {
            "schema_version": 1,
            "receipt_type": "github_app_g4_runtime_receipt",
            "app_slug": "termux-fleet-collector",
        }
        with self.assertRaisesRegex(ValueError, "exactly the required fields"):
            telemetry.validate_g4_receipt(receipt)

    def test_g4_runtime_receipt_rejects_credential_fields(self):
        receipt = {
            "schema_version": 1,
            "receipt_type": "github_app_g4_runtime_receipt",
            "app_slug": "termux-fleet-collector",
            "mint_outcome": "success",
            "rate_limit_before": {"limit": 5000, "remaining": 4990, "reset": 1900000000},
            "rate_limit_after": {"limit": 5000, "remaining": 4984, "reset": 1900000000},
            "api_calls_by_status": {"200": 5},
            "repositories_inspected": 1,
            "workflow": {"run_id": 12345, "attempt": 1, "head_sha": "a" * 40},
            "duration_seconds": 12.5,
            "conclusion": "success",
            "observed_at": "2026-10-30T07:00:00Z",
            "installation_token": "must-never-be-present",
        }
        with self.assertRaisesRegex(ValueError, "exactly the required fields"):
            telemetry.validate_g4_receipt(receipt)

    def test_g4_runtime_receipt_rejects_invalid_status_and_sha(self):
        receipt = {
            "schema_version": 1,
            "receipt_type": "github_app_g4_runtime_receipt",
            "app_slug": "termux-fleet-collector",
            "mint_outcome": "success",
            "rate_limit_before": {"limit": 5000, "remaining": 4990, "reset": 1900000000},
            "rate_limit_after": {"limit": 5000, "remaining": 4984, "reset": 1900000000},
            "api_calls_by_status": {"200": -1},
            "repositories_inspected": 1,
            "workflow": {"run_id": 12345, "attempt": 1, "head_sha": "not-a-sha"},
            "duration_seconds": 12.5,
            "conclusion": "success",
            "observed_at": "2026-10-30T07:00:00Z",
        }
        with self.assertRaisesRegex(ValueError, "API status counts"):
            telemetry.validate_g4_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
