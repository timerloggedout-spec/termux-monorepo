"""IO refuses symlink writes."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from ml.pipelines.lib.io import dump_json, load_json


class TestIo(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            dump_json(path, {"ok": True})
            self.assertEqual(load_json(path)["ok"], True)

    def test_symlink_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "real.json"
            target.write_text("{}\n", encoding="utf-8")
            link = Path(tmp) / "link.json"
            os.symlink(target.name, link)
            with self.assertRaises(OSError):
                dump_json(link, {"nope": True})


if __name__ == "__main__":
    unittest.main()
