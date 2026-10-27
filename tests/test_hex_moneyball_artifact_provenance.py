import hashlib
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from hex_moneyball_artifact_provenance import create_inventory


class HexArtifactProvenanceTest(unittest.TestCase):
    def _bundle(self, root: Path, *, source_sha: str = "a" * 40):
        files = {
            "evidence.ndjson": '{"contract_version":"3l0.moneyball.v1"}\n',
            "evidence.csv": "contract_version\n3l0.moneyball.v1\n",
            "receipt.json": json.dumps({
                "contract_version": "3l0.moneyball.v1",
                "validation_status": "VALIDATED",
                "privacy_assertion": "passed",
                "raw_content_exported": False,
                "snapshot_id": "123-2",
                "source_sha": source_sha,
                "source_ref": "master",
            }),
        }
        for name, content in files.items():
            (root / name).write_text(content, encoding="utf-8")

    def test_inventory_pins_run_attempt_source_and_content_checksums(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._bundle(root)
            inventory = create_inventory(
                root,
                run_id="123",
                run_attempt="2",
                source_sha="a" * 40,
                source_ref="master",
                source_path="agent_telemetry_stream.json",
                generated_at="2026-10-22T00:00:00Z",
            )
            self.assertEqual(inventory["schema_version"], "hex-moneyball-artifact-provenance/v1")
            self.assertEqual(inventory["artifact_kind"], "sanitized_github_actions_artifact")
            self.assertFalse(inventory["native_hex_export"])
            self.assertFalse(inventory["hex_import_confirmed"])
            self.assertEqual(inventory["producer"]["run_uid"], "gha:timerloggedout-spec/termux-monorepo:123:2")
            self.assertEqual(inventory["source"]["sha"], "a" * 40)
            self.assertEqual(inventory["generated_at"], "2026-10-22T00:00:00Z")
            by_path = {entry["path"]: entry for entry in inventory["contents"]}
            self.assertEqual(set(by_path), {"evidence.ndjson", "evidence.csv", "receipt.json"})
            expected = hashlib.sha256((root / "evidence.ndjson").read_bytes()).hexdigest()
            self.assertEqual(by_path["evidence.ndjson"]["sha256"], expected)
            self.assertEqual(by_path["evidence.ndjson"]["size_bytes"], (root / "evidence.ndjson").stat().st_size)

    def test_rejects_short_sha(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._bundle(root)
            with self.assertRaisesRegex(ValueError, "40-character"):
                create_inventory(
                    root, run_id="123", run_attempt="2", source_sha="short",
                    source_ref="master", source_path="agent_telemetry_stream.json",
                )

    def test_rejects_mismatched_run_attempt(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._bundle(root)
            with self.assertRaisesRegex(ValueError, "snapshot_id"):
                create_inventory(
                    root, run_id="123", run_attempt="1", source_sha="a" * 40,
                    source_ref="master", source_path="agent_telemetry_stream.json",
                )

    def test_rejects_source_mismatch(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._bundle(root)
            with self.assertRaisesRegex(ValueError, "source provenance"):
                create_inventory(
                    root, run_id="123", run_attempt="2", source_sha="b" * 40,
                    source_ref="master", source_path="agent_telemetry_stream.json",
                )


if __name__ == "__main__":
    unittest.main()
