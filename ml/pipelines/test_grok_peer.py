import unittest
from ml.pipelines.peers.grok import IDENTITY, is_operator_extract
from ml.pipelines.peers.registry import classify_login

class GrokPeerTest(unittest.TestCase):
    def test_identity(self) -> None:
        self.assertIn("Grok", IDENTITY)
        self.assertTrue(is_operator_extract("feat(ml): keep-alive"))
        self.assertEqual(classify_login("timerloggedout-spec"), "operator")
