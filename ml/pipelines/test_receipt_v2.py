import unittest
from ml.pipelines.command_center.receipt import receipt

class ReceiptV2Test(unittest.TestCase):
    def test_no_pulse(self) -> None:
        rec = receipt("cycle", {"ok": True})
        self.assertFalse(rec["pulse_comment"])
        self.assertEqual(rec["kind"], "cycle")
