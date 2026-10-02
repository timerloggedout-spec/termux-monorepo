import unittest
from ml.pipelines.command_center.session import current
from ml.pipelines.operator.live import DUAL_GATE, is_observer_tip, is_product_sha

class SessionTest(unittest.TestCase):
    def test_session(self) -> None:
        s = current()
        self.assertTrue(s.session_id.startswith("20260926"))
        self.assertTrue(is_product_sha(s.product_sha))
        self.assertFalse(is_observer_tip(s.product_sha))
        self.assertEqual(DUAL_GATE["conclusion"], "success")
