import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from scripts.notation import toon_interop

class ToonInteropTests(unittest.TestCase):
    @patch("scripts.notation.toon_interop.shutil.which", return_value="/usr/bin/toon")
    @patch("scripts.notation.toon_interop.subprocess.run")
    def test_compare_reports_lossless_round_trip(self, run, _which):
        run.side_effect = [
            CompletedProcess([], 0, "users[1]{id,name}:\n  1,Ada\n", ""),
            CompletedProcess([], 0, '{"users":[{"id":1,"name":"Ada"}]}', ""),
        ]
        report = toon_interop.compare_json_to_toon(
            '{"users":[{"id":1,"name":"Ada"}]}', "/usr/bin/toon"
        )
        self.assertTrue(report["round_trip_equal"])
        self.assertEqual(report["round_trip_status"], "PASS")
        self.assertTrue(report["policy"]["json_remains_canonical"])
        self.assertEqual(run.call_count, 2)

    @patch("scripts.notation.toon_interop.subprocess.run")
    def test_compare_detects_data_loss(self, run):
        run.side_effect = [
            CompletedProcess([], 0, "name: Ada\n", ""),
            CompletedProcess([], 0, '{"name":"Eve"}', ""),
        ]
        report = toon_interop.compare_json_to_toon('{"name":"Ada"}', "/usr/bin/toon")
        self.assertFalse(report["round_trip_equal"])
        self.assertEqual(report["round_trip_status"], "FAIL")

    def test_strict_json_rejects_nan(self):
        with self.assertRaises(ValueError):
            toon_interop._strict_json_loads('{"value":NaN}')

    def test_strict_json_rejects_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
            toon_interop._strict_json_loads('{"value":1,"value":2}')

    def test_strict_json_rejects_float_overflow(self):
        with self.assertRaisesRegex(ValueError, "finite numeric range"):
            toon_interop._strict_json_loads('{"value":1e400}')

    def test_json_equality_ignores_object_key_order(self):
        self.assertTrue(toon_interop._json_equal(
            {"a": 1, "b": [True, None]}, {"b": [True, None], "a": 1.0}
        ))

    def test_json_equality_does_not_confuse_boolean_and_number(self):
        self.assertFalse(toon_interop._json_equal({"value": True}, {"value": 1}))

    @patch("scripts.notation.toon_interop.shutil.which", return_value=None)
    def test_missing_cli_fails_closed(self, _which):
        with self.assertRaises(toon_interop.InteropError):
            toon_interop._resolve_toon("toon-that-is-not-installed")

if __name__ == "__main__":
    unittest.main()
