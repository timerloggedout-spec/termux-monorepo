#!/usr/bin/env python3
"""Tests for scripts/ci/build_repo_index.py — git-fixture qualification."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "ci"))
import build_repo_index as bri  # noqa: E402


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class RepoIndexFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        sh(self.root, "git", "init", "-q")
        sh(self.root, "git", "config", "user.email", "t@t")
        sh(self.root, "git", "config", "user.name", "t")
        (self.root / "pkg").mkdir()
        (self.root / "pkg/core.py").write_text(
            "def core_fn(x):\n    return x\n")
        (self.root / "pkg/user.py").write_text(
            "from .core import core_fn\n\ndef use_it():\n    return core_fn(1)\n")
        (self.root / "app.js").write_text(
            "import {x} from './lib.js';\nconsole.log(x);\n")
        (self.root / "lib.js").write_text("export const x = 1;\n")
        idx = self.root / "workspace/llm_map"
        idx.mkdir(parents=True)
        (idx / "func_index.jsonl").write_text(json.dumps(
            {"file": "pkg/core.py", "name": "core_fn", "kind": "de",
             "sig": "def core_fn(x):"}) + "\n")
        sh(self.root, "git", "add", "-A")
        sh(self.root, "git", "commit", "-qm", "fixture")

    def tearDown(self):
        self.tmp.cleanup()

    def test_schema_and_graph(self):
        final, graph, _ = bri.build(self.root)
        by_path = {e["p"]: e for e in final}
        self.assertEqual(by_path["pkg/core.py"]["by"], 1)
        self.assertEqual(by_path["pkg/user.py"]["d"], ["pkg/core.py"])
        self.assertEqual(by_path["app.js"]["d"], ["lib.js"])
        self.assertEqual(by_path["lib.js"]["by"], 1)
        self.assertEqual(by_path["pkg/core.py"]["pj"], "pkg")
        self.assertTrue(by_path["pkg/core.py"]["ah"])
        self.assertIn("core_fn", by_path["pkg/core.py"]["as"])
        self.assertTrue(by_path["pkg/core.py"]["ts"])
        self.assertEqual(by_path["pkg/core.py"]["l"], "python")
        # sort: non-bloat first, higher 'by' earlier within group
        self.assertEqual(final[0]["by"], max(e["by"] for e in final))

    def test_outputs_written(self):
        final, graph, snippets = bri.build(self.root)
        bri.write_outputs(self.root, final, graph, snippets)
        lines = (self.root / "workspace/llm_map/llm_index_compact.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), len(final))
        md = (self.root / "workspace/llm_map/CAVEMAN_INDEX.md").read_text()
        self.assertIn("pkg/core.py", md)


if __name__ == "__main__":
    unittest.main()
