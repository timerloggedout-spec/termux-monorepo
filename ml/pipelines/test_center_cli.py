import json
import unittest
from ml.pipelines.cli import main
from io import StringIO
from unittest.mock import patch

class CenterCliTest(unittest.TestCase):
    def test_matrix_still_works(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            rc = main(["matrix"])
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertTrue(any(row.get("p") == 0 for row in data))
