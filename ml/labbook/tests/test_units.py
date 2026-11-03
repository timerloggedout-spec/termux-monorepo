"""Unit tests for labbook primitives: CAS, formats, yaml subset, gates,
catalog, ledger. Run: python -m unittest discover -s tests -v"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from labbook import formats, gates, yamlmini
from labbook.cas import CAS
from labbook.catalog import Catalog
from labbook.errors import LabbookError
from labbook.ledger import Ledger


class TestCAS(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.cas = CAS(os.path.join(self.td.name, "store"))

    def tearDown(self):
        self.td.cleanup()

    def test_roundtrip_and_dedup(self):
        h = self.cas.put(b"payload")
        self.assertEqual(self.cas.get(h), b"payload")
        self.assertEqual(self.cas.put(b"payload"), h)
        self.assertTrue(self.cas.has(h))

    def test_missing_bytes_fail_loudly_by_hash(self):
        with self.assertRaises(LabbookError) as cm:
            self.cas.get("ab" * 32)
        self.assertIn("ab" * 32, str(cm.exception))

    def test_corruption_fails_loudly(self):
        h = self.cas.put(b"payload")
        with open(self.cas.path(h), "r+b") as f:
            f.write(b"X")
        with self.assertRaises(LabbookError):
            self.cas.get(h)


class TestFormats(unittest.TestCase):
    def test_csv_roundtrip_exact_floats(self):
        rows = [{"x": 0.1, "y": 3, "s": "a"}, {"x": -2.25, "y": 4, "s": "b"}]
        self.assertEqual(formats.read("csv", formats.write("csv", rows)), rows)

    def test_json_npz_text_roundtrip(self):
        self.assertEqual(
            formats.read("json", formats.write("json", {"a": [1.5]})),
            {"a": [1.5]})
        self.assertEqual(
            formats.read("npz", formats.write("npz", {"w": [1.0, 2.5]})),
            {"w": [1.0, 2.5]})
        self.assertEqual(
            formats.read("text", formats.write("text", "hi")), "hi")

    def test_pickle_class_is_flagged_and_named(self):
        self.assertTrue(formats.is_pickle_class("pickle-class"))
        self.assertFalse(formats.is_pickle_class("json"))
        self.assertEqual(formats.reader_path("pickle-class"),
                         "labbook.formats:read_pickle")

    def test_unknown_format_named(self):
        with self.assertRaises(LabbookError) as cm:
            formats.write("parquet-ish", 1)
        self.assertIn("parquet-ish", str(cm.exception))


class TestYaml(unittest.TestCase):
    def test_roundtrip(self):
        doc = {"a": 1, "b": {"c": [1, 2], "d": "x < 1.0"},
               "e": [{"name": "n", "gate": None}], "f": True}
        self.assertEqual(yamlmini.load(yamlmini.dump(doc)), doc)


class TestGates(unittest.TestCase):
    def test_evaluate_and_inputs_recorded(self):
        result, used = gates.evaluate("cv < 1.0 and k == 2",
                                      {"cv": 0.29, "k": 2})
        self.assertTrue(result)
        self.assertEqual(used, {"cv": 0.29, "k": 2})

    def test_unknown_name_is_named(self):
        with self.assertRaises(LabbookError) as cm:
            gates.evaluate("nope > 1", {"a": 1})
        self.assertIn("nope", str(cm.exception))

    def test_code_is_refused(self):
        with self.assertRaises(LabbookError):
            gates.evaluate("__import__('os')", {})


class TestCatalog(unittest.TestCase):
    def test_from_dict_and_list(self):
        cat = Catalog.from_dict({
            "dataset": {"kind": "dataset", "format": "csv"},
            "blob": {"kind": "model", "format": "pickle-class"}})
        listing = cat.list()
        self.assertEqual([e["name"] for e in listing], ["blob", "dataset"])
        self.assertEqual(cat["dataset"]["reader"], "labbook.formats:read_csv")

    def test_unknown_asset_named(self):
        cat = Catalog.from_dict({})
        with self.assertRaises(LabbookError) as cm:
            cat["ghost"]
        self.assertIn("ghost", str(cm.exception))


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.led = Ledger(os.path.join(self.td.name, "ledger.db"))

    def tearDown(self):
        self.led.close()
        self.td.cleanup()

    def _run(self):
        return self.led.create_run(
            ir_hash="h", pipeline_name="p", stack_name="local",
            code_sha="git:abc", env_spec="{}", params={"a": 1},
            actor="test", cache_policy="per-artifact-store")

    def test_lifecycle_stamps(self):
        rid = self._run()
        self.led.stamp_lifecycle(rid, "running")
        rec = self.led.get_run(rid)
        self.assertEqual(rec["lifecycle"], "running")
        self.assertIsNotNone(rec["started_at"])
        self.led.stamp_lifecycle(rid, "completed")
        rec = self.led.get_run(rid)
        self.assertEqual(rec["lifecycle"], "completed")
        self.assertIsNotNone(rec["finished_at"])

    def test_materialization_history_is_append_only(self):
        rid = self._run()
        self.led.ensure_asset("m", "model", "json")
        for i in range(2):
            self.led.record_materialization(
                asset_name="m", run_id=rid, node_name="n", instance="",
                content_hash=f"{i}" * 64, size_bytes=3, store_path="/x",
                reader="labbook.formats:read_json", typed_metadata={"i": i},
                input_hashes=[], cache_key=None)
        mats = self.led.materializations("m")
        self.assertEqual(len(mats), 2)
        self.assertEqual(self.led.latest("m")["typed_metadata"], {"i": 1})

    def test_promotion_alias_resolves_latest_set(self):
        rid = self._run()
        self.led.ensure_asset("m", "model", "json")
        mid = self.led.record_materialization(
            asset_name="m", run_id=rid, node_name="n", instance="",
            content_hash="f" * 64, size_bytes=3, store_path="/x",
            reader="labbook.formats:read_json", typed_metadata={},
            input_hashes=[], cache_key=None)
        self.led.promote("m", "champion", mid, set_by="test")
        res = self.led.resolve_alias("m", "champion")
        self.assertEqual(res["materialization_id"], mid)
        self.assertEqual(res["set_by"], "test")


if __name__ == "__main__":
    unittest.main()
