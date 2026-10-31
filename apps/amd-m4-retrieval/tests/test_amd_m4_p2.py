"""P2 tests for the AMD M4 retrieval agent — hardening + robustness + budgets.

Run:  python3 -m unittest discover -s tests -v     (from apps/amd-m4-retrieval/)
Offline except loopback probe servers (redirects / non-HTML / byte cap /
timeout are exercised against 127.0.0.1 only; ∅ external network).
Claims under test:
  unseen2  => >= 20 NEW unseen queries across factual / table / list /
              multi-hop (>= 5) / negative-honesty (>= 3) categories
  property => citations cited in an answer ⊆ pages actually fetched;
              answers never contain content unique to fixtures the run did
              NOT fetch; repeated runs are byte-identical (determinism)
  robust   => malformed HTML, huge pages (byte cap + bounded run), redirect
              chains + loops, non-HTML bodies, fetch timeouts — the agent
              degrades to an explicit no-answer, never crashes, never invents
  budget   => --selfcheck numbers are functional: startup measured, page
              bound exercised on an endless chain, byte cap + timeout real
"""

from __future__ import annotations

import re
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import (  # noqa: E402
    MAX_PAGES,
    MAX_RESPONSE_BYTES,
    HeuristicPlanner,
    RetrievalAgent,
    extract,
    fetch,
    run_selfcheck,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"

HOME = "https://library.example.test/"
CATALOG = "https://library.example.test/catalog"
EVENTS = "https://library.example.test/events"
EVENTS2 = "https://library.example.test/events-2"
MUSEUM = "https://museum.example.test/visit"
BOTANIC = "https://botanic.example.test/"
ORCHID = "https://botanic.example.test/orchid-house"
MALFORMED = "https://harbour.example.test/tide-gauge"
HUGE = "https://huge.example.test/guide"

_PAGES = {
    HOME: "site_a_home.html",
    CATALOG: "site_a_catalog.html",
    EVENTS: "site_a_events.html",
    EVENTS2: "site_a_events2.html",
    MUSEUM: "site_b_museum.html",
    BOTANIC: "site_c_botanic_home.html",
    ORCHID: "site_c_orchid.html",
    MALFORMED: "site_e_malformed.html",
}


def fake_fetch(url: str) -> str:
    if url == HUGE:
        return _huge_page()
    name = _PAGES[url]  # KeyError (unmapped URL) => agent skips the source
    return (FIXTURES / name).read_text(encoding="utf-8")


def _huge_page() -> str:
    filler = "\n".join(
        f"<p>Filler paragraph {i} about harbour paperwork and filing.</p>"
        for i in range(8000))
    return ("<html><head><title>Harbour Guide</title></head><body>"
            "<p>The harbour guide office issues visitor permits at the "
            "north gate desk.</p>" + filler + "</body></html>")


def make_agent(**kw) -> RetrievalAgent:
    return RetrievalAgent(planner=HeuristicPlanner(), fetcher=fake_fetch, **kw)


def cited_urls(ans) -> set[str]:
    idx = {int(m) for m in re.findall(r"\[(\d+)\]", ans.answer)}
    return {c.url for c in ans.citations if c.index in idx}


NO_MATCH = "did not contain a passage matching"
NO_SOURCES = "No sources could be retrieved"

# >= 20 NEW unseen queries (wording in NO fixture — asserted below).
# Row: (category, query, seeds, required fragments, min distinct cited sources)
UNSEEN_P2 = [
    # -- factual lookup ------------------------------------------------------
    ("factual", "What must I bring to sign up for library membership?",
     [HOME], ["photo ID"], 1),
    ("factual", "At what time do guided tours of the museum start?",
     [MUSEUM], ["11 AM"], 1),
    ("factual", "Until when does the Signals and Storms exhibition run?",
     [MUSEUM], ["end of March"], 1),
    ("factual", "On which floor are new library arrivals shelved during "
     "their first month?", [HOME], ["second floor"], 1),
    ("factual", "Where in Harborview is the library, relative to the "
     "ferry terminal?", [HOME], ["ferry terminal"], 1),
    ("factual", "How often can a borrowed library item be renewed?",
     [HOME], ["once per item"], 1),
    ("factual", "What are the museum hours, opening and closing?",
     [MUSEUM], ["10 AM", "6 PM"], 1),
    # -- table extraction ----------------------------------------------------
    ("table", "Who authored A Field Guide to Tides?",
     [CATALOG], ["Jonas Okafor"], 1),
    ("table", "Which catalog titles are currently checked out?",
     [CATALOG], ["A Field Guide to Tides", "Checked out"], 1),
    ("table", "Give me the author and availability of The Clockwork Reef "
     "from the catalog table.", [CATALOG], ["Mira Chen", "Available"], 1),
    ("table", "In the new arrivals catalog, what is the status of "
     "Paper Boats?", [HOME], ["Available"], 1),
    ("table", "In the catalog, who wrote The Clockwork Reef?",
     [CATALOG], ["Mira Chen"], 1),
    # -- list extraction -----------------------------------------------------
    ("list", "Is there a workshop on the second page of the library "
     "events listing?", [EVENTS], ["Book binding workshop"], 1),
    ("list", "What activities are listed for young children at the library?",
     [EVENTS], ["Story time for toddlers"], 1),
    ("list", "Are Vanda and Dendrobium among the species on display?",
     [ORCHID], ["Vanda coerulea", "Dendrobium nobile"], 1),
    # -- multi-hop (must cite >= 2 distinct sources) --------------------------
    ("multihop", "What are the museum opening hours and what is the "
     "library loan period?", [MUSEUM, HOME], ["10 AM", "three weeks"], 2),
    ("multihop", "Tell me the botanic garden address and the name of the "
     "orchid house head keeper.", [BOTANIC],
     ["77 Fern Hollow Road", "Priya Raman"], 2),
    ("multihop", "When does the chess club meet and when is the book "
     "binding workshop?", [EVENTS], ["Wednesday 4 PM", "Saturday 11 AM"], 2),
    ("multihop", "What does museum entry cost for an adult and what must "
     "residents bring for free library membership?", [MUSEUM, HOME],
     ["14 dollars", "photo ID"], 2),
    ("multihop", "What time is last entry at the botanic garden and what "
     "humidity does the orchid house maintain?", [BOTANIC],
     ["5 PM", "70 percent"], 2),
    ("multihop", "Which books in the catalog are available and when does "
     "the museum close?", [HOME, MUSEUM], ["Clockwork Reef", "6 PM"], 2),
]

# Negative / honesty: the retrieved pages hold no answer; the agent must say
# so explicitly instead of inventing one. (category, query, seeds, marker)
NEGATIVE_P2 = [
    # wording avoids the sites' own name terms on purpose: a query sharing
    # zero content terms with every retrieved passage must yield NO_MATCH
    ("negative", "What is the wifi password here?",
     [HOME], NO_MATCH),
    ("negative", "How much does parking cost?",
     [BOTANIC], NO_MATCH),
    ("negative", "How many ships are in the collection?",
     [MUSEUM], NO_MATCH),
    ("negative", "What are the opening hours of the observatory?",
     ["https://observatory.example.test/"], NO_SOURCES),
]


class TestUnseenQueriesP2(unittest.TestCase):
    def test_category_coverage(self):
        self.assertGreaterEqual(len(UNSEEN_P2), 20)
        cats = [c for c, *_ in UNSEEN_P2 + NEGATIVE_P2]
        self.assertGreaterEqual(cats.count("multihop"), 5)
        self.assertGreaterEqual(cats.count("negative"), 3)
        for cat in ("factual", "table", "list"):
            self.assertGreaterEqual(cats.count(cat), 3)

    def test_unseen_queries_p2(self):
        fixture_text = " ".join(
            p.read_text(encoding="utf-8") for p in FIXTURES.glob("*.html")
        ).lower()
        for cat, query, seeds, fragments, min_sources in UNSEEN_P2:
            self.assertNotIn(query.lower(), fixture_text)  # genuinely unseen
            with self.subTest(category=cat, query=query):
                ans = make_agent().run(query, seeds)
                self.assertGreaterEqual(len(ans.citations), 1)
                self.assertRegex(ans.answer, r"\[\d+\]")
                self.assertLessEqual({c.url for c in ans.citations},
                                     set(ans.pages_fetched))
                for frag in fragments:
                    self.assertIn(frag, ans.answer)
                self.assertGreaterEqual(len(cited_urls(ans)), min_sources)

    def test_negative_queries_stay_honest(self):
        for cat, query, seeds, marker in NEGATIVE_P2:
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                self.assertIn(marker, ans.answer)


class TestAnswerProperties(unittest.TestCase):
    def test_cited_sources_always_subset_of_fetched(self):
        for _cat, query, seeds, _f, _m in UNSEEN_P2:
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                self.assertLessEqual(cited_urls(ans), set(ans.pages_fetched))
                self.assertLessEqual({c.url for c in ans.citations},
                                     set(ans.pages_fetched))

    def test_no_content_from_unfetched_fixtures(self):
        # strings unique to one fixture must never surface in a run that
        # never fetched that fixture's page
        cases = [
            ("How much is adult admission?", [MUSEUM],
             ["Priya Raman", "214 Seabird Lane", "Jonas Okafor"]),
            ("What temperature is the orchid house kept at?", [ORCHID],
             ["14 dollars", "three weeks"]),
            ("When does the chess club meet?", [EVENTS],
             ["Jonas Okafor", "70 percent"]),
        ]
        for query, seeds, forbidden in cases:
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                for s in forbidden:
                    self.assertNotIn(s, ans.answer)

    def test_no_fixture_internals_in_any_answer(self):
        for _cat, query, seeds, _f, _m in UNSEEN_P2:
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                for junk in ("FIXTURE-LEAK-MARKER", "data-fixture",
                             ".html", "SCRIPTJUNK", "STYLEJUNK"):
                    self.assertNotIn(junk, ans.answer)

    def test_determinism_across_repeat_runs(self):
        probes = [UNSEEN_P2[0], UNSEEN_P2[13], UNSEEN_P2[16]]
        for _cat, query, seeds, _f, _m in probes:
            with self.subTest(query=query):
                first = make_agent().run(query, seeds)
                second = make_agent().run(query, seeds)
                self.assertEqual(first.answer, second.answer)
                self.assertEqual(first.pages_fetched, second.pages_fetched)
                self.assertEqual(
                    [(c.index, c.url) for c in first.citations],
                    [(c.index, c.url) for c in second.citations])


class TestRobustnessOffline(unittest.TestCase):
    def test_malformed_html_still_answers(self):
        page = extract(fake_fetch(MALFORMED), MALFORMED)
        self.assertTrue(any("7 AM" in b for b in page.blocks))
        ans = make_agent().run("When does the tide gauge office open?",
                               [MALFORMED])
        self.assertIn("7 AM", ans.answer)
        self.assertIn(MALFORMED, {c.url for c in ans.citations})

    def test_binary_garbage_degrades_to_no_match(self):
        garbage = "%PDF-1.4 \x00\x01\x02 binarygarbage \xff\xfe not html"
        agent = RetrievalAgent(planner=HeuristicPlanner(),
                               fetcher=lambda u: garbage)
        ans = agent.run("What are the harbour office hours?",
                        ["https://files.example.test/blob"])
        self.assertIn(NO_MATCH, ans.answer)

    def test_timeout_fetcher_degrades_to_no_sources(self):
        def slow_fetch(url: str) -> str:
            raise TimeoutError("timed out")

        agent = RetrievalAgent(planner=HeuristicPlanner(), fetcher=slow_fetch)
        ans = agent.run("What are the library opening hours?",
                        ["https://slow.example.test/"])
        self.assertIn(NO_SOURCES, ans.answer)
        self.assertEqual(ans.citations, [])

    def test_huge_page_bounded_and_answers(self):
        start = time.perf_counter()
        ans = make_agent().run("Where does the harbour guide office issue "
                               "visitor permits?", [HUGE])
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 10)
        self.assertLessEqual(len(ans.pages_fetched), MAX_PAGES)
        self.assertIn("north gate desk", ans.answer)
        self.assertIn(HUGE, {c.url for c in ans.citations})


