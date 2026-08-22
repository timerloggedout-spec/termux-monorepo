from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "ci" / "recon_intel_discovery.py"
SPEC = importlib.util.spec_from_file_location("recon_intel_discovery", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ReconIntelDiscoveryTests(unittest.TestCase):
    def classify(self, github: str, gitlab: str, merge_bases: set[frozenset[str]], ancestors: set[tuple[str, str]]) -> str:
        return MODULE.classify_topology(
            github,
            gitlab,
            lambda left, right: frozenset((left, right)) in merge_bases,
            lambda left, right: (left, right) in ancestors,
        )

    def test_identical_sha_is_aligned(self) -> None:
        self.assertEqual("aligned", self.classify("abc", "abc", set(), set()))

    def test_gitlab_ancestor_means_github_ahead(self) -> None:
        self.assertEqual(
            "github-ahead",
            self.classify("github", "gitlab", {frozenset(("github", "gitlab"))}, {("gitlab", "github")}),
        )

    def test_github_ancestor_means_gitlab_ahead(self) -> None:
        self.assertEqual(
            "gitlab-ahead",
            self.classify("github", "gitlab", {frozenset(("github", "gitlab"))}, {("github", "gitlab")}),
        )

    def test_shared_history_without_ancestry_is_diverged(self) -> None:
        self.assertEqual(
            "diverged",
            self.classify("github", "gitlab", {frozenset(("github", "gitlab"))}, set()),
        )

    def test_absent_merge_base_is_no_common_ancestor(self) -> None:
        self.assertEqual("no-common-ancestor", self.classify("github", "gitlab", set(), set()))

    def test_missing_token_is_non_destructive_not_configured_result(self) -> None:
        result = MODULE.discovery_result("deadbeef", "master", "")
        self.assertEqual("not-configured", result.state)
        self.assertEqual("not-configured", result.lane)
        self.assertEqual("", result.gitlab_sha)
        self.assertIn("advisory only", result.detail)

    def test_non_allowlisted_ref_is_rejected_before_fetch(self) -> None:
        result = MODULE.discovery_result("deadbeef", "feature/untrusted", "present")
        self.assertEqual("external-access-denied", result.state)
        self.assertEqual("", result.gitlab_sha)
        self.assertIn("not allowlisted", result.detail)


if __name__ == "__main__":
    unittest.main()
