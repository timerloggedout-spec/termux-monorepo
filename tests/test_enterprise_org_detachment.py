import unittest

from scripts.github.verify_enterprise_org_detachment import compare_snapshots


def snapshot(plan="enterprise"):
    return {
        "organization": {
            "id": "313697792",
            "plan": plan,
            "repositories": [{
                "id": "1324746630",
                "name": "termux-monorepo_enterprise",
                "full_name": "search-astute-ly/termux-monorepo_enterprise",
                "branches_status": "observed",
                "branches": [{"name": "master", "sha": "a"}],
                "tags_status": "observed",
                "tags": [{"name": "v1", "sha": "b"}],
                "releases_status": "observed",
                "releases": [{"id": "1", "tag_name": "v1"}],
                "workflows_status": "observed",
                "workflows": [{"id": "10", "name": "CI"}],
                "hooks_status": "observed",
                "hooks": [],
                "deployments_status": "observed",
                "deployments": [],
                "actions_secrets_status": "observed",
                "actions_secret_names": ["REPO_TOKEN"],
                "actions_variables_status": "observed",
                "actions_variable_names": ["REPO_MODE"],
                "environments_status": "observed",
                "environments": ["production"],
            }],
            "integrations": {
                "actions_secrets_status": "observed",
                "actions_secret_names": ["ORG_TOKEN"],
                "actions_variables_status": "observed",
                "actions_variable_names": ["ORG_MODE"],
                "webhooks_status": "observed",
                "webhooks": [{"id": "20"}],
                "app_installations_status": "observed",
                "app_installations": [{"id": "30"}],
            },
        }
    }


class EnterpriseOrgDetachmentTests(unittest.TestCase):
    def test_plan_downgrade_preserves_inventory(self):
        self.assertEqual(compare_snapshots(snapshot(), snapshot("free")), [])

    def test_missing_repository_is_reported(self):
        after = snapshot("free")
        after["organization"]["repositories"] = []
        findings = compare_snapshots(snapshot(), after)
        self.assertTrue(any(item.startswith("repository_missing:") for item in findings))

    def test_missing_branch_is_reported(self):
        after = snapshot("free")
        after["organization"]["repositories"][0]["branches"] = []
        findings = compare_snapshots(snapshot(), after)
        self.assertTrue(any(item.startswith("items_missing:") and ":branches:" in item for item in findings))

    def test_missing_secret_name_is_reported(self):
        after = snapshot("free")
        after["organization"]["integrations"]["actions_secret_names"] = []
        findings = compare_snapshots(snapshot(), after)
        self.assertTrue(any(item.startswith("integration_items_missing:actions_secret_names:") for item in findings))

    def test_unavailable_inventory_is_explicit(self):
        after = snapshot("free")
        after["organization"]["integrations"]["app_installations_status"] = "unavailable"
        findings = compare_snapshots(snapshot(), after)
        self.assertIn("integration_unverified:app_installations", findings)


    def test_transfer_allows_destination_organization_identity(self):
        before = snapshot()
        after = snapshot("free")
        after["organization"]["id"] = "999999999"
        after["organization"]["repositories"][0]["full_name"] = "asastraneonexus/termux-monorepo_enterprise"
        findings = compare_snapshots(before, after, "transferred", "asastraneonexus")
        self.assertEqual(findings, [])

    def test_transfer_flags_repository_owner_mismatch(self):
        before = snapshot()
        after = snapshot("free")
        after["organization"]["id"] = "999999999"
        after["organization"]["repositories"][0]["full_name"] = "unexpected-owner/termux-monorepo_enterprise"
        findings = compare_snapshots(before, after, "transferred", "asastraneonexus")
        self.assertTrue(any(item.startswith("repository_owner_path_mismatch:") for item in findings))

    def test_detachment_requires_same_organization_identity(self):
        after = snapshot("free")
        after["organization"]["id"] = "999999999"
        findings = compare_snapshots(snapshot(), after, "detached", "search-astute-ly")
        self.assertIn("organization_id_changed", findings)


if __name__ == "__main__":
    unittest.main()
