from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "architecture_docs.py"
SPEC = importlib.util.spec_from_file_location("architecture_docs", MODULE_PATH)
architecture_docs = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(architecture_docs)


class ArchitectureDocumentationTests(unittest.TestCase):
    def make_root(self, root: Path) -> None:
        (root / "docs/architecture/flows").mkdir(parents=True)
        (root / "docs/ops/diagrams").mkdir(parents=True)
        (root / "docs/architecture/generated/flows").mkdir(parents=True)
        files = {
            "architecture.md": "# Repository Architecture\n",
            "docs/architecture/README.md": "# Architecture index\n",
            "docs/architecture/VERSION": "1.0.0\n",
            "docs/architecture/VERSIONING.md": "# Versioning\n",
            "docs/architecture/CHANGELOG.md": "# Changelog\n\n## 1.0.0 \u2014 2026-11-22\n- Initial baseline.\n",
            "docs/architecture/flows/sample.md": "# Sample flow\n",
            "docs/architecture/flows/sample.mmd": "flowchart LR\n A --> B\n",
            "docs/ops/diagrams/ops.mmd": "flowchart TD\n A --> B\n",
        }
        for relative, value in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
        (root / "docs/architecture/generated/flows/sample.svg").write_text(
            "<svg>sample</svg>\n", encoding="utf-8"
        )
        (root / "docs/ops/generated").mkdir(parents=True)
        (root / "docs/ops/generated/ops.png").write_bytes(b"png-fixture")

    def test_manifest_is_deterministic_and_covers_architecture_and_diagrams(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            first = architecture_docs.build_manifest(root)
            self.assertEqual(first, architecture_docs.build_manifest(root))
            self.assertEqual(first["schema"], "repository-architecture-manifest/v1")
            self.assertEqual(first["architecture_version"], "1.0.0")
            paths = {item["path"] for item in first["sources"]}
            self.assertIn("architecture.md", paths)
            self.assertIn("docs/architecture/flows/sample.mmd", paths)
            self.assertIn("docs/ops/diagrams/ops.mmd", paths)
            self.assertEqual(len(first["source_set_sha256"]), 64)
            self.assertEqual(len(first["diagrams"]), 2)

    def test_manifest_rejects_unpaired_flow_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            (root / "docs/architecture/flows/sample.md").unlink()
            with self.assertRaisesRegex(ValueError, "missing paired architecture flow mapping"):
                architecture_docs.build_manifest(root)

    def test_manifest_rejects_missing_render(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            (root / "docs/architecture/generated/flows/sample.svg").unlink()
            with self.assertRaisesRegex(ValueError, "missing architecture diagram render"):
                architecture_docs.build_manifest(root)

    def test_write_and_check_detect_stale_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            self.assertFalse(architecture_docs.check_manifest(root))
            architecture_docs.write_manifest(root)
            self.assertTrue(architecture_docs.check_manifest(root))
            (root / "architecture.md").write_text("# Changed\n", encoding="utf-8")
            self.assertFalse(architecture_docs.check_manifest(root))

    def test_invalid_semver_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            (root / "docs/architecture/VERSION").write_text("v1.0\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "semantic version"):
                architecture_docs.build_manifest(root)

    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)

    def test_version_check_accepts_initial_1_0_0_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            (root / "docs/architecture/VERSION").unlink()
            (root / "docs/architecture/CHANGELOG.md").unlink()
            self.init_git(root)
            (root / "architecture.md").write_text("# Initial governed architecture\\n", encoding="utf-8")
            (root / "docs/architecture/VERSION").write_text("1.0.0\\n", encoding="utf-8")
            (root / "docs/architecture/CHANGELOG.md").write_text(
                "# Changelog\\n\\n## 1.0.0 \\u2014 2026-11-22\\n- Initial baseline.\\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "initial architecture baseline"], cwd=root, check=True)
            self.assertTrue(architecture_docs.check_version_bump(root, "HEAD~1"))

    def test_version_check_requires_bump_and_changelog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            self.init_git(root)
            (root / "architecture.md").write_text("# Architecture v2\n", encoding="utf-8")
            (root / "docs/architecture/VERSION").write_text("1.1.0\n", encoding="utf-8")
            (root / "docs/architecture/CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.1.0 \u2014 2026-11-22\n- Add architecture versioning.\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "architecture version bump"], cwd=root, check=True)
            self.assertTrue(architecture_docs.check_version_bump(root, "HEAD~1"))

    def test_version_file_change_requires_matching_changelog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            self.init_git(root)
            (root / "docs/architecture/VERSION").write_text("1.1.0\\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "version-only change"], cwd=root, check=True)
            with self.assertRaisesRegex(ValueError, "VERSION and CHANGELOG"):
                architecture_docs.check_version_bump(root, "HEAD~1")

    def test_version_check_rejects_missing_bump(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            self.init_git(root)
            (root / "architecture.md").write_text("# Architecture changed\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "unversioned architecture change"], cwd=root, check=True)
            with self.assertRaisesRegex(ValueError, "VERSION and CHANGELOG"):
                architecture_docs.check_version_bump(root, "HEAD~1")

    def test_version_check_rejects_non_increasing_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_root(root)
            self.init_git(root)
            (root / "architecture.md").write_text("# Architecture changed\n", encoding="utf-8")
            (root / "docs/architecture/VERSION").write_text("0.9.0\n", encoding="utf-8")
            (root / "docs/architecture/CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.9.0 \u2014 2026-11-22\n- Repeated version.\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "unchanged version"], cwd=root, check=True)
            with self.assertRaisesRegex(ValueError, "increase architecture version"):
                architecture_docs.check_version_bump(root, "HEAD~1")


if __name__ == "__main__":
    unittest.main()
