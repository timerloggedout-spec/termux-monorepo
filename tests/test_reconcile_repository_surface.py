from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from reconcile_repository_surface import (  # noqa: E402
    MANAGED_MARKER,
    Finding,
    ReconcilerError,
    Repository,
    _decode_content,
    _report,
    _workflow_state,
    list_accessible_repositories,
    reconcile,
)


CANONICAL = f"{MANAGED_MARKER}\nname: Publish wiki\n"


class FakeClient:
    def __init__(self, responses: dict[tuple[str, str], object]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str]] = []

    def request(self, method: str, endpoint: str, **_: object) -> object:
        self.calls.append((method, endpoint))
        response = self.responses[(method, endpoint)]
        if isinstance(response, Exception):
            raise response
        return response


class RepositorySurfaceReconcilerTests(unittest.TestCase):
    def test_list_accessible_repositories_paginates_and_sorts(self) -> None:
        first_page = [
            {"full_name": f"timerloggedout-spec/repo-{index:03d}", "default_branch": "main", "archived": False, "fork": False}
            for index in range(100)
        ]
        second_page = [{"full_name": "octo-org/z-last", "default_branch": "master", "archived": False, "fork": True}]
        client = FakeClient(
            {
                (
                    "GET",
                    "user/repos?affiliation=owner,organization_member,collaborator&sort=full_name&per_page=100&page=1",
                ): first_page,
                (
                    "GET",
                    "user/repos?affiliation=owner,organization_member,collaborator&sort=full_name&per_page=100&page=2",
                ): second_page,
            }
        )

        repositories = list_accessible_repositories(client)

        self.assertEqual(101, len(repositories))
        self.assertEqual("octo-org/z-last", repositories[0].full_name)
        self.assertEqual("timerloggedout-spec/repo-000", repositories[1].full_name)
        self.assertEqual(
            [
                ("GET", "user/repos?affiliation=owner,organization_member,collaborator&sort=full_name&per_page=100&page=1"),
                ("GET", "user/repos?affiliation=owner,organization_member,collaborator&sort=full_name&per_page=100&page=2"),
            ],
            client.calls,
        )

    def test_decode_content_accepts_github_base64_line_wrapping(self) -> None:
        source = "# managed publisher\nname: Publish wiki\n"
        wrapped = base64.encodebytes(source.encode("utf-8")).decode("ascii")
        self.assertEqual(source, _decode_content({"encoding": "base64", "content": wrapped}))

    def test_unmanaged_workflow_is_never_classified_as_writable(self) -> None:
        state, detail = _workflow_state(("name: bespoke publisher\n", "blob"), CANONICAL)
        self.assertEqual("unmanaged", state)
        self.assertIn("will not be overwritten", detail)

    def test_reconcile_default_is_read_only(self) -> None:
        repository = Repository("timerloggedout-spec/managed-repo", "master", False, True, "public")
        with patch("reconcile_repository_surface.list_accessible_repositories", return_value=[repository]), patch(
            "reconcile_repository_surface._content", return_value=None
        ), patch("reconcile_repository_surface._write_and_open_pr") as write_pr:
            findings = reconcile(
                object(),
                source_repository="timerloggedout-spec/termux-monorepo",
                canonical_workflow=CANONICAL,
                apply=False,
            )

        self.assertEqual([Finding(repository.full_name, "master", "missing", "report", "The managed publisher workflow is absent.")], findings)
        write_pr.assert_not_called()
        report = _report(findings, source_repository="timerloggedout-spec/termux-monorepo", apply=False)
        self.assertEqual("dry_run", report["mode"])
        self.assertEqual("operator-token", report["credential_lane"])

    def test_apply_opens_pull_request_only_for_missing_or_drifted_managed_workflows(self) -> None:
        missing = Repository("timerloggedout-spec/missing", "master", False, True, "public")
        unmanaged = Repository("timerloggedout-spec/bespoke", "main", False, False, "public")
        archived = Repository("timerloggedout-spec/archived", "main", True, False, "public")
        contents = {
            missing.full_name: None,
            unmanaged.full_name: ("name: bespoke\n", "blob-bespoke"),
        }
        with patch("reconcile_repository_surface.list_accessible_repositories", return_value=[missing, unmanaged, archived]), patch(
            "reconcile_repository_surface._content", side_effect=lambda _client, repo, _branch: contents.get(repo)
        ), patch(
            "reconcile_repository_surface._write_and_open_pr", return_value="https://example.test/pull/1"
        ) as write_pr:
            findings = reconcile(
                object(),
                source_repository="timerloggedout-spec/termux-monorepo",
                canonical_workflow=CANONICAL,
                apply=True,
            )

        self.assertEqual("pull_request", findings[0].operation)
        self.assertEqual("https://example.test/pull/1", findings[0].pull_request)
        self.assertEqual("unmanaged", findings[1].state)
        self.assertEqual("excluded", findings[2].state)
        write_pr.assert_called_once()
        self.assertEqual(missing, write_pr.call_args.args[1])

    def test_missing_management_marker_rejects_before_repository_reads(self) -> None:
        with patch("reconcile_repository_surface.list_accessible_repositories") as list_repositories:
            with self.assertRaises(ReconcilerError):
                reconcile(object(), source_repository="timerloggedout-spec/termux-monorepo", canonical_workflow="name: unsafe\n", apply=True)
        list_repositories.assert_not_called()


if __name__ == "__main__":
    unittest.main()
