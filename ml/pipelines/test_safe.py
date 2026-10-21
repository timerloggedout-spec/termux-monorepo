import unittest
from ml.pipelines.lib.safe import redact

class SafeTest(unittest.TestCase):
    def test_redact(self) -> None:
        out = redact({"token": "abc", "ok": 1, "nested": {"password": "x"}})
        self.assertEqual(out["token"], "[redacted]")
        self.assertEqual(out["nested"]["password"], "[redacted]")
        self.assertEqual(out["ok"], 1)

if __name__ == "__main__":
    unittest.main()
