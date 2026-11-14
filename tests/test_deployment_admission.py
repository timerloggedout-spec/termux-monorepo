import unittest
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ci.deployment_admission import SCHEMA, evaluate

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
SHA = "a" * 40


def document():
    return {
        "schema": SCHEMA,
        "workload": "mcp",
        "source_sha": SHA,
        "safety_fraction": 0.9,
        "max_observation_age_seconds": 900,
        "quota": {
            "provider": "vercel", "resource_id": "vercel.deployments",
            "authority": "provider_enforcement", "used": 20, "limit": 100,
            "window_id": "team:rolling-24h:2026-11-02T12Z",
            "scope_id": "vercel-team:verified",
            "observed_at": "2026-11-02T11:59:00Z",
        },
        "alternates": [],
    }


def ready_alternate(workload="mcp"):
    return {
        "lane_id": "candidate-mcp", "status": "READY", "workload": workload,
        "provider": "cloudflare", "independent_failure_domain": True,
        "source_sha": SHA, "project_verified": True, "root_verified": True,
        "domain_verified": True, "secrets_verified": True,
        "healthcheck_verified": True, "protocol_compatible": True,
        "state_dependency_verified": True,
    }


class DeploymentAdmissionTests(unittest.TestCase):
    def test_admits_primary_only_with_fresh_authoritative_quota(self):
        result = evaluate(document(), now=NOW)
        self.assertEqual(result["decision"], "ADMIT_PRIMARY")
        self.assertEqual(result["selected_lane"], "vercel")

    def test_non_authoritative_listing_never_grants_admission(self):
        data = document(); data["quota"]["authority"] = "deployment_listing"
        result = evaluate(data, now=NOW)
        self.assertEqual(result["reason"], "QUOTA_NOT_AUTHORITATIVE")
        self.assertEqual(result["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_stale_and_unknown_quota_fail_closed(self):
        data = document(); data["quota"]["observed_at"] = "2026-11-02T11:00:00Z"
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")
        data["quota"] = None
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_threshold_reached_blocks_primary(self):
        data = document(); data["quota"]["used"] = 90
        self.assertEqual(evaluate(data, now=NOW)["reason"], "QUOTA_SAFETY_THRESHOLD_REACHED")

    def test_verified_alternate_requires_exact_sha_and_all_contracts(self):
        data = document(); data["quota"]["authority"] = "deployment_listing"
        data["alternates"] = [ready_alternate()]
        self.assertEqual(evaluate(data, now=NOW)["decision"], "SELECT_VERIFIED_ALTERNATE")
        data["alternates"][0]["source_sha"] = "b" * 40
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_same_provider_is_not_redundancy(self):
        data = document(); data["quota"]["authority"] = "deployment_listing"
        lane = ready_alternate(); lane["provider"] = "vercel"
        data["alternates"] = [lane]
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_static_fallback_cannot_serve_mcp(self):
        data = document(); data["quota"]["authority"] = "deployment_listing"
        data["alternates"] = [ready_alternate(workload="static")]
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_missing_health_or_state_proof_blocks_alternate(self):
        data = document(); data["quota"]["authority"] = "deployment_listing"
        lane = ready_alternate(); lane["state_dependency_verified"] = False
        data["alternates"] = [lane]
        self.assertEqual(evaluate(data, now=NOW)["decision"], "BLOCK_OPTIONAL_DEPLOYMENT")

    def test_decision_never_mutates_traffic(self):
        for data in (document(), {**document(), "quota": None}):
            self.assertIs(evaluate(data, now=NOW)["traffic_mutated"], False)


if __name__ == "__main__":
    unittest.main()
