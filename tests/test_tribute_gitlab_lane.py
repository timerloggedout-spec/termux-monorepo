"""Offline planner and mocked read-only GitLab collector tests."""
import json
import subprocess
import unittest
from types import SimpleNamespace

from scripts.ci.tribute_gitlab_lane import collect, plan

SHA = "a" * 40


class GitLabTributePlannerTests(unittest.TestCase):
    def snapshot(self, **updates):
        value = {"project": {"path_with_namespace": "team/demo", "web_url": "https://gitlab.com/team/demo"},
                 "head_sha": SHA, "items": [
                     {"kind": "issue", "iid": 8, "state": "opened", "title": "Improve docs",
                      "labels": ["help wanted", "docs"], "assignees": [], "milestone": {"title": "v1"}},
                     {"kind": "merge_request", "iid": 9, "state": "opened", "title": "Fix",
                      "assignees": [{"username": "someone"}], "pipeline": {"status": "success"}},
                     {"kind": "issue", "iid": 10, "state": "closed", "title": "closed"}]}
        value.update(updates)
        return value

    def test_native_requires_allowlist_even_with_matching_canonical_evidence(self):
        canonical = {"repository": "team/demo", "head_sha": SHA}
        denied = plan(self.snapshot(), "native_gitlab", github_canonical=canonical)
        allowed = plan(self.snapshot(), "native_gitlab", {"team/demo"}, canonical)
        self.assertFalse(denied["candidates"][0]["eligible_for_review"])
        self.assertTrue(allowed["candidates"][0]["eligible_for_review"])
        self.assertIsNone(allowed["github_authority"])
        self.assertEqual(allowed["write_plan"], [])

    def test_mirror_allows_different_namespaces_but_requires_valid_identity_and_sha(self):
        canonical = {"repository": "github-owner/demo", "head_sha": SHA}
        good = plan(self.snapshot(), "github_mirror", github_canonical=canonical)
        self.assertTrue(good["candidates"][0]["eligible_for_review"])
        self.assertEqual(good["canonical_evidence"], "caller_supplied_not_independently_verified")
        for repo, sha in (("invalid-repository", SHA), ("team/demo", "abc123"), ("team/demo", "g" * 40), ("team/demo", "b" * 64)):
            bad = plan(self.snapshot(), "github_mirror", github_canonical={"repository": repo, "head_sha": sha})
            self.assertFalse(bad["candidates"][0]["eligible_for_review"])
            self.assertEqual(bad["candidates"][0]["sync_state"], "unknown")

    def test_empty_plans_preserve_disabled_collection_and_unaligned_state(self):
        snapshot = self.snapshot(items=[], collection_status={"issues": "disabled", "merge_requests": "disabled"})
        result = plan(snapshot, "github_mirror", github_canonical={"repository": "owner/demo", "head_sha": "b" * 40})
        self.assertEqual(result["collection_status"], snapshot["collection_status"])
        self.assertEqual(result["sync_state"], "unknown")
        self.assertEqual(result["write_plan"], [])

    def test_assigned_mr_observe_only_and_invalid_modes_or_urls_rejected(self):
        result = plan(self.snapshot(), "github_mirror", github_canonical={"repository": "team/demo", "head_sha": SHA})
        mr = result["candidates"][1]
        self.assertEqual(mr["plan"], "observe_only")
        self.assertEqual(mr["gitlab_pipeline_status"], "success")
        with self.assertRaises(ValueError):
            plan(self.snapshot(), "surprise")
        with self.assertRaises(ValueError):
            plan(self.snapshot(project={"path_with_namespace": "team/demo", "web_url": "https://evil.test/x"}), "native_gitlab")


