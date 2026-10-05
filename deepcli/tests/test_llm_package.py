"""deepcli.llm — base dataclasses/ABC, registry, quota, router.

All offline: registry/quota state is redirected to a tmpdir; router's
classifier and adapter resolution are monkeypatched, so no network, no
sqlite, no real sleeps.
"""

import pathlib
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))

from deepcli.llm import base, quota, registry, router  # noqa: E402


class TestBaseDataclasses(unittest.TestCase):
    def test_layer_defaults(self):
        layer = base.Layer("research", "liner", "find papers")
        self.assertEqual(layer.role, "research")
        self.assertEqual(layer.app, "liner")
        self.assertEqual(layer.prompt, "find papers")
        self.assertIsNone(layer.depends_on)

    def test_layer_depends_on(self):
        layer = base.Layer("draft", "deepseek", "write", depends_on="research")
        self.assertEqual(layer.depends_on, "research")

    def test_plan_defaults(self):
        plan = base.Plan(layers=[])
        self.assertEqual(plan.layers, [])
        self.assertEqual(plan.rationale, "")
        self.assertEqual(plan.classifier, "deepseek")

    def test_plan_holds_layers(self):
        layers = [base.Layer("route", "deepseek", "hi")]
        plan = base.Plan(layers=layers, rationale="why")
        self.assertIs(plan.layers, layers)
        self.assertEqual(plan.rationale, "why")

    def test_reply_defaults(self):
        reply = base.Reply(app="deepseek", text="hello")
        self.assertIsNone(reply.raw)
        self.assertFalse(reply.interrupted)
        self.assertEqual(reply.quota_used, 1)

    def test_reply_overrides(self):
        reply = base.Reply(
            app="x", text="t", raw={"a": 1}, interrupted=True, quota_used=3
        )
        self.assertEqual(reply.raw, {"a": 1})
        self.assertTrue(reply.interrupted)
        self.assertEqual(reply.quota_used, 3)


class _Concrete(base.LLMAdapter):
    name = "concrete"

    def __init__(self):
        self.asked = []

    def ask(self, prompt, **kw):
        self.asked.append(prompt)
        return base.Reply(app=self.name, text=f"echo:{prompt}")

    def models(self):
        return ["m1", "m2"]


class TestLLMAdapter(unittest.TestCase):
    def test_cannot_instantiate_abstract(self):
        with self.assertRaises(TypeError):
            base.LLMAdapter()

    def test_class_defaults(self):
        self.assertEqual(base.LLMAdapter.name, "abstract")
        self.assertEqual(base.LLMAdapter.package, "")
        self.assertEqual(base.LLMAdapter.role, "llm")
        self.assertEqual(base.LLMAdapter.categories, ())

    def test_concrete_ask(self):
        a = _Concrete()
        rep = a.ask("hi")
        self.assertEqual(rep.text, "echo:hi")
        self.assertEqual(a.asked, ["hi"])

    def test_stream_default_yields_full_text(self):
        a = _Concrete()
        self.assertEqual(list(a.stream("yo")), ["echo:yo"])

    def test_quota_default(self):
        self.assertEqual(
            _Concrete().quota(),
            {"remaining": None, "resets": None, "mode": "unknown"},
        )

    def test_resume_default_reasks(self):
        a = _Concrete()
        rep = a.resume({"prompt": "resume me"})
        self.assertEqual(rep.text, "echo:resume me")

    def test_resume_default_no_prompt(self):
        a = _Concrete()
        rep = a.resume({})
        self.assertEqual(rep.text, "echo:")


