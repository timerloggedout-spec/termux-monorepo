"""First test coverage for the deepcli.observatory package.

Covers the pure/offline surface: kev (verifier), jev (critic),
mev (producer), laya (merger), doe (experiment design), leaderboard,
trial + tournament orchestration. All network hops are injected via a
``client_factory`` or an explicit Leaderboard path, so nothing here opens
a socket, touches the real ~/.deepcli/leaderboard.json, or sleeps.
"""

import asyncio
import pathlib
import sys
import tempfile
import unittest


def _repo_root():
    # The importable package is <checkout>/deepcli, i.e. the directory that
    # CONTAINS the deepcli/ package directory. From the test file, walk up to
    # the first ancestor holding deepcli/observatory (so the tests always
    # bind to THIS checkout, never $HOME/deepcli).
    here = pathlib.Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "deepcli" / "observatory").is_dir():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))

from deepcli.observatory import kev, jev, mev, laya, doe  # noqa: E402
from deepcli.observatory.leaderboard import Leaderboard  # noqa: E402
from deepcli.observatory.tournament import campaign  # noqa: E402


class _FakeReply:
    def __init__(self, text, tokens_in=0, tokens_out=0, cost_usd=0.0):
        self.text = text
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.cost_usd = cost_usd


class _FakeClient:
    def __init__(self, reply, factory=None):
        self._reply = reply
        self._factory = factory
        self.prompts = []

    async def ask(self, prompt, **kw):
        self.prompts.append(prompt)
        if self._factory is not None:
            self._factory(prompt)
        if isinstance(self._reply, Exception):
            raise self._reply
        return self._reply


def _factory_for(reply):
    def factory(provider, model):
        return _FakeClient(reply)

    return factory


class TestKev(unittest.TestCase):
    def test_token_f1_identical(self):
        out = kev.verify(
            {"text": "the quick brown fox"}, {"text": "the quick brown fox"}
        )
        self.assertEqual(out["role"], "kev")
        self.assertEqual(out["match_score"], 1.0)
        self.assertEqual(out["deltas"], [])

    def test_token_f1_partial_and_deltas(self):
        out = kev.verify({"text": "the quick brown fox"}, {"text": "the quick red fox"})
        self.assertAlmostEqual(out["match_score"], 0.75, places=4)
        self.assertEqual(out["deltas"], ["red"])

    def test_token_f1_empty_side(self):
        self.assertEqual(kev.verify({"text": ""}, {"text": "abc"})["match_score"], 0.0)
        self.assertEqual(kev.verify({"text": "abc"}, {"text": ""})["match_score"], 0.0)

    def test_reference_id_and_content_fallback(self):
        out = kev.verify({"text": "a b"}, {"content": "a b", "id": "ref-7"})
        self.assertEqual(out["reference_id"], "ref-7")
        self.assertEqual(out["match_score"], 1.0)

    def test_exact_match_and_mismatch(self):
        ok = kev.verify({"text": " hi "}, {"text": "hi"}, method="exact")
        self.assertEqual(ok["match_score"], 1.0)
        self.assertEqual(ok["deltas"], [])
        bad = kev.verify({"text": "hi"}, {"text": "bye"}, method="exact")
        self.assertEqual(bad["match_score"], 0.0)
        self.assertEqual(bad["deltas"], ["bye"])

    def test_unknown_method_raises(self):
        with self.assertRaises(ValueError):
            kev.verify({"text": "x"}, {"text": "y"}, method="nope")

    def test_deltas_capped_at_40(self):
        ref = " ".join(f"t{i}" for i in range(100))
        out = kev.verify({"text": ""}, {"text": ref})
        self.assertEqual(out["match_score"], 0.0)
        self.assertEqual(out["deltas"], [])
        out2 = kev.verify({"text": "t0"}, {"text": ref})
        self.assertLessEqual(len(out2["deltas"]), 40)


