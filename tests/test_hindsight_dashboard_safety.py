"""Offline database-observer and hs-dash receipt safety regressions."""
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE = ROOT / "deepcli/tools/hindsight-lifecycle"
SECTIONS = LIFECYCLE / "dashboard/sections"
DB_SECTIONS = ("00-overview.sh", "20-banks.sh", "30-extraction.sh",
               "90-integrity.sh", "99-template.sh")


class DashboardSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dashboard-safety-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.env = os.environ.copy()
        self.env.update(HOME=str(self.home), PGPASSWORD="receipt-must-not-leak",
                        DASHBOARD_RUN_ID="offline-regression")
        self.env.pop("PSQL", None)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        # Do not contact even localhost during these offline observer tests.
        self.executable("curl", "#!/bin/sh\nprintf 000\n")
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env["PATH"]

    def executable(self, name, body):
        path = self.bin / name
        path.write_text(body)
        path.chmod(0o700)
        return str(path)

    def client(self, mode):
        self.env["PSQL"] = self.executable("psql", '''#!/usr/bin/env bash
case "${FAKE_PSQL_MODE}" in
 connection) echo "$PGPASSWORD" >&2; exit 2 ;;
 sql)
  # psql script mode can otherwise exit zero despite a statement error.
  case " $* " in *" ON_ERROR_STOP=1 "*) exit 3 ;; *) exit 0 ;; esac ;;
 success)
  case " $* " in *" -X "*) ;; *) exit 91 ;; esac
  case " $* " in *" ON_ERROR_STOP=1 "*) ;; *) exit 92 ;; esac
  printf '0\\n' ;;
esac
''')
        self.env["FAKE_PSQL_MODE"] = mode

    def run_section(self, name):
        return subprocess.run(["bash", str(SECTIONS / name)], env=self.env,
                              text=True, capture_output=True, timeout=15)

    def test_missing_required_client_fails_every_db_section(self):
        for name in DB_SECTIONS:
            with self.subTest(section=name):
                result = self.run_section(name)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("unavailable", result.stdout + result.stderr)

    def test_connection_errors_fail_without_leaking_stderr(self):
        self.client("connection")
        for name in DB_SECTIONS:
            with self.subTest(section=name):
                result = self.run_section(name)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertNotIn(self.env["PGPASSWORD"], result.stdout + result.stderr)

    def test_sql_statement_errors_cannot_be_reported_as_success(self):
        self.client("sql")
        for name in DB_SECTIONS:
            with self.subTest(section=name):
                result = self.run_section(name)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_successful_db_observations_pass_with_optional_telemetry_absent(self):
        self.client("success")
        for name in DB_SECTIONS:
            with self.subTest(section=name):
                result = self.run_section(name)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_later_success_cannot_hide_an_earlier_query_failure(self):
        self.env["PSQL"] = self.executable("psql", '''#!/usr/bin/env bash
case "$*" in *memory_units*) exit 3 ;; *) echo 0 ;; esac
''')
        for name in ("00-overview.sh", "90-integrity.sh"):
            with self.subTest(section=name):
                result = self.run_section(name)
                self.assertNotEqual(result.returncode, 0, result.stdout)

    def runner(self):
        """Exercise the exact shipped receipt loop without remote bootstrap."""
        section_dir = self.home / "sections"
        section_dir.mkdir()
        for name in DB_SECTIONS:
            shutil.copyfile(SECTIONS / name, section_dir / name)
        (section_dir / "zz-following.sh").write_text("echo later-section-ran\n")
        source = (LIFECYCLE / "hs-dash").read_text()
        remote = source.split("<<'REMOTE'\n", 1)[1].rsplit("\nREMOTE", 1)[0]
        loop = remote[remote.index("fail=0; count=0"):]
        loop = loop.replace("/tmp/dashboard/sections/*.sh",
                            shlex.quote(str(section_dir)) + "/*.sh")
        return subprocess.run(["bash", "-u", "-c", loop], env=self.env,
                              text=True, capture_output=True, timeout=30)

    def test_runner_reports_failures_and_continues_after_failed_sections(self):
        self.client("sql")
        result = self.runner()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("failures:  5", result.stdout)
        self.assertIn("sections:  6", result.stdout)
        self.assertIn("later-section-ran", result.stdout)
        for name in DB_SECTIONS:
            self.assertIn("result: FAIL (" + name, result.stdout)
            self.assertNotIn("result: PASS (" + name, result.stdout)

    def test_runner_success_receipt(self):
        self.client("success")
        result = self.runner()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("failures:  0", result.stdout)
        for name in DB_SECTIONS:
            self.assertIn("result: PASS (" + name, result.stdout)


if __name__ == "__main__":
    unittest.main()
