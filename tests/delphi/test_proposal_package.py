import base64
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
from gate import verify_issue_package_binding


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

    def test_delphi_gate_binds_immutable_package_and_all_file_bytes(self):
        package_path = "docs/proposals/que-sie-test"
        package_root = self.root / package_path
        package_root.mkdir(parents=True)
        for name in ("RFP.md", "MANIFEST.md", "ITEMS.md"):
            (package_root / name).write_bytes((self.root / name).read_bytes())
        manifest = build_manifest(
            source_ref="a" * 40,
            package_id="que-sie-test",
            package_path=package_path,
            package_author="builder",
            root=self.root,
            files=[f"{package_path}/{name}" for name in ("RFP.md", "MANIFEST.md", "ITEMS.md")],
        )
        manifest_path = package_path + "/PACKAGE.json"
        payloads = {
            manifest_path: json.dumps(manifest).encode("utf-8"),
            **{f"{package_path}/{name}": (package_root / name).read_bytes()
               for name in ("RFP.md", "MANIFEST.md", "ITEMS.md")},
        }

        manifest_ref = "b" * 40

        class FakeGitHub:
            def __init__(self):
                self.refs = []
            def req(self, method, path):
                if path.startswith("/git/commits/"):
                    ref = path.rsplit("/", 1)[1]
                    return {"sha": ref, "tree": {"sha": "c" * 40 if ref == manifest_ref else "d" * 40}}
                ref = path.rsplit("?ref=", 1)[1]
                if path.startswith("/git/trees/"):
                    tree_sha = path.split("/git/trees/", 1)[1].split("?", 1)[0]
                    paths = ([manifest_path] if tree_sha == "c" * 40 else
                             [f"{package_path}/{name}" for name in ("ITEMS.md", "MANIFEST.md", "RFP.md")])
                    return {"truncated": False, "tree": [
                        {"path": item, "type": "blob", "mode": "100644"} for item in paths
                    ]}
                content_path = path.split("/contents/", 1)[1].split("?ref=", 1)[0]
                self.refs.append((content_path, ref))
                raw = payloads[content_path]
                return {"type": "file", "encoding": "base64",
                        "content": base64.b64encode(raw).decode("ascii")}

        gh = FakeGitHub()
        issue = {"body": (
            "### Proposal source ref\n" + manifest["source_ref"] +
            "\n### Proposal manifest ref\n" + manifest_ref +
            "\n### Proposal manifest path\n" + manifest_path +
            "\n### Expected package digest\n" + manifest["package_digest"] + "\n"
        )}
        binding = verify_issue_package_binding(gh, issue)
        self.assertEqual(binding["manifest_ref"], manifest_ref)
        self.assertEqual(gh.refs, [(manifest_path, manifest_ref),
                                   *[(f"{package_path}/{name}", manifest["source_ref"])
                                     for name in ("ITEMS.md", "MANIFEST.md", "RFP.md")]])
        self.assertEqual(binding["package_digest"], manifest["package_digest"])
        self.assertEqual(binding["file_count"], 3)

        payloads[package_path + "/RFP.md"] = b"# drift\n"
        with self.assertRaisesRegex(ValueError, "file hash mismatch"):
            verify_issue_package_binding(FakeGitHub(), issue)

    def test_delphi_gate_requires_all_package_binding_fields_together(self):
        issue = {"body": "### Proposal source ref\n" + "a" * 40 + "\n"}
        with self.assertRaisesRegex(ValueError, "all required"):
            verify_issue_package_binding(object(), issue)

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

    def test_award_requires_authenticated_author_reviewer_and_canonical_ledger(self):
        manifest = self.manifest()
        award = {"package_digest": manifest["package_digest"],
                 "decision": "shadow", "ledger_ref": "issue-comment:99",
                 "reviewer_login": "reviewer"}
        ledger = dict(award)
        ledger["ledger_ref"] = award["ledger_ref"]
        lookup = lambda ref: ledger if ref == ledger["ledger_ref"] else None
        good = verify_award(manifest=manifest, award=award,
                            package_author="builder", reviewer="reviewer",
                            ledger_lookup=lookup)
        self.assertEqual(good["disposition"], "VERIFIED")

        # A caller-supplied ledger reference is not proof that Delphi recorded an award.
        unverified = verify_award(manifest=manifest, award=award,
                                  package_author="builder", reviewer="reviewer")
        self.assertEqual(unverified["disposition"], "HELD")
        self.assertTrue(any("ledger lookup is unavailable" in error
                            for error in unverified["errors"]))

        stale = dict(award, package_digest="c" * 64)
        self.assertEqual(verify_award(manifest=manifest, award=stale,
                                      package_author="builder", reviewer="reviewer",
                                      ledger_lookup=lookup)["disposition"], "HELD")
        self.assertEqual(verify_award(manifest=manifest, award=award,
                                      package_author="attacker", reviewer="reviewer",
                                      ledger_lookup=lookup)["disposition"], "HELD")
        self.assertEqual(verify_award(manifest=manifest, award=award,
                                      package_author="builder", reviewer="builder",
                                      ledger_lookup=lookup)["disposition"], "HELD")

        # Keep the award and identities valid while mutating one canonical ledger field.
        for field, value in (("package_digest", "d" * 64),
                             ("decision", "parked"),
                             ("reviewer_login", "different-reviewer")):
            original = ledger[field]
            ledger[field] = value
            mismatch = verify_award(
                manifest=manifest, award=award,
                package_author="builder", reviewer="reviewer",
                ledger_lookup=lookup,
            )
            self.assertEqual(mismatch["disposition"], "HELD", field)
            ledger[field] = original

    def test_malformed_manifest_inventory_and_unknown_fields_fail_closed(self):
        manifest = self.manifest()
        malformed = dict(manifest, files=None)
        self.assertTrue(validate_manifest(malformed))
        malformed = dict(manifest, unexpected=True)
        self.assertTrue(any("unsupported properties" in error
                            for error in validate_manifest(malformed)))
        malformed = self.manifest()
        malformed["files"][0]["unexpected"] = True
        self.assertTrue(any("unsupported properties" in error
                            for error in validate_manifest(malformed)))

    def test_nested_symlink_is_rejected(self):
        outside = self.root / "outside-proposal.md"
        outside.write_text("# Outside\n")
        nested = self.root / "nested"
        nested.mkdir()
        (nested / "linked.md").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"):
            build_manifest(
                source_ref="a" * 40, package_id="pkg",
                package_path="docs/pkg", package_author="builder",
                root=self.root, files=["nested/linked.md"],
            )
        outside.unlink()

    def test_mutating_manifest_inventory_or_author_invalidates_digest(self):
        manifest = self.manifest()
        manifest["files"][0]["sha256"] = "f" * 64
        self.assertTrue(validate_manifest(manifest))
        manifest = self.manifest()
        manifest["package_author"] = "other-builder"
        self.assertTrue(validate_manifest(manifest))


if __name__ == "__main__":
    unittest.main()