class TestJev(unittest.TestCase):
    def test_self_judging_rejected(self):
        art = {"provider": "deepseek", "model": "v3", "text": "x"}
        with self.assertRaises(ValueError):
            asyncio.run(
                jev.critique(
                    art,
                    {},
                    "deepseek",
                    "v3",
                    client_factory=_factory_for(_FakeReply("{}")),
                )
            )

    def test_parses_strict_json(self):
        reply = _FakeReply(
            'noise {"scores": {"clarity": 0.9}, "rationale": "good"} tail'
        )
        out = asyncio.run(
            jev.critique(
                {"provider": "a", "model": "m", "text": "hi"},
                {"clarity": "x"},
                "b",
                "n",
                client_factory=_factory_for(reply),
            )
        )
        self.assertEqual(out["scores"], {"clarity": 0.9})
        self.assertEqual(out["rationale"], "good")
        self.assertEqual(out["judge_provider"], "b")
        self.assertEqual(out["judge_model"], "n")

    def test_non_json_falls_back(self):
        out = asyncio.run(
            jev.critique(
                {"provider": "a", "model": "m", "text": "hi"},
                {},
                "b",
                "n",
                client_factory=_factory_for(_FakeReply("not json at all")),
            )
        )
        self.assertEqual(out["scores"], {})
        self.assertEqual(out["rationale"], "not json at all")

    def test_empty_braces_yields_empty(self):
        out = asyncio.run(
            jev.critique(
                {"provider": "a", "model": "m", "text": "hi"},
                {},
                "b",
                "n",
                client_factory=_factory_for(_FakeReply("{}")),
            )
        )
        self.assertEqual(out["scores"], {})

    def test_rubric_braces_do_not_crash_prompt(self):
        # Regression: a JSON rubric used to hit str.format() and raise
        # KeyError on the literal braces. Must build a prompt cleanly.
        seen = {}

        def factory(prompt):
            seen["prompt"] = prompt

        asyncio.run(
            jev.critique(
                {"provider": "a", "model": "m", "text": "hi"},
                {"clarity": {"weight": 1}, "style": {"weight": 2}},
                "b",
                "n",
                client_factory=lambda p, m: _FakeClient(
                    _FakeReply("{}"), factory=factory
                ),
            )
        )
        self.assertIn("clarity", seen["prompt"])

    def test_artifact_text_truncated_in_prompt(self):
        seen = {}

        def factory(prompt):
            seen["prompt"] = prompt

        big = "Z" * 9000
        asyncio.run(
            jev.critique(
                {"provider": "a", "model": "m", "text": big},
                {},
                "b",
                "n",
                client_factory=lambda p, m: _FakeClient(
                    _FakeReply("{}"), factory=factory
                ),
            )
        )
        self.assertLess(len(seen["prompt"]), 9000)


class TestMev(unittest.TestCase):
    def test_produce_captures_fields(self):
        reply = _FakeReply("hello world", tokens_in=3, tokens_out=5, cost_usd=0.02)
        out = asyncio.run(
            mev.produce("p", "prov", "mod", client_factory=_factory_for(reply))
        )
        self.assertEqual(out["role"], "mev")
        self.assertEqual(out["text"], "hello world")
        self.assertEqual(out["tokens_in"], 3)
        self.assertEqual(out["tokens_out"], 5)
        self.assertEqual(out["cost_usd"], 0.02)
        self.assertGreaterEqual(out["latency_ms"], 0)

    def test_produce_defaults_for_bare_string(self):
        out = asyncio.run(
            mev.produce("p", "prov", "mod", client_factory=_factory_for("plain"))
        )
        self.assertEqual(out["text"], "plain")
        self.assertEqual(out["tokens_in"], 0)
        self.assertEqual(out["cost_usd"], 0.0)


class TestLaya(unittest.TestCase):
    def _art(self, provider, text):
        return {"provider": provider, "model": "m", "text": text}

    def test_ranking_and_winner(self):
        arts = [self._art("low", "L"), self._art("high", "H")]
        js = [
            {"scores": {"a": 0.1}, "judge_model": "j"},
            {"scores": {"a": 0.9}, "judge_model": "j"},
        ]
        ks = [
            {"match_score": 0.0, "reference_id": "r"},
            {"match_score": 1.0, "reference_id": "r"},
        ]
        out = laya.synthesize(arts, js, ks)
        self.assertEqual(out["role"], "laya")
        self.assertEqual(out["winner"]["provider"], "high")
        self.assertEqual(out["synthesis"], "H")
        self.assertEqual([r["provider"] for r in out["ranked"]], ["high", "low"])

    def test_empty_inputs(self):
        out = laya.synthesize([], [], [])
        self.assertIsNone(out["winner"])
        self.assertEqual(out["ranked"], [])
        self.assertEqual(out["synthesis"], "")

    def test_custom_weights(self):
        arts = [self._art("a", "A")]
        js = [{"scores": {"x": 1.0}}]
        ks = [{"match_score": 0.0}]
        out = laya.synthesize(arts, js, ks, weights={"jev": 0.0, "kev": 1.0})
        self.assertEqual(out["ranked"][0]["composite"], 0.0)
        self.assertEqual(out["weights"], {"jev": 0.0, "kev": 1.0})

    def test_tie_broken_by_kev(self):
        arts = [self._art("p1", "1"), self._art("p2", "2")]
        js = [{"scores": {"a": 0.5}}, {"scores": {"a": 0.5}}]
        ks = [{"match_score": 0.0}, {"match_score": 0.0}]
        out = laya.synthesize(arts, js, ks)
        self.assertEqual(len(out["ranked"]), 2)
        self.assertEqual(len(out["provenance"]), 2)


