import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "antigravity" / "settings.py"
spec = importlib.util.spec_from_file_location("agy_settings", MODULE_PATH)
settings = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = settings
spec.loader.exec_module(settings)


class PrepareTests(unittest.TestCase):
    def test_preserves_formatting_and_changes_only_value_span(self):
        raw = b'{  "verbosity" : "low",\n "toolPermission":"always-proceed", "artifactReviewPolicy" : "agent-decides", "extra": {"verbosity":"low"} }  \n'
        expected = raw.replace(b'"low"', b'"high"', 1)
        self.assertEqual(settings.prepare(raw), expected)

    def test_escaped_top_level_key_is_recognized(self):
        raw = b'{"ver\\u0062osity":"low","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}'
        self.assertEqual(settings.prepare(raw), raw.replace(b'"low"', b'"high"', 1))

    def test_nested_verbosity_does_not_satisfy_required_top_level(self):
        raw = b'{"nested":{"verbosity":"low"},"toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}'
        with self.assertRaises(settings.SettingsError):
            settings.prepare(raw)

    def test_duplicate_any_key_rejected(self):
        for raw in (
            b'{"verbosity":"low","verbosity":"high","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}',
            b'{"verbosity":"low","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides","n":{"x":1,"x":2}}',
        ):
            with self.subTest(raw=raw), self.assertRaises(settings.SettingsError):
                settings.prepare(raw)

    def test_malformed_nonfinite_wrong_policy_and_shape_rejected(self):
        valid = b'{"verbosity":"low","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}'
        cases = [b'{', valid[:-1] + b',}', valid.replace(b'"low"', b'NaN'), valid.replace(b'"low"', b'Infinity'),
                 valid.replace(b'always-proceed', b'ask'), valid.replace(b'agent-decides', b'auto'),
                 b'[]', valid.replace(b'"low"', b'1'), valid.replace(b'"verbosity"', b'"other"'),
                 b'\xef\xbb\xbf' + valid, valid + b' ' * settings.MAX_BYTES]
        for raw in cases:
            with self.subTest(raw=raw[:40]), self.assertRaises(settings.SettingsError):
                settings.prepare(raw)

    def test_high_is_idempotent(self):
        raw = b'{ \n"verbosity" : "high", "toolPermission":"always-proceed", "artifactReviewPolicy":"agent-decides" }'
        self.assertIs(settings.prepare(raw), raw)

    def test_duplicate_escaped_key_rejected(self):
        raw = br'{"verbosity":"low","ver\u0062osity":"high","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}'
        with self.assertRaises(settings.SettingsError):
            settings.prepare(raw)


class CliTests(unittest.TestCase):
    def test_cli_outputs_only_hash_receipt_and_creates_private_exclusive_file(self):
        secret = "private-setting-value-never-print"
        raw = ('{"verbosity":"low","toolPermission":"always-proceed",'
               '"artifactReviewPolicy":"agent-decides","private":"' + secret + '"}').encode()
        expected = raw.replace(b'"low"', b'"high"', 1)
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.json"
            dest = Path(temp) / "candidate.json"
            source.write_bytes(raw)
            result = subprocess.run([sys.executable, str(MODULE_PATH), "--input", str(source), "--output", str(dest)],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(dest.read_bytes(), expected)
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode), 0o600)
            self.assertEqual(result.stdout, f"BEFORE_SHA256={hashlib.sha256(raw).hexdigest()} AFTER_SHA256={hashlib.sha256(expected).hexdigest()}\n")
            self.assertNotIn(secret, result.stdout + result.stderr)
            again = subprocess.run([sys.executable, str(MODULE_PATH), "--input", str(source), "--output", str(dest)],
                                   capture_output=True, text=True, check=False)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(dest.read_bytes(), expected)

    def test_cli_rejects_symlink_output(self):
        raw = b'{"verbosity":"low","toolPermission":"always-proceed","artifactReviewPolicy":"agent-decides"}'
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            target = Path(temp) / "target"
            dest = Path(temp) / "link"
            source.write_bytes(raw)
            target.write_bytes(b"untouched")
            dest.symlink_to(target)
            result = subprocess.run([sys.executable, str(MODULE_PATH), "--input", str(source), "--output", str(dest)],
                                    capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_bytes(), b"untouched")


if __name__ == "__main__":
    unittest.main()
