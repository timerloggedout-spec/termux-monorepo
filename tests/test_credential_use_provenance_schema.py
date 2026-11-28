"""Structural safety tests for the credential-use provenance contract."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/ops/credential-use-provenance.schema.json"
PROBE_WORKFLOW = ROOT / ".github/workflows/credential-family-probe.yml"
FORBIDDEN_KEYS = {
    "token", "token_value", "pat", "pat_value", "secret_value",
    "password", "private_key", "authorization", "bearer",
    "cookie", "api_key_value", "credential_hash", "token_hash",
}


class CredentialUseProvenanceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_is_closed_at_every_identity_boundary(self):
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(self.schema["properties"]["schema"]["const"], "credential-use-provenance/v1")
        for section in ("credential", "consumer", "inference", "execution", "usage", "attribution"):
            self.assertFalse(self.schema["properties"][section]["additionalProperties"])

    def test_secret_material_fields_are_not_admitted(self):
        def walk(node, path="$"):
            if isinstance(node, dict):
                for key in node.get("properties", {}):
                    self.assertNotIn(key.lower(), FORBIDDEN_KEYS, f"{path}.{key}")
                for key, value in node.items():
                    walk(value, f"{path}.{key}")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f"{path}[{index}]")
        walk(self.schema)

    def test_credential_reference_is_opaque_and_not_value_derived(self):
        credential = self.schema["properties"]["credential"]["properties"]
        self.assertIn("ref", credential)
        self.assertIn("mapping_status", credential)
        self.assertNotIn("fingerprint", credential)
        self.assertNotIn("value", credential)
        self.assertNotIn("hash", credential)

    def test_doe_instance_and_execution_join_fields_are_required(self):
        consumer = self.schema["properties"]["consumer"]
        execution = self.schema["properties"]["execution"]
        self.assertTrue({"moniker", "role", "context", "instance_key"} <= set(consumer["required"]))
        self.assertTrue({"workflow", "run_id", "run_attempt", "job", "step", "source_sha"} <= set(execution["required"]))

    def test_credential_family_workflow_never_reads_or_transmits_secrets(self):
        workflow = PROBE_WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("${{ secrets.", workflow)
        self.assertNotIn("Authorization:", workflow)
        self.assertNotIn("curl ", workflow)
        self.assertNotIn("api.deepseek.com", workflow)
        self.assertNotIn("api.github.com", workflow)
        self.assertIn("contents: read", workflow)
        self.assertNotIn("issues: write", workflow)

    def test_shared_bucket_usage_can_remain_unknown_without_fabrication(self):
        usage = self.schema["properties"]["usage"]["properties"]
        self.assertIn("null", usage["value"]["type"])
        self.assertIn(None, usage["match"]["enum"])
        self.assertEqual(usage["status"]["enum"], ["established", "activity-only", "waived", "fault", "pending"])


if __name__ == "__main__":
    unittest.main()
