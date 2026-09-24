import json
import tempfile
import unittest
from pathlib import Path

from ml.pipelines.lib.errors import SnapshotError
from ml.pipelines.lib.io import dump_json, load_json


class IoTests(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            dump_json(path, {"n": 1})
            self.assertEqual(load_json(path)["n"], 1)

    def test_missing(self) -> None:
        with self.assertRaises(SnapshotError):
            load_json(Path("/no/such/file.json"))
