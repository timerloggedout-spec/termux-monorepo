from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from uuid import uuid4

from hub_mcp.policy import PolicyError, get_capability
from hub_mcp.protocol import Job, JobValidationError, redact
from hub_mcp.runner import ReplayStore, execute


def payload(**overrides):
    now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
    base = {
        "job_id": str(uuid4()),
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=10)).isoformat(),
        "requested_by": "operator",
        "capability": "repository.status",
        "arguments": {},
        "approval_level": "OBSERVE",
    }
    base.update(overrides)
    return base


class HubProtocolTests(TestCase):
    def test_policy_rejects_unknown_capability(self):
        with self.assertRaisesRegex(PolicyError, "Unknown or inactive"):
            get_capability("shell.execute")

    def test_observe_job_parses_with_fixed_time(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        job = Job.from_mapping(payload(), now=now)
        self.assertEqual(job.capability, "repository.status")
        self.assertEqual(len(job.digest), 64)

    def test_expired_job_is_rejected(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        expired = payload(
            issued_at=(now - timedelta(minutes=10)).isoformat(),
            expires_at=(now - timedelta(minutes=1)).isoformat(),
        )
        with self.assertRaisesRegex(JobValidationError, "expired"):
            Job.from_mapping(expired, now=now)

    def test_unknown_job_field_is_rejected(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        with self.assertRaisesRegex(JobValidationError, "Unknown job field"):
            Job.from_mapping(payload(shell="rm -rf /"), now=now)

    def test_operate_job_requires_operate_approval(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        with self.assertRaisesRegex(JobValidationError, "requires OPERATE"):
            Job.from_mapping(payload(capability="repository.repo_gate"), now=now)

    def test_redact_common_tailscale_secret(self):
        self.assertNotIn("tskey", redact("token=tskey-api-ABCDEFGHIJKLMNOP"))

    def test_replay_store_rejects_second_execution(self):
        now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
        job = Job.from_mapping(payload(), now=now)
        with TemporaryDirectory() as directory:
            store = ReplayStore(Path(directory) / "processed_jobs.json")
            result = execute(job, Path.cwd(), store)
            self.assertTrue(result.success)
            with self.assertRaisesRegex(JobValidationError, "Replay rejected"):
                execute(job, Path.cwd(), store)


if __name__ == "__main__":
    main()
