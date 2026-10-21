import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "agentic"))
import flywheel


def plan():
    def phase(pid, deps=(), approval=False):
        return {"phase_id": pid, "title": f"Phase {pid}", "description": "Offline test phase", "project": {"title_marker": pid},
                "approval_required": approval, "depends_on": list(deps),
                "completion": {"required_checks": ["ci"], "merged_pr": True},
                "execution": {"mode": "agent", "preferred_agent": "worker"}}
    return {"schema_version": 1, "plan_id": "test", "title": "Offline test", "base_branch": "master",
            "project": {"owner": "owner", "number": 1, "id": "P1", "url": "https://example.test", "status_field_id": "S1",
                        "status_options": {"Todo": "t", "In progress": "i", "Done": "d"}},
            "policy": {"dispatch_agents": ["worker"]}, "phases": [phase("PH-B"), phase("PH-A"), phase("PH-C", ["PH-A"], True)]}


class FlywheelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.plan_path = Path(self.temp.name) / "plan.json"
        self.snapshot_path = Path(self.temp.name) / "snapshot.json"
        self.plan_path.write_text(json.dumps(plan()))
        self.snapshot_path.write_text(json.dumps({}))

    def test_deterministic_triage_and_handoff_key(self):
        result, code = flywheel.make_report(plan(), {}, None, False)
        self.assertEqual(code, 0)
        self.assertEqual([(x["wave"], x["phase_id"]) for x in result["triage"]], [(0, "PH-A"), (0, "PH-B"), (1, "PH-C")])
        self.assertEqual(result["receipt"]["selected_phase"], "PH-A")
        self.assertEqual(result["handoff"]["idempotency_key"], result["receipt"]["idempotency_key"])
        self.assertEqual(result["receipt"]["task_outcome"], "UNKNOWN")
        self.assertFalse(result["receipt"]["deployed"])

    def test_blocked_dependency_approval_and_claims_prevent_execution(self):
        p = plan()
        snapshot = {"claims": [{"idempotency_key": f"PH-A:{flywheel.plan_digest(p)}", "active": True}],
                    "approvals": {"PH-C": False}}
        report, code = flywheel.make_report(p, snapshot, "PH-A", True)
        self.assertEqual(code, 1)
        self.assertEqual(report["receipt"]["execution_status"], "BLOCKED")
        self.assertEqual(report["receipt"]["gates"], [])
        report, code = flywheel.make_report(p, {}, "PH-C", True)
        self.assertEqual(code, 1)

    def test_invalid_plan_and_unknown_phase_are_rejected(self):
        with self.assertRaises(Exception):
            flywheel.make_report({}, {}, None, False)
        with self.assertRaises(ValueError):
            flywheel.make_report(plan(), {}, "NOT-HERE", False)

    def test_fixed_allowlist_no_plan_command_and_exit_codes_only(self):
        with mock.patch.object(flywheel, "lock_path", return_value=Path(self.temp.name) / "lock"), mock.patch.object(flywheel, "run_gates", return_value=("PASS", [{"gate": "repo_gate", "exit_code": 0, "output_sha256": "x"}])) as gates:
            report, code = flywheel.make_report(plan(), {}, "PH-A", True)
        self.assertEqual(code, 0)
        gates.assert_called_once_with()
        self.assertEqual(report["receipt"]["execution_status"], "PASS")
        self.assertNotIn('"output":', json.dumps(report))
        self.assertFalse(report["receipt"]["feedback_posted"])

    def test_timeout_and_failed_gate(self):
        with mock.patch.object(flywheel.subprocess, "run", side_effect=subprocess.TimeoutExpired(["gate"], 1, output=b"secret")):
            status, outputs = flywheel.run_gates()
        self.assertEqual(status, "FAIL")
        self.assertNotIn("secret", json.dumps(outputs))
        self.assertNotIn("output", outputs[0])

    def test_lock_conflict_blocks_and_lock_releases(self):
        lock_path = Path(self.temp.name) / "lock"
        with mock.patch.object(flywheel, "lock_path", return_value=lock_path):
            with lock_path.open("a") as locked:
                import fcntl
                fcntl.flock(locked.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                result, code = flywheel.make_report(plan(), {}, "PH-A", True)
            self.assertEqual(code, 1)
            self.assertEqual(result["receipt"]["execution_status"], "BLOCKED")
            with lock_path.open("a") as second:
                fcntl.flock(second.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(second.fileno(), fcntl.LOCK_UN)

    def test_cli_outputs_json_and_status(self):
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/agentic/flywheel.py"), "--plan", str(self.plan_path), "--snapshot", str(self.snapshot_path)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["receipt"]["mode"], "report")
        self.assertEqual(result["receipt"]["execution_status"], "NOT_RUN")
        self.assertEqual(result["receipt"]["task_outcome"], "UNKNOWN")

    def test_snapshot_change_blocks_before_gates(self):
        self.snapshot_path.write_text(json.dumps({"approvals": {"PH-C": True}}))
        with mock.patch.object(flywheel, "lock_path", return_value=Path(self.temp.name) / "lock"), mock.patch.object(flywheel, "run_gates") as gates:
            report, code = flywheel.make_report(plan(), {}, "PH-A", True, snapshot_file=self.snapshot_path)
        self.assertEqual(code, 1)
        self.assertEqual(report["receipt"]["status"], "BLOCKED")
        self.assertEqual(report["receipt"]["snapshot_sha256"], flywheel.plan_digest({}))
        gates.assert_not_called()

    def test_source_change_fails_even_when_gates_pass(self):
        with mock.patch.object(flywheel, "lock_path", return_value=Path(self.temp.name) / "lock"), mock.patch.object(flywheel, "source_provenance", side_effect=[{"repository_head": "a"}, {"repository_head": "a"}, {"repository_head": "b"}]), mock.patch.object(flywheel, "run_gates", return_value=("PASS", [])):
            report, code = flywheel.make_report(plan(), {}, "PH-A", True)
        self.assertEqual(code, 1)
        self.assertEqual(report["receipt"]["status"], "FAIL")
        self.assertEqual(report["receipt"]["repository_head"], "a")

    def test_commands_are_fixed_and_failure_stops_loop(self):
        completed = subprocess.CompletedProcess([], 2, stdout=b"private diagnostic")
        with mock.patch.object(flywheel.subprocess, "run", return_value=completed) as run:
            status, gates = flywheel.run_gates()
        self.assertEqual(status, "FAIL")
        self.assertEqual(len(gates), 1)
        args, kwargs = run.call_args
        self.assertEqual(args[0], [sys.executable, str(ROOT / "scripts/ci/repo_gate.py")])
        self.assertIs(kwargs["shell"], False)
        self.assertEqual(gates[0]["exit_code"], 2)
        self.assertNotIn("private diagnostic", json.dumps(gates))

    def test_cli_errors_do_not_echo_private_input(self):
        self.snapshot_path.write_text("private secret invalid json")
        completed = subprocess.run([sys.executable, str(ROOT / "scripts/agentic/flywheel.py"), "--plan", str(self.plan_path), "--snapshot", str(self.snapshot_path), "--execute"], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertNotIn("private secret", completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["receipt"]["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
