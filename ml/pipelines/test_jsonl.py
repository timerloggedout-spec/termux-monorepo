import tempfile
import unittest
from pathlib import Path
from ml.pipelines.replay.jsonl import append_row, read_rows
from ml.pipelines.replay.seeklog import to_seeklog
from ml.pipelines.replay.evidence import envelope

class JsonlTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "e.jsonl"
            append_row(p, {"sha": "abc", "kind": "gate"})
            rows = read_rows(p)
            self.assertEqual(rows[0]["sha"], "abc")
            self.assertEqual(to_seeklog(rows[0])["sha"], "abc")
    def test_envelope_rejects_parking(self) -> None:
        with self.assertRaises(ValueError):
            envelope("abc", {}, "HOLD")
