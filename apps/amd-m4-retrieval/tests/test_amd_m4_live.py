"""LIVE public-site tests for the AMD M4 retrieval agent — OPT-IN ONLY.

Skipped by default (including in CI): run explicitly with

    AMD_M4_LIVE=1 python3 -m unittest tests.test_amd_m4_live -v

from apps/amd-m4-retrieval/. These hit real public pages over the network,
so assertions are structural only (sources fetched, citations consistent,
no invented content markers) — never memorized page text.
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import RetrievalAgent  # noqa: E402

LIVE = os.environ.get("AMD_M4_LIVE") == "1"


@unittest.skipUnless(LIVE, "live network suite: set AMD_M4_LIVE=1 to run")
class TestLivePublicSites(unittest.TestCase):
    def _check(self, query: str, url: str) -> None:
        ans = RetrievalAgent().run(query, [url])
        self.assertIn(url, ans.pages_fetched)
        self.assertGreaterEqual(len(ans.citations), 1)
        self.assertRegex(ans.answer, r"\[\d+\]")
        self.assertLessEqual({c.url for c in ans.citations},
                             set(ans.pages_fetched))

    def test_example_com(self):
        self._check("What is this domain intended for?",
                    "https://example.com/")

    def test_example_org(self):
        self._check("What does this page explain about the domain?",
                    "https://example.org/")


if __name__ == "__main__":
    unittest.main()
