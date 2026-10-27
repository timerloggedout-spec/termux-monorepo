from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from devin_wiki_indexing import (  # noqa: E402
    BranchIndex,
    DevinClient,
    GateRefusal,
    IndexingError,
    _account_summary_report,
    _report,
    _summary_report,
    check_gates,
    index_account,
    index_branches,
    main,
    parse_branch_statuses,
    projected_acu_range,
    select_branches,
)
from reconcile_devin_wiki_access import Repository as AccessibleRepository  # noqa: E402

REPO = "timerloggedout-spec/termux-monorepo"


class FakeGitHub:
    def __init__(self, branches: list[str], default: str = "master", prs: list[dict] | None = None) -> None:
        self.branches = branches
        self.default = default
        self.prs = prs or []
        self.calls: list[tuple[str, str]] = []

    def request(self, method: str, endpoint: str, **_: object) -> object:
        self.calls.append((method, endpoint))
        if endpoint.startswith(f"repos/{REPO}/branches"):
            return [{"name": name} for name in self.branches]
        if endpoint == f"repos/{REPO}":
            return {"default_branch": self.default}
        if endpoint.startswith(f"repos/{REPO}/pulls"):
            return self.prs
        raise AssertionError(f"unexpected endpoint {endpoint}")


class FakeDevin:
    def __init__(self) -> None:
        self.calls: list[tuple[str, list[str]]] = []

    def index_repository(self, org_id: str, repository: str, branch_names: list[str]) -> dict:
        self.calls.append((repository, list(branch_names)))
        return {
            "indexing_status": {
                "latest_indexes": [
                    {"branch_name": name, "status": "completed", "commit": "abc123", "job_id": "job-1"}
                    for name in branch_names
                ]
            }
        }


def pr(ref: str, full_name: str = REPO) -> dict:
    return {"head": {"ref": ref, "repo": {"full_name": full_name}}}


class SelectionTests(unittest.TestCase):
    def test_first_pass_is_default_plus_same_repo_open_pr_heads_deduped(self) -> None:
        github = FakeGitHub(
            branches=["master", "lane/a", "lane/b", "stale"],
            prs=[pr("lane/a"), pr("lane/b"), pr("lane/a"), pr("fork-only", "someone-else/fork")],
        )
        selected, skipped = select_branches(github, REPO, scope="first-pass")  # type: ignore[arg-type]
        self.assertEqual(["master", "lane/a", "lane/b"], selected)
        self.assertEqual([], skipped)

    def test_all_scope_returns_every_existing_branch(self) -> None:
        github = FakeGitHub(branches=["master", "backup/2026-01", "lane/a"])
        selected, _ = select_branches(github, REPO, scope="all")  # type: ignore[arg-type]
        self.assertEqual(["master", "backup/2026-01", "lane/a"], selected)

    def test_single_scope_skips_missing_and_unsafe_branches(self) -> None:
        github = FakeGitHub(branches=["master", "lane/a"])
        selected, skipped = select_branches(
            github, REPO, scope="single", explicit=["lane/a", "gone", "../evil"]  # type: ignore[arg-type]
        )
        self.assertEqual(["lane/a"], selected)
        self.assertEqual(["gone", "../evil"], skipped)

    def test_single_scope_requires_a_branch(self) -> None:
        github = FakeGitHub(branches=["master"])
        with self.assertRaises(IndexingError):
            select_branches(github, REPO, scope="single", explicit=[])  # type: ignore[arg-type]


