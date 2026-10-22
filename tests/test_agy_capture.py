"""No producer or model is launched: every input here is a local fixture."""
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts/antigravity"
sys.path.insert(0, str(SCRIPT_DIR))
from capture import capture, captured_lines
from telemetry import MAX_EVENT_BYTES


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy capture ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "run"

    def test_full_bytes_private_with_separate_steering(self):
        payload = b'PRIVATE DIAGNOSTIC\x00\xff\n' + json.dumps({
            "event": "result", "result": {"status": "SUCCESS", "response": "SECRET RESPONSE",
            "usage": {"total_tokens": 12}}}).encode() + b"\n"
        diagnostics = self.root / "stderr"
        diagnostics.write_bytes(b"PRIVATE STDERR\x00\xff")
        record, summary = capture(io.BytesIO(payload), self.destination, diagnostics=diagnostics)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), payload)
        self.assertEqual((self.destination / "diagnostics.stderr").read_bytes(), diagnostics.read_bytes())
        self.assertEqual(record["usage"]["total_tokens"], 12)
        self.assertEqual(record["malformed_events"], 1)
        self.assertEqual(len(summary.splitlines()), 3)
        self.assertNotIn("SECRET", summary + (self.destination / "record.json").read_text())
        self.assertEqual(stat.S_IMODE(self.destination.stat().st_mode), 0o700)
        for path in self.destination.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_oversized_event_retained_but_not_parsed(self):
        payload = b"x" * (MAX_EVENT_BYTES * 3) + b'\n{"event":"result","result":{"status":"SUCCESS"}}'
        record, _ = capture(io.BytesIO(payload), self.destination)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), payload)
        self.assertEqual(record["malformed_events"], 1)
        self.assertEqual(record["status"], "SUCCESS")

    def test_no_overwrite(self):
        capture(io.BytesIO(b"original"), self.destination)
        with self.assertRaises(FileExistsError):
            capture(io.BytesIO(b"replacement"), self.destination)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), b"original")

    def test_destination_symlink_rejected(self):
        self.destination.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            capture(io.BytesIO(b"data"), self.destination)

    def test_chunk_boundaries_and_incomplete_utf8(self):
        class ShortReads(io.BytesIO):
            def read1(self, size):
                return super().read(min(size, 7))
        payload = 'first\nUnicode café\nlast'.encode()
        raw = io.BytesIO()
        self.assertEqual(list(captured_lines(ShortReads(payload), raw)), ["first", "Unicode café", "last"])
        self.assertEqual(raw.getvalue(), payload)

    def test_crlf_and_blanks_preserved(self):
        payload = b'\r\n{"event":"result","result":{"status":"SUCCESS"}}\r\n'
        record, _ = capture(io.BytesIO(payload), self.destination)
        self.assertEqual(record["status"], "SUCCESS")
        self.assertEqual(record["malformed_events"], 0)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), payload)

    def test_cli_incomplete_is_not_success(self):
        result = subprocess.run([sys.executable, str(SCRIPT_DIR / "capture.py"),
                                 "--capture-dir", str(self.destination)], input=b"partial",
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(len(result.stdout.decode().splitlines()), 3)
        self.assertIn("INCOMPLETE", result.stdout.decode())

    def test_failed_result_stays_failed(self):
        record, summary = capture(io.BytesIO(b'{"event":"result","result":{"status":"ERROR"}}'), self.destination)
        self.assertEqual(record["status"], "ERROR")
        self.assertIn("ERROR", summary)

    def test_giant_numbers_and_deep_json_do_not_break_capture(self):
        payload = b'{"unused":' + b'[' * 2000 + b'0' + b']' * 2001 + b'}\n'
        payload += json.dumps({"event": "result", "result": {
            "status": "SUCCESS", "duration_seconds": 10**400,
            "usage": {"total_tokens": 10**400}}}).encode()
        record, summary = capture(io.BytesIO(payload), self.destination)
        self.assertEqual((self.destination / "stream.ndjson").read_bytes(), payload)
        self.assertEqual(record["malformed_events"], 1)
        self.assertIsNone(record["duration_seconds"])
        self.assertIsNone(record["usage"]["total_tokens"])
        self.assertEqual(len(summary.splitlines()), 3)
        self.assertLess(len(summary), 500)

    def test_filter_sources_cannot_launch_cli_or_change_permissions(self):
        import ast
        for name in ("capture.py", "telemetry.py"):
            tree = ast.parse((SCRIPT_DIR / name).read_text())
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            self.assertFalse(any("subprocess" in ast.unparse(node) for node in imports))
            self.assertNotIn("settings.json", (SCRIPT_DIR / name).read_text())

    def test_cli_quota_read_errors_oversize_deep_nesting_and_non_object_fail_fast_64(self):
        cases = [
            ("missing", self.root / "nonexistent.json", None),
            ("oversize", self.root / "huge.json", b"{" + b'"a":' * 200000 + b"1" + b"}" * 200000),
            ("deep_nesting", self.root / "deep.json", b"[" * 3000 + b"0" + b"]" * 3000),
            ("non_object", self.root / "array.json", b"[1, 2, 3]"),
            ("unsupported_constant", self.root / "const.json", b'{"x": NaN}'),
            ("positive_infinity", self.root / "infinity.json", b'{"x": Infinity}'),
            ("negative_infinity", self.root / "negative-infinity.json", b'{"x": -Infinity}'),
        ]
        for name, path, content in cases:
            with self.subTest(name=name):
                if content is not None:
                    path.write_bytes(content)
                target = self.root / f"run_{name}"
                proc = subprocess.run([
                    sys.executable, str(SCRIPT_DIR / "capture.py"),
                    "--capture-dir", str(target),
                    "--quota", str(path),
                ], input=b"line1\nline2\n", capture_output=True, timeout=5)
                self.assertEqual(proc.returncode, 64, proc.stderr)
                self.assertIn("Invalid quota observation", proc.stderr.decode())
                self.assertFalse(target.exists(), f"Capture directory {target} must not be created on quota error")


if __name__ == "__main__":
    unittest.main()
