"""_extract_calls shapes."""
import sys, pathlib, unittest


def _repo_root():
    """Return the checkout that owns this test file's ``_v1_tools.py``.

    Walk up from __file__ to the directory that directly contains
    ``_v1_tools.py`` (the repo root; ``tests/`` sits one level below it).
    A ``$HOME/deepcli`` fallback preserves the old behaviour when no
    checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "_v1_tools.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
from _v1_tools import _extract_calls

class TestExtract(unittest.TestCase):
    def test_xml_one(self):
        c = _extract_calls('<tool_call>{"name":"run","arguments":{"argv":["pwd"]}}</tool_call>')
        self.assertEqual(len(c), 1); self.assertEqual(c[0]["function"]["name"], "run")
    def test_xml_two(self):
        s = '<tool_call>{"name":"a","arguments":{}}</tool_call><tool_call>{"name":"b","arguments":{}}</tool_call>'
        self.assertEqual(len(_extract_calls(s)), 2)
    def test_empty(self):
        self.assertEqual(_extract_calls(""), [])
        self.assertEqual(_extract_calls(None), [])
    def test_prose_only(self):
        self.assertEqual(_extract_calls("just prose"), [])
    def test_multiline(self):
        c = _extract_calls('<tool_call>{"name":"run",\n"arguments":{"argv":["ls"]}}</tool_call>')
        self.assertEqual(len(c), 1)


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "_v1_tools.py").is_file())
        # The resolved root must be an ancestor of this test file.
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


if __name__ == "__main__": unittest.main()