class GateTests(unittest.TestCase):
    def test_missing_provisioning_names_only(self) -> None:
        with self.assertRaises(GateRefusal) as caught:
            check_gates(
                api_key=None, org_id=None, effort="low",
                scope="first-pass", approve_nonlow_effort=False, branch_count=1,
            )
        self.assertEqual("not_provisioned", caught.exception.state)
        self.assertIn("DEVIN_API_KEY", caught.exception.detail)
        self.assertIn("DEVIN_ORG_ID", caught.exception.detail)

    def test_slug_org_id_is_refused_with_copy_guidance(self) -> None:
        with self.assertRaises(GateRefusal) as caught:
            check_gates(
                api_key="cog_test", org_id="timerloggedout-spec", effort="low",
                scope="first-pass", approve_nonlow_effort=False, branch_count=1,
            )
        self.assertEqual("invalid_org_id", caught.exception.state)
        self.assertIn("Settings -> General", caught.exception.detail)

    def test_unrecorded_effort_blocks_any_run(self) -> None:
        with self.assertRaises(GateRefusal) as caught:
            check_gates(
                api_key="cog_test", org_id="org-123", effort=None,
                scope="first-pass", approve_nonlow_effort=False, branch_count=1,
            )
        self.assertEqual("effort_unrecorded", caught.exception.state)

    def test_bulk_at_medium_effort_needs_approval_and_projects_acus(self) -> None:
        with self.assertRaises(GateRefusal) as caught:
            check_gates(
                api_key="cog_test", org_id="org-123", effort="medium",
                scope="all", approve_nonlow_effort=False, branch_count=1726,
            )
        self.assertEqual("cost_gate", caught.exception.state)
        self.assertIn("8630-17260 ACUs", caught.exception.detail)
        approved = check_gates(
            api_key="cog_test", org_id="org-123", effort="medium",
            scope="all", approve_nonlow_effort=True, branch_count=1726,
        )
        self.assertEqual("medium", approved)

    def test_bulk_at_low_effort_passes_and_first_pass_at_high_passes(self) -> None:
        self.assertEqual(
            "low",
            check_gates(
                api_key="cog_test", org_id="org-123", effort="low",
                scope="all", approve_nonlow_effort=False, branch_count=1726,
            ),
        )
        self.assertEqual(
            "high",
            check_gates(
                api_key="cog_test", org_id="org-123", effort="high",
                scope="first-pass", approve_nonlow_effort=False, branch_count=82,
            ),
        )

    def test_projection_math(self) -> None:
        self.assertEqual((0, 0), projected_acu_range("low", 1726))
        self.assertEqual((410, 820), projected_acu_range("medium", 82))
        self.assertEqual((34520, 69040), projected_acu_range("high", 1726))


class IndexingTests(unittest.TestCase):
    def test_index_branches_chunks_at_fifty_and_parses_statuses(self) -> None:
        devin = FakeDevin()
        branches = [f"branch-{index:03d}" for index in range(120)]
        results = index_branches(devin, org_id="org-123", repository=REPO, branches=branches)  # type: ignore[arg-type]
        self.assertEqual([50, 50, 20], [len(call[1]) for call in devin.calls])
        self.assertEqual(120, len(results))
        self.assertTrue(all(result.status == "completed" for result in results))
        self.assertTrue(all(result.commit == "abc123" for result in results))

    def test_parse_statuses_marks_unreported_branches(self) -> None:
        response = {"indexing_status": {"latest_indexes": [
            {"branch_name": "master", "status": "running", "commit": "def456", "job_id": "job-9"}
        ]}}
        results = parse_branch_statuses(response, ["master", "lane/a"])
        self.assertEqual(
            [BranchIndex("master", "running", "def456", "job-9"), BranchIndex("lane/a", "not_reported")],
            results,
        )

    def test_client_retries_404_with_encoded_repository_path_only(self) -> None:
        import io
        import urllib.error
        from unittest.mock import patch

        import devin_wiki_indexing as module

        calls: list[str] = []

        class _Response:
            def __enter__(self) -> "_Response":
                return self

            def __exit__(self, *args: object) -> bool:
                return False

            def read(self) -> bytes:
                return b'{"indexing_status": {"latest_indexes": []}}'

        def fake_urlopen(request: object, timeout: int = 0) -> _Response:
            url = str(getattr(request, "full_url"))
            calls.append(url)
            if "%2F" not in url:
                raise urllib.error.HTTPError(url, 404, "not found", {}, io.BytesIO(b"nope"))  # type: ignore[arg-type]
            return _Response()

        client = DevinClient("cog_test")
        with patch.object(module.urllib.request, "urlopen", fake_urlopen):
            client.index_repository("org-123", REPO, ["master"])
        self.assertEqual(2, len(calls))
        self.assertIn("timerloggedout-spec%2Ftermux-monorepo", calls[1])

        calls.clear()

        def fake_403(request: object, timeout: int = 0) -> _Response:
            url = str(getattr(request, "full_url"))
            calls.append(url)
            raise urllib.error.HTTPError(url, 403, "forbidden", {}, io.BytesIO(b"denied"))  # type: ignore[arg-type]

        with patch.object(module.urllib.request, "urlopen", fake_403):
            with self.assertRaises(IndexingError):
                client.index_repository("org-123", REPO, ["master"])
        self.assertEqual(1, len(calls))

    def test_indexing_is_additive_only_no_delete_surface(self) -> None:
        self.assertFalse(hasattr(DevinClient, "delete"))
        self.assertFalse(hasattr(DevinClient, "remove"))

    def test_summary_redacts_org_commits_and_jobs(self) -> None:
        report = _report(
            repository=REPO, scope="first-pass", effort="low", mode="apply",
            selected=["master"], skipped=[],
            results=[BranchIndex("master", "completed", "abc123", "job-1")],
        )
        summary = _summary_report(report)
        serialized = str(summary)
        self.assertEqual({"completed": 1}, summary["status_counts"])
        self.assertNotIn("abc123", serialized)
        self.assertNotIn("job-1", serialized)
        self.assertTrue(summary["additive_only"])


