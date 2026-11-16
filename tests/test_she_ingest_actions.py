"""SHE P0.2 Actions ingest normalizer tests — stdlib unittest."""
from __future__ import annotations

from unittest import TestCase, main

from she.incident import IncidentState
from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)


SAMPLE_WEBHOOK = {
    "action": "completed",
    "workflow_run": {
        "id": 32770520722,
        "name": "Continuous Evaluation",
        "head_branch": "master",
        "head_sha": "0330f885e14f9c393d21c618fb4778d8913c18da",
        "path": ".github/workflows/continuous-evaluation.yml",
        "conclusion": "failure",
        "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/32770520722",
        "event": "workflow_dispatch",
    },
    "repository": {"full_name": "timerloggedout-spec/termux-monorepo"},
    "job": {"name": "discover", "conclusion": "failure"},
}


class SheIngestActionsTests(TestCase):
    def test_fingerprint_stable(self):
        a = fingerprint_workflow_run(
            workflow_name="Continuous Evaluation",
            conclusion="failure",
            head_sha="0330f885e14f9c393d21c618fb4778d8913c18da",
            job_name="discover",
        )
        b = fingerprint_workflow_run(
            workflow_name="Continuous Evaluation",
            conclusion="failure",
            head_sha="0330f885e14f9c393d21c618fb4778d8913c18da",
            job_name="discover",
        )
        self.assertEqual(a, b)
        self.assertIn("gha:continuous-evaluation:failure:0330f885e14f", a)
        self.assertIn("discover", a)

    def test_normalize_webhook_shape(self):
        fields = normalize_workflow_run_payload(SAMPLE_WEBHOOK)
        self.assertEqual(fields["source"], "github.actions")
        self.assertEqual(fields["repository"], "timerloggedout-spec/termux-monorepo")
        self.assertEqual(fields["ref"], "refs/heads/master")
        self.assertEqual(fields["sha"], "0330f885e14f9c393d21c618fb4778d8913c18da")
        self.assertEqual(fields["severity"], "high")
        self.assertEqual(fields["classification"], "workflow-failure")
        self.assertIn("actions://run/32770520722", fields["evidence_refs"])
        self.assertEqual(fields["authority_scope"], ["L0-observe"])
        self.assertIn("gha:continuous-evaluation:failure", fields["fingerprint"])
        self.assertEqual(fields["metadata"]["job_name"], "discover")

    def test_normalize_flattened_run(self):
        flat = {
            "id": 1,
            "name": "repo-gate",
            "head_branch": "master",
            "head_sha": "abc123def4567890",
            "conclusion": "success",
        }
        fields = normalize_workflow_run_payload(flat)
        self.assertEqual(fields["severity"], "medium")
        self.assertEqual(fields["classification"], "workflow-success")
        self.assertTrue(fields["fingerprint"].startswith("gha:repo-gate:success:abc123def456"))

    def test_incident_from_workflow_run(self):
        inc = incident_from_workflow_run(SAMPLE_WEBHOOK, incident_id="inc-ce-001")
        self.assertEqual(inc.state, IncidentState.DETECTED)
        self.assertEqual(inc.incident_id, "inc-ce-001")
        self.assertEqual(inc.source, "github.actions")
        self.assertEqual(inc.sha, "0330f885e14f9c393d21c618fb4778d8913c18da")
        self.assertEqual(inc.fingerprint, fingerprint_workflow_run(
            workflow_name="Continuous Evaluation",
            conclusion="failure",
            head_sha="0330f885e14f9c393d21c618fb4778d8913c18da",
            job_name="discover",
        ))
        self.assertFalse(inc.is_terminal)

    def test_missing_workflow_run_raises(self):
        with self.assertRaises(ValueError):
            normalize_workflow_run_payload({"action": "completed"})

    def test_non_mapping_raises(self):
        with self.assertRaises(TypeError):
            normalize_workflow_run_payload([])  # type: ignore[arg-type]


if __name__ == "__main__":
    main()
