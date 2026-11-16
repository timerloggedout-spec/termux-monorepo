"""P1 tests for the AMD M4 retrieval agent (offline; fake fetcher + fixtures).

Run:  python3 -m unittest discover -s tests -v     (from apps/amd-m4-retrieval/)
Claims under test:
  multihop => planner decomposition + evidence-link following merges passages
              from >= 2 sources, each cited, within MAX_PAGES/MAX_HOPS bounds
  extract+ => lists captured, tables => structured records, generic pagination
              labels ("More events") followed as chains
  llm      => LLMPlanner activates ONLY on a detected LOCAL model (loopback
              endpoint / weights+runtime); fake local model drives a real
              plan; non-loopback + absent + dead endpoints fall back to the
              heuristic planner; NO external call is ever made
  unseen+  => >= 10 further unseen queries, structural assertions (+ content
              spot-checks), incl. multi-hop queries citing >= 2 sources
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import (  # noqa: E402
    HeuristicPlanner,
    LLMPlanner,
    RetrievalAgent,
    decompose,
    extract,
    local_model_status,
    make_planner,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"

HOME = "https://library.example.test/"
CATALOG = "https://library.example.test/catalog"
EVENTS = "https://library.example.test/events"
EVENTS2 = "https://library.example.test/events-2"
MUSEUM = "https://museum.example.test/visit"
BOTANIC = "https://botanic.example.test/"
ORCHID = "https://botanic.example.test/orchid-house"

_PAGES = {
    HOME: "site_a_home.html",
    CATALOG: "site_a_catalog.html",
    EVENTS: "site_a_events.html",
    EVENTS2: "site_a_events2.html",
    MUSEUM: "site_b_museum.html",
    BOTANIC: "site_c_botanic_home.html",
    ORCHID: "site_c_orchid.html",
}


def fake_fetch(url: str) -> str:
    name = _PAGES[url]  # KeyError (unmapped URL) => agent skips the source
    return (FIXTURES / name).read_text(encoding="utf-8")


def make_agent(**kw) -> RetrievalAgent:
    return RetrievalAgent(planner=HeuristicPlanner(), fetcher=fake_fetch, **kw)


def cited_urls(ans) -> set[str]:
    idx = {int(m) for m in re.findall(r"\[(\d+)\]", ans.answer)}
    return {c.url for c in ans.citations if c.index in idx}


class TestExtractPlus(unittest.TestCase):
    def test_lists_captured(self):
        page = extract(fake_fetch(ORCHID), ORCHID)
        self.assertIn(["Phalaenopsis amabilis", "Vanda coerulea",
                       "Dendrobium nobile"], page.lists)
        self.assertTrue(any(items and "timed ticket" in items[0]
                            for items in page.lists))

    def test_table_becomes_structured_records(self):
        page = extract(fake_fetch(CATALOG), CATALOG)
        self.assertEqual(len(page.records), 3)
        self.assertIn({"Title": "Paper Boats", "Author": "Lucia Ferrante",
                       "Status": "Available"}, page.records)
        self.assertEqual(page.records[1]["Status"], "Checked out")

    def test_links_captured_with_text(self):
        page = extract(fake_fetch(BOTANIC), BOTANIC)
        self.assertIn(("Visit the Orchid House", ORCHID), page.links)

    def test_generic_pagination_label_detected(self):
        # no rel=next anywhere: the "More events" anchor text alone chains it
        page = extract(fake_fetch(EVENTS), EVENTS)
        self.assertEqual(page.next_url, EVENTS2)

    def test_pagination_chain_followed(self):
        ans = make_agent().run("When is the night sky astronomy talk?",
                               [EVENTS])
        self.assertIn(EVENTS2, ans.pages_fetched)
        self.assertIn("Friday 7 PM", ans.answer)


class TestMultiHop(unittest.TestCase):
    def test_decomposition_splits_compound_request(self):
        subs = decompose("What are the opening hours and where is the "
                         "library located?")
        self.assertGreaterEqual(len(subs), 2)
        single = decompose("What are the opening hours?")
        self.assertEqual(len(single), 1)

    def test_cross_page_chain_two_sources_cited(self):
        ans = make_agent().run(
            "What are the botanic garden opening hours and what temperature "
            "is the orchid house kept at?", [BOTANIC])
        self.assertIn("8 AM to 6 PM", ans.answer)
        self.assertIn("24 degrees Celsius", ans.answer)
        self.assertGreaterEqual(len(cited_urls(ans)), 2)
        self.assertLessEqual({BOTANIC, ORCHID}, cited_urls(ans))

    def test_multihop_across_two_sites(self):
        ans = make_agent().run(
            "What does museum adult admission cost and what are the library "
            "opening hours?", [MUSEUM, HOME])
        self.assertIn("14 dollars", ans.answer)
        self.assertIn("9 AM to 8 PM", ans.answer)
        self.assertGreaterEqual(len(cited_urls(ans)), 2)

    def test_hop_bound_respected(self):
        ans = make_agent(max_hops=0).run(
            "What temperature is the orchid house kept at?", [BOTANIC])
        self.assertNotIn(ORCHID, ans.pages_fetched)
        self.assertNotIn("24 degrees", ans.answer)


class _FakeModelHandler(BaseHTTPRequestHandler):
    """Minimal local OpenAI-compatible server: /v1/models + chat completions
    returning one canned plan JSON. Stands in for llama.cpp/vLLM/Ollama."""

    hits: list[str] = []
    PLAN = {"urls": ["https://museum.example.test/visit"],
            "subqueries": ["adult admission price at the museum",
                           "museum opening and closing times"],
            "follow_pagination": False}

    def log_message(self, *args):
        pass

    def _send(self, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        type(self).hits.append(self.path)
        if self.path == "/v1/models":
            self._send({"data": [{"id": "fake-local-model"}]})
        else:
            self._send({})

    def do_POST(self):  # noqa: N802
        type(self).hits.append(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        if self.path == "/v1/chat/completions":
            self._send({"choices": [{"message": {
                "content": json.dumps(type(self).PLAN)}}]})
        else:
            self._send({})


class TestLLMPlannerLocalModel(unittest.TestCase):
    def setUp(self):
        _FakeModelHandler.hits = []
        self.server = HTTPServer(("127.0.0.1", 0), _FakeModelHandler)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_fake_local_model_drives_plan(self):
        env = {"AMD_M4_LOCAL_MODEL_URL": self.url}
        status = local_model_status(env)
        self.assertTrue(status["available"])
        self.assertEqual(status["kind"], "endpoint")
        planner = LLMPlanner(env=env)
        plan = planner.plan("How much is adult admission at the museum?")
        self.assertIn(MUSEUM, plan.urls)             # seed came from the model
        self.assertEqual(plan.subqueries, _FakeModelHandler.PLAN["subqueries"])
        self.assertFalse(plan.follow_pagination)
        self.assertIn("/v1/chat/completions", _FakeModelHandler.hits)
        # and the model-planned run actually answers from the fetched page
        agent = RetrievalAgent(planner=planner, fetcher=fake_fetch)
        ans = agent.run("How much is adult admission at the museum?")
        self.assertIn("14 dollars", ans.answer)

    def test_no_model_falls_back_to_heuristic(self):
        env = {"AMD_M4_MODEL_DIR": "/nonexistent-models-dir"}
        status = local_model_status(env)
        self.assertFalse(status["available"])
        plan = LLMPlanner(env=env).plan("What are the library opening hours?")
        self.assertEqual(plan.subqueries,
                         HeuristicPlanner().plan(
                             "What are the library opening hours?").subqueries)

    def test_dead_loopback_endpoint_falls_back(self):
        env = {"AMD_M4_LOCAL_MODEL_URL": "http://127.0.0.1:1"}
        self.assertFalse(local_model_status(env)["available"])
        plan = LLMPlanner(env=env).plan("What are the library opening hours?")
        self.assertEqual(plan.query, "What are the library opening hours?")

    def test_non_loopback_endpoint_refused_no_external_call(self):
        def forbidden_chat(prompt):  # must never be invoked
            raise AssertionError("external model call attempted")

        env = {"AMD_M4_LOCAL_MODEL_URL": "https://api.example.com"}
        status = local_model_status(env)
        self.assertFalse(status["available"])
        self.assertIn("refused", status["detail"])
        planner = LLMPlanner(status=status, env=env, chat=forbidden_chat)
        plan = planner.plan("What are the library opening hours?")
        self.assertEqual(plan.subqueries,
                         HeuristicPlanner().plan(
                             "What are the library opening hours?").subqueries)

    def test_weights_without_runtime_detected_not_available(self):
        try:
            import llama_cpp  # noqa: F401
            self.skipTest("llama_cpp present in this environment")
        except Exception:
            pass
        try:
            import transformers  # noqa: F401
            self.skipTest("transformers present in this environment")
        except Exception:
            pass
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "model.gguf").write_bytes(b"fake-weights")
            status = local_model_status({"AMD_M4_MODEL_DIR": tmp})
        self.assertFalse(status["available"])
        self.assertEqual(status["kind"], "inprocess")
        self.assertIn("no local runtime", status["detail"])

    def test_auto_planner_selects_heuristic_without_model(self):
        old = os.environ.get("AMD_M4_MODEL_DIR")
        os.environ["AMD_M4_MODEL_DIR"] = "/nonexistent-models-dir"
        try:
            self.assertIsInstance(make_planner("auto"), HeuristicPlanner)
        finally:
            if old is None:
                del os.environ["AMD_M4_MODEL_DIR"]
            else:
                os.environ["AMD_M4_MODEL_DIR"] = old


# >= 10 MORE unseen queries (wording in NO fixture). Structural assertions on
# all; content spot-checks where retrieval is deterministic; starred entries
# are multi-hop and must cite >= 2 distinct sources.
UNSEEN_P1 = [
    # (query, seeds, required answer fragments, min distinct cited sources)
    ("On Saturdays, when does the library open and what is the loan period "
     "for a borrowed book?", [HOME], ["10 AM", "three weeks"], 2),          # *
    ("What time does the botanic garden close and what humidity is the "
     "orchid house kept at?", [BOTANIC], ["6 PM", "70 percent"], 2),       # *
    ("Which orchid species are on display and who is the head keeper?",
     [ORCHID], ["Vanda coerulea", "Priya Raman"], 1),
    ("How do I visit the orchid house, step by step?",
     [BOTANIC], ["timed ticket"], 1),
    ("Can children get into the maritime museum for free?",
     [MUSEUM], ["children under 12 enter free"], 1),
    ("Is A Field Guide to Tides available to borrow right now?",
     [HOME], ["Checked out"], 1),
    ("Who wrote Paper Boats?", [HOME], ["Lucia Ferrante"], 1),
    ("When is the chess club at the library?", [EVENTS], ["Wednesday 4 PM"], 1),
    ("When is the night sky astronomy talk and where is it held?",
     [EVENTS], ["Friday 7 PM", "courtyard"], 1),
    ("What is the current exhibition at the museum and what does it cover?",
     [MUSEUM], ["Signals and Storms", "lighthouse"], 1),
    ("Where is the botanic garden located and when is last entry?",
     [BOTANIC], ["77 Fern Hollow Road", "5 PM"], 1),
    ("What does a museum adult ticket cost and when does the library shut "
     "on weekdays?", [MUSEUM, HOME], ["14 dollars", "8 PM"], 2),           # *
]


class TestUnseenQueriesP1(unittest.TestCase):
    def test_unseen_queries_p1(self):
        self.assertGreaterEqual(len(UNSEEN_P1), 10)
        fixture_text = " ".join(
            p.read_text(encoding="utf-8") for p in FIXTURES.glob("*.html")
        ).lower()
        for query, seeds, fragments, min_sources in UNSEEN_P1:
            self.assertNotIn(query.lower(), fixture_text)  # genuinely unseen
            with self.subTest(query=query):
                ans = make_agent().run(query, seeds)
                self.assertGreaterEqual(len(ans.citations), 1)
                self.assertRegex(ans.answer, r"\[\d+\]")
                self.assertLessEqual({c.url for c in ans.citations},
                                     set(ans.pages_fetched))
                self.assertNotIn("FIXTURE-LEAK-MARKER", ans.answer)
                self.assertNotIn("data-fixture", ans.answer)
                self.assertNotIn(".html", ans.answer)
                for frag in fragments:
                    self.assertIn(frag, ans.answer)
                self.assertGreaterEqual(len(cited_urls(ans)), min_sources)


if __name__ == "__main__":
    unittest.main()
