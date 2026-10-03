"""LocalHindsightClient constructor + trivial async stubs."""

import asyncio
import os
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
from deepcli._v1_hindsight_local import (
    DB_DEFAULT,
    LocalHindsightClient,
)


def run(coro):
    return asyncio.run(coro)


class TestCtor(unittest.TestCase):
    def test_default_db_path(self):
        c = LocalHindsightClient()
        self.assertEqual(c.db_path, DB_DEFAULT)

    def test_custom_db_path_is_coerced_to_pathlib(self):
        c = LocalHindsightClient(db_path="/tmp/x.db")
        self.assertIsInstance(c.db_path, pathlib.Path)
        self.assertEqual(str(c.db_path), "/tmp/x.db")

    def test_explicit_bank_id_wins(self):
        c = LocalHindsightClient(bank_id="b::explicit")
        self.assertEqual(c.default_bank_id, "b::explicit")

    def test_bank_id_falls_back_to_env(self):
        os.environ["HINDSIGHT_BANK_ID"] = "b::env"
        try:
            c = LocalHindsightClient()
            self.assertEqual(c.default_bank_id, "b::env")
        finally:
            os.environ.pop("HINDSIGHT_BANK_ID", None)


class TestAsyncStubs(unittest.TestCase):
    def test_areflect_is_local_only(self):
        c = LocalHindsightClient()
        out = run(c.areflect("q"))
        self.assertTrue(out["local"])
        self.assertIsNone(out["answer"])
        self.assertEqual(out["reason"], "local-only")

    def test_aclose_is_noop(self):
        c = LocalHindsightClient()
        self.assertIsNone(run(c.aclose()))


if __name__ == "__main__":
    unittest.main()
