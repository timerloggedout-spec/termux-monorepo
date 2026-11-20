import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs/schemas/cns-writer-lease-receipt.schema.json"


class WriterLeaseSchemaTests(unittest.TestCase):
    def test_schema_defines_revision_bound_resource_and_owner(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "urn:timerloggedout-spec:cns:writer-lease-receipt:v1")
        self.assertTrue({
            "schema_version", "lease_id", "lease_key", "resource", "owner",
            "epoch", "state", "observed_at", "expires_at", "evidence_ref",
        }.issubset(set(schema["required"])))
        self.assertTrue({
            "repository_id", "pull_request_number", "revision_sha",
        }.issubset(set(schema["properties"]["resource"]["required"])))
        self.assertTrue({
            "provider_id", "agent_id", "adapter_id", "invocation_id",
        }.issubset(set(schema["properties"]["owner"]["required"])))

    def test_schema_has_fencing_states_and_excludes_secret_tokens(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["properties"]["state"]["enum"]), {
            "acquired", "renewed", "released", "expired", "rejected", "recovered",
        })
        self.assertNotIn("fencing_token", schema["properties"])
        self.assertNotIn("token", schema["properties"])
        self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
