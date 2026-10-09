import json
import unittest
from io import StringIO
from unittest.mock import patch

from ml.pipelines.cli import main


class ReconCliTest(unittest.TestCase):
    def test_recon_command(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["recon"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["version"], "0.7.0")
        self.assertFalse(payload["promotable_observer_tip"])

    def test_steward_command(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["steward"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertFalse(payload["writes"])
        self.assertEqual(payload["rules_failed"], [])


if __name__ == "__main__":
    unittest.main()
