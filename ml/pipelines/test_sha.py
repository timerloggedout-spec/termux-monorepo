import unittest
from ml.pipelines.lib.sha import short_sha, same_sha

class ShaTest(unittest.TestCase):
    def test_short(self) -> None:
        self.assertEqual(short_sha("a3423d9760dd372967a765d16696db7cc67ca300"), "a3423d97")
    def test_same(self) -> None:
        self.assertTrue(same_sha("a3423d97", "a3423d9760dd"))

if __name__ == "__main__":
    unittest.main()
