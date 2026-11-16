import os
import stat
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from uuid import uuid4

from hub_mcp.cli import main as cli_main
from hub_mcp.policy import PolicyError, get_capability
from hub_mcp.protocol import Job, JobValidationError
from hub_mcp.runner import ReplayStore, execute, execute_payload


def make_job():
    now = datetime(2026, 8, 15, 12, 0, tzinfo=UTC)
    payload = {
        "job_id": str(uuid4()),
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=10)).isoformat(),
        "requested_by": "operator",
        "capability": "repository.status",
        "arguments": {},
        "approval_level": "OBSERVE",
    }
    return Job.from_mapping(payload, now=now)


class HubMcpPrivilegeTests(TestCase):
    def test_replay_store_symlink_file_rejection(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            target_file = tmp_path / "actual_store.json"
            target_file.write_text("[]")
            symlink_store = tmp_path / "symlink_store.json"
            symlink_store.symlink_to(target_file)

            store = ReplayStore(symlink_store)
            with self.assertRaisesRegex(JobValidationError, "Symlink replay store path"):
                store.contains("job-123")

            with self.assertRaisesRegex(JobValidationError, "Symlink replay store path"):
                store.record("job-123")

    def test_replay_store_symlink_directory_rejection(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            real_dir = tmp_path / "real_dir"
            real_dir.mkdir()
            symlink_dir = tmp_path / "symlink_dir"
            symlink_dir.symlink_to(real_dir)

            store = ReplayStore(symlink_dir / "processed_jobs.json")
            with self.assertRaisesRegex(JobValidationError, "Symlink replay directory"):
                store.record("job-123")

    def test_replay_store_permissions_enforcement(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            store_dir = tmp_path / "state_dir"
            store_file = store_dir / "processed_jobs.json"

            store = ReplayStore(store_file)
            store.record("job-100")

            # Verify store_dir has 0o700 permissions
            dir_mode = stat.S_IMODE(os.stat(store_dir).st_mode)
            self.assertEqual(dir_mode, 0o700)

            # Verify store_file has 0o600 permissions
            file_mode = stat.S_IMODE(os.stat(store_file).st_mode)
            self.assertEqual(file_mode, 0o600)

    def test_render_command_path_traversal_rejection(self):
        cap = get_capability("repository.status")
        bad_path = Path("relative/../path")
        with self.assertRaisesRegex(PolicyError, "Path traversal in repository path"):
            cap.render_command(bad_path, {})

    def test_render_command_symlink_rejection(self):
        cap = get_capability("repository.status")
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            real_repo = tmp_path / "real_repo"
            real_repo.mkdir()
            symlink_repo = tmp_path / "symlink_repo"
            symlink_repo.symlink_to(real_repo)

            with self.assertRaisesRegex(PolicyError, "Symlink repository path"):
                cap.render_command(symlink_repo, {})

    def test_execute_path_traversal_rejection(self):
        job = make_job()
        with TemporaryDirectory() as tmp_dir:
            store = ReplayStore(Path(tmp_dir) / "processed_jobs.json")
            bad_path = Path("relative/../path")
            with self.assertRaisesRegex(JobValidationError, "Path traversal in repository path"):
                execute(job, bad_path, store)

    def test_execute_symlink_repository_rejection(self):
        job = make_job()
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            real_repo = tmp_path / "real_repo"
            real_repo.mkdir()
            symlink_repo = tmp_path / "symlink_repo"
            symlink_repo.symlink_to(real_repo)

            store = ReplayStore(tmp_path / "processed_jobs.json")
            with self.assertRaisesRegex(JobValidationError, "Symlink repository path"):
                execute(job, symlink_repo, store)

    def test_cli_job_path_traversal_rejection(self):
        exit_code = cli_main(["some/../job.json"])
        self.assertEqual(exit_code, 2)

    def test_cli_job_symlink_rejection(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            target = tmp_path / "actual.json"
            target.write_text("{}")
            symlink_job = tmp_path / "symlink.json"
            symlink_job.symlink_to(target)

            exit_code = cli_main([str(symlink_job)])
            self.assertEqual(exit_code, 2)

    def test_execute_payload_state_directory_traversal_rejection(self):
        with TemporaryDirectory() as tmp_dir:
            bad_state = Path(tmp_dir) / "sub/../state"
            with self.assertRaisesRegex(JobValidationError, "Path traversal in state directory"):
                execute_payload({}, Path(tmp_dir), bad_state)

    def test_execute_payload_state_directory_symlink_rejection(self):
        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            real_state = tmp_path / "real_state"
            real_state.mkdir()
            symlink_state = tmp_path / "symlink_state"
            symlink_state.symlink_to(real_state)

            with self.assertRaisesRegex(JobValidationError, "Symlink state directory"):
                execute_payload({}, tmp_path, symlink_state)


if __name__ == "__main__":
    main()
