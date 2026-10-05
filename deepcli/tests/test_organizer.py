"""organizer.extract_code_blocks + Project round-trip coverage.

Offline-only tests for the pure helpers in deepcli.organizer. The
module does ``ORGA_DIR.mkdir(...)`` at import time (writes only under
~/.deepcli/organizer) and imports ``rich``; both are safe here. No
network, no prompts, no console I/O is exercised.
"""

import pathlib
import sys
import unittest


def _repo_root():
    """Resolve the checkout that contains this test file.

    tests/ -> deepcli/ -> <repo root>. Keeps the harness importing
    ``deepcli`` from *this* checkout rather than a hardcoded $HOME path.
    """
    here = pathlib.Path(__file__).resolve()
    return here.parents[2]


sys.path.insert(0, str(_repo_root()))
from deepcli import organizer  # noqa: E402


class TestExtractCodeBlocks(unittest.TestCase):
    def test_no_blocks_returns_empty(self):
        self.assertEqual(organizer.extract_code_blocks("just prose"), [])

    def test_language_tagged_block(self):
        md = "see:\n```python\nprint(1)\n```\ndone"
        blocks = organizer.extract_code_blocks(md)
        self.assertEqual(blocks, [{"language": "python", "code": "print(1)"}])

    def test_untagged_block_defaults_to_text(self):
        md = "```\nplain stuff\n```"
        blocks = organizer.extract_code_blocks(md)
        self.assertEqual(blocks[0]["language"], "text")
        self.assertEqual(blocks[0]["code"], "plain stuff")

    def test_language_is_lowercased(self):
        md = "```Python\nx=1\n```"
        self.assertEqual(organizer.extract_code_blocks(md)[0]["language"], "python")

    def test_multiple_blocks_preserve_order(self):
        md = "```bash\na\n```\ntext\n```json\n{}\n```"
        blocks = organizer.extract_code_blocks(md)
        self.assertEqual([b["language"] for b in blocks], ["bash", "json"])

    def test_whitespace_only_block_is_skipped(self):
        md = "```python\n\n   \n```"
        self.assertEqual(organizer.extract_code_blocks(md), [])

    def test_multiline_body_is_preserved(self):
        md = "```python\nline1\nline2\n```"
        self.assertEqual(organizer.extract_code_blocks(md)[0]["code"], "line1\nline2")

    def test_trailing_newlines_are_stripped(self):
        md = "```python\nx=1\n\n\n```"
        self.assertEqual(organizer.extract_code_blocks(md)[0]["code"], "x=1")


class TestProjectRoundTrip(unittest.TestCase):
    def test_to_dict_has_expected_keys(self):
        p = organizer.Project("demo", "a description")
        d = p.to_dict()
        self.assertEqual(d["name"], "demo")
        self.assertEqual(d["description"], "a description")
        self.assertEqual(d["snippets"], [])
        self.assertIn("created_at", d)

    def test_from_dict_restores_fields(self):
        d = {
            "name": "n",
            "description": "d",
            "created_at": 123.0,
            "snippets": [{"language": "python", "code": "x"}],
        }
        p = organizer.Project.from_dict(d)
        self.assertEqual(p.name, "n")
        self.assertEqual(p.description, "d")
        self.assertEqual(p.created_at, 123.0)
        self.assertEqual(p.snippets, d["snippets"])

    def test_round_trip_is_lossless(self):
        p = organizer.Project("rt", "round trip")
        p.created_at = 42.5
        p.snippets = [{"language": "bash", "code": "ls"}]
        again = organizer.Project.from_dict(p.to_dict())
        self.assertEqual(again.to_dict(), p.to_dict())

    def test_from_dict_tolerates_missing_optional(self):
        p = organizer.Project.from_dict({"name": "minimal"})
        self.assertEqual(p.name, "minimal")
        self.assertEqual(p.description, "")
        self.assertEqual(p.snippets, [])


if __name__ == "__main__":
    unittest.main()
