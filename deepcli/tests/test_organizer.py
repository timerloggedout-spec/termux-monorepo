#!/usr/bin/env python3
"""Tests for deepcli.organizer -- the project/code-snippet manager.

First test coverage for deepcli/deepcli/organizer.py. All offline: the
storage path is redirected to a temp dir so the real
~/.deepcli/organizer/projects.json is never touched. Console output is
captured via a stub so no rich rendering is exercised.

Covers:
  - extract_code_blocks(): language tagging, default text, rstrip,
    whitespace-only blocks dropped, multiple blocks, DOTALL multi-line.
  - Project.to_dict()/from_dict(): round-trip, defaults on missing keys,
    snippet list preserved.
  - load_projects()/save_projects(): empty -> {}, round-trip via temp
    file, non-ASCII description preserved (ensure_ascii=False).
  - cmd_create_project(): creates + persists; duplicate is a no-op.
  - cmd_delete_project(): missing is a no-op; Confirm=yes deletes.
  - cmd_add_snippet(): missing project no-op; no code blocks no-op;
    appends snippet with hash/lang; extra metadata injected.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from deepcli import organizer as org


class _StubConsole:
    """Capture .print() calls instead of rendering rich markup."""

    def __init__(self):
        self.calls = []

    def print(self, *a, **k):
        self.calls.append(a)

    def text(self):
        return "\n".join(str(c[0]) if c else "" for c in self.calls)


class OrganizerTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._orig_file = org.PROJECTS_FILE
        self._orig_dir = org.ORGA_DIR
        org.ORGA_DIR = Path(self._tmp.name)
        org.PROJECTS_FILE = Path(self._tmp.name) / "projects.json"
        self.addCleanup(self._restore)
        self.console = _StubConsole()
        self._orig_console = org.console
        org.console = self.console
        self.addCleanup(lambda: setattr(org, "console", self._orig_console))

    def _restore(self):
        org.PROJECTS_FILE = self._orig_file
        org.ORGA_DIR = self._orig_dir


class TestExtractCodeBlocks(unittest.TestCase):
    def test_language_tagged_block(self):
        blocks = org.extract_code_blocks("```python\nprint(1)\n```")
        self.assertEqual(blocks, [{"language": "python", "code": "print(1)"}])

    def test_untagged_block_defaults_to_text(self):
        blocks = org.extract_code_blocks("```\nhi\n```")
        self.assertEqual(blocks, [{"language": "text", "code": "hi"}])

    def test_language_lowercased(self):
        blocks = org.extract_code_blocks("```PYTHON\nx=1\n```")
        self.assertEqual(blocks[0]["language"], "python")

    def test_multiline_code_preserved(self):
        blocks = org.extract_code_blocks("```py\na=1\nb=2\n```")
        self.assertEqual(blocks[0]["code"], "a=1\nb=2")

    def test_trailing_newline_stripped(self):
        blocks = org.extract_code_blocks("```py\nx=1\n\n```")
        self.assertEqual(blocks[0]["code"], "x=1")

    def test_whitespace_only_block_dropped(self):
        self.assertEqual(org.extract_code_blocks("```py\n   \n```"), [])

    def test_multiple_blocks_in_order(self):
        text = "```py\na\n```\ntext\n```js\nb\n```"
        blocks = org.extract_code_blocks(text)
        self.assertEqual([b["language"] for b in blocks], ["py", "js"])
        self.assertEqual([b["code"] for b in blocks], ["a", "b"])

    def test_no_blocks_returns_empty(self):
        self.assertEqual(org.extract_code_blocks("just prose"), [])


class TestProjectModel(unittest.TestCase):
    def test_to_dict_shape(self):
        p = org.Project("demo", "desc")
        d = p.to_dict()
        self.assertEqual(d["name"], "demo")
        self.assertEqual(d["description"], "desc")
        self.assertEqual(d["snippets"], [])
        self.assertIn("created_at", d)

    def test_from_dict_round_trip(self):
        p = org.Project("demo", "desc")
        p.snippets.append({"language": "py", "code": "x"})
        p2 = org.Project.from_dict(p.to_dict())
        self.assertEqual(p2.name, "demo")
        self.assertEqual(p2.description, "desc")
        self.assertEqual(p2.created_at, p.created_at)
        self.assertEqual(p2.snippets, p.snippets)

    def test_from_dict_defaults(self):
        p = org.Project.from_dict({"name": "bare"})
        self.assertEqual(p.description, "")
        self.assertEqual(p.snippets, [])
        self.assertIsInstance(p.created_at, float)


class TestStorage(OrganizerTestBase):
    def test_load_missing_returns_empty(self):
        self.assertEqual(org.load_projects(), {})

    def test_save_then_load_round_trip(self):
        projects = {"a": org.Project("a", "first")}
        projects["a"].snippets.append({"language": "py", "code": "x"})
        org.save_projects(projects)
        loaded = org.load_projects()
        self.assertEqual(set(loaded), {"a"})
        self.assertEqual(loaded["a"].description, "first")
        self.assertEqual(loaded["a"].snippets, [{"language": "py", "code": "x"}])

    def test_save_is_ensure_ascii_false(self):
        org.save_projects({"k": org.Project("k", "caf\u00e9")})
        raw = org.PROJECTS_FILE.read_text()
        self.assertIn("caf\u00e9", raw)


class TestCommands(OrganizerTestBase):
    def test_create_project_persists(self):
        org.cmd_create_project("p1", "hello")
        loaded = org.load_projects()
        self.assertIn("p1", loaded)
        self.assertEqual(loaded["p1"].description, "hello")

    def test_create_duplicate_is_noop(self):
        org.cmd_create_project("p1", "first")
        org.cmd_create_project("p1", "second")
        self.assertEqual(org.load_projects()["p1"].description, "first")

    def test_delete_missing_is_noop(self):
        org.cmd_delete_project("ghost")
        self.assertEqual(org.load_projects(), {})

    def test_delete_confirmed_removes(self):
        org.cmd_create_project("p1")
        with mock.patch.object(org.Confirm, "ask", return_value=True):
            org.cmd_delete_project("p1")
        self.assertEqual(org.load_projects(), {})

    def test_delete_declined_keeps(self):
        org.cmd_create_project("p1")
        with mock.patch.object(org.Confirm, "ask", return_value=False):
            org.cmd_delete_project("p1")
        self.assertIn("p1", org.load_projects())

    def test_add_snippet_missing_project_is_noop(self):
        org.cmd_add_snippet("nope", "```py\nx=1\n```")
        self.assertEqual(org.load_projects(), {})

    def test_add_snippet_no_blocks_is_noop(self):
        org.cmd_create_project("p1")
        org.cmd_add_snippet("p1", "no code here")
        self.assertEqual(org.load_projects()["p1"].snippets, [])

    def test_add_snippet_appends_with_hash(self):
        org.cmd_create_project("p1")
        org.cmd_add_snippet(
            "p1", "```py\nx=1\n```", conversation_id="sid", message_id="m1", note="n"
        )
        snips = org.load_projects()["p1"].snippets
        self.assertEqual(len(snips), 1)
        self.assertEqual(snips[0]["language"], "py")
        self.assertEqual(snips[0]["code"], "x=1")
        self.assertEqual(snips[0]["conversation_id"], "sid")
        self.assertEqual(snips[0]["message_id"], "m1")
        self.assertEqual(snips[0]["note"], "n")
        self.assertEqual(len(snips[0]["hash"]), 12)

    def test_add_snippet_multiple_blocks(self):
        org.cmd_create_project("p1")
        org.cmd_add_snippet("p1", "```py\na\n```\n```js\nb\n```")
        snips = org.load_projects()["p1"].snippets
        self.assertEqual([s["language"] for s in snips], ["py", "js"])


if __name__ == "__main__":
    unittest.main()
