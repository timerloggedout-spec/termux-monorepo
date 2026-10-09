import unittest

from ml.pipelines.recon07.stamp import (
    OBSERVER_TIP,
    PRODUCT_SHA,
    is_observer_tip,
    is_product_sha,
    promotable_tip,
    stamp_report,
)


class StampTest(unittest.TestCase):
    def test_roles_do_not_collapse(self) -> None:
        self.assertTrue(is_product_sha(PRODUCT_SHA))
        self.assertTrue(is_observer_tip(OBSERVER_TIP))
        self.assertFalse(is_product_sha(OBSERVER_TIP))
        self.assertFalse(promotable_tip(OBSERVER_TIP))

    def test_report_marks_issue_stamp_stale(self) -> None:
        report = stamp_report()
        self.assertEqual(report["version"], "0.7.0")
        self.assertFalse(report["issue_body_current"])
        self.assertFalse(report["promotable_observer_tip"])


if __name__ == "__main__":
    unittest.main()
