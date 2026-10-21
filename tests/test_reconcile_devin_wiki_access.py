from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))

from reconcile_devin_wiki_access import (  # noqa: E402
    DEVIN_APP_SLUG,
    Finding,
    Installation,
    ReconcilerError,
    Repository,
    _report,
    _summary_report,
    list_devin_installations,
    reconcile,
)


class FakeClient:
    def __init__(self, responses: dict[tuple[str, str], object] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, str]] = []

    def request(self, method: str, endpoint: str, **_: object) -> object:
        self.calls.append((method, endpoint))
        response = self.responses.get((method, endpoint), {})
        if isinstance(response, Exception):
            raise response
        return response


class DevinWikiAccessReconcilerTests(unittest.TestCase):
    def test_list_devin_installations_selects_only_the_known_app(self) -> None:
        client = FakeClient(
            {
                (
                    "GET",
                    "user/installations?per_page=100",
                ): {
                    "installations": [
                        {
                            "id": 101,
                            "app_slug": "other-app",
                            "account": {"login": "timerloggedout-spec"},
                            "repository_selection": "all",
                        },
                        {
                            "id": 202,
                            "app_slug": DEVIN_APP_SLUG,
                            "account": {"login": "timerloggedout-spec"},
                            "repository_selection": "selected",
                        },
                    ]
                }
            }
        )

        installations = list_devin_installations(client)  # type: ignore[arg-type]

        self.assertEqual([Installation(202, "timerloggedout-spec", "selected")], installations)
        self.assertEqual([("GET", "user/installations?per_page=100")], client.calls)

    def test_dry_run_reports_missing_selected_access_without_writing(self) -> None:
        repository = Repository(42, "timerloggedout-spec/new-repository", "master", False)
        installation = Installation(202, "timerloggedout-spec", "selected")
        client = FakeClient()
        with patch("reconcile_devin_wiki_access.list_accessible_repositories", return_value=[repository]), patch(
            "reconcile_devin_wiki_access.list_devin_installations", return_value=[installation]
        ), patch("reconcile_devin_wiki_access.list_installation_repository_ids", return_value=set()):
            findings = reconcile(client, source_repository="timerloggedout-spec/termux-monorepo", apply=False)  # type: ignore[arg-type]

        self.assertEqual(
            [
                Finding(
                    "timerloggedout-spec/new-repository",
                    "missing",
                    "report",
                    "Repository is not assigned to the selected Devin GitHub App installation.",
                    202,
                )
            ],
            findings,
        )
        self.assertEqual([], client.calls)

    def test_apply_uses_only_documented_installation_assignment_endpoint(self) -> None:
        repository = Repository(42, "timerloggedout-spec/new-repository", "master", False)
        installation = Installation(202, "timerloggedout-spec", "selected")
        client = FakeClient(
            {
                (
                    "PUT",
                    "user/installations/202/repositories/42",
                ): {}
            }
        )
        with patch("reconcile_devin_wiki_access.list_accessible_repositories", return_value=[repository]), patch(
            "reconcile_devin_wiki_access.list_devin_installations", return_value=[installation]
        ), patch("reconcile_devin_wiki_access.list_installation_repository_ids", return_value=set()):
            findings = reconcile(client, source_repository="timerloggedout-spec/termux-monorepo", apply=True)  # type: ignore[arg-type]

        self.assertEqual("missing", findings[0].state)
        self.assertEqual("app_access_granted", findings[0].operation)
        self.assertEqual(
            [("PUT", "user/installations/202/repositories/42")],
            client.calls,
        )

    def test_all_repository_installation_is_current_without_assignment_request(self) -> None:
        repository = Repository(42, "timerloggedout-spec/new-repository", "master", False)
        installation = Installation(202, "timerloggedout-spec", "all")
        client = FakeClient()
        with patch("reconcile_devin_wiki_access.list_accessible_repositories", return_value=[repository]), patch(
            "reconcile_devin_wiki_access.list_devin_installations", return_value=[installation]
        ):
            findings = reconcile(client, source_repository="timerloggedout-spec/termux-monorepo", apply=True)  # type: ignore[arg-type]

        self.assertEqual("current", findings[0].state)
        self.assertEqual("none", findings[0].operation)
        self.assertEqual([], client.calls)

    def test_unavailable_installation_discovery_blocks_without_assignment_attempt(self) -> None:
        repository = Repository(42, "timerloggedout-spec/new-repository", "master", False)
        client = FakeClient()
        with patch("reconcile_devin_wiki_access.list_accessible_repositories", return_value=[repository]), patch(
            "reconcile_devin_wiki_access.list_devin_installations",
            side_effect=ReconcilerError("classic PAT with repo scope required"),
        ):
            findings = reconcile(client, source_repository="timerloggedout-spec/termux-monorepo", apply=True)  # type: ignore[arg-type]

        self.assertEqual("blocked", findings[0].state)
        self.assertEqual("none", findings[0].operation)
        self.assertEqual([], client.calls)

    def test_summary_report_redacts_repository_and_installation_identifiers(self) -> None:
        findings = [
            Finding(
                "timerloggedout-spec/private-repository",
                "missing",
                "app_access_granted",
                "Internal diagnostic",
                202,
            )
        ]

        summary = _summary_report(
            _report(findings, source_repository="timerloggedout-spec/termux-monorepo", apply=True)
        )

        serialized = str(summary)
        self.assertEqual({"missing": 1}, summary["counts"])
        self.assertEqual({"app_access_granted": 1}, summary["operations"])
        self.assertNotIn("private-repository", serialized)
        self.assertNotIn("202", serialized)
        self.assertNotIn("Internal diagnostic", serialized)
        self.assertIn("provider-managed", summary["public_deepwiki"])


if __name__ == "__main__":
    unittest.main()