class AccountGateTests(unittest.TestCase):
    def test_account_wide_at_medium_needs_approval_even_for_first_pass(self) -> None:
        with self.assertRaises(GateRefusal) as caught:
            check_gates(
                api_key="cog_test", org_id="org-123", effort="medium",
                scope="first-pass", approve_nonlow_effort=False, branch_count=1400,
                account_wide=True,
            )
        self.assertEqual("cost_gate", caught.exception.state)
        self.assertIn("7000-14000 ACUs", caught.exception.detail)

    def test_account_wide_at_low_is_free_and_passes(self) -> None:
        self.assertEqual(
            "low",
            check_gates(
                api_key="cog_test", org_id="org-123", effort="low",
                scope="all", approve_nonlow_effort=False, branch_count=5000,
                account_wide=True,
            ),
        )


class FakeGitHubGeneric:
    def __init__(self, branches_by_repo: dict[str, list[str]]) -> None:
        self.branches_by_repo = branches_by_repo

    def request(self, method: str, endpoint: str, **_: object) -> object:
        for full_name, branches in self.branches_by_repo.items():
            if endpoint.startswith(f"repos/{full_name}/branches"):
                return [{"name": name} for name in branches]
            if endpoint == f"repos/{full_name}":
                return {"default_branch": branches[0]}
            if endpoint.startswith(f"repos/{full_name}/pulls"):
                return []
        raise AssertionError(f"unexpected endpoint {endpoint}")


class SelectiveDevin(FakeDevin):
    def index_repository(self, org_id: str, repository: str, branch_names: list[str]) -> dict:
        if repository == "owner/broken":
            raise IndexingError("Devin indexing request failed: http 403: denied")
        return super().index_repository(org_id, repository, branch_names)


class AccountIndexingTests(unittest.TestCase):
    def test_account_indexes_all_repos_skips_archived_and_isolates_failures(self) -> None:
        inventory = [
            AccessibleRepository(1, "owner/one", "master", False),
            AccessibleRepository(2, "owner/broken", "master", False),
            AccessibleRepository(3, "owner/old", "master", True),
        ]
        github = FakeGitHubGeneric({"owner/one": ["master", "lane/a"], "owner/broken": ["master"]})
        devin = SelectiveDevin()
        with patch("devin_wiki_indexing.list_accessible_repositories", return_value=inventory):
            report = index_account(devin, github, org_id="org-123", scope="all", effort="low")  # type: ignore[arg-type]
        self.assertTrue(report["account_wide"])
        self.assertEqual(2, report["repository_count"])
        self.assertEqual(1, report["failed_repository_count"])
        self.assertEqual(3, report["branch_count"])
        self.assertEqual({"completed": 2}, report["status_counts"])
        self.assertEqual("partial", report["state"])

    def test_account_dry_run_selects_without_devin_calls(self) -> None:
        inventory = [AccessibleRepository(1, "owner/one", "master", False)]
        github = FakeGitHubGeneric({"owner/one": ["master", "lane/a"]})
        with patch("devin_wiki_indexing.list_accessible_repositories", return_value=inventory):
            report = index_account(None, github, org_id="", scope="all", effort="low")  # type: ignore[arg-type]
        self.assertEqual("dry_run", report["mode"])
        self.assertEqual(2, report["branch_count"])

    def test_account_summary_redacts_repository_names(self) -> None:
        inventory = [AccessibleRepository(1, "owner/secret-project", "master", False)]
        github = FakeGitHubGeneric({"owner/secret-project": ["master"]})
        devin = FakeDevin()
        with patch("devin_wiki_indexing.list_accessible_repositories", return_value=inventory):
            report = index_account(devin, github, org_id="org-123", scope="all", effort="low")  # type: ignore[arg-type]
        summary = _account_summary_report(report)
        self.assertNotIn("secret-project", str(summary))
        self.assertEqual(1, summary["repository_count"])
        self.assertEqual(1, summary["branch_count"])

    def test_cli_requires_exactly_one_target(self) -> None:
        with self.assertRaises(IndexingError):
            main(["--report", "unused.json"])
        with self.assertRaises(IndexingError):
            main(["--repo", REPO, "--all-repos", "--report", "unused.json"])


if __name__ == "__main__":
    unittest.main()
