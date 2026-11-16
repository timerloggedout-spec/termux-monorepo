"""Offline fixture tests for the AMD M4 retrieval agent (P0).

Run:  python3 -m unittest discover -s tests -v     (from apps/amd-m4-retrieval/)
No network: a fake fetcher serves saved HTML fixtures for *.example.test URLs.
Claims under test:
  extract  => prose blocks, tables, pagination (next) links; script/style excluded
  navigate => agent follows next-links within the page bound
  answer   => passages come from fetched pages only, each cited [n] => sources list
  unseen   => queries whose wording appears in NO fixture still answer structurally
              (>= 1 citation, citations subset of fetched URLs, no fixture leakage)
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import HeuristicPlanner, RetrievalAgent, extract  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"

HOME = "https://library.example.test/"
CATALOG = "https://library.example.test/catalog"
MUSEUM = "https://museum.example.test/visit"

_PAGES = {
    HOME: "site_a_home.html",
    CATALOG: "site_a_catalog.html",
    MUSEUM: "site_b_museum.html",
}


def fake_fetch(url: str) -> str:
    """Offline fetcher: fixture file for a known URL, else raise (agent skips)."""
    name = _PAGES[url]
    return (FIXTURES / name).read_text(encoding="utf-8")


def make_agent() -> RetrievalAgent:
    return RetrievalAgent(planner=HeuristicPlanner(), fetcher=fake_fetch)


class TestExtract(unittest.TestCase):
    def test_blocks_tables_next_and_no_junk(self):
        home = extract(fake_fetch(HOME), HOME)
        self.assertEqual(home.title, "Harborview Public Library — Home")
        self.assertTrue(any("9 AM to 8 PM" in b for b in home.blocks))
        self.assertEqual(home.next_url, CATALOG)
        joined = " ".join(home.blocks)
        self.assertNotIn("SCRIPTJUNK", joined)
        self.assertNotIn("STYLEJUNK", joined)
        self.assertNotIn("FIXTURE-LEAK-MARKER", joined)

        catalog = extract(fake_fetch(CATALOG), CATALOG)
        self.assertEqual(len(catalog.tables), 1)
        rows = catalog.tables[0]
        self.assertEqual(rows[0], ["Title", "Author", "Status"])
        self.assertIn(["The Clockwork Reef", "Mira Chen", "Available"], rows)
        self.assertIsNone(catalog.next_url)


class TestAgentEndToEnd(unittest.TestCase):
    def test_prose_question_cites_its_page(self):
        ans = make_agent().run("What are the library opening hours?", [HOME])
        self.assertIn("9 AM to 8 PM", ans.answer)
        self.assertGreaterEqual(len(ans.citations), 1)
        self.assertEqual(ans.citations[0].url, HOME)
        self.assertIn("[1]", ans.answer)

    def test_pagination_followed_for_table_question(self):
        # seed = home only; the answer lives behind the next-link (catalog table)
        ans = make_agent().run("Is The Clockwork Reef available?", [HOME])
        self.assertIn(CATALOG, ans.pages_fetched)
        self.assertIn("The Clockwork Reef", ans.answer)
        self.assertIn("Available", ans.answer)
        cited = {c.url for c in ans.citations}
        self.assertIn(CATALOG, cited)

    def test_multi_site_run(self):
        ans = make_agent().run("How much is adult admission at the museum?",
                               [HOME, MUSEUM])
        self.assertIn("14 dollars", ans.answer)
        self.assertIn(MUSEUM, {c.url for c in ans.citations})

    def test_url_named_in_request_is_used(self):
        ans = make_agent().run(
            f"Tell me the library address via {HOME}")
        self.assertIn("214 Seabird Lane", ans.answer)

    def test_no_sources_means_no_invented_answer(self):
        agent = RetrievalAgent(planner=HeuristicPlanner(),
                               fetcher=lambda u: (_ for _ in ()).throw(OSError("down")))
        ans = agent.run("What are the library opening hours?",
                        ["https://unreachable.example.test/"])
        self.assertEqual(ans.citations, [])
        self.assertIn("No sources could be retrieved", ans.answer)


# Queries whose exact wording appears in NO fixture (checked against fixture
# text in test_unseen_queries_structural). Structural assertions only — this is
# the anti-hardcoding guard: the agent must answer from retrieval, not memory.
UNSEEN_QUERIES = [
    ("On which weekday evening does the library shut earliest?", [HOME]),
    ("Can I borrow Paper Boats right now, or is it out on loan?", [HOME]),
    ("What does a grown-up pay to get into the maritime museum?", [MUSEUM]),
    ("Where exactly is the library building situated?", [HOME]),
    ("Which exhibits are on at the museum this season?", [MUSEUM]),
]


class TestUnseenQueries(unittest.TestCase):
    def test_unseen_queries_structural(self):
        fixture_text = " ".join(
            p.read_text(encoding="utf-8") for p in FIXTURES.glob("*.html")
        ).lower()
        for query, seeds in UNSEEN_QUERIES:
            self.assertNotIn(query.lower(), fixture_text)  # genuinely unseen
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                # >= 1 citation, rendered as an [n] marker in the answer text
                self.assertGreaterEqual(len(ans.citations), 1)
                self.assertRegex(ans.answer, r"\[\d+\]")
                # citations point only at pages actually fetched
                self.assertLessEqual({c.url for c in ans.citations},
                                     set(ans.pages_fetched))
                # no fixture leakage: markers / attribute names / file names
                self.assertNotIn("FIXTURE-LEAK-MARKER", ans.answer)
                self.assertNotIn("data-fixture", ans.answer)
                self.assertNotIn(".html", ans.answer)


if __name__ == "__main__":
    unittest.main()
