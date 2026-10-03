"""_v1_hindsight_local: offline sqlite-backed LocalHindsightClient.

Every method is async, but the body is synchronous sqlite I/O. Tests
drive the coroutines with asyncio.run and a temp DB so the suite never
touches ~/.deepcli/bank-local.db.
"""

import asyncio
import json
import pathlib
import sqlite3
import tempfile
import unittest

import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from deepcli._v1_hindsight_local import LocalHindsightClient  # noqa: E402


SCHEMA = [
    "CREATE TABLE IF NOT EXISTS memory ("
    "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
    "  source TEXT, key TEXT, content TEXT, metadata TEXT)",
    "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5("
    "  content, content='memory', content_rowid='id')",
    "CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN "
    "  INSERT INTO memory_fts(rowid, content) VALUES (new.id, new.content); END",
]


def run(coro):
    return asyncio.run(coro)


class TestHindsightLocal(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.db = self.tmp / "bank.db"
        c = sqlite3.connect(self.db)
        for stmt in SCHEMA:
            c.execute(stmt)
        c.commit()
        c.close()
        self.client = LocalHindsightClient(db_path=self.db, bank_id="test::bank")

    def test_default_bank_id_from_env(self):
        self.assertEqual(self.client.default_bank_id, "test::bank")

    def test_retain_inserts_row_and_reports_success(self):
        out = run(self.client.aretain("hello world"))
        self.assertTrue(out["success"])
        self.assertTrue(out["local"])
        self.assertEqual(out["bank_id"], "test::bank")
        self.assertEqual(out["items_count"], 1)
        self.assertTrue(out["id"].startswith("local:"))
        c = sqlite3.connect(self.db)
        n = c.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        c.close()
        self.assertEqual(n, 1)

    def test_retain_caps_content_at_8000(self):
        run(self.client.aretain("x" * 9000))
        c = sqlite3.connect(self.db)
        (content,) = c.execute("SELECT content FROM memory").fetchone()
        c.close()
        self.assertEqual(len(content), 8000)

    def test_retain_metadata_is_stringified(self):
        run(self.client.aretain("m", metadata={"n": 7, "flag": True}))
        c = sqlite3.connect(self.db)
        (mj,) = c.execute("SELECT metadata FROM memory").fetchone()
        c.close()
        meta = json.loads(mj)
        self.assertEqual(meta["n"], "7")
        self.assertEqual(meta["flag"], "True")
        self.assertEqual(meta["bank_id"], "test::bank")
        self.assertEqual(meta["local_write"], "1")

    def test_retain_custom_bank_id_overrides_default(self):
        out = run(self.client.aretain("z", bank_id="other::bank"))
        self.assertEqual(out["bank_id"], "other::bank")

    def test_recall_empty_query_returns_no_results(self):
        out = run(self.client.arecall(""))
        self.assertEqual(out["results"], [])
        self.assertTrue(out["local"])

    def test_recall_whitespace_query_returns_no_results(self):
        out = run(self.client.arecall("   "))
        self.assertEqual(out["results"], [])

    def test_recall_finds_retained_content(self):
        run(self.client.aretain("the quick brown fox jumps"))
        out = run(self.client.arecall("brown"))
        self.assertGreaterEqual(out["count"], 1)
        hit = out["results"][0]
        self.assertIn("brown", hit["text"])
        self.assertEqual(hit["type"], "observation")
        self.assertTrue(hit["id"].startswith("local:"))

    def test_recall_honours_limit(self):
        for i in range(5):
            run(self.client.aretain(f"needle item {i}"))
        out = run(self.client.arecall("needle", limit=2))
        self.assertLessEqual(out["count"], 2)

    def test_recall_missing_fts_table_falls_back_to_like(self):
        # DB without memory_fts: the MATCH query raises OperationalError
        # and arecall must degrade to a LIKE scan instead of blowing up.
        bare = self.tmp / "bare.db"
        c = sqlite3.connect(bare)
        c.execute(
            "CREATE TABLE memory (id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "source TEXT, key TEXT, content TEXT, metadata TEXT)"
        )
        c.execute(
            "INSERT INTO memory(source,key,content,metadata) VALUES(?,?,?,?)",
            ("local_retain", "local:abc", "fallback needle", "{}"),
        )
        c.commit()
        c.close()
        client = LocalHindsightClient(db_path=bare, bank_id="b")
        out = run(client.arecall("fallback"))
        self.assertEqual(out["count"], 1)
        self.assertIn("needle", out["results"][0]["text"])

    def test_recall_malformed_metadata_json_degrades_to_empty(self):
        c = sqlite3.connect(self.db)
        c.execute(
            "INSERT INTO memory(source,key,content,metadata) VALUES(?,?,?,?)",
            ("local_retain", "local:bad", "garbled meta", "{not json"),
        )
        c.commit()
        c.close()
        out = run(self.client.arecall("garbled"))
        self.assertEqual(out["count"], 1)
        self.assertEqual(out["results"][0]["metadata"], {})

    def test_reflect_is_local_only_stub(self):
        out = run(self.client.areflect("anything"))
        self.assertIsNone(out["answer"])
        self.assertEqual(out["reason"], "local-only")
        self.assertTrue(out["local"])

    def test_aclose_is_noop(self):
        self.assertIsNone(run(self.client.aclose()))


if __name__ == "__main__":
    unittest.main()
