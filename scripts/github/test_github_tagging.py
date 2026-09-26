#!/usr/bin/env python3
"""Unit tests for github_tagging (no network)."""
from __future__ import annotations

import unittest

import github_tagging as gt


class TagRepoTests(unittest.TestCase):
    def test_mcp_server(self):
        t = gt.tag_repo("termux-mcp", "P0 Termux MCP server", "TypeScript", False, False)
        self.assertIn("mcp-server", t["type"])
        self.assertEqual(t["priority"], "P0")
        self.assertEqual(t["relationship"], "own")

    def test_coding_agent_fork(self):
        t = gt.tag_repo("hermes-agent_fork", "The agent that grows with you", "Python", True, False)
        self.assertIn("coding-agent", t["type"])
        self.assertEqual(t["relationship"], "fork")

    def test_legal(self):
        t = gt.tag_repo("catala_fork", "Programming language for law", "OCaml", True, False)
        self.assertIn("legal-dfir", t["type"])
        self.assertIn("legaltech", t["domain"])

    def test_language_family(self):
        self.assertEqual(gt.language_family("Rust"), "rust")
        self.assertEqual(gt.language_family(None), "unknown")


class BuildExportTests(unittest.TestCase):
    def test_build_export_stats(self):
        owned = [{
            "name": "termux-monorepo",
            "full_name": "timerloggedout-spec/termux-monorepo",
            "html_url": "https://github.com/timerloggedout-spec/termux-monorepo",
            "description": "monorepo",
            "language": "Python",
            "fork": False,
            "archived": False,
            "stargazers_count": 1,
            "updated_at": "2026-01-01T00:00:00Z",
            "created_at": "2026-01-01T00:00:00Z",
            "owner": {"login": "timerloggedout-spec"},
            "parent": {},
        }]
        starred = [{
            "name": "openclaw",
            "full_name": "openclaw/openclaw",
            "html_url": "https://github.com/openclaw/openclaw",
            "description": "AI coding agent",
            "language": "TypeScript",
            "fork": False,
            "archived": False,
            "stargazers_count": 100,
            "updated_at": "2026-01-01T00:00:00Z",
        }]
        export = gt.build_export(owned, starred, "timerloggedout-spec")
        self.assertEqual(export["repos_indexed"], 1)
        self.assertEqual(export["stars_indexed"], 1)
        self.assertEqual(len(export["snapshot_hash"]), 64)
        self.assertIn("P0", export["stats"]["by_priority"])


if __name__ == "__main__":
    unittest.main()
