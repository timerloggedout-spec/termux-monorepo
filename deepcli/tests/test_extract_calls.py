"""_extract_calls shapes."""

import sys, pathlib, unittest


def _repo_root():
    """Walk up from this file to the checkout root holding the deepcli package.

    Lets the module run from any worktree without a hardcoded $HOME/deepcli,
    so a worktree run actually imports the worktree's _v1_tools.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "deepcli" / "_v1_tools.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


ROOT = _repo_root()
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))
sys.path.insert(0, str(ROOT))

from _v1_tools import _extract_calls


class TestExtract(unittest.TestCase):
    def test_xml_one(self):
        c = _extract_calls(
            '<tool_call>{"name":"run","arguments":{"argv":["pwd"]}}</tool_call>'
        )
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0]["function"]["name"], "run")

    def test_xml_two(self):
        s = '<tool_call>{"name":"a","arguments":{}}</tool_call><tool_call>{"name":"b","arguments":{}}</tool_call>'
        self.assertEqual(len(_extract_calls(s)), 2)

    def test_empty(self):
        self.assertEqual(_extract_calls(""), [])
        self.assertEqual(_extract_calls(None), [])

    def test_prose_only(self):
        self.assertEqual(_extract_calls("just prose"), [])

    def test_multiline(self):
        c = _extract_calls(
            '<tool_call>{"name":"run",\n"arguments":{"argv":["ls"]}}</tool_call>'
        )
        self.assertEqual(len(c), 1)


if __name__ == "__main__":
    unittest.main()
