import json
import unittest
from ml.pipelines.cli import main
from io import StringIO
from unittest.mock import patch

class CliTest(unittest.TestCase):
    def test_status(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["status"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["issue"], 175)
    def test_run(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["run"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertTrue(payload["summary"]["ok"])
    def test_gate_48(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["gate", "48"])
        self.assertEqual(code, 2)

if __name__ == "__main__":
    unittest.main()
