import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from proposal_package import (
    build_manifest, package_digest, validate_manifest, verify_award, verify_files,
)


class TestProposalPackage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "MANIFEST.md").write_text("# Proposal\n")
        (self.root / "ITEMS.md").write_text("# Items\n")
        (self.root / "RFP.md").write_text("# Request\n")

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self):
        return build_manifest(
            source_ref="a" * 40,
            package_id="que-sie-test",
            package_path="docs/proposals/que-sie-test",
            package_author="builder",
            root=self.root,
            files=["RFP.md", "MANIFEST.md", "ITEMS.md"],
            excluded_paths=["PROVENANCE.json"],
        )

    def test_manifest_digest_is_stable_under_inventory_reordering(self):
        manifest = self.manifest()
        reversed_digest = package_digest(
            manifest["source_ref"], manifest["package_id"],
            manifest["package_path"], list(reversed(manifest["files"])), manifest["package_author"],
        )
        self.assertEqual(manifest["package_digest"], reversed_digest)
        self.assertEqual(validate_manifest(manifest), [])
        self.assertEqual(verify_files(manifest, self.root), [])
        self.assertEqual(verify_files(manifest, self.root, checkout_sha="a" * 40), [])
        self.assertTrue(any("checked-out source SHA" in error
                            for error in verify_files(manifest, self.root, checkout_sha="b" * 40)))

    def test_each_included_document_change_invalidates_package(self):
        manifest = self.manifest()
        original = manifest["package_digest"]
        for name in ("MANIFEST.md", "ITEMS.md", "RFP.md"):
            (self.root / name).write_text((self.root / name).read_text() + "\nchanged\n")
            updated = self.manifest()
            self.assertNotEqual(original, updated["package_digest"])
            original = updated["package_digest"]

    def test_duplicate_and_traversal_paths_fail_closed(self):
        rows = [{"path": "RFP.md", "sha256": "b" * 64}]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            package_digest("a" * 40, "pkg", "docs/pkg", rows + rows)
        with self.assertRaisesRegex(ValueError, "unsafe"):
            package_digest("a" * 40, "pkg", "docs/pkg",
                           [{"path": "../secret.md", "sha256": "b" * 64}])

    def test_mutable_refs_and_malformed_hashes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "immutable"):
            package_digest("main", "pkg", "docs/pkg",
                           [{"path": "RFP.md", "sha256": "b" * 64}])
        with self.assertRaisesRegex(ValueError, "malformed"):
            package_digest("a" * 40, "pkg", "docs/pkg",
                           [{"path": "RFP.md", "sha256": "bad"}])

    def test_missing_and_changed_files_hold_consumer(self):
        manifest = self.manifest()
        (self.root / "RFP.md").write_text("# Drifted\n")
        errors = verify_files(manifest, self.root)
        self.assertTrue(any("hash mismatch" in error for error in errors))
        (self.root / "ITEMS.md").unlink()
        self.assertTrue(any("missing" in error for error in verify_files(manifest, self.root)))

    def test_award_digest_and_independent_reviewer_are_required(self):
        manifest = self.manifest()
        award = {"package_digest": manifest["package_digest"],
                 "decision": "shadow", "ledger_ref": "issue-comment:99",
                 "reviewer_login": "reviewer"}
        good = verify_award(manifest=manifest, award=award,
                            package_author="builder", reviewer="reviewer")
        self.assertEqual(good["disposition"], "VERIFIED")
        stale = dict(award, package_digest="c" * 64)
        self.assertEqual(verify_award(manifest=manifest, award=stale,
                                      package_author="builder", reviewer="reviewer")["disposition"],
                         "HELD")
        self.assertEqual(verify_award(manifest=manifest, award=award,
                                      package_author="builder", reviewer="builder")["disposition"],
                         "HELD")

    def test_mutating_manifest_inventory_invalidates_digest(self):
        manifest = self.manifest()
        manifest["files"][0]["sha256"] = "f" * 64
        self.assertTrue(validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
