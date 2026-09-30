import unittest
from ml.pipelines.operator.live import OBSERVER_TIP, PRODUCT_SHA, is_observer_tip, is_product_sha

class OperatorLiveTest(unittest.TestCase):
    def test_shas(self) -> None:
        self.assertTrue(is_product_sha(PRODUCT_SHA))
        self.assertTrue(is_observer_tip(OBSERVER_TIP))
        self.assertNotEqual(PRODUCT_SHA, OBSERVER_TIP)
