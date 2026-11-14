#!/usr/bin/env python3
"""Tests for scripts/ci/dangle_check.py — seeded-fixture qualification.

Fixtures plant one dangling reference of every class plus clean controls;
the checker must return exactly the planted set (precision = recall = 1 on
the fixture universe). Rename fixtures model a workflow rename: old display
name, filename, dispatch type and workflow_run subscription must ALL be
caught, since those are the surfaces that break silently.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import dangle_check as dc  # noqa: E402


def write(root, relpath, text):
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


class CensusFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, "docs/page.md",
              "# Title\n\n[ok](../scripts/tool.py)\n[bad](../scripts/gone.py)\n"
              "[anchor](#title)\n[badanchor](#nope)\n")
        write(self.root, "scripts/tool.py", "print('ok')\n")
        write(self.root, "apps/site/index.html",
              '<a href="missing.html">x</a><a href="ok.html">y</a>'
              '<h1 id="top">t</h1><a href="#top">top</a>\n')
        write(self.root, "apps/site/ok.html", "<p>ok</p>\n")
        write(self.root, "apps/site/data/feed.json",
              json.dumps({"good": "scripts/tool.py",
                          "bad": "scripts/vanished.py",
                          "url": "https://example.com/x.py",
                          "num": 3}))
        write(self.root, ".github/workflows/clean.yml",
              "name: clean flow\non:\n  workflow_dispatch:\njobs:\n"
              "  run:\n    steps:\n      - run: python3 scripts/tool.py\n")
        write(self.root, ".github/workflows/broken.yml",
              "name: broken flow\non:\n  workflow_dispatch:\njobs:\n"
              "  run:\n    steps:\n      - uses: ./actions/nope\n"
              "      - run: python3 scripts/absent.py\n")
        (self.root / "docs/deadlink.md").symlink_to("no-such-target.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_exact_planted_set(self):
        got = {(f["kind"], f["path"]) for f in
               dc.check_links(self.root) + dc.check_feeds(self.root)
               + dc.check_workflows(self.root) + dc.check_symlinks(self.root)}
        want = {
            ("dangling-link", "docs/page.md"),
            ("dangling-anchor", "docs/page.md"),
            ("dangling-link", "apps/site/index.html"),
            ("dangling-feed-ref", "apps/site/data/feed.json"),
            ("dangling-local-uses", ".github/workflows/broken.yml"),
            ("dangling-run-script", ".github/workflows/broken.yml"),
            ("dangling-symlink", "docs/deadlink.md"),
        }
        self.assertEqual(got, want)


class RenameFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        write(self.root, ".github/workflows/old-flow.yml",
              "name: Old Flow\n"
              "on:\n"
              "  repository_dispatch:\n"
              "    types: [old-flow-run]\n"
              "  workflow_run:\n"
              "    workflows: [\"Old Flow\", \"Other Flow\"]\n"
              "    types: [completed]\n"
              "  push:\n"
              "    paths:\n"
              "      - 'scripts/old_flow.py'\n"
              "concurrency:\n"
              "  group: old-flow-${{ github.ref }}\n"
              "jobs:\n  run:\n    steps:\n      - run: echo ok\n")
        write(self.root, "scripts/caller.py",
              "# dispatches old-flow-run to Old Flow\nprint('x')\n")
        write(self.root, "docs/note.md", "See the Old Flow docs.\n")
        write(self.root, "ops/series.jsonl",
              '{"lane": "old-flow"}\n{"lane": "new-flow"}\n')
        self.old_ids = [{"old": "Old Flow"}, {"old": "old-flow"},
                        {"old": "old_flow"}]

    def tearDown(self):
        self.tmp.cleanup()

    def test_all_trigger_surfaces_caught(self):
        got = {(f["ref"], f["surface"]) for f in
               dc.check_workflows(self.root, self.old_ids)
               if f["kind"] == "residual-old-id"}
        want = {
            ("old-flow", "filename"),
            ("Old Flow", "name"),
            ("old-flow", "repository_dispatch.types"),
            ("Old Flow", "workflow_run.workflows"),
            ("old_flow", "paths"),
            ("old-flow", "concurrency.group"),
        }
        self.assertEqual(got, want)

    def test_pointers_caught(self):
        got = {(f["path"], f["ref"]) for f in
               dc.check_pointers(self.root, self.old_ids, set())}
        self.assertIn(("scripts/caller.py", "old-flow"), got)
        self.assertIn(("docs/note.md", "Old Flow"), got)
        # #3751: .jsonl series files are pointer-scan sources.
        self.assertIn(("ops/series.jsonl", "old-flow"), got)


class BaselineRatchet(unittest.TestCase):
    def test_known_findings_do_not_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root, "docs/a.md", "[x](gone.md)\n")
            out = root / "r1.json"
            rc = dc.main(["--root", str(root), "--out", str(out)])
            self.assertEqual(rc, 1)
            base = root / "base.json"
            dc.main(["--root", str(root), "--write-baseline", str(base),
                     "--report-only"])
            rc2 = dc.main(["--root", str(root), "--baseline", str(base)])
            self.assertEqual(rc2, 0)


class DynamicReferenceFixture(unittest.TestCase):
    def test_dynamic_html_fragments_do_not_hide_static_missing_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root, "apps/page.html",
                  '<a href="${GH}${esc(doc.path)}">dynamic</a>\n'
                  '<a href="\'+GH+\'/issues/1487#issuecomment-\'+esc(cid)+\'">dynamic</a>\n'
                  '<a href="missing.html">missing</a>\n'
                  '<a href="missing-query.html?term=${value}">static path</a>\n'
                  '<a href="ok.html#${anchor}">dynamic anchor</a>\n'
                  '<a href="docs/c++.md">literal plus</a>')
            write(root, "apps/ok.html", '<h1 id="top">ok</h1>')
            findings = dc.check_links(root)
        self.assertEqual([f["ref"] for f in findings],
                         ["missing.html", "missing-query.html?term=${value}",
                          "docs/c++.md"])

    def test_feed_compounds_preserve_literal_paths_with_spaces_and_plus(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write(root, "apps/data/feed.json", json.dumps({
                "description": "docs/a.md + scripts/b.py",
                "compound": "docs/a.md and scripts/b.py",
                "space_path": "docs/release notes.md",
                "plus_path": "docs/c++.md",
                "missing": "scripts/actually-missing.py",
                "dynamic_query": "scripts/missing.py?term=${value}",
            }))
            findings = dc.check_feeds(root)
        self.assertEqual([f["ref"] for f in findings],
                         ["docs/release notes.md", "docs/c++.md",
                          "scripts/actually-missing.py", "scripts/missing.py"])


if __name__ == "__main__":
    unittest.main()
