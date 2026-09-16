"""Stacked SHE P0.2 (Dependabot, termux-smoke) + P0.3 L0 recovery tests."""
from __future__ import annotations

from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.ingest.dependabot import incident_from_dependabot, normalize_dependabot_payload
from she.ingest.termux_smoke import incident_from_termux_smoke
from she.recovery.l0 import L0_ACTIONS, plan_l0_recovery


class StackedSheTests(TestCase):
    def test_dependabot_critical(self):
        payload = {
            "alert": {
                "number": 42,
                "state": "open",
                "dependency": {"package": {"name": "lodash", "ecosystem": "npm"}},
                "security_advisory": {
                    "severity": "critical",
                    "ghsa_id": "GHSA-xxxx",
                    "cve_id": "CVE-2024-0001",
                },
                "html_url": "https://github.com/example/alert/42",
            },
            "repository": {"full_name": "timerloggedout-spec/termux-monorepo"},
        }
        fields = normalize_dependabot_payload(payload)
        self.assertEqual(fields["severity"], "high")
        self.assertTrue(fields["fingerprint"].startswith("dependabot:npm:lodash:critical"))
        inc = incident_from_dependabot(payload)
        self.assertEqual(inc.state, IncidentState.DETECTED)
        plan = plan_l0_recovery(inc)
        self.assertEqual(plan.actions, ("observe_only",))
        self.assertFalse(plan.mutates_source)

    def test_termux_smoke_failure(self):
        payload = {
            "ok": False,
            "failures": ["daemon not reachable"],
            "sha": "abc123def4567890aaaaaaaaaaaaaaaaaaaaaaaa",
            "repository": "timerloggedout-spec/termux-monorepo",
            "name": "termux-smoke",
        }
        inc = incident_from_termux_smoke(payload)
        self.assertEqual(inc.classification, "smoke-failure")
        plan = plan_l0_recovery(inc)
        self.assertIn("retry", plan.actions)
        self.assertTrue(set(plan.actions).issubset(L0_ACTIONS))

    def test_workflow_l0_retry_path(self):
        inc = Incident.create(
            source="github.actions",
            event_provenance="workflow_run:ce:failure",
            repository="timerloggedout-spec/termux-monorepo",
            ref="refs/heads/master",
            sha="deadbeefcafebabe000011112222333344445555",
            classification="workflow-failure",
            fingerprint="gha:continuous-team-evaluation:failure:deadbeefcafe",
        )
        plan = plan_l0_recovery(inc, max_attempts=2)
        self.assertEqual(plan.max_attempts, 2)
        self.assertIn("retry", plan.actions)
        self.assertFalse(plan.mutates_source)

    def test_terminal_blocks_l0(self):
        inc = Incident.create(
            source="t",
            event_provenance="t",
            repository="a/b",
            ref="refs/heads/master",
            sha="0" * 40,
        )
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(ValueError, "terminal"):
            plan_l0_recovery(inc)


if __name__ == "__main__":
    main()
