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

    def test_rest_commit_counts_preserve_single_writer_topology_states(self) -> None:
        self.assertEqual("aligned", MODULE.classify_commit_counts(0, 0))
        self.assertEqual("github-ahead", MODULE.classify_commit_counts(3, 0))
        self.assertEqual("gitlab-ahead", MODULE.classify_commit_counts(0, 2))
        self.assertEqual("diverged", MODULE.classify_commit_counts(2, 4))

    def test_native_mirror_histories_find_the_observed_shared_anchor_and_divergence_counts(self) -> None:
        original_github_get = MODULE.github_rest_get
        original_gitlab_get = MODULE.rest_get
        github_history = [{"sha": f"github-{index}"} for index in range(16)] + [{"sha": "shared-anchor"}]
        gitlab_history = [{"id": f"gitlab-{index}"} for index in range(5)] + [{"id": "shared-anchor"}]
        try:
            MODULE.github_rest_get = lambda path, token, query=None: (200, github_history)
            MODULE.rest_get = lambda path, token, query=None: (200, gitlab_history)
            overlapping, github_only, gitlab_only, detail = MODULE.mirror_history_counts(
                "github-tip", "gitlab-tip", "gitlab-token", "github-token"
            )
        finally:
            MODULE.github_rest_get = original_github_get
            MODULE.rest_get = original_gitlab_get
        self.assertTrue(overlapping)
        self.assertEqual(16, github_only)
        self.assertEqual(5, gitlab_only)
        self.assertEqual("diverged", MODULE.classify_commit_counts(github_only, gitlab_only))
        self.assertIn("share anchor shared-ancho", detail)

    def test_native_mirror_history_counts_preserve_one_sided_ahead_states(self) -> None:
        self.assertEqual("github-ahead", MODULE.classify_commit_counts(1, 0))
        self.assertEqual("gitlab-ahead", MODULE.classify_commit_counts(0, 1))

    def test_native_mirror_histories_without_overlap_remain_fail_closed(self) -> None:
        original_github_get = MODULE.github_rest_get
        original_gitlab_get = MODULE.rest_get
        try:
            MODULE.github_rest_get = lambda path, token, query=None: (200, [{"sha": "github-tip"}])
            MODULE.rest_get = lambda path, token, query=None: (200, [{"id": "gitlab-tip"}])
            overlapping, github_only, gitlab_only, detail = MODULE.mirror_history_counts(
                "github-tip", "gitlab-tip", "gitlab-token", "github-token"
            )
        finally:
            MODULE.github_rest_get = original_github_get
            MODULE.rest_get = original_gitlab_get
        self.assertFalse(overlapping)
        self.assertEqual((0, 0), (github_only, gitlab_only))
        self.assertIn("No shared commit", detail)

    def test_transport_denial_uses_rest_fallback_without_reclassifying_access(self) -> None:
        original_fetch = MODULE.fetch_gitlab_ref
        original_rest = MODULE.rest_gitlab_discovery
        try:
            MODULE.fetch_gitlab_ref = lambda ref, token: (False, "", "transport denied")
            MODULE.rest_gitlab_discovery = lambda github, ref, token, github_token: (
                "github-ahead",
                "gitlabsha",
                "GitLab Git transport was unavailable; read-only REST topology comparison succeeded.",
            )
            result = MODULE.discovery_result("githubsha", "master", "present")
        finally:
            MODULE.fetch_gitlab_ref = original_fetch
            MODULE.rest_gitlab_discovery = original_rest
        self.assertEqual("github-ahead", result.state)
        self.assertEqual("github-primary", result.lane)
        self.assertEqual("gitlabsha", result.gitlab_sha)
        self.assertIn("REST topology comparison succeeded", result.detail)

    def test_rest_merge_base_foreign_sha_uses_native_overlap_before_classifying_unrelated(self) -> None:
        for merge_base_status in (400, 404):
            with self.subTest(merge_base_status=merge_base_status):
                original_rest_get = MODULE.rest_get
                original_mirror_counts = MODULE.mirror_history_counts
                mirror_calls = []
                try:
                    def fake_rest_get(path, token, query=None):
                        if "/repository/branches/" in path:
                            return 200, {"commit": {"id": "gitlabsha"}}
                        if path.endswith("/repository/merge_base"):
                            return merge_base_status, {}
                        self.fail(f"unexpected endpoint {path}")

                    MODULE.rest_get = fake_rest_get
                    MODULE.mirror_history_counts = lambda *args: (mirror_calls.append(args) or (True, 16, 5, "Native histories share anchor shared-ancho."))
                    state, gitlab_sha, detail = MODULE.rest_gitlab_discovery("githubsha", "master", "present", "github-token")
                finally:
                    MODULE.rest_get = original_rest_get
                    MODULE.mirror_history_counts = original_mirror_counts
                self.assertEqual("diverged", state)
                self.assertEqual("gitlabsha", gitlab_sha)
                self.assertEqual(1, len(mirror_calls))
                self.assertIn("share anchor", detail)


if __name__ == "__main__":
    unittest.main()
