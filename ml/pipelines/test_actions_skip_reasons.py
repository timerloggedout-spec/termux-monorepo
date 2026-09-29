import unittest
from ml.pipelines.actions.skip_reasons import REASONS, is_non_gate_skip

class ActionsSkipTest(unittest.TestCase):
    def test_catalog(self) -> None:
        self.assertIn("dirty", REASONS)
        self.assertTrue(is_non_gate_skip("observer"))
