import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from scripts.ci import hub_result_audit


GOOD = {
    "schema_version": 1,
    "job_id": "job-123",
    "job_digest": "a" * 64,
    "capability": "termux.smoke",
    "success": True,
    "exit_code": 0,
    "stdout": "ok\n",
    "stderr": "",
    "started_at": "2026-01-01T00:00:00Z",
    "finished_at": "2026-01-01T00:00:01Z",
    "result_digest": "b" * 64,
}


def run_main(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = hub_result_audit.main(args)
    return rc, out.getvalue(), err.getvalue()


def write_json(directory, payload):
    path = Path(directory) / "result.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


class HubResultAuditTests(unittest.TestCase):
    def test_accepts_complete_envelope_and_reports_job(self):
        with tempfile.TemporaryDirectory() as directory:
            rc, out, err = run_main([write_json(directory, GOOD)])
        self.assertEqual(rc, 0)
        self.assertEqual(err, "")
        self.assertEqual(out, "OK: audited result job-123 for termux.smoke\n")

    def test_wrong_argument_count_returns_usage_exit_two(self):
        for args in ([], ["a.json", "b.json"]):
            with self.subTest(args=args):
                rc, out, err = run_main(args)
                self.assertEqual(rc, 2)
                self.assertEqual(out, "")
                self.assertEqual(err, "Usage: hub_result_audit.py <result.json>\n")

    def test_missing_file_returns_exit_one(self):
        rc, out, err = run_main(["/nonexistent/does-not-exist.json"])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("FAIL: cannot load result envelope:"))

    def test_malformed_json_returns_exit_one(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            rc, out, err = run_main([str(path)])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("FAIL: cannot load result envelope:"))

    def test_missing_key_reported_and_exit_one(self):
        payload = dict(GOOD)
        del payload["result_digest"]
        with tempfile.TemporaryDirectory() as directory:
            rc, out, err = run_main([write_json(directory, payload)])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertIn("missing=['result_digest']", err)
        self.assertIn("unknown=[]", err)

    def test_unknown_key_reported_and_exit_one(self):
        payload = dict(GOOD)
        payload["surprise"] = 1
        with tempfile.TemporaryDirectory() as directory:
            rc, out, err = run_main([write_json(directory, payload)])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertIn("missing=[]", err)
        self.assertIn("unknown=['surprise']", err)

    def test_credential_shaped_value_rejected(self):
        for field in ("stdout", "stderr"):
            with self.subTest(field=field):
                payload = dict(GOOD)
                payload[field] = "token ghp_abcdef123456 leaked"
                with tempfile.TemporaryDirectory() as directory:
                    rc, out, err = run_main([write_json(directory, payload)])
                self.assertEqual(rc, 1)
                self.assertEqual(out, "")
                self.assertEqual(
                    err,
                    "FAIL: result contains an unredacted credential-shaped value\n",
                )

    def test_unsupported_schema_version_rejected(self):
        payload = dict(GOOD)
        payload["schema_version"] = 2
        with tempfile.TemporaryDirectory() as directory:
            rc, out, err = run_main([write_json(directory, payload)])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, "FAIL: unsupported result envelope schema\n")

    def test_non_boolean_success_rejected(self):
        payload = dict(GOOD)
        payload["success"] = 1
        with tempfile.TemporaryDirectory() as directory:
            rc, out, err = run_main([write_json(directory, payload)])
        self.assertEqual(rc, 1)
        self.assertEqual(out, "")
        self.assertEqual(err, "FAIL: unsupported result envelope schema\n")


if __name__ == "__main__":
    unittest.main()
