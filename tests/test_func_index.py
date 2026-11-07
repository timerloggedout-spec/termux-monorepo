#!/usr/bin/env python3
"""Tests for scripts/ci/func_index.py — extraction-depth qualification:
the original regex indexer missed async defs, nested defs and methods;
this variant must catch all of them."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import func_index as fi  # noqa: E402

PY = '''
def top():
    """Top doc."""
    def inner():
        return 1
    return inner

async def fetch_it(url):
    return url

class Widget:
    """A widget."""

    def render(self):
        return "x"

    async def load(self):
        return None
'''

JS = """
export function makeThing() { return 1; }
const arrow = (a) => a + 1;
class Box {
  open() { return 1; }
  async close() { return 2; }
}
"""


class PyDefs(unittest.TestCase):
    def test_depth_and_kinds(self):
        got = {(d["qual"], d["kind"]) for d in fi.py_defs(PY)}
        # kind codes = precursor value domain (de/clas), per Delphi read
        want = {("top", "de"), ("top.inner", "de"), ("fetch_it", "de"),
                ("Widget", "clas"), ("Widget.render", "de"),
                ("Widget.load", "de")}
        self.assertEqual(got, want)

    def test_docstring_captured(self):
        docs = {d["qual"]: d["doc"] for d in fi.py_defs(PY)}
        self.assertEqual(docs["top"], "Top doc.")
        self.assertEqual(docs["Widget"], "A widget.")


class JsDefs(unittest.TestCase):
    def test_js_surface(self):
        names = {d["name"] for d in fi.js_defs(JS)}
        self.assertTrue({"makeThing", "arrow", "Box", "open", "close"} <= names)


if __name__ == "__main__":
    unittest.main()
