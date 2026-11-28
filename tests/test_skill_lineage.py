"""Focused tests for immutable source pins and candidate lineage."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from scripts.ci.verify_skill_lineage import verify_manifest

def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

class SkillLineageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "original").mkdir()
        (self.root / "candidate").mkdir()
        (self.root / "original/SKILL.md").write_bytes(b"original vendor bytes\n")
        (self.root / "candidate/normalized.md").write_bytes(b"normalized derivative\n")
        (self.root / "candidate/enhanced.md").write_bytes(b"enhanced derivative\n")
        self.source_hash = sha(b"original vendor bytes\n")
        self.manifest = {
            "schema_version": "1.0",
            "sources": [{
                "id": "vendor:sample", "path": "original/SKILL.md",
                "sha256": self.source_hash, "provenance": "vendor-export",
                "checksum_status": "unverified"
            }],
            "candidates": [
                {"id": "sample:normalized", "source_id": "vendor:sample",
                 "path": "candidate/normalized.md", "parent_sha256": self.source_hash,
                 "sha256": sha(b"normalized derivative\n"), "transformation_id": "normalize-v1"},
                {"id": "sample:enhanced", "source_id": "vendor:sample",
                 "path": "candidate/enhanced.md", "parent_sha256": self.source_hash,
                 "sha256": sha(b"enhanced derivative\n"), "transformation_id": "enhance-v1"}
            ]
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_multiple_candidates_share_one_immutable_source(self):
        self.assertEqual([], verify_manifest(self.manifest, self.root))

    def test_parent_hash_mismatch_fails(self):
        self.manifest["candidates"][1]["parent_sha256"] = "0" * 64
        self.assertTrue(any("parent SHA-256" in e for e in verify_manifest(self.manifest, self.root)))

    def test_path_alias_cannot_be_candidate(self):
        self.manifest["candidates"][0]["path"] = "./original/../original/SKILL.md"
        self.assertTrue(any("aliases an original" in e for e in verify_manifest(self.manifest, self.root)))

    def test_existing_baseline_pin_cannot_be_rewritten_or_removed(self):
        baseline = {"sources": [dict(self.manifest["sources"][0])]}
        self.manifest["sources"][0]["sha256"] = "f" * 64
        self.assertTrue(any("baseline source pin changed" in e for e in verify_manifest(self.manifest, self.root, baseline)))
        self.manifest["sources"] = []
        self.assertTrue(any("baseline source pin removed" in e for e in verify_manifest(self.manifest, self.root, baseline)))

if __name__ == "__main__":
    unittest.main()
