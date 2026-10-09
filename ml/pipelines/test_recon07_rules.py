import unittest

from ml.pipelines.recon07.registry import evaluate_rules
from ml.pipelines.recon07.stamp import stamp_report


class RulesTest(unittest.TestCase):
    def test_default_context_passes(self) -> None:
        findings = evaluate_rules(stamp_report())
        failed = [row.rule_id for row in findings if not row.ok]
        self.assertEqual(failed, [])
        self.assertGreaterEqual(len(findings), 12)

    def test_force_push_fails_closed(self) -> None:
        ctx = dict(stamp_report())
        ctx["force_push"] = True
        failed = [row.rule_id for row in evaluate_rules(ctx) if not row.ok]
        self.assertIn("R02", failed)


if __name__ == "__main__":
    unittest.main()
