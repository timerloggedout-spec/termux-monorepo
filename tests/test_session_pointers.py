"""Session-pointer exposure: one pointer record per feed row."""
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "sp", ROOT / "scripts/telemetry_ingest/session_pointers.py")
sp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sp)

FEED = ROOT / "ops/telemetry/session-history.jsonl"


class TestSessionPointers(unittest.TestCase):
    def test_target_kinds(self):
        chat = sp.target_for({"chat_id": "0b0272f1-x", "turn_anchor": "m1"})
        self.assertEqual(chat["kind"], "muse-message")
        pr = sp.target_for({"chat_id": "pr-3356", "turn_anchor": "body"})
        self.assertEqual(pr["kind"], "github-pr-body")
        self.assertEqual(pr["pr_number"], 3356)

    def test_feed_corpus_pointers(self):
        lines = [l for l in FEED.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 614)
        first = json.loads(lines[0])
        self.assertTrue(first["dispatch_id"].startswith("sess:"))
        self.assertEqual(len(first["content_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
