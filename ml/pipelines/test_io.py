import json
import tempfile
import unittest
from pathlib import Path
from ml.pipelines.lib.io import dump_json, load_json

class IoTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.json"
            dump_json(path, {"ok": True})
            self.assertEqual(load_json(path)["ok"], True)

if __name__ == "__main__":
    unittest.main()
