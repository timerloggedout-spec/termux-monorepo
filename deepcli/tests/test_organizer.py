"""Unit tests for deepcli.organizer.extract_code_blocks (offline, no network)."""

import pathlib, sys, unittest

# Locate the deepcli package root relative to this test file, so the test
# works from any checkout without depending on an absolute $HOME path.
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deepcli.organizer import extract_code_blocks


class TestExtractCodeBlocks(unittest.TestCase):
    def test_single_python_block(self):
        blocks = extract_code_blocks("```python\nx = 1\n```")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["language"], "python")
        self.assertEqual(blocks[0]["code"], "x = 1")

    def test_language_normalized_lowercase(self):
        blocks = extract_code_blocks("```PYTHON\nx = 1\n```")
        self.assertEqual(blocks[0]["language"], "python")

    def test_missing_language_defaults_to_text(self):
        blocks = extract_code_blocks("```\nplain\n```")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["language"], "text")

    def test_multiple_blocks_preserve_order(self):
        content = "```python\na=1\n```\ntext\n```js\nb=2\n```"
        blocks = extract_code_blocks(content)
        self.assertEqual([b["language"] for b in blocks], ["python", "js"])
        self.assertEqual(blocks[1]["code"], "b=2")

    def test_blank_or_unterminated_blocks_ignored(self):
        self.assertEqual(extract_code_blocks("```python\n\n```"), [])
        self.assertEqual(extract_code_blocks("```python\nx=1"), [])

    def test_no_fences_returns_empty(self):
        self.assertEqual(extract_code_blocks("just prose, no code"), [])
        self.assertEqual(extract_code_blocks(""), [])


if __name__ == "__main__":
    unittest.main()