class CollectorTests(unittest.TestCase):
    def test_fixed_host_metadata_scrubbing_and_url_encoded_branch(self):
        calls = []
        def runner(command, **kwargs):
            calls.append((command, kwargs))
            endpoint = command[-1]
            if endpoint == "projects/85129320":
                data = {"path_with_namespace": "team/demo", "web_url": "https://gitlab.com/team/demo", "default_branch": "feature/a b",
                        "issues_enabled": True, "merge_requests_enabled": True}
            elif "repository/commits" in endpoint:
                data = [{"id": SHA}]
            elif "/issues?" in endpoint:
                data = [{"iid": 1, "state": "opened", "title": "I", "description": "secret body", "labels": [],
                         "assignees": [{"username": "alice", "email": "hidden"}],
                         "author": {"username": "bob", "email": "hidden"},
                         "milestone": {"id": 3, "title": "v1", "description": "hidden"}}]
            else:
                data = [{"iid": 2, "state": "opened", "title": "MR", "description": "secret body", "head_pipeline": {"status": "success"}}]
            return SimpleNamespace(stdout=json.dumps(data))
        snapshot = collect(runner=runner)
        self.assertEqual(snapshot["head_sha"], SHA)
        self.assertIn("ref_name=feature%2Fa%20b", calls[1][0][-1])
        rendered = json.dumps(snapshot)
        for secret in ("description", "email", "hidden", "secret body"):
            self.assertNotIn(secret, rendered)
        item = snapshot["items"][0]
        self.assertEqual(item["author"], {"username": "bob"})
        self.assertEqual(item["assignees"], [{"username": "alice"}])
        self.assertEqual(item["milestone"], {"id": 3, "title": "v1"})
        self.assertEqual(snapshot["collection_status"], {"issues": "collected", "merge_requests": "collected"})
        self.assertEqual(len(calls), 4)
        for command, kwargs in calls:
            self.assertEqual(command[:4], ["glab", "api", "--hostname", "gitlab.com"])
            self.assertNotIn("-X", command)
            self.assertEqual(kwargs["timeout"], 20)

    def test_disabled_features_skip_endpoint_and_report_status(self):
        calls = []
        def runner(command, **kwargs):
            endpoint = command[-1]
            calls.append(endpoint)
            if endpoint == "projects/85129320":
                data = {"path_with_namespace": "team/demo", "default_branch": None,
                        "issues_enabled": True, "merge_requests_enabled": False,
                        "merge_requests_access_level": "disabled"}
            elif "/issues?" in endpoint:
                data = []
            else:
                self.fail("disabled feature endpoint must not be called")
            return SimpleNamespace(stdout=json.dumps(data))
        result = collect(runner=runner)
        self.assertEqual(result["collection_status"], {"issues": "collected", "merge_requests": "disabled"})
        self.assertEqual(calls, ["projects/85129320", "projects/85129320/issues?state=opened&per_page=100&page=1"])

    def test_enabled_or_unknown_permission_errors_propagate(self):
        for feature_metadata in ({"issues_enabled": True}, {}):
            def runner(command, **kwargs):
                endpoint = command[-1]
                if endpoint == "projects/85129320":
                    return SimpleNamespace(stdout=json.dumps({"path_with_namespace": "team/demo", "default_branch": None, **feature_metadata}))
                raise subprocess.CalledProcessError(403, command)
            with self.assertRaises(subprocess.CalledProcessError):
                collect(runner=runner)

    def test_pagination_is_capped_and_truncation_reported(self):
        pages = []
        def runner(command, **kwargs):
            endpoint = command[-1]
            if endpoint == "projects/85129320":
                data = {"path_with_namespace": "team/demo", "default_branch": None, "merge_requests_enabled": False}
            elif "/issues?" in endpoint:
                pages.append(endpoint)
                data = [{"iid": i, "state": "opened", "title": "x"} for i in range(100)]
            else:
                self.fail("unexpected endpoint")
            return SimpleNamespace(stdout=json.dumps(data))
        result = collect(max_pages=2, runner=runner)
        self.assertTrue(result["pagination_truncated"])
        self.assertEqual(len(pages), 2)
        self.assertIn("page=2", pages[-1])

    def test_rejects_nonpositive_ids_and_glab_failure_propagates(self):
        for invalid in (0, -1, True):
            with self.assertRaises(ValueError):
                collect(project_id=invalid)
        def fail(*args, **kwargs):
            raise subprocess.CalledProcessError(1, args[0])
        with self.assertRaises(subprocess.CalledProcessError):
            collect(runner=fail)


if __name__ == "__main__":
    unittest.main()
