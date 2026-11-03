import json
import unittest

from scripts.ci.validate_agent_toolchain_portfolio import REQUIRED, validate_data

BASE = {
    "schema_version": "1.0.0",
    "integrations": [
        {
            "id": identifier,
            "name": name,
            "discovery_state": "tool_connected_in_session" if identifier != "smart-model-router" else "discovered",
            "authority": "advisory-only",
            "write_boundary": "read-only by default",
            "next_step": "verify with fixtures",
        }
        for identifier, name in REQUIRED.items()
    ],
}
MATRIX = "\n".join(REQUIRED.values())


class AgentToolchainPortfolioTests(unittest.TestCase):
    def test_valid_portfolio_passes(self):
        self.assertEqual(validate_data(json.dumps(BASE), MATRIX), [])

    def test_missing_integration_fails(self):
        data = dict(BASE)
        data["integrations"] = BASE["integrations"][:-1]
        self.assertTrue(any("missing canonical integration" in x for x in validate_data(json.dumps(data), MATRIX)))

    def test_duplicate_id_fails(self):
        data = dict(BASE)
        data["integrations"] = BASE["integrations"] + [BASE["integrations"][0]]
        self.assertTrue(any("duplicate integration id" in x for x in validate_data(json.dumps(data), MATRIX)))

    def test_unknown_discovery_state_fails(self):
        data = json.loads(json.dumps(BASE))
        data["integrations"][0]["discovery_state"] = "production_ready"
        self.assertTrue(any("invalid discovery_state" in x for x in validate_data(json.dumps(data), MATRIX)))

    def test_missing_authority_fails(self):
        data = json.loads(json.dumps(BASE))
        data["integrations"][0]["authority"] = ""
        self.assertTrue(any("authority and write_boundary" in x for x in validate_data(json.dumps(data), MATRIX)))

    def test_credential_shaped_value_fails(self):
        self.assertTrue(any("credential-shaped" in x for x in validate_data(json.dumps(BASE) + "\nAKIA1234567890ABCDEF", MATRIX)))

    def test_registry_boolean_shortcut_fails(self):
        self.assertTrue(any("integrated boolean" in x for x in validate_data(json.dumps(BASE) + '\n"integrated": true', MATRIX)))


if __name__ == "__main__":
    unittest.main()
