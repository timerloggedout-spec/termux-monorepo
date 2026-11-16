import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.ci.create_artifact_evidence import MAX_FILE_BYTES, build_manifest, safe_relative
from scripts.ci.verify_artifact_evidence import verify_manifest


class ArtifactEvidenceTests(unittest.TestCase):
    def test_builds_single_file_digest_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "policy-tests.txt"
            payload.write_text("six passed\n", encoding="utf-8")
            manifest = build_manifest(root, ["policy-tests.txt"])
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(
                manifest["files"],
                [
                    {
                        "path": "policy-tests.txt",
                        "sha256": hashlib.sha256(b"six passed\n").hexdigest(),
                        "bytes": len(b"six passed\n"),
                    }
                ],
            )

    def test_rejects_hidden_absolute_and_traversal_entries(self):
        for value in (".secret", "/etc/passwd", "../outside.txt", "nested/file.txt"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    safe_relative(value)

    def test_rejects_missing_duplicate_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "present.txt").write_text("ok", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_manifest(root, ["missing.txt"])
            with self.assertRaises(ValueError):
                build_manifest(root, ["present.txt", "present.txt"])
            (root / "large.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
            with self.assertRaises(ValueError):
                build_manifest(root, ["large.txt"])

    def test_consumer_verifies_manifest_then_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "policy-tests.txt"
            evidence.write_text("six passed\n", encoding="utf-8")
            manifest = root / "evidence-manifest.json"
            import json

            manifest.write_text(json.dumps(build_manifest(root, ["policy-tests.txt"])), encoding="utf-8")
            self.assertEqual(verify_manifest(root, manifest), 1)
            evidence.write_text("tampered\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_manifest(root, manifest)


if __name__ == "__main__":
    unittest.main()
