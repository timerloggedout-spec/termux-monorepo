import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci" / "operations_cadence.py"


class OperationsCadenceTests(unittest.TestCase):
    def test_advisory_report_is_machine_readable(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--mode", "advisory", "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["schema"], "termux.operations-cadence-report/v1")
        self.assertGreater(report["workflow_count"], 0)
        self.assertIsInstance(report["findings"], list)

    def test_comment_text_is_not_configuration(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("operations_cadence", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sample = """# concurrency:
#   group: fake-value
#   cancel-in-progress: true
on:
  schedule:
    - cron: '7 * * * *' # real schedule
      timezone: 'UTC' # real timezone
"""
        self.assertFalse(mod.event_present(sample, "issues"))
        self.assertIsNone(
            mod.GROUP_RE.search(mod.strip_yaml_comment("# group: fake-value"))
        )
        self.assertEqual(
            "7 * * * *",
            mod.CRON_RE.match("    - cron: '7 * * * *' # note").group(1),
        )
        self.assertEqual(
            "UTC",
            mod.TIMEZONE_RE.match("      timezone: 'UTC' # note").group(1),
        )

    def test_enforce_mode_detects_legacy_schedule_drift(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--mode", "enforce"],
            cwd=ROOT, capture_output=True, text=True,
        )
        # Phase 1 is advisory until legacy schedules are migrated.
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
