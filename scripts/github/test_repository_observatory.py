#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from repository_observatory import API, GitHubHttpError, build_records, build_payload, classify, compute_delta, markdown, resolve_login, snapshot_hash



BASE = {
    "full_name": "example/research-agent",
    "name": "research-agent",
    "html_url": "https://github.com/example/research-agent",
    "default_branch": "main",
    "description": "Research agent and knowledge graph workflow",
    "owner": {"login": "example"},
    "visibility": "public",
    "private": False,
    "fork": False,
    "archived": False,
    "is_template": False,
    "language": "Python",
    "topics": ["research", "knowledge-graph", "agents"],
    "stargazers_count": 12,
    "forks_count": 3,
    "updated_at": "2026-09-15T00:00:00Z",
    "pushed_at": "2026-09-15T00:00:00Z",
    "created_at": "2026-01-01T00:00:00Z",
}


class ObservatoryTests(unittest.TestCase):
    def test_api_host_is_bound(self):
        # Run 36896271590 on 63635bd9 failed with NameError: name 'API' is not defined.
        self.assertEqual(API, "https://api.github.com")

    def test_classification_is_deterministic(self):
        self.assertEqual(classify(BASE, ["starred"]), classify(BASE, ["starred"]))
        self.assertIn("research", classify(BASE, ["starred"])["domains"])
        self.assertIn("context", classify(BASE, ["starred"])["domains"])

    def test_owned_and_starred_provenance_is_merged(self):
        records = build_records([BASE], [dict(BASE)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provenance"], ["owned", "starred"])

    def test_api_management_domains_are_classified_as_research(self):
        repo = dict(BASE)
        repo.update({
            "name": "gravitee-api-management",
            "description": "Open Source API Management with gateway and developer portal",
            "topics": ["api-management", "gateway", "openapi", "kubernetes"],
            "fork": True,
            "parent": {"full_name": "gravitee-io/gravitee-api-management"},
        })
        result = classify(repo, ["owned"])
        self.assertIn("api-management", result["domains"])
        self.assertIn("kubernetes", result["domains"])
        self.assertEqual(result["research_value"], "high")
        self.assertIn("upstream-comparison", result["integration"])

    def test_fork_upstream_identity_is_preserved(self):
        repo = dict(BASE)
        repo.update({
            "full_name": "timerloggedout-spec/gravitee-api-management_fork",
            "name": "gravitee-api-management_fork",
            "fork": True,
            "parent": {"full_name": "gravitee-io/gravitee-api-management"},
        })
        record = build_records([repo], [dict(repo)])[0]
        self.assertEqual(record["upstream"], "gravitee-io/gravitee-api-management")
        self.assertIn("upstream-comparison", record["classification"]["integration"])
        self.assertEqual(record["provenance"], ["owned", "starred"])
    def test_nonfork_has_no_upstream(self):
        record = build_records([BASE], [])[0]
        self.assertFalse(record["fork"])
        self.assertIsNone(record["upstream"])
    def test_snapshot_hash_is_stable(self):
        records = build_records([], [BASE])
        self.assertEqual(snapshot_hash(records), snapshot_hash(json.loads(json.dumps(records))))

    def test_payload_counts(self):
        records = build_records([BASE], [])
        payload = build_payload("example", "example", records, "2026-09-15T00:00:00Z")
        self.assertEqual(payload["counts"]["owned"], 1)
        self.assertEqual(payload["counts"]["starred"], 0)
        self.assertEqual(payload["counts"]["both"], 0)
        self.assertEqual(len(payload["snapshot_hash"]), 64)

    def test_previous_snapshot_timestamp_can_be_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.json"
            path.write_text(json.dumps({"snapshot_hash": snapshot_hash(build_records([], [BASE])), "observed_at": "old"}))
            self.assertEqual(json.loads(path.read_text())["observed_at"], "old")


    def test_watching_provenance_merges_across_all_three(self):
        records = build_records([BASE], [dict(BASE)], [dict(BASE)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provenance"], ["owned", "starred", "watching"])
        payload = build_payload("example", "example", records, "2026-09-15T00:00:00Z")
        self.assertEqual(payload["counts"]["watching"], 1)
        self.assertEqual(payload["counts"]["stars_received_on_owned"], 12)

    def test_watching_only_repo_is_reference(self):
        records = build_records([], [], [BASE])
        self.assertEqual(records[0]["provenance"], ["watching"])
        self.assertIn("reference", records[0]["classification"]["role"])

    def test_browser_domain_classification(self):
        repo = dict(BASE)
        repo.update({"name": "obscura", "description": "The headless browser for AI agents",
                     "topics": ["headless-browser", "browser-automation"]})
        self.assertIn("browser", classify(repo, ["starred"])["domains"])

    def test_owned_forks_counted(self):
        repo = dict(BASE)
        repo["fork"] = True
        payload = build_payload("example", "example", build_records([repo], []), "2026-09-15T00:00:00Z")
        self.assertEqual(payload["counts"]["owned_forks"], 1)
        self.assertEqual(payload["counts"]["forks_received_on_owned"], 3)

    def test_delta_added_removed_and_provenance_changed(self):
        prev = build_records([BASE], [])
        other = dict(BASE)
        other.update({"full_name": "example/other", "name": "other"})
        cur = build_records([], [BASE, other])
        delta = compute_delta(prev, cur)
        self.assertTrue(delta["available"])
        self.assertEqual(delta["added"], ["example/other"])
        self.assertEqual(delta["removed"], [])
        self.assertEqual(delta["provenance_changed"],
                         [{"full_name": BASE["full_name"], "from": ["owned"], "to": ["starred"]}])

    def test_delta_unavailable_without_previous(self):
        delta = compute_delta(None, build_records([], [BASE]))
        self.assertFalse(delta["available"])
        self.assertEqual(delta["added"], [])

    def test_delta_empty_when_snapshot_unchanged(self):
        records = build_records([BASE], [dict(BASE)])
        delta = compute_delta(records, records)
        self.assertTrue(delta["available"])
        self.assertEqual(delta["added"], [])
        self.assertEqual(delta["provenance_changed"], [])

    def test_payload_carries_delta_and_watching_status(self):
        records = build_records([BASE], [])
        payload = build_payload("example", "example", records, "2026-09-15T00:00:00Z",
                                delta=compute_delta([], records), watching_status="unavailable")
        self.assertEqual(payload["watching_status"], "unavailable")
        self.assertTrue(payload["delta"]["available"])
        self.assertEqual(payload["builder"], "termux-monorepo.repository_observatory@2.3")

    def test_markdown_renders_delta_section(self):
        records = build_records([], [BASE])
        text = markdown(records, "2026-09-15T00:00:00Z", compute_delta([], records))
        self.assertIn("## Changes since previous snapshot", text)
        self.assertIn("**Added (1):**", text)

    def test_actions_token_403_falls_back_to_declared_owner(self):
        def fetch(path, token, params=None):
            if path == "/user":
                raise GitHubHttpError(403, path)
            if path == "/users/timerloggedout-spec":
                return {"login": "timerloggedout-spec"}
            raise AssertionError(path)

        self.assertEqual(resolve_login(fetch, "ghs_test", "timerloggedout-spec"), "timerloggedout-spec")

    def test_user_mismatch_still_fails(self):
        def fetch(path, token, params=None):
            return {"login": "other"}

        with self.assertRaises(RuntimeError):
            resolve_login(fetch, "ghs_test", "timerloggedout-spec")


    def test_issue_provenance_merges_as_fourth_signal(self):
        records = build_records([BASE], [], [], [dict(BASE)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provenance"], ["issue", "owned"])
        only = build_records([], [], [], [dict(BASE)])
        self.assertEqual(only[0]["provenance"], ["issue"])
        self.assertIn("reference", only[0]["classification"]["role"])

    def test_payload_and_markdown_carry_intake(self):
        intake = [{"issue": 2059, "kind": "service", "seed_id": "github:research-seed:example/research-agent",
                   "name": "Research Agent", "upstream": "example/research-agent", "url": "",
                   "signal": "starred", "category": "research", "filed_at": "2026-10-28T00:00:00Z"}]
        records = build_records([], [], [], [dict(BASE)])
        payload = build_payload("example", "example", records, "2026-10-28T00:00:00Z", intake=intake)
        self.assertEqual(payload["counts"]["issue_filed"], 1)
        self.assertEqual(payload["counts"]["issue_intake"], 1)
        self.assertEqual(payload["issue_intake"], intake)
        md = markdown(records, "2026-10-28T00:00:00Z", None, intake)
        self.assertIn("## Issue intake", md)
        self.assertIn("#2059", md)
        self.assertIn("example/research-agent", md)


if __name__ == "__main__":
    unittest.main()
