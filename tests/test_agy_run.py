"""One-shot runner contracts: only local Python fixture producers are launched."""
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts/antigravity"
sys.path.insert(0, str(SCRIPT_DIR))
from run import run
from telemetry import MAX_EVENT_BYTES


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy runner ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "run"

    def invoke(self, source, **kwargs):
        return run([sys.executable, "-c", source], self.destination, **kwargs)

    def result_source(self, status="SUCCESS", code=0):
        event = {"event": "result", "result": {"status": status,
                 "response": "PRIVATE RESPONSE", "usage": {"total_tokens": 12}}}
        return f"import sys; print({json.dumps(event)!r}); sys.exit({code})"

    def test_success_private_full_streams_and_three_lines(self):
        source = ("import sys; sys.stderr.buffer.write(b'PRIVATE STDERR\\x00\\xff'); "
                  + self.result_source())
        record, summary, code = self.invoke(source)
        self.assertEqual(code, 0)
        self.assertEqual(record["producer_exit_code"], 0)
        self.assertEqual(record["usage"]["total_tokens"], 12)
        self.assertEqual(record["usage_scope"], "run")
        self.assertEqual(record["quota"]["status"], "unknown")
        self.assertEqual((self.destination / "diagnostics.stderr").read_bytes(), b"PRIVATE STDERR\x00\xff")
        self.assertIn(b"PRIVATE RESPONSE", (self.destination / "stream.ndjson").read_bytes())
        self.assertNotIn("PRIVATE", summary + (self.destination / "record.json").read_text())
        self.assertEqual(len(summary.splitlines()), 3)
        self.assertIn("EXIT 0", summary)
        self.assertEqual(stat.S_IMODE(self.destination.stat().st_mode), 0o700)
        for path in self.destination.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual((self.destination / "steering.txt").read_text(), summary)

    def test_nonzero_process_does_not_hide_behind_success_result(self):
        record, summary, code = self.invoke(self.result_source(code=7))
        self.assertEqual(record["status"], "SUCCESS")
        self.assertEqual(record["producer_exit_code"], 7)
        self.assertEqual(code, 7)
        self.assertIn("EXIT 7", summary)
        self.assertIn("inspect private diagnostics", summary)

    def test_terminal_error_with_zero_process_is_not_success(self):
        record, summary, code = self.invoke(self.result_source("ERROR"))
        self.assertEqual(code, 1)
        self.assertEqual(record["producer_exit_code"], 0)
        self.assertIn("RUN ERROR", summary)

    def test_empty_or_truncated_zero_exit_is_incomplete(self):
        record, summary, code = self.invoke("print('partial')")
        self.assertEqual(code, 2)
        self.assertEqual(record["status"], "INCOMPLETE")
        self.assertIsNone(record["usage"]["total_tokens"])
        self.assertEqual(len(summary.splitlines()), 3)

    def test_process_failure_without_result_is_preserved(self):
        record, _, code = self.invoke("import sys; sys.exit(23)")
        self.assertEqual(code, 23)
        self.assertEqual(record["status"], "INCOMPLETE")

    def test_launch_error_is_private_and_not_retried(self):
        record, summary, code = run([str(self.root / "missing PRIVATE executable")], self.destination)
        self.assertEqual(code, 3)
        self.assertIsNone(record["producer_exit_code"])
        self.assertEqual(record["producer_launch_error"], "FileNotFoundError")
        self.assertNotIn("PRIVATE", summary)
        self.assertIn("LAUNCH FAILED", summary)

    def test_signal_return_code_is_distinct(self):
        record, summary, code = self.invoke("import os, signal; os.kill(os.getpid(), signal.SIGTERM)")
        self.assertEqual(record["producer_exit_code"], -signal.SIGTERM)
        self.assertEqual(code, 128 + signal.SIGTERM)
        self.assertIn("EXIT -15", summary)

    def test_existing_directory_prevents_launch(self):
        self.destination.mkdir()
        marker = self.root / "launched"
        with self.assertRaises(FileExistsError):
            self.invoke(f"from pathlib import Path; Path({str(marker)!r}).touch()")
        self.assertFalse(marker.exists())

    def test_symlink_directory_prevents_launch(self):
        self.destination.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            self.invoke("raise RuntimeError('must not launch')")

    def test_large_stderr_does_not_deadlock_and_oversized_stdout_is_retained(self):
        size = MAX_EVENT_BYTES * 2
        source = (f"import sys; sys.stderr.buffer.write(b'e'*{size}); "
                  f"sys.stdout.buffer.write(b'\\xff'*{size}+b'\\n'); sys.stdout.flush(); "
                  + self.result_source())
        record, _, code = self.invoke(source)
        self.assertEqual(code, 0)
        self.assertEqual(record["malformed_events"], 1)
        self.assertEqual((self.destination / "diagnostics.stderr").stat().st_size, size)
        self.assertTrue((self.destination / "stream.ndjson").read_bytes().startswith(b"\xff" * size + b"\n"))

    def test_command_arguments_are_literal_and_exactly_one_invocation(self):
        marker = self.root / "count"
        argument = f"; touch {self.root / 'injected'} $(echo SECRET)"
        source = (f"from pathlib import Path; p=Path({str(marker)!r}); "
                  "p.write_text(p.read_text()+'x' if p.exists() else 'x'); "
                  "import sys; sys.stderr.write(sys.argv[1]); " + self.result_source())
        run([sys.executable, "-c", source, argument], self.destination)
        self.assertEqual(marker.read_text(), "x")
        self.assertEqual((self.destination / "diagnostics.stderr").read_text(), argument)
        self.assertFalse((self.root / "injected").exists())

    def cli(self, *args, **kwargs):
        return subprocess.run([sys.executable, str(SCRIPT_DIR / "run.py"),
                               "--capture-dir", str(self.destination), *args],
                              capture_output=True, timeout=10, **kwargs)

    def test_explicit_command_separator_required(self):
        for args in ([], ["--"], [sys.executable, "-c", "pass"]):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.destination.exists())

    def test_cli_inherits_stdin_and_preserves_final_unterminated_line(self):
        payload = json.dumps({"event": "result", "result": {"status": "SUCCESS"}}).encode()
        result = self.cli("--", sys.executable, "-c",
                          "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())", input=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), payload)
        self.assertEqual(len(result.stdout.splitlines()), 3)
        self.assertEqual(result.stderr, b"")

    def test_invalid_quota_prevents_launch(self):
        quota = self.root / "quota.json"
        quota.write_text("[]")
        result = self.cli("--quota", str(quota), "--", sys.executable, "-c", "pass")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.destination.exists())

    def test_archive_failure_stops_producer_and_leaves_no_completion_record(self):
        processes = []
        original = subprocess.Popen

        def launch(*args, **kwargs):
            process = original(*args, **kwargs)
            processes.append(process)
            return process

        with mock.patch("run.subprocess.Popen", side_effect=launch):
            with mock.patch("run.normalize", side_effect=OSError("fixture disk failure")):
                with self.assertRaises(OSError):
                    self.invoke("import time; time.sleep(60)")
        self.assertEqual(len(processes), 1)
        self.assertIsNotNone(processes[0].poll())
        self.assertFalse((self.destination / "record.json").exists())
        self.assertFalse((self.destination / "steering.txt").exists())

    def test_latest_cumulative_result_not_sum_or_router_counter(self):
        events = [{"event": "step_update", "step_update": {"usage": {"total_tokens": 999}}},
                  {"event": "result", "result": {"status": "SUCCESS", "usage": {"total_tokens": 12}}},
                  {"event": "result", "result": {"status": "SUCCESS", "usage": {"total_tokens": 20}}}]
        record, _, _ = self.invoke(f"print({chr(10).join(map(json.dumps, events))!r})")
        self.assertEqual(record["usage"]["total_tokens"], 20)
        self.assertNotIn("router_invocations", record)
        self.assertEqual(record["quota"]["source"], "unavailable")


if __name__ == "__main__":
    unittest.main()
