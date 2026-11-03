import copy
import json
import unittest
from pathlib import Path
from scripts.validate_federated_app_registry import validate

ROOT = Path(__file__).resolve().parents[1]

class FederatedAppRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "docs/ops/federated-app-registry.json").read_text())
        cls.schema = json.loads((ROOT / "docs/ops/federated-app-registry.schema.json").read_text())

    def test_checked_in_registry_is_valid(self):
        self.assertEqual(validate(self.data, self.schema), [])

    def test_duplicate_product_app_key_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["applications"].append(copy.deepcopy(data["applications"][0]))
        self.assertTrue(any("duplicate app_key" in e for e in validate(data, self.schema)))

    def test_duplicate_product_app_id_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["applications"][0]["product_app_id"] = "prod-123"
        data["applications"][1]["product_app_id"] = "prod-123"
        self.assertTrue(any("duplicate product_app_id" in e for e in validate(data, self.schema)))

    def test_duplicate_release_lane_id_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["applications"][1]["release_lanes"][0]["lane_id"] = data["applications"][0]["release_lanes"][0]["lane_id"]
        self.assertTrue(any("duplicate release lane id" in e for e in validate(data, self.schema)))

    def test_duplicate_automation_id_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["automation_identities"].append(copy.deepcopy(data["automation_identities"][0]))
        self.assertTrue(any("duplicate automation identity key" in e for e in validate(data, self.schema)))

    def test_product_and_automation_domains_are_separate(self):
        data = copy.deepcopy(self.data)
        data["applications"][0]["identity_domain"] = "github-app"
        self.assertTrue(any("identity_domain" in e for e in validate(data, self.schema)))

    def test_released_lane_requires_evidence(self):
        data = copy.deepcopy(self.data)
        data["applications"][0]["release_lanes"][0]["evidence_refs"] = []
        self.assertTrue(any("released lane requires evidence_refs" in e for e in validate(data, self.schema)))

    def test_released_lane_requires_version_authority(self):
        data = copy.deepcopy(self.data)
        data["applications"][0]["release_lanes"][0]["version_authority"] = None
        self.assertTrue(any("released lane requires version_authority" in e for e in validate(data, self.schema)))

    def test_malformed_repository_identity_is_rejected(self):
        data = copy.deepcopy(self.data)
        data["applications"][0]["repository"]["full_name"] = "not-a-repository"
        self.assertTrue(any("owner/repository" in e for e in validate(data, self.schema)))

    def test_independent_studysprint_release_lane_is_registered(self):
        app = next(a for a in self.data["applications"] if a["app_key"] == "studysprint.agent")
        self.assertEqual(app["repository"]["full_name"], "timerloggedout-spec/studysprint")
        self.assertEqual(app["release_lanes"][0]["current_version"], "0.2.0")
        self.assertIsNone(app["product_app_id"])
        self.assertEqual(app["release_lanes"][0]["status"], "configured")

    def test_listinglens_scaffold_is_not_misrepresented_as_released(self):
        app = next(a for a in self.data["applications"] if a["app_key"] == "listinglens.web")
        self.assertEqual(app["lifecycle"], "proposed")
        self.assertEqual(app["release_lanes"], [])
        self.assertIsNone(app["product_app_id"])

    def test_output_is_deterministic(self):
        self.assertEqual(validate(self.data, self.schema), validate(json.loads(json.dumps(self.data)), self.schema))

if __name__ == "__main__":
    unittest.main()
