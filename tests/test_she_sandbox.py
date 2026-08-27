"""SHE P0.5 repair sandbox planner tests — stdlib unittest."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest import TestCase, main

from she.incident import Incident, IncidentState
from she.sandbox import (
    SANDBOX_BRANCH_PREFIX,
    SandboxError,
    SandboxPlan,
    plan_repair_sandbox,
    sandbox_branch_name,
)

FIXED = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def _inc(**overrides) -> Incident:
    kwargs = dict(
        source="github.actions",
        event_provenance="workflow_run:repo-gate:failure",
        repository="timerloggedout-spec/termux-monorepo",
        ref="refs/heads/master",
        sha="deadbeefcafebabe",
        severity="high",
        classification="gate-failure",
        fingerprint="repo-gate:python-syntax",
        authority_scope=["L0-retry"],
        at=FIXED,
        incident_id="inc-sandbox-001",
    )
    kwargs.update(overrides)
    return Incident.create(**kwargs)


class SheSandboxTests(TestCase):
    def test_branch_is_isolated_and_stable(self):
        inc = _inc()
        name = sandbox_branch_name(inc)
        self.assertTrue(name.startswith(SANDBOX_BRANCH_PREFIX))
        self.assertIn("inc-sandbox-001", name)
        self.assertEqual(name, sandbox_branch_name(inc))

    def test_plan_paths_and_profiles(self):
        inc = _inc()
        plan = plan_repair_sandbox(inc)
        self.assertEqual(plan.incident_id, "inc-sandbox-001")
        self.assertEqual(plan.base_sha, "deadbeefcafebabe")
        self.assertEqual(plan.base_ref, "refs/heads/master")
        self.assertEqual(plan.worktree_path, ".she/worktrees/inc-sandbox-001")
        self.assertEqual(plan.evidence_dir, ".she/evidence/inc-sandbox-001")
        self.assertEqual(plan.credential_profile, "actions_rerun")
        self.assertEqual(plan.env_profile, "ci-linux")
        self.assertFalse(plan.mutates_source)
        self.assertFalse(plan.live)
        self.assertIn("isolated_branch_only", plan.constraints)

    def test_termux_env_profile(self):
        inc = _inc(source="termux.smoke", fingerprint="termux-smoke:pkg")
        plan = plan_repair_sandbox(inc)
        self.assertEqual(plan.env_profile, "termux-android")

    def test_dependabot_gets_no_credentials(self):
        inc = _inc(
            classification="dependabot-high",
            fingerprint="dependabot:pip:requests",
            authority_scope=["L1-repair"],
        )
        plan = plan_repair_sandbox(inc)
        self.assertEqual(plan.credential_profile, "none")

    def test_write_scope_when_explicit(self):
        inc = _inc(authority_scope=["L1-repair"])
        plan = plan_repair_sandbox(inc)
        self.assertEqual(plan.credential_profile, "write_repair_branch")

    def test_terminal_states_rejected(self):
        inc = _inc()
        inc.transition(IncidentState.QUARANTINED, by="policy")
        with self.assertRaisesRegex(SandboxError, "terminal"):
            plan_repair_sandbox(inc)

    def test_round_trip_json(self):
        plan = plan_repair_sandbox(_inc())
        raw = json.dumps(plan.to_mapping())
        restored = SandboxPlan.from_mapping(json.loads(raw))
        self.assertEqual(restored.branch, plan.branch)
        self.assertEqual(restored.worktree_path, plan.worktree_path)
        self.assertEqual(restored.credential_profile, plan.credential_profile)

    def test_from_mapping_rejects_foreign_branch(self):
        data = plan_repair_sandbox(_inc()).to_mapping()
        data["branch"] = "master"
        with self.assertRaisesRegex(SandboxError, "sandbox branch"):
            SandboxPlan.from_mapping(data)


if __name__ == "__main__":
    main()
