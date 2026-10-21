"""Offline source-pin checks; never initialize or import the optional SDK."""
import configparser
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SwarmsReferenceTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((ROOT / "integrations/swarms/source-lock.json").read_text())

    def test_canonical_reference_metadata(self):
        self.assertEqual(self.lock["target_path"], "refTemplates/smods/swarms")
        self.assertEqual(self.lock["repository"], "kyegomez/swarms")
        self.assertTrue(self.lock["reference_only"])
        self.assertFalse(self.lock["runtime_install_automatic"])
        self.assertRegex(self.lock["revision"], r"^[0-9a-f]{40}$")
        modules = configparser.ConfigParser(interpolation=None)
        modules.read(ROOT / ".gitmodules")
        entry = modules['submodule "refTemplates/smods/swarms"']
        self.assertEqual(entry["url"], self.lock["source_url"])
        self.assertEqual(entry["path"], self.lock["target_path"])
        self.assertTrue(entry.getboolean("shallow"))

    def test_gitlink_matches_lock(self):
        line = subprocess.check_output(
            ["git", "ls-files", "--stage", "--", self.lock["target_path"]],
            cwd=ROOT, text=True,
        ).strip()
        self.assertTrue(line, "Swarms source must be registered as a gitlink")
        mode, revision, _ = line.split(maxsplit=2)
        self.assertEqual(mode, "160000")
        self.assertEqual(revision, self.lock["revision"])

    def test_materialized_source_hashes_when_available(self):
        checkout = ROOT / self.lock["target_path"]
        if not (checkout / "pyproject.toml").is_file():
            self.skipTest("Optional source checkout is not initialized")
        for relative, evidence in self.lock["files"].items():
            with self.subTest(path=relative):
                self.assertEqual(
                    hashlib.sha256((checkout / relative).read_bytes()).hexdigest(),
                    evidence["sha256"],
                )
                self.assertIn(self.lock["revision"], evidence["url"])


if __name__ == "__main__":
    unittest.main()