class _ProbeHandler(BaseHTTPRequestHandler):
    """Loopback probe routes for real-fetch behaviour (redirects, non-HTML,
    byte cap, timeout). 127.0.0.1 only — ∅ external network."""

    def log_message(self, *args):
        pass

    def _reply(self, code: int, body: bytes, ctype: str = "text/html",
               location: str | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        if location:
            self.send_header("Location", location)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # client stopped reading early (byte cap) — expected

    def do_GET(self):  # noqa: N802
        if self.path == "/r1":
            self._reply(302, b"", location="/r2")
        elif self.path == "/r2":
            self._reply(302, b"", location="/final")
        elif self.path == "/final":
            self._reply(200, b"<html><body><p>The ferry ticket office "
                             b"opens at 6 AM every morning.</p>"
                             b"</body></html>")
        elif self.path == "/loop":
            self._reply(302, b"", location="/loop")
        elif self.path == "/data.json":
            self._reply(200, b'{"ferry": "sails at dawn", "count": 3}',
                        ctype="application/json")
        elif self.path == "/big":
            self._reply(200, b"x" * (MAX_RESPONSE_BYTES + 1_000_000))
        elif self.path == "/slow":
            time.sleep(4)
            self._reply(200, b"<html><body>slow</body></html>")
        else:
            self._reply(404, b"nope")


class TestRobustnessLoopback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), _ProbeHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_redirect_chain_followed_by_agent(self):
        agent = RetrievalAgent(planner=HeuristicPlanner())  # real fetch
        ans = agent.run("When does the ferry ticket office open?",
                        [self.base + "/r1"])
        self.assertIn("6 AM", ans.answer)
        self.assertIn(self.base + "/r1", ans.pages_fetched)

    def test_redirect_loop_degrades_to_no_sources(self):
        agent = RetrievalAgent(planner=HeuristicPlanner())
        ans = agent.run("When does the ferry ticket office open?",
                        [self.base + "/loop"])
        self.assertIn(NO_SOURCES, ans.answer)

    def test_non_html_body_degrades_to_no_match(self):
        agent = RetrievalAgent(planner=HeuristicPlanner())
        ans = agent.run("When does the ferry sail?",
                        [self.base + "/data.json"])
        self.assertIn(self.base + "/data.json", ans.pages_fetched)
        self.assertIn(NO_MATCH, ans.answer)

    def test_fetch_caps_huge_body(self):
        body = fetch(self.base + "/big")
        self.assertLessEqual(len(body), MAX_RESPONSE_BYTES)

    def test_fetch_timeout_is_enforced(self):
        t0 = time.perf_counter()
        with self.assertRaises(Exception):
            fetch(self.base + "/slow", timeout=1)
        self.assertLess(time.perf_counter() - t0, 3.5)


class TestSelfcheck(unittest.TestCase):
    def test_selfcheck_budgets_functional(self):
        report = run_selfcheck()
        self.assertTrue(report["ok"], report)
        self.assertTrue(all(report["checks"].values()))
        self.assertLessEqual(report["startup_s"], report["startup_budget_s"])
        self.assertEqual(report["max_pages_seen_on_endless_chain"],
                         report["max_pages"])
        self.assertEqual(report["worst_case_fetch_time_s"],
                         report["max_pages"] * report["fetch_timeout_s"])


if __name__ == "__main__":
    unittest.main()
