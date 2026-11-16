import unittest
from ml.pipelines.command_center.bind import bind, require_this_sha

class BindTest(unittest.TestCase):
    def test_green_on_product_sha(self) -> None:
        checks = [
            {"name": "repo gate", "conclusion": "success"},
            {"name": "termux smoke", "conclusion": "success"},
        ]
        out = bind("8d36f149214f4a147932188bc424e7c29b8de444", checks)
        self.assertEqual(out["dual_gate"], "GREEN")
        self.assertTrue(out["promotable"])
    def test_old_evidence_does_not_authorize_new(self) -> None:
        self.assertFalse(require_this_sha("aaa", "bbb"))
        self.assertTrue(require_this_sha("abc", "abc"))
