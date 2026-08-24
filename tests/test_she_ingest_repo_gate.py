"""SHE P0.2 repo-gate ingest tests — stdlib unittest."""
from __future__ import annotations

from unittest import TestCase, main

from she.incident import IncidentState
from she.ingest.repo_gate import (
    fingerprint_repo_gate,
    incident_from_repo_gate,
    normalize_repo_gate_payload,
)


class RepoGateIngestTests(TestCase):
    def test_fingerprint_stable(self):
        a = fingerprint_repo_gate(
            check_name="repo gate", conclusion="failure", head_sha="abcdef1234567890"
        )
        b = fingerprint_repo_gate(
            check_name="Repo Gate", conclusion="FAILURE", head_sha="abcdef1234567890xxxx"
        )
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("repo-gate:repo-gate:failure:abcdef123456"))

    def test_gate_result_shape(self):
        payload = {
            "ok": False,
            "failures": ["syntax: archwiz/linear_sync.py:237", "orphan proposal dirs"],
            "sha": "deadbeefcafebabe000011112222333344445555",
            "repository": "timerloggedout-spec/termux-monorepo",
            "ref": "master",
            "name": "repo-gate",
        }
        fields = normalize_repo_gate_payload(payload)
        self.assertEqual(fields["source"], "github.repo-gate")
        self.assertEqual(fields["severity"], "high")
        self.assertEqual(fields["classification"], "gate-failure")
        self.assertIn("repo-gate:repo-gate:failure:deadbeefcafe", fields["fingerprint"])
        self.assertEqual(fields["sha"], payload["sha"])
        self.assertTrue(fields["ref"].startswith("refs/heads/"))

        inc = incident_from_repo_gate(payload, incident_id="inc-rg-1")
        self.assertEqual(inc.state, IncidentState.DETECTED)
        self.assertEqual(inc.incident_id, "inc-rg-1")
        self.assertEqual(inc.authority_scope, ["L0-observe"])

    def test_check_run_shape(self):
        payload = {
            "check_run": {
                "name": "repo gate",
                "conclusion": "failure",
                "head_sha": "aaaabbbbccccddddeeeeffff0000111122223333",
                "html_url": "https://example.test/check/1",
            },
            "repository": {"full_name": "timerloggedout-spec/termux-monorepo"},
        }
        fields = normalize_repo_gate_payload(payload)
        self.assertEqual(fields["repository"], "timerloggedout-spec/termux-monorepo")
        self.assertIn("https://example.test/check/1", fields["evidence_refs"])
        self.assertEqual(fields["metadata"]["check_name"], "repo gate")

    def test_missing_fields_safe_defaults(self):
        fields = normalize_repo_gate_payload({"ok": False})
        self.assertEqual(fields["repository"], "unknown/unknown")
        self.assertEqual(len(fields["sha"]), 40)
        self.assertEqual(fields["severity"], "high")


if __name__ == "__main__":
    main()