class TestDoe(unittest.TestCase):
    def test_full_factorial(self):
        out = doe.full_factorial({"a": [1, 2], "b": ["x", "y"]})
        self.assertEqual(len(out), 4)
        self.assertIn({"a": 1, "b": "x"}, out)

    def test_full_factorial_single(self):
        self.assertEqual(doe.full_factorial({"a": [1]}), [{"a": 1}])

    def test_taguchi_l9_shape(self):
        factors = {"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]}
        rows = doe.taguchi_l9(factors)
        self.assertEqual(len(rows), 9)
        for r in rows:
            self.assertEqual(set(r), {"a", "b", "c"})

    def test_taguchi_rejects_bad_shape(self):
        with self.assertRaises(ValueError):
            doe.taguchi_l9({"a": [1, 2], "b": [1, 2, 3]})
        with self.assertRaises(ValueError):
            doe.taguchi_l9({f"f{i}": [1, 2, 3] for i in range(5)})

    def test_mvt_shuffle_deterministic(self):
        a = doe.mvt_shuffle(["x", "y", "z"], 20, seed=1)
        b = doe.mvt_shuffle(["x", "y", "z"], 20, seed=1)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 20)
        self.assertTrue(set(a) <= {"x", "y", "z"})

    def test_mvt_shuffle_empty(self):
        self.assertEqual(doe.mvt_shuffle(["x"], 0, seed=2), [])


class TestLeaderboard(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp()) / "lb.json"
        self.lb = Leaderboard(str(self.tmp))

    def test_record_and_top(self):
        self.lb.record(
            "role", "task", "prov", "m", score=0.8, cost=0.01, latency_ms=100
        )
        self.lb.record(
            "role", "task", "prov", "m", score=0.6, cost=0.01, latency_ms=200
        )
        top = self.lb.top("role", "task")
        self.assertEqual(len(top), 1)
        self.assertAlmostEqual(top[0]["avg_score"], 0.7, places=4)
        self.assertEqual(top[0]["runs"], 2)
        self.assertAlmostEqual(top[0]["avg_latency_ms"], 150.0, places=1)

    def test_ok_rate_reduces_composite(self):
        self.lb.record("r", "t", "p", "m", score=1.0, ok=True)
        self.lb.record("r", "t", "p", "m", score=1.0, ok=False)
        top = self.lb.top("r", "t")
        self.assertEqual(top[0]["ok_rate"], 0.5)
        self.assertAlmostEqual(top[0]["composite"], 0.5, places=4)

    def test_persistence_roundtrip(self):
        self.lb.record("r", "t", "p", "m", score=0.5)
        reloaded = Leaderboard(str(self.tmp))
        self.assertEqual(len(reloaded.top("r", "t")), 1)

    def test_corrupt_file_is_reset(self):
        self.tmp.write_text("{not json")
        lb = Leaderboard(str(self.tmp))
        self.assertEqual(lb.data, {})

    def test_top_filters_by_role_and_task(self):
        self.lb.record("r", "t", "p", "m", score=0.5)
        self.lb.record("other", "t", "p", "m", score=0.5)
        self.lb.record("r", "other", "p", "m", score=0.5)
        self.assertEqual(len(self.lb.top("r", "t")), 1)

    def test_composition_hash_in_key(self):
        self.lb.record("r", "t", "p", "m", score=0.5, composition_hash="abc")
        self.lb.record("r", "t", "p", "m", score=0.5, composition_hash="def")
        self.assertEqual(len(self.lb.top("r", "t")), 2)

    def test_worst_is_reverse_of_top(self):
        self.lb.record("r", "t", "hi", "m", score=0.9)
        self.lb.record("r", "t", "lo", "m", score=0.1)
        worst = self.lb.worst("r", "t")
        self.assertEqual(worst[0]["provider"], "lo")


class TestTournament(unittest.TestCase):
    def test_campaign_records_and_ranks(self):
        tmp = pathlib.Path(tempfile.mkdtemp()) / "lb.json"
        lb = Leaderboard(str(tmp))
        results = [
            {"provider": "a", "model": "m", "composite": 0.9, "ok": True},
            {"provider": "b", "model": "m", "composite": 0.2, "ok": True},
        ]
        out = campaign("role", "task", results, leaderboard=lb)
        self.assertEqual(out["trials"], 2)
        self.assertEqual(out["winners"][0]["provider"], "a")
        self.assertEqual(out["losers"][0]["provider"], "b")

    def test_campaign_defaults_missing_fields(self):
        tmp = pathlib.Path(tempfile.mkdtemp()) / "lb.json"
        lb = Leaderboard(str(tmp))
        out = campaign("role", "task", [{}], leaderboard=lb)
        self.assertEqual(out["trials"], 1)
        self.assertEqual(out["winners"][0]["provider"], "?")


if __name__ == "__main__":
    unittest.main()