class TestQuota(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self._orig = quota.STATE
        quota.STATE = self.tmp

    def tearDown(self):
        quota.STATE = self._orig

    def test_load_missing_returns_defaults(self):
        rec = quota.load("fresh")
        self.assertEqual(rec["calls_today"], 0)
        self.assertEqual(rec["mode"], "unknown")
        self.assertIsNone(rec["checkpoint"])
        self.assertEqual(rec["day"], quota._today())

    def test_save_then_load_roundtrip(self):
        quota.save("app", {"calls_today": 5, "day": quota._today()})
        rec = quota.load("app")
        self.assertEqual(rec["calls_today"], 5)

    def test_record_ok_increments_and_stamps(self):
        quota.record_ok("app")
        rec = quota.load("app")
        self.assertEqual(rec["calls_today"], 1)
        self.assertIsNotNone(rec["last_ok"])
        self.assertIsNone(rec["backoff_until"])

    def test_record_ok_resets_on_new_day(self):
        quota.save(
            "app",
            {
                "calls_today": 9,
                "day": "1970-01-01",
                "backoff_until": None,
                "checkpoint": None,
            },
        )
        quota.record_ok("app")
        rec = quota.load("app")
        self.assertEqual(rec["calls_today"], 1)
        self.assertEqual(rec["day"], quota._today())

    def test_set_backoff_blocks(self):
        quota.set_backoff("app", 60, "rate-limited")
        rec = quota.load("app")
        self.assertGreater(rec["backoff_until"], time.time())
        self.assertEqual(rec["backoff_reason"], "rate-limited")

    def test_is_available_ok(self):
        avail, why = quota.is_available("app")
        self.assertTrue(avail)
        self.assertEqual(why, "ok")

    def test_is_available_new_day(self):
        quota.save(
            "app",
            {
                "calls_today": 3,
                "day": "1970-01-01",
                "backoff_until": time.time() + 999,
                "checkpoint": None,
            },
        )
        avail, why = quota.is_available("app")
        self.assertTrue(avail)
        self.assertEqual(why, "new-day")

    def test_is_available_backoff(self):
        quota.set_backoff("app", 120, "x")
        avail, why = quota.is_available("app")
        self.assertFalse(avail)
        self.assertTrue(why.startswith("backoff "))

    def test_is_available_expired_backoff(self):
        quota.save(
            "app",
            {
                "calls_today": 1,
                "day": quota._today(),
                "backoff_until": time.time() - 5,
                "checkpoint": None,
            },
        )
        avail, why = quota.is_available("app")
        self.assertTrue(avail)
        self.assertEqual(why, "ok")

    def test_checkpoint_set_and_clear(self):
        quota.checkpoint("app", {"prompt": "p", "cursor": 3})
        self.assertEqual(quota.load("app")["checkpoint"], {"prompt": "p", "cursor": 3})
        quota.clear_checkpoint("app")
        self.assertIsNone(quota.load("app")["checkpoint"])

    def test_f_helper_path(self):
        self.assertEqual(quota._f("x"), self.tmp / "x.json")


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.surface = self.tmp / "surface.json"
        self._orig = registry.SURFACE
        registry.SURFACE = self.surface

    def tearDown(self):
        registry.SURFACE = self._orig

    def _write(self, obj):
        import json

        self.surface.write_text(json.dumps(obj))

    def test_load_surface_missing(self):
        self.assertEqual(registry.load_surface(), {"apps": [], "by_role": {}})

    def test_load_surface_reads_json(self):
        self._write({"apps": [{"name": "a"}]})
        self.assertEqual(registry.load_surface(), {"apps": [{"name": "a"}]})

    def test_by_role(self):
        self._write(
            {
                "apps": [
                    {"name": "liner", "role": "research"},
                    {"name": "deepseek", "role": "llm"},
                    {"name": "perplexity", "role": "research"},
                ]
            }
        )
        names = [a["name"] for a in registry.by_role("research")]
        self.assertEqual(names, ["liner", "perplexity"])

    def test_by_name_found_and_missing(self):
        self._write({"apps": [{"name": "liner", "role": "research"}]})
        self.assertEqual(registry.by_name("liner")["role"], "research")
        self.assertIsNone(registry.by_name("nope"))

    def test_all_names(self):
        self._write({"apps": [{"name": "a"}, {"name": "b"}]})
        self.assertEqual(registry.all_names(), ["a", "b"])

    def test_catalog_groups_by_role_and_skips_empty(self):
        self._write(
            {
                "apps": [
                    {"name": "deepseek", "role": "llm", "categories": ["code", "chat"]},
                    {"name": "liner", "role": "research", "categories": ["papers"]},
                ]
            }
        )
        out = registry.catalog_for_classifier()
        self.assertIn("[llm]", out)
        self.assertIn("[research]", out)
        self.assertIn("deepseek", out)
        self.assertIn("code,chat", out)
        self.assertNotIn("[agent]", out)

    def test_resolve_missing_returns_none(self):
        self.assertIsNone(registry.resolve("definitely_not_a_real_adapter_xyz"))

    def test_resolve_loads_adapter_class(self):
        # inject a fake module into sys.modules for both candidate paths
        import types
        import sys as _sys

        mod = types.ModuleType("deepcli.llm.adapters.fake_adapter")

        class Adapter:
            name = "fake"

        mod.Adapter = Adapter
        _sys.modules["deepcli.llm.adapters.fake_adapter"] = mod
        try:
            got = registry.resolve("fake_adapter")
        finally:
            _sys.modules.pop("deepcli.llm.adapters.fake_adapter", None)
        self.assertIsInstance(got, Adapter)

    def test_resolve_module_without_adapter_attr(self):
        import types
        import sys as _sys

        mod = types.ModuleType("deepcli.llm.adapters.empty_mod")
        _sys.modules["deepcli.llm.adapters.empty_mod"] = mod
        try:
            self.assertIsNone(registry.resolve("empty_mod"))
        finally:
            _sys.modules.pop("deepcli.llm.adapters.empty_mod", None)


class TestRouterDispatch(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self._orig_state = quota.STATE
        quota.STATE = self.tmp

    def tearDown(self):
        quota.STATE = self._orig_state

    def test_dispatch_preview_does_not_resolve(self):
        plan = base.Plan(layers=[base.Layer("route", "deepseek", "hi")])
        res = router.dispatch(plan, execute=False)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["status"], "preview")
        self.assertEqual(res[0]["index"], 0)
        self.assertEqual(res[0]["role"], "route")
        self.assertIn("quota", res[0])

    def test_dispatch_execute_no_adapter(self):
        plan = base.Plan(layers=[base.Layer("route", "ghost", "hi")])
        res = router.dispatch(plan, execute=True)
        self.assertEqual(res[0]["status"], "no-adapter")

    def test_dispatch_execute_skipped_on_backoff(self):
        quota.set_backoff("busy", 300, "rl")
        plan = base.Plan(layers=[base.Layer("route", "busy", "hi")])
        res = router.dispatch(plan, execute=True)
        self.assertEqual(res[0]["status"], "skipped-quota")

    def test_dispatch_execute_ok_and_feeds_previous(self):
        calls = []

        class FakeAdapter:
            def ask(self, prompt, **kw):
                calls.append(prompt)
                return base.Reply(app="fake", text=f"out{len(calls)}")

        _orig_resolve = registry.resolve
        registry.resolve = lambda name: FakeAdapter() if name == "fake" else None
        try:
            plan = base.Plan(
                layers=[
                    base.Layer("research", "fake", "first"),
                    base.Layer("draft", "fake", "second"),
                ]
            )
            res = router.dispatch(plan, execute=True)
        finally:
            registry.resolve = _orig_resolve
        self.assertEqual([r["status"] for r in res], ["ok", "ok"])
        self.assertEqual(res[1]["reply_head"], "out2")
        # second prompt must carry previous output, first must not
        self.assertEqual(calls[0], "first")
        self.assertIn("INPUT FROM PREVIOUS LAYER:\nout1", calls[1])

    def test_dispatch_depends_on_skips_injection(self):
        calls = []

        class FakeAdapter:
            def ask(self, prompt, **kw):
                calls.append(prompt)
                return base.Reply(app="fake", text="X")

        _orig_resolve = registry.resolve
        registry.resolve = lambda name: FakeAdapter()
        try:
            plan = base.Plan(
                layers=[
                    base.Layer("research", "fake", "a"),
                    base.Layer("draft", "fake", "b", depends_on="research"),
                ]
            )
            router.dispatch(plan, execute=True)
        finally:
            registry.resolve = _orig_resolve
        self.assertEqual(calls[1], "b")

    def test_dispatch_execute_error_captured(self):
        class BoomAdapter:
            def ask(self, prompt, **kw):
                raise ValueError("kaboom")

        _orig_resolve = registry.resolve
        registry.resolve = lambda name: BoomAdapter()
        try:
            plan = base.Plan(layers=[base.Layer("route", "boom", "hi")])
            res = router.dispatch(plan, execute=True)
        finally:
            registry.resolve = _orig_resolve
        self.assertEqual(res[0]["status"], "error: ValueError")
        self.assertEqual(res[0]["error"], "kaboom")

    def test_classifier_prompt_has_placeholders(self):
        self.assertIn("{catalog}", router.CLASSIFIER_PROMPT)
        self.assertIn("{prompt}", router.CLASSIFIER_PROMPT)


class TestRouterClassify(unittest.TestCase):
    """Exercise _classify with a stubbed deepcli.core module."""

    def setUp(self):
        import types
        import sys as _sys

        self.surface_tmp = pathlib.Path(tempfile.mkdtemp()) / "surface.json"
        import json as _json

        self.surface_tmp.write_text(
            _json.dumps(
                {
                    "apps": [
                        {"name": "deepseek", "role": "llm", "categories": ["code"]},
                        {"name": "liner", "role": "research", "categories": ["papers"]},
                    ]
                }
            )
        )
        self._orig_surface = registry.SURFACE
        registry.SURFACE = self.surface_tmp

        self.core = types.ModuleType("deepcli.core")
        self.core.get_token = lambda: "tok"
        self.core.create_session = lambda tok, model_type="default": "sid"
        self.reply_box = {"reply": ""}
        self.core.chat_completion = lambda tok, prompt, sid, max_continues=1: (
            self.reply_box["reply"]
        )
        self._sys = _sys
        self._orig_core = _sys.modules.get("deepcli.core")
        _sys.modules["deepcli.core"] = self.core

    def tearDown(self):
        registry.SURFACE = self._orig_surface
        if self._orig_core is not None:
            self._sys.modules["deepcli.core"] = self._orig_core
        else:
            self._sys.modules.pop("deepcli.core", None)

    def test_classify_valid_json(self):
        self.reply_box["reply"] = (
            '{"layers": [{"role": "research", "app": "liner", '
            '"prompt": "go"}], "rationale": "because"}'
        )
        plan = router._classify("study")
        self.assertEqual(plan.rationale, "because")
        self.assertEqual(len(plan.layers), 1)
        self.assertEqual(plan.layers[0].app, "liner")

    def test_classify_invalid_app_falls_back_to_deepseek(self):
        self.reply_box["reply"] = (
            '{"layers": [{"role": "x", "app": "ghost", "prompt": "p"}]}'
        )
        plan = router._classify("q")
        self.assertEqual(plan.layers[0].app, "deepseek")

    def test_classify_defaults_for_missing_fields(self):
        self.reply_box["reply"] = '{"layers": [{"app": "liner"}]}'
        plan = router._classify("q")
        self.assertEqual(plan.layers[0].role, "route")
        self.assertEqual(plan.layers[0].prompt, "q")

    def test_classify_non_json_falls_back(self):
        self.reply_box["reply"] = "no json here at all"
        plan = router._classify("q")
        self.assertEqual(plan.layers[0].app, "deepseek")
        self.assertIn("non-JSON", plan.rationale)

    def test_classify_bad_json_falls_back(self):
        self.reply_box["reply"] = "{not valid json}"
        plan = router._classify("q")
        self.assertEqual(plan.layers[0].app, "deepseek")
        self.assertIn("parse failed", plan.rationale)

    def test_plan_public_wrapper(self):
        self.reply_box["reply"] = '{"layers": [], "rationale": "r"}'
        plan = router.plan("q")
        self.assertEqual(plan.rationale, "r")
        self.assertEqual(plan.layers, [])


if __name__ == "__main__":
    unittest.main()
